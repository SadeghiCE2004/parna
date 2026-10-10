import os
import sys
import random
import pytesseract

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
    RESOURCE_DIR = getattr(sys, '_MEIPASS', BASE_DIR)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    RESOURCE_DIR = BASE_DIR

WAIT_TIMEOUT = 120
MIN_SLEEP = 1.5
MAX_SLEEP = 4

STATE_FILE = os.path.join(BASE_DIR, "letter_state.json")
DELETED_LOG_FILE = os.path.join(BASE_DIR, "deleted_letters.log")
RESULT_FILE = os.path.join(BASE_DIR, "all_extracted_letters.txt")

_OCR_DIRS = [os.path.join(RESOURCE_DIR, "ocr")]
if BASE_DIR != RESOURCE_DIR:
    _OCR_DIRS.append(os.path.join(BASE_DIR, "ocr"))

OCR_DIR = next(
    (path for path in _OCR_DIRS if os.path.isfile(os.path.join(path, "tesseract.exe"))),
    _OCR_DIRS[0],
)
TESSERACT_PATH = os.path.join(OCR_DIR, "tesseract.exe")
TESSDATA_PATH = os.path.join(OCR_DIR, "tessdata")

INITIAL_URL = "https://didgah.khrtvto.ir/Didgah/UserLogin/Login"
TARGET_URL = "https://didgah.khrtvto.ir/Default.dap"

pytesseract.pytesseract.tesseract_cmd = TESSERACT_PATH
os.environ["TESSDATA_PREFIX"] = TESSDATA_PATH

def random_sleep(min_sec=MIN_SLEEP, max_sec=MAX_SLEEP):
    from utils.stop_control import interruptible_sleep
    interruptible_sleep(random.uniform(min_sec, max_sec))
