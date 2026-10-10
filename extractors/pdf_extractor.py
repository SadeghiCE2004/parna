import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.helpers import clean_text, is_number, is_slash, normalize_number
from config import WAIT_TIMEOUT
from utils.stop_control import StopRequested, stop_aware_condition

def find_pdf_iframe(driver):
    driver.switch_to.default_content()
    print("🔍 جستجوی iframe مربوط به PDF.js...")

    try:
        WebDriverWait(driver, WAIT_TIMEOUT).until(stop_aware_condition(
            lambda d:len(d.find_elements(By.TAG_NAME, "iframe")) > 0
        ))

    except StopRequested:
        raise
    except Exception:
        return None

    for frame in driver.find_elements(By.TAG_NAME, "iframe"):
            try:
                src = frame.get_attribute("src") or ""
                if "pdfjs" in src.lower() or "viewer-2." in src.lower() or "viewer.html" in src.lower():
                    print("🎯 iframe مربوط به PDF.js پیدا شد.")
                    return frame
            except Exception:
                continue

    return None

def switch_to_pdf_js(driver):
    frame = find_pdf_iframe(driver)

    if frame is None:
        raise Exception("❌ iframe مربوط به PDF.js پیدا نشد.")

    driver.switch_to.frame(frame)
    print("✅ وارد iframe PDF.js شدیم.")

    WebDriverWait(driver, WAIT_TIMEOUT).until(stop_aware_condition(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".textLayer"))
    ))

    WebDriverWait(driver, WAIT_TIMEOUT).until(stop_aware_condition(
        lambda d: len(d.find_elements(By.CSS_SELECTOR, ".textLayer span")) > 0
    ))

    print("✅ Text Layer آماده است.")

def collect_pdf_spans(driver):
    items = []

    for index, span in enumerate(driver.find_elements(By.CSS_SELECTOR, ".textLayer span")):
        try:
            text = clean_text(span.get_attribute("textContent") or "")
            if not text:
                continue

            rect = span.rect
            items.append({
                "index": index,
                "text": text,
                "x": float(rect["x"]),
                "y": float(rect["y"]),
                "width": float(rect["width"]),
                "height": float(rect["height"])
            })
        except Exception:
            continue

    print(f"📊 spanهای دارای متن: {len(items)}")
    return items

def same_line(a, b):
    center_a = a["y"] + a["height"] / 2
    center_b = b["y"] + b["height"] / 2
    tolerance = max(a["height"], b["height"], 5) * 0.6
    return abs(center_a - center_b) <= tolerance

def group_into_lines(items):
    sorted_items = sorted(items, key=lambda x: (x["y"], x["x"]))
    lines = []

    for item in sorted_items:
        placed = False
        for line in lines:
            if same_line(item, line[0]):
                line.append(item)
                placed = True
                break
        if not placed:
            lines.append([item])

    lines.sort(key=lambda line: min(item["y"] for item in line))
    print(f"📊 تعداد خطوط تشخیص داده‌شده: {len(lines)}")
    return lines

def merge_numeric_tokens(tokens):
    result = []
    i = 0

    while i < len(tokens):
        if (i + 4 < len(tokens) and is_number(tokens[i]) and is_slash(tokens[i + 1]) and
            is_number(tokens[i + 2]) and is_slash(tokens[i + 3]) and is_number(tokens[i + 4])):
            result.append(normalize_number(tokens[i] + "/" + tokens[i + 2] + "/" + tokens[i + 4]))
            i += 5
            continue

        if (i + 2 < len(tokens) and is_number(tokens[i]) and is_slash(tokens[i + 1]) and
            is_number(tokens[i + 2])):
            result.append(normalize_number(tokens[i] + "/" + tokens[i + 2]))
            i += 3
            continue

        result.append(tokens[i])
        i += 1

    return result

def build_line(line):
    if not line:
        return ""

    ordered = sorted(line, key=lambda x: x["x"], reverse=True)
    tokens = [clean_text(item["text"]) for item in ordered if clean_text(item["text"])]

    if not tokens:
        return ""

    fixed_tokens = []
    i = 0

    while i < len(tokens):
        if (i + 4 < len(tokens) and is_number(tokens[i]) and is_slash(tokens[i + 1]) and
            is_number(tokens[i + 2]) and is_slash(tokens[i + 3]) and is_number(tokens[i + 4])):
            numeric_group = [tokens[i], tokens[i + 1], tokens[i + 2], tokens[i + 3], tokens[i + 4]]
            numeric_group.reverse()
            fixed_tokens.extend(numeric_group)
            i += 5
            continue

        if (i + 2 < len(tokens) and is_number(tokens[i]) and is_slash(tokens[i + 1]) and
            is_number(tokens[i + 2])):
            numeric_group = [tokens[i], tokens[i + 1], tokens[i + 2]]
            numeric_group.reverse()
            fixed_tokens.extend(numeric_group)
            i += 3
            continue

        fixed_tokens.append(tokens[i])
        i += 1

    fixed_tokens = merge_numeric_tokens(fixed_tokens)

    result = ""
    for token in fixed_tokens:
        if not result:
            result = token
        elif token == "/":
            result += "/"
        elif result.endswith("/"):
            result += token
        else:
            result += " " + token

    return result.strip()

def normalize_text(lines):
    result = []
    for line in lines:
        line = re.sub(r"\s*/\s*", "/", line)
        line = re.sub(r"[ \t]+", " ", line)
        line = re.sub(r"\s+([،؛:.؟!])", r"\1", line)
        line = line.strip()
        if line:
            result.append(line)
    return "\n".join(result)
