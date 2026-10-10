
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.helpers import clean_text, split_date_time, normalize_number
from config import WAIT_TIMEOUT, random_sleep
from utils.stop_control import StopRequested, raise_if_stop_requested, stop_aware_condition

def switch_to_main_iframe(driver):

    raise_if_stop_requested()

    driver.switch_to.default_content()
    print("🔍 در حال پیدا کردن iframe اصلی...")

    try:
        WebDriverWait(driver, 60).until(stop_aware_condition(
            lambda d: len(d.find_elements(By.TAG_NAME, "iframe")) > 0
        ))
    except StopRequested:
        raise
    except Exception:
        random_sleep(3, 5)

    frames = driver.find_elements(By.TAG_NAME, "iframe")

    if not frames:
        raise Exception("هیچ iframeای در صفحه پیدا نشد.")

    for index, frame in enumerate(frames):
        raise_if_stop_requested()

        try:
            driver.switch_to.frame(frame)

            if driver.find_elements(By.ID, "CartableGrid"):
                print(f"✅ iframe اصلی پیدا شد. شماره: {index}")
                return True

            driver.switch_to.default_content()

        except StopRequested:
            raise
        except Exception:
            driver.switch_to.default_content()

    driver.switch_to.default_content()

    raise Exception("❌ iframe مربوط به CartableGrid پیدا نشد.")

def get_cartable_grid(driver):

    raise_if_stop_requested()

    table = WebDriverWait(driver, WAIT_TIMEOUT).until(stop_aware_condition(
        EC.presence_of_element_located((By.ID, "CartableGrid"))
    ))

    print("✅ جدول CartableGrid پیدا شد.")
    return table

def get_letter_rows(table):

    tbody = table.find_element(By.TAG_NAME, "tbody")
    rows = tbody.find_elements(By.TAG_NAME, "tr")
    valid_rows = []

    print(f"📊 تعداد ردیف‌های جدول: {len(rows)}")

    for row in rows:
        try:
            cells = row.find_elements(By.TAG_NAME, "td")

            if len(cells) < 41:
                continue

            date_time = clean_text(cells[7].text)
            date, letter_time = split_date_time(date_time)

            normalized_number = normalize_number(clean_text(cells[11].text))
            subject = clean_text(cells[14].text) or clean_text(cells[14].get_attribute("innerHTML") or "")
            signer = clean_text(cells[9].text)
            referral_description = clean_text(cells[40].text)

            if not date_time and not normalized_number:
                continue

            valid_rows.append(
                {
                    "row": row,
                    "cells": cells,
                    "number": normalized_number,
                    "date": date,
                    "time": letter_time,
                    "subject": subject,
                    "signer": signer,
                    "referral_description": referral_description
                }
            )

        except Exception:
            continue

    print(f"📋 تعداد نامه‌های معتبر: {len(valid_rows)}")
    return valid_rows

def get_current_letters(driver):

    raise_if_stop_requested()

    print("🔄 رفتن به iframe اصلی...")
    switch_to_main_iframe(driver)
    random_sleep(1, 2)
    table = get_cartable_grid(driver)
    random_sleep(1, 2)
    return get_letter_rows(table)

