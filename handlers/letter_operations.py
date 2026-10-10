
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from utils.helpers import normalize_number, clean_text
from config import WAIT_TIMEOUT, random_sleep
from utils.stop_control import StopRequested, interruptible_sleep, raise_if_stop_requested, stop_aware_condition

def open_letter(driver, letter):
    raise_if_stop_requested()
    number = normalize_number(letter.get("number", ""))

    print()
    print(f"📄 در حال باز کردن نامه: {number}")

    from handlers.iframe_handlers import get_cartable_grid

    try:
        table = get_cartable_grid(driver)
        tbody = table.find_element(By.TAG_NAME, "tbody")
        rows = tbody.find_elements(By.TAG_NAME, "tr")
    except StopRequested:
        raise
    except Exception as e:
        raise Exception(f"❌ خطا در پیدا کردن جدول: {e}")

    target_row = None
    for row in rows:
        raise_if_stop_requested()
        try:
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) < 12:
                continue
            current_number = normalize_number(clean_text(cells[11].text))
            if current_number == number:
                target_row = row
                break
        except Exception:
            continue

    if target_row is None:
        raise Exception(f"❌ ردیف نامه {number} در جدول پیدا نشد.")

    driver.execute_script(
        """
        var element = arguments[0];
        var event = new MouseEvent(
            'dblclick',
            {
                view: window,
                bubbles: true,
                cancelable: true
            }
        );
        element.dispatchEvent(event);
        """,
        target_row
    )

    print("✅ دابل‌کلیک با JavaScript انجام شد.")

    driver.switch_to.default_content()
    random_sleep(1, 2)

    print("⏳ منتظر باز شدن پنجره نامه...")

    try:
        WebDriverWait(
            driver,
            WAIT_TIMEOUT
        ).until(stop_aware_condition(
            lambda d:
            len(
                d.find_elements(
                    By.XPATH,
                    "//*[contains(text(), 'فایل') "
                    "or contains(text(), 'فايل')]"
                )
            ) > 0
        ))

        print("✅ پنجره نامه باز شد.")

    except StopRequested:
        raise
    except Exception:
        print("⚠️ پنجره باز شد ولی تشخیص خودکار آن انجام نشد.")

    return number

def close_letter_window(driver, letter_number):
    raise_if_stop_requested()
    letter_number = normalize_number(letter_number)

    print()
    print(f"🔴 تلاش برای بستن پنجره نامه: {letter_number}")

    try:
        windows = driver.find_elements(
            By.XPATH,
            "//div[@draggable='true']"
            "[.//div[contains(@class,'window-title')]]"
        )

        if not windows:
            print("⚠️ هیچ پنجره‌ای برای بستن پیدا نشد.")
            return False

        target_window = None

        for window in windows:
            try:
                title = clean_text(
                    window.find_element(
                        By.CLASS_NAME,
                        "window-title"
                    ).text
                )

                if (
                    letter_number
                    and
                    letter_number in normalize_number(title)
                ):
                    target_window = window
                    break

            except Exception:
                continue

        if target_window is None:
            if len(windows) == 1:
                target_window = windows[0]
            else:
                print("⚠️ پنجره‌ی مربوط به شماره‌ی نامه مشخص نشد؛ پنجره‌ای بسته نشد.")
                return False

        close_buttons = target_window.find_elements(
            By.XPATH,
            ".//div[contains(@class,'action') "
            "and @title='close']"
        )

        if not close_buttons:
            close_buttons = target_window.find_elements(
                By.XPATH,
                ".//*[contains(@class,'close')]"
            )

        if not close_buttons:
            print("⚠️ دکمه بستن پنجره پیدا نشد.")
            return False

        close_button = close_buttons[-1]

        try:
            driver.execute_script(
                "arguments[0].click();",
                close_button
            )
        except Exception:
            close_button.click()

        print("✅ فرمان بستن پنجره ارسال شد.")
        interruptible_sleep(1)
        return True

    except StopRequested:
        raise
    except Exception as e:
        print(f"⚠️ خطا در بستن پنجره: {e}")
        return False
