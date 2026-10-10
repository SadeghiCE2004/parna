
import re
from datetime import datetime
from config import DELETED_LOG_FILE

def clean_text(text):
    """پاکسازی متن از خط جدید، تب و فاصله‌های اضافی"""
    if not text:
        return ""

    text = str(text)

    for char in "\n\r\t":
        text = text.replace(char, " ")

    return re.sub(r"\s+", " ", text).strip()

def split_date_time(value):
    """جداسازی تاریخ و ساعت از یک رشته"""
    value = clean_text(value)

    if not value:
        return "", ""

    match = re.search(
        r"(\d{4}/\d{1,2}/\d{1,2})\s+(\d{1,2}:\d{2}:\d{2})",
        value
    )

    if match:
        return match.group(1), match.group(2)

    return "", ""

def contains_persian(text):
    """بررسی وجود کاراکتر فارسی در متن"""
    if not text:
        return False
    return bool(re.search(r"[\u0600-\u06FF]", text))

def is_number(text):
    """بررسی عدد بودن متن (فارسی/عربی/انگلیسی)"""
    if not text:
        return False
    return bool(re.fullmatch(r"[۰-۹0-9٠-٩]+", text.strip()))

def is_slash(text):
    """بررسی اسلش بودن"""
    return text.strip() == "/"

def normalize_digits(value):
    """تبدیل رقم‌های فارسی و عربی به رقم انگلیسی بدون تغییر متن"""
    if value is None:
        return ""

    translation = str.maketrans(
        "۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩",
        "01234567890123456789"
    )
    return str(value).translate(translation)

def normalize_number(number):
    """تبدیل اعداد فارسی/عربی به انگلیسی و حذف کاراکترهای غیرمجاز"""
    if number is None:
        return ""

    number = normalize_digits(number).strip()

    if not number:
        return ""

    number = re.sub(r"\s+", "", number)
    number = re.sub(r"[^0-9/-]", "", number)

    return number

def remove_latin_words(text: str) -> str:
    """حذف کلمات لاتین از متن"""
    if not text:
        return ""

    text = re.sub(r"\b[A-Za-z][A-Za-z0-9_./-]*\b", "", text)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\s+([،؛:.؟!])", r"\1", text)
    return text.strip()

def log_deleted_letter(number):
    """ثبت نامه حذف‌شده در فایل لاگ"""
    number = normalize_number(number)

    if not number:
        return

    try:
        with open(DELETED_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"{datetime.now().isoformat()} - نامه {number} حذف/ارجاع شد.\n")
    except Exception as e:
        print(f"⚠️ خطا در ثبت لاگ حذف: {e}")
