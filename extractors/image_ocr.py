import base64
import re
from io import BytesIO

import pytesseract
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

from config import WAIT_TIMEOUT
from utils.stop_control import stop_aware_condition


IMAGE_SELECTOR = "img, canvas, object, embed"
IMAGE_WRAPPER_SELECTOR = ".didgah-extension-image-wrapper"
MIN_IMAGE_AREA = 20_000
MAX_FRAME_DEPTH = 6


def _is_visible(element):
    try:
        return element.is_displayed()
    except Exception:
        return False


def _image_area(driver, element):
    try:
        dimensions = driver.execute_script(
            """
            const element = arguments[0];
            const rect = element.getBoundingClientRect();
            return {
                naturalWidth: element.naturalWidth || element.width || 0,
                naturalHeight: element.naturalHeight || element.height || 0,
                width: rect.width || 0,
                height: rect.height || 0,
                complete: element.complete !== false
            };
            """,
            element,
        )
        width = max(dimensions["naturalWidth"], dimensions["width"])
        height = max(dimensions["naturalHeight"], dimensions["height"])
        if not dimensions["complete"] or width < 1 or height < 1:
            return 0
        return width * height
    except Exception:
        return 0


def _find_image_in_current_context(driver, depth=0, frame_path=()):
    candidates = []
    wrapper_element_ids = set()

    try:
        wrappers = driver.find_elements(By.CSS_SELECTOR, IMAGE_WRAPPER_SELECTOR)
    except Exception:
        wrappers = []

    for wrapper in wrappers:
        if not _is_visible(wrapper):
            continue

        try:
            nested_images = wrapper.find_elements(By.CSS_SELECTOR, IMAGE_SELECTOR)
        except Exception:
            nested_images = []

        visible_nested_images = [image for image in nested_images if _is_visible(image)]
        if visible_nested_images:
            for image in visible_nested_images:
                area = _image_area(driver, image)
                if area >= MIN_IMAGE_AREA:
                    candidates.append((area + 1_000_000_000, image, frame_path))
                    wrapper_element_ids.add(image.id)
        else:
            area = _image_area(driver, wrapper)
            if area >= MIN_IMAGE_AREA:
                candidates.append((area + 500_000_000, wrapper, frame_path))

    try:
        images = driver.find_elements(By.CSS_SELECTOR, IMAGE_SELECTOR)
    except Exception:
        images = []

    for image in images:
        if image.id in wrapper_element_ids or not _is_visible(image):
            continue
        area = _image_area(driver, image)
        if area >= MIN_IMAGE_AREA:
            candidates.append((area, image, frame_path))

    try:
        background_image = driver.execute_script(
            """
            const elements = Array.from(document.querySelectorAll("*"));
            let best = null;
            let bestArea = 0;
            for (const element of elements) {
                const rect = element.getBoundingClientRect();
                const style = getComputedStyle(element);
                if (style.display === "none" || style.visibility === "hidden" ||
                    !style.backgroundImage.includes("url(")) continue;
                const area = rect.width * rect.height;
                if (area > bestArea) {
                    best = element;
                    bestArea = area;
                }
            }
            return bestArea >= 20000 ? best : null;
            """
        )
        if background_image is not None and _is_visible(background_image):
            area = _image_area(driver, background_image)
            candidates.append((area, background_image, frame_path))
    except Exception:
        pass

    best_candidate = max(candidates, key=lambda candidate: candidate[0]) if candidates else None

    if depth >= MAX_FRAME_DEPTH:
        return best_candidate

    try:
        frames = driver.find_elements(By.CSS_SELECTOR, "iframe, frame")
    except Exception:
        frames = []

    for frame in frames:
        entered_frame = False
        try:
            driver.switch_to.frame(frame)
            entered_frame = True
            candidate = _find_image_in_current_context(
                driver,
                depth + 1,
                frame_path + (frame,),
            )
        except Exception:
            candidate = None
        finally:
            if entered_frame:
                try:
                    driver.switch_to.parent_frame()
                except Exception:
                    try:
                        driver.switch_to.default_content()
                    except Exception:
                        pass

        if candidate is not None and (
            best_candidate is None or candidate[0] > best_candidate[0]
        ):
            best_candidate = candidate

    return best_candidate


def _find_letter_image(driver):
    try:
        driver.switch_to.default_content()
        candidate = _find_image_in_current_context(driver)
        driver.switch_to.default_content()
        if candidate is None:
            return None

        for frame in candidate[2]:
            try:
                driver.switch_to.frame(frame)
            except Exception:
                driver.switch_to.default_content()
                return None
        return candidate[1]
    except Exception:
        try:
            driver.switch_to.default_content()
        except Exception:
            pass
        return None


def _browser_image_bytes(driver, image_element):
    result = driver.execute_async_script(
        """
        const element = arguments[0];
        const done = arguments[arguments.length - 1];

        if (element.tagName.toLowerCase() === "canvas") {
            try {
                done({data: element.toDataURL("image/png")});
            } catch (error) {
                done({error: String(error)});
            }
            return;
        }

        let source = element.currentSrc || element.src || element.data ||
            element.getAttribute("data") || "";
        if (!source) {
            const background = getComputedStyle(element).backgroundImage;
            const match = background.match(/url\(["']?(.*?)["']?\)/);
            if (match) source = match[1];
        }
        if (!source) {
            done({error: "Image source is empty"});
            return;
        }

        fetch(source, {credentials: "include", cache: "no-store"})
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Image request failed with HTTP ${response.status}`);
                }
                return response.blob();
            })
            .then(blob => {
                const reader = new FileReader();
                reader.onload = () => done({data: reader.result});
                reader.onerror = () => done({error: "Could not read image data"});
                reader.readAsDataURL(blob);
            })
            .catch(error => done({error: String(error)}));
        """,
        image_element,
    )

    data_url = result.get("data", "") if isinstance(result, dict) else ""
    if not data_url.startswith("data:") or "," not in data_url:
        return None

    try:
        return base64.b64decode(data_url.split(",", 1)[1])
    except (ValueError, TypeError):
        return None


def _load_image(driver, image_element):
    try:
        image_bytes = image_element.screenshot_as_png
    except Exception as error:
        print(f"⚠️ دریافت تصویر از نمای مرورگر ناموفق بود: {error}")
        image_bytes = None

    if not image_bytes:
        try:
            image_bytes = _browser_image_bytes(driver, image_element)
        except Exception as error:
            raise RuntimeError(f"دریافت تصویر از مرورگر ناموفق بود: {error}") from error

    if not image_bytes:
        raise RuntimeError("محتوای تصویر خالی است.")

    try:
        image = Image.open(BytesIO(image_bytes))
        image = ImageOps.exif_transpose(image)
        if image.mode not in ("RGB", "L"):
            image = image.convert("RGB")
        return image.copy()
    except Exception as error:
        raise RuntimeError(f"محتوای دریافت‌شده تصویر قابل‌خواندن نیست: {error}") from error


def extract_image_text(driver):
    print("\n" + "=" * 80)
    print("🖼️ استخراج متن از تصویر نامه")
    print("=" * 80)

    try:
        print("🔍 جست‌وجوی تصویر در صفحه و قاب‌های داخلی...")
        image_element = WebDriverWait(driver, WAIT_TIMEOUT).until(
            stop_aware_condition(lambda current_driver: _find_letter_image(current_driver))
        )

        print("📥 دریافت تصویر از نشست مرورگر...")
        original_image = _load_image(driver, image_element)

        image = original_image.resize(
            (original_image.width * 2, original_image.height * 2),
            Image.Resampling.LANCZOS,
        )
        image = image.convert("L")
        image = ImageEnhance.Contrast(image).enhance(1.8)
        image = image.filter(ImageFilter.SHARPEN)
        image = image.filter(ImageFilter.UnsharpMask(radius=1, percent=150, threshold=3))

        print("🔬 اجرای Tesseract OCR...")
        text = pytesseract.image_to_string(image, lang="fas+eng", config="--psm 6")
        text = text.replace("\r", "")
        text = re.sub(r"\n{3,}", "\n\n", text).strip()

        print("\n" + "=" * 80)
        print("📝 متن OCR")
        print("=" * 80)
        print(text)
        print("=" * 80)

        print("✅ OCR با موفقیت انجام شد." if text else "⚠️ OCR متنی پیدا نکرد.")
        return text

    except Exception as error:
        print(f"❌ خطا در OCR تصویر: {error}")
        raise

    finally:
        try:
            driver.switch_to.default_content()
        except Exception:
            pass
