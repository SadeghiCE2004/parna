import random
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from utils.helpers import clean_text
from config import random_sleep

def find_text_file_menu(driver):

    print("🔍 جستجوی گزینه «فایل‌های متن»...")

    selectors = [
        "//*[contains(text(), 'فایل‌های متن')]",
        "//*[contains(text(), 'فايل‌های متن')]",
        "//*[contains(text(), 'فایل های متن')]",
        "//*[contains(text(), 'فايل های متن')]",
        "//*[contains(text(), 'فایل') and contains(text(), 'متن')]",
        "//*[contains(text(), 'فايل') and contains(text(), 'متن')]",
        "//a[contains(text(), 'متن')]",
        "//button[contains(text(), 'متن')]",
        "//li[contains(text(), 'متن')]"
    ]

    for selector in selectors:

        try:

            for element in driver.find_elements(By.XPATH, selector):
                try:

                    if element.is_displayed() and element.is_enabled():
                        print("✅ گزینه «فایل‌های متن» پیدا شد.")
                        return element

                except Exception:
                    continue

        except Exception:
            continue

    try:
        for element in driver.find_elements(By.XPATH,"//*[self::a or self::button ""or self::li or self::div]"):

            try:
                if element.is_displayed():
                    text = clean_text(element.text)
                    if text and ("فایل" in text or "فايل" in text) and "متن" in text:
                        return element

            except Exception:
                continue

    except Exception as e:
        print(f"⚠️ خطا در جستجوی گسترده: {e}")

    return None

def click_text_file_menu(driver):
    file_menu = find_text_file_menu(driver)

    if file_menu is None:
        raise Exception("❌ گزینه «فایل‌های متن» پیدا نشد.")

    try:

        ActionChains(driver) \
            .move_to_element(file_menu) \
            .pause(random.uniform(0.5, 1)) \
            .click() \
            .perform()

        print("✅ روی «فایل‌های متن» کلیک شد.")

    except Exception:
        driver.execute_script("arguments[0].click();",file_menu)

    random_sleep(3, 5)