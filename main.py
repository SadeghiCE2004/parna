import random
from core.browser_manager import get_driver
from processor.processor import process_letter
from handlers.tracker import LetterTracker
from handlers.iframe_handlers import get_current_letters
from utils.helpers import normalize_number
from utils.result_saver import save_results
from config import *
from ai.runtime_setup import ensure_model
from utils.stop_control import StopRequested, interruptible_sleep, stop_requested
from utils.progress_control import report_progress

def find_new_letters(current_letters, tracker):
    new_letters = []

    for letter in current_letters:
        number = normalize_number(letter.get("number", ""))
        if number and not tracker.is_processed(number):
            letter["number"] = number
            new_letters.append(letter)

    return new_letters

def main():
    driver = None

    print("\n" + "=" * 80)
    print("🤖 LETTER BOT - شروع به کار")
    print("=" * 80)

    try:
        report_progress(None, "در حال بازکردن مرورگر...")
        driver = get_driver(INITIAL_URL, TARGET_URL)
        if stop_requested() or driver is None:
            return
        tracker = LetterTracker()
        all_results = []
        interruptible_sleep(random.uniform(2, 4))

        print("\n" + "=" * 80)
        print("🔍 شروع بررسی کارتابل")
        print("=" * 80)

        report_progress(None, "در حال بارگذاری کارتابل...")
        current_letters = get_current_letters(driver)

        print(f"\n📊 تعداد نامه‌های فعلی: {len(current_letters)}")
        print(f"🧠 پردازش‌شده: {tracker.get_all_processed()}")

        new_letters = find_new_letters(current_letters, tracker)
        if not new_letters:
            report_progress(100, "بررسی کارتابل کامل شد؛ نامه‌ی جدیدی نیست.")

        if new_letters:
            print(f"\n📥 {len(new_letters)} نامه جدید پیدا شد.")

            print("\n" + "=" * 80)
            print("🤖 آماده‌سازی Ollama برای پردازش نامه‌ها...")
            print("=" * 80)
            try:
                report_progress(None, "در حال آماده‌سازی مدل هوش مصنوعی...")
                ensure_model()
                print("✅ Ollama آماده است.")
            except Exception as e:
                print(f"⚠️ خطا در آماده‌سازی Ollama: {e}")
                print("⏳ پردازش ادامه می‌یابد؛ ممکن است خلاصه‌سازی هوش مصنوعی در دسترس نباشد.")

            if stop_requested():
                return
        else:
            print("\n📭 هیچ نامه جدیدی یافت نشد.")

        for idx, letter in enumerate(new_letters):

            if stop_requested():
                print("\n" + "=" * 80)
                print("⏹️ توقف ربات درخواست شد - حلقه پردازش متوقف شد.")
                print("=" * 80)
                break

            number = normalize_number(letter.get("number", ""))

            print(f"\n{'=' * 80}")
            print(f"📨 نامه جدید {idx + 1}/{len(new_letters)}")
            print(f"📄 شماره: {number}")
            print("=" * 80)

            result = process_letter(driver, letter)

            if result.get("cancelled") or stop_requested():
                break

            if not result.get("text", "").strip():
                print(f"⚠️ نامه {number} پردازش نشد؛ در حافظه ثبت نمی‌شود.")
                continue

            tracker.mark_processed(number)
            all_results.append(result)

            save_results(all_results, RESULT_FILE)
            report_progress(100, "ذخیره‌ی نتیجه‌ی نامه کامل شد.", number, letter.get("title", ""))

            if idx < len(new_letters) - 1:
                pause = random.uniform(3, 6)
                print(f"⏳ مکث {pause:.1f} ثانیه...")
                interruptible_sleep(pause)

        print(f"\n{'=' * 80}")
        print("✅ بررسی کارتابل تمام شد.")
        print("=" * 80)

        print("\n👋 برنامه کارش تمام شد.")
        print("🌐 مرورگر عمداً باز نگه داشته شد.")

    except StopRequested:
        print("\nBot stopped by user.")

    except KeyboardInterrupt:
        print("\n🛑 برنامه توسط کاربر متوقف شد.")

    except Exception as e:
        import traceback
        print(f"\n{'=' * 80}")
        print("❌ خطا در اجرای اصلی برنامه")
        print("=" * 80)
        print(f"نوع خطا: {type(e).__name__}")
        print(f"پیام: {e}")
        traceback.print_exc()
        raise

    finally:
        print(f"\n{'=' * 80}")
        print("🌐 مرورگر باز نگه داشته شده است.")
        print("=" * 80)

if __name__ == "__main__":
    main()
