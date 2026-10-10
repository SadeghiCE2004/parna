
from selenium.webdriver.common.by import By
from extractors.pdf_extractor import (
    switch_to_pdf_js,
    collect_pdf_spans,
    group_into_lines,
    build_line,
    normalize_text
)
from extractors.image_ocr import extract_image_text

def extract_letter_text(driver):
    print("\n" + "=" * 80)
    print("🔬 استخراج متن واقعی نامه")
    print("=" * 80)

    try:
        driver.switch_to.default_content()

        pdf_found = any(
            "pdfjs" in (frame.get_attribute("src") or "").lower()
            or "viewer-2." in (frame.get_attribute("src") or "").lower()
            or "viewer.html" in (frame.get_attribute("src") or "").lower()
            for frame in driver.find_elements(By.TAG_NAME, "iframe")
        )

        if pdf_found:
            print("📄 فرمت PDF تشخیص داده شد.")
            switch_to_pdf_js(driver)

            items = collect_pdf_spans(driver)
            if not items:
                raise Exception("هیچ متن قابل استخراجی از PDF پیدا نشد.")

            lines = group_into_lines(items)
            final_lines = []
            for line in lines:
                built_line = build_line(line)
                if built_line:
                    final_lines.append(built_line)
            final_text = normalize_text(final_lines)

            print("\n" + "=" * 80)
            print("📝 متن نهایی PDF")
            print("=" * 80)
            print(final_text)
            print("=" * 80)

            return final_text

        print("🖼️ PDF.js پیدا نشد؛ بررسی تصویر نامه...")
        return extract_image_text(driver)

    finally:
        try:
            driver.switch_to.default_content()
        except Exception:
            pass
