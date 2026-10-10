import os
import json
from config import STATE_FILE
from utils.helpers import normalize_number

class LetterTracker:

    def __init__(self, state_file=STATE_FILE):
        self.state_file = state_file
        self.processed_numbers = set()
        self.load_state()

    def load_state(self):
        if not os.path.exists(self.state_file):
            print("🧠 فایل حافظه وجود ندارد؛ حافظه جدید ساخته می‌شود.")
            return

        try:
            with open(self.state_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.processed_numbers = {
                normalize_number(n) for n in data.get("processed", [])
                if normalize_number(n)
            }

            print("🧠 حافظه بارگذاری شد.")
            print(f"   پردازش‌شده: {len(self.processed_numbers)}")

        except Exception as e:
            print(f"⚠️ خطا در خواندن حافظه: {e}")
            self.processed_numbers = set()

    def save_state(self):
        try:
            data = {
                "processed": sorted(self.processed_numbers)
            }
            temp_file = self.state_file + ".tmp"
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            os.replace(temp_file, self.state_file)
        except Exception as e:
            print(f"❌ خطا در ذخیره حافظه: {e}")

    def mark_processed(self, number):
        number = normalize_number(number)
        if number:
            self.processed_numbers.add(number)
            self.save_state()

    def is_processed(self, number):
        return normalize_number(number) in self.processed_numbers

    def get_all_processed(self):
        return self.processed_numbers.copy()