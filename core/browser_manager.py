

import os
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import SessionNotCreatedException, WebDriverException
from utils.stop_control import interruptible_sleep, stop_requested
from utils.progress_control import report_progress

def get_driver(initial_url=None, target_url=None):

    if stop_requested():
        return None

    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    driver_path = os.path.join(base_dir, "chromedriver.exe")

    if not os.path.exists(driver_path):
        print()
        print("=" * 80)
        print("❌ فایل chromedriver.exe پیدا نشد!")
        print("=" * 80)
        print(f"📌 مسیر مورد انتظار:")
        print(f"   {driver_path}")
        print()
        print("📥 لطفاً فایل chromedriver.exe را دانلود کنید و در پوشه بالا قرار دهید.")
        print()
        print("🔗 لینک دانلود:")
        print("   https://googlechromelabs.github.io/chrome-for-testing/")
        print()
        print("📌 نسخه مورد نیاز:")
        print("   1. کروم خود را باز کنید و به آدرس chrome://version/ بروید")
        print("   2. نسخه کروم (مثلاً 153.0.8010.52) را یادداشت کنید")
        print("   3. chromedriver هم‌نسخه را از لینک بالا دانلود کنید")
        print("   4. فایل chromedriver.exe را در پوشه LetterBot قرار دهید")
        print("=" * 80)
        raise FileNotFoundError("chromedriver.exe یافت نشد.")

    options = Options()
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-extensions")
    options.add_experimental_option("detach", True)

    try:
        service = Service(executable_path=driver_path)
        driver = webdriver.Chrome(service=service, options=options)
        report_progress(None, "مرورگر باز شد.")
        print("✅ کروم باز شد.")

    except SessionNotCreatedException as e:
        print()
        print("=" * 80)
        print("❌ نسخه chromedriver با کروم شما هماهنگ نیست!")
        print("=" * 80)
        print(f"پیام خطا: {e}")
        print()
        print("📌 راه‌حل:")
        print("1. کروم خود را باز کنید و به آدرس chrome://version/ بروید")
        print("2. نسخه کروم را یادداشت کنید (مثلاً 153.0.8010.52)")
        print("3. از لینک زیر chromedriver هم‌نسخه را دانلود کنید:")
        print("   https://googlechromelabs.github.io/chrome-for-testing/")
        print("4. فایل chromedriver.exe را جایگزین فایل قدیمی کنید")
        print(f"   مسیر: {driver_path}")
        print("=" * 80)
        raise

    except WebDriverException as e:
        print(f"❌ خطا در باز کردن کروم: {e}")
        raise

    if initial_url:
        print(f"🌐 باز کردن URL اولیه:\n{initial_url}")
        driver.get(initial_url)
        interruptible_sleep(3)

    if target_url:
        report_progress(None, "در انتظار ورود به سامانه و بازشدن کارتابل...")
        print()
        print("=" * 80)
        print("👤 لطفاً وارد سیستم شوید و به صفحه کارتابل بروید.")
        print()
        print(f"🎯 منتظر رسیدن به:")
        print(target_url)
        print()
        print("⏳ برنامه منتظر می‌ماند تا وارد کارتابل شوید...")
        print("=" * 80)

        while not stop_requested():
            try:
                current_url = driver.current_url
                if target_url in current_url:
                    print()
                    print("✅ ورود به صفحه موردنظر تشخیص داده شد.")
                    print(f"📍 URL فعلی:\n{current_url}")
                    break
            except Exception as e:
                print(f"⚠️ خطا هنگام بررسی URL: {e}")
            interruptible_sleep(0.25)

        if stop_requested():
            print("Bot stop requested while waiting for the cartable page.")
            return None

        print("🚀 شروع فرآیند استخراج...")
        interruptible_sleep(3)

    return driver
