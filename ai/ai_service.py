
import json
import re
import queue
import threading
import requests
from utils.helpers import normalize_digits, normalize_number, remove_latin_words
from utils.stop_control import StopRequested, stop_requested

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "qwen3.5:latest"

def build_prompt(letter_text: str) -> str:
    return f"""
تو یک دستیار هوش مصنوعی برای خلاصه‌سازی نامه‌های اداری فارسی هستی.

وظیفه تو فقط تحلیل محتوای نامه و تولید یک خلاصه کوتاه و رسمی است.

قوانین خلاصه:

1. خلاصه باید دقیقاً 2 جمله کوتاه و رسمی فارسی باشد.

2. خلاصه باید بر اساس محتوای اصلی نامه نوشته شود، نه صرفاً عنوان یا اولین جمله نامه.

3. در خلاصه مشخص کن:
   - نامه درباره چیست؟
   - چه درخواست، اطلاع‌رسانی یا اقدامی مطرح شده است؟

4. اگر نامه از مخاطب انجام کاری می‌خواهد، آن اقدام را در خلاصه بیاور.

5. از جملاتی مانند این‌ها استفاده نکن:
   - «این نامه در پاسخ به...»
   - «نامه مذکور...»
   - «در این نامه آمده است...»
   - «پاسخ به نامه...»
   مگر اینکه واقعاً محتوای اصلی نامه درباره پاسخ به یک نامه قبلی باشد.

6. متن نامه را کپی نکن؛ آن را خلاصه کن.

7. اطلاعات فرعی، شماره نامه، شناسه ملی، قیمت‌ها، جدول‌ها و موارد کم‌اهمیت را فقط در صورتی در خلاصه بیاور که برای درک موضوع اصلی ضروری باشند.

8. خلاصه باید طبیعی، قابل فهم و مناسب ثبت در یک سامانه اداری باشد.

9. هیچ کلمه انگلیسی در مقدار summary ننویس.

10. اگر نامه ددلاین، مهلت انجام کار یا تاریخ مشخص برای انجام یک اقدام دارد، فقط همان تاریخ را در deadline قرار بده.

11. تاریخ ابتدای نامه یا تاریخ صدور نامه، ددلاین محسوب نمی‌شود؛ مگر اینکه متن صراحتاً آن تاریخ را به عنوان مهلت انجام کار مشخص کرده باشد.

12. اگر هیچ ددلاین مشخصی وجود ندارد، مقدار deadline باید null باشد.

13. تاریخ‌ها را دقیقاً مطابق متن نامه نگه دار.

14. خروجی فقط JSON باشد.

15. نام کلیدهای JSON باید دقیقاً همین دو مورد باشند:
summary
deadline

این دو کلید انگلیسی هستند و نباید حذف، ترجمه یا تغییر داده شوند.

قالب خروجی:

{{
  "summary": "خلاصه دو تا سه جمله‌ای فارسی",
  "deadline": null
}}

متن نامه:
--------------------
{letter_text}
--------------------
""".strip()

def _extract_date_only(text: str):
    if not text:
        return None

    text = normalize_number(str(text)).strip()

    for pattern in (
        r"\b(\d{4})[/-](\d{1,2})[/-](\d{1,2})\b",
        r"\b(\d{1,2})[/-](\d{1,2})[/-](\d{4})\b"
    ):
        match = re.search(pattern, text)
        if match:
            a, b, c = match.groups()
            if len(a) == 4:
                return f"{a.zfill(4)}/{b.zfill(2)}/{c.zfill(2)}"
            return f"{c.zfill(4)}/{b.zfill(2)}/{a.zfill(2)}"

    return None

def normalize_deadline(deadline):
    return _extract_date_only(deadline)

def extract_deadline_from_text(letter_text: str):
    if not letter_text:
        return None

    text = normalize_digits(letter_text)

    for pattern in (
        r"تا\s*تاریخ\s*(\d{4}/\d{1,2}/\d{1,2})",
        r"تا\s+(\d{4}/\d{1,2}/\d{1,2})",
        r"لغایت\s*(\d{4}/\d{1,2}/\d{1,2})",
        r"مهلت.{0,100}?(?:تا\s*)?(\d{4}/\d{1,2}/\d{1,2})",
        r"حداکثر.{0,50}?(?:تا\s*)?(\d{4}/\d{1,2}/\d{1,2})",
        r"(?:اعلام|ارسال|ارائه|انجام|تحویل).{0,100}?(?:تا|لغایت)\s*(\d{4}/\d{1,2}/\d{1,2})"
    ):
        match = re.search(pattern, text, flags=re.IGNORECASE | re.DOTALL)
        if match:
            return normalize_deadline(match.group(1))

    return None

def _extract_json_object(raw_text: str) -> dict:
    if not raw_text:
        return {}

    cleaned = raw_text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned)

    match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
    if not match:
        return {}

    try:
        data = json.loads(match.group(0))
        if isinstance(data, dict):
            return data
    except Exception:
        pass

    return {}

def _get_summary_from_data(data):
    if not isinstance(data, dict):
        return ""

    for key in ("summary", "خلاصه", "description", "توضیح"):
        if data.get(key):
            return str(data[key]).strip()

    values = [
        str(v).strip()
        for k, v in data.items()
        if k not in ("deadline", "ددلاین") and v
    ]

    return " ".join(values) if values else ""

def _get_deadline_from_data(data):
    if not isinstance(data, dict):
        return None

    for key in ("deadline", "ددلاین", "مهلت"):
        value = data.get(key)
        if value is not None and value not in ("", "null", "None"):
            return normalize_deadline(value)

    return None

def _generate_response(payload: dict) -> str:
    """Read Ollama's streamed response while checking for a stop request."""
    events = queue.Queue()
    response_holder = {"response": None}

    def request_worker():
        response = None
        try:
            response = requests.post(
                OLLAMA_URL,
                json=payload,
                stream=True,
                timeout=(5, 600),
            )
            response_holder["response"] = response
            if response.status_code != 200:
                events.put(("error", RuntimeError("Ollama request failed")))
                return

            for line in response.iter_lines(decode_unicode=True):
                if not line:
                    continue
                if isinstance(line, bytes):
                    line = line.decode("utf-8", errors="replace")
                item = json.loads(line)
                chunk = item.get("response", "")
                if chunk:
                    events.put(("chunk", chunk))
                if item.get("done"):
                    break
            events.put(("done", None))
        except Exception as error:
            events.put(("error", error))
        finally:
            if response is not None:
                try:
                    response.close()
                except requests.RequestException:
                    pass

    threading.Thread(target=request_worker, daemon=True).start()
    chunks = []

    while True:
        if stop_requested():
            response = response_holder["response"]
            if response is not None:
                try:
                    response.close()
                except Exception:
                    pass
            raise StopRequested("Bot stopped during AI analysis")

        try:
            kind, value = events.get(timeout=0.2)
        except queue.Empty:
            continue

        if kind == "chunk":
            chunks.append(value)
        elif kind == "error":
            raise value
        else:
            return "".join(chunks)

def ask_ai(letter_text: str) -> dict:
    prompt = build_prompt(letter_text)

    raw_answer = _generate_response({
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": True,
        "think": False,
        "format": "json",
        "options": {
            "temperature": 0,
            "top_p": 0.8
        }
    }).strip()

    print("\n" + "=" * 80)
    print("🤖 پاسخ خام هوش مصنوعی")
    print("=" * 80)
    print(raw_answer)
    print("=" * 80)

    data = _extract_json_object(raw_answer)

    summary = remove_latin_words(_get_summary_from_data(data))
    deadline = _get_deadline_from_data(data)

    if not deadline:
        deadline = extract_deadline_from_text(letter_text)

    print("\n" + "=" * 80)
    print("📋 نتیجه نهایی AI")
    print("=" * 80)
    print(f"📝 خلاصه: {summary}")
    print(f"⏰ ددلاین: {deadline}")
    print("=" * 80)

    return {
        "summary": summary,
        "deadline": deadline
    }
