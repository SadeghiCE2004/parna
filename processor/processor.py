import time
from extractors.text_extractor import extract_letter_text
from handlers.iframe_handlers import switch_to_main_iframe
from handlers.file_menu import click_text_file_menu
from handlers.letter_operations import open_letter, close_letter_window
from utils.helpers import clean_text, normalize_number
from ai.ai_service import ask_ai
from config import random_sleep

from data_bridge import add_letter_to_storage
import builtins
from utils.stop_control import StopRequested
from utils.progress_control import report_progress

def process_letter(driver, letter):

    if getattr(builtins, 'STOP_BOT', False):
        print("⏹️ توقف درخواست شده - پردازش نامه متوقف شد.")
        return {
            "letter_number": letter.get("number", ""),
            "number": letter.get("number", ""),
            "date": letter.get("date", ""),
            "time": letter.get("time", ""),
            "title": letter.get("title", ""),
            "text": "",
            "ai_result": {"summary": "", "deadline": None},
            "cancelled": True,
        }

    number = normalize_number(letter.get("number", "")) or f"unknown_{int(time.time())}"

    title = clean_text(letter.get("title", "")) or clean_text(letter.get("subject", ""))
    date = clean_text(letter.get("date", ""))
    letter_time = clean_text(letter.get("time", ""))

    print(f"\n{'=' * 80}")
    print(f"📄 پردازش نامه: {number}")
    print(f"📅 تاریخ: {date}")
    print(f"⏰ ساعت: {letter_time}")
    print(f"📌 موضوع: {title}")
    print("=" * 80)

    text = ""
    ai_result = {"summary": "", "deadline": None}

    def report_stage(completed_steps, message):
        report_progress(round(completed_steps * 100 / 7), message, number, title)

    report_stage(0, "در حال بازکردن نامه...")

    try:
        open_letter(driver, letter)
        report_stage(1, "نامه باز شد؛ در حال بازکردن بخش فایل‌های متنی...")
        click_text_file_menu(driver)

        report_stage(2, "بخش فایل‌های متنی باز شد؛ در حال استخراج متن...")
        text = extract_letter_text(driver)
        if not text.strip():
            raise Exception("متن نامه خالی است.")

        print(f"\n{'=' * 80}")
        print("🤖 ارسال متن به هوش مصنوعی...")
        print("=" * 80)

        report_stage(3, "متن استخراج شد؛ در حال تحلیل با هوش مصنوعی...")

        ai_succeeded = True
        try:
            ai_result = ask_ai(text)
            if not isinstance(ai_result, dict):
                ai_result = {"summary": str(ai_result), "deadline": None}

            print("✅ تحلیل هوش مصنوعی انجام شد.")
            print(f"📝 خلاصه: {ai_result.get('summary', '')}")
            print(f"⏰ ددلاین: {ai_result.get('deadline')}")

        except StopRequested:
            raise
        except Exception as e:
            ai_succeeded = False
            print(f"⚠️ خطا در هوش مصنوعی: {e}")
            ai_result = {"summary": "", "deadline": None}

        if ai_succeeded:
            report_stage(4, "تحلیل هوش مصنوعی کامل شد؛ در حال بستن نامه...")
        else:
            report_stage(4, "تحلیل هوش مصنوعی ناموفق بود؛ در حال بستن نامه...")
        close_letter_window(driver, number)
        random_sleep(1, 2)

        driver.switch_to.default_content()
        switch_to_main_iframe(driver)
        random_sleep(1, 2)
        report_stage(5, "نامه بسته شد و کارتابل آماده است؛ در حال ثبت اطلاعات...")

        try:
            add_letter_to_storage({
                "number": number,
                "date": date,
                "time": letter_time,
                "title": title,
                "signer": letter.get("signer", ""),
                "referral_description": letter.get("referral_description", ""),
                "ai_result": ai_result
            })
            report_stage(6, "اطلاعات نامه ثبت شد؛ در انتظار ذخیره‌ی نهایی...")
        except Exception as e:
            print(f"⚠️ خطا در ارسال به گرافیک: {e}")
            report_stage(6, "ثبت اطلاعات پایان یافت؛ در انتظار ذخیره‌ی نهایی...")

        return {
            "letter_number": number,
            "number": number,
            "date": date,
            "time": letter_time,
            "title": title,
            "text": text,
            "ai_result": ai_result
        }

    except StopRequested:
        return {
            "letter_number": number,
            "number": number,
            "date": date,
            "time": letter_time,
            "title": title,
            "text": "",
            "ai_result": {"summary": "", "deadline": None},
            "cancelled": True,
        }

    except Exception as e:
        error_detail = f"{type(e).__name__}: {e}"
        print(f"\n{'=' * 80}")
        print(f"❌ خطا در پردازش نامه {number}")
        print("=" * 80)
        print(f"جزئیات: {error_detail}")

        error_callback = getattr(builtins, "BOT_LETTER_ERROR_CALLBACK", None)
        if callable(error_callback):
            try:
                error_callback(number, error_detail)
            except Exception:
                pass

        try:
            driver.switch_to.default_content()
            close_letter_window(driver, number)
        except Exception as close_error:
            print(f"⚠️ بستن پنجره‌ی نامه ناموفق بود: {close_error}")

        try:
            driver.switch_to.default_content()
            switch_to_main_iframe(driver)
        except Exception as recovery_error:
            print(f"⚠️ بازیابی ناموفق: {recovery_error}")

        return {
            "letter_number": number,
            "number": number,
            "date": date,
            "time": letter_time,
            "title": title,
            "text": text,
            "ai_result": ai_result,
            "error": error_detail,
        }

