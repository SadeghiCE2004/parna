"""
پل ارتباطی بین ربات و گرافیک از طریق data_storage.json
"""

import os
import sys
import json
import threading
from datetime import datetime
from utils.json_storage import write_json_atomic

if getattr(sys, 'frozen', False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATA_FILE = os.path.join(BASE_DIR, "data_storage.json")

def add_letter_to_storage(letter_data):
    """اضافه کردن اطلاعات یک نامه به data_storage.json"""
    try:
        records = []
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                records = json.load(f)
        
        record = {
            "زمان_پردازش": get_persian_datetime(),
            "شماره": letter_data.get("number", ""),
            "تاریخ": letter_data.get("date", ""),
            "ساعت": letter_data.get("time", ""),
            "موضوع": letter_data.get("title", ""),
            "امضاکننده": letter_data.get("signer", ""),
            "شرح ارجاع": letter_data.get("referral_description", ""),
            "خلاصه": letter_data.get("ai_result", {}).get("summary", ""),
            "ددلاین": letter_data.get("ai_result", {}).get("deadline", ""),
            "دستور ارجاع": ""
        }
        
        records.append(record)
        
        write_json_atomic(DATA_FILE, records)
        
        print(f"✅ نامه {record['شماره']} به data_storage.json اضافه شد.")
        return True, len(records)
        
    except Exception as e:
        print(f"❌ خطا در ذخیره data_storage.json: {e}")
        return False, 0

def sync_data_to_gui(data_manager):
    """همگام‌سازی داده‌ها با DataManager گرافیک - برگرداندن تعداد جدید"""
    try:
        if not os.path.exists(DATA_FILE):
            return 0
        
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            new_records = json.load(f)
        
        if not new_records:
            return 0
        
        old_count = len(data_manager.records)
        
        data_manager.records = new_records
        data_manager.save_data()
        
        new_count = len(new_records) - old_count
        return new_count if new_count > 0 else 0
        
    except Exception as e:
        print(f"❌ خطا در همگام‌سازی: {e}")
        return 0

def get_persian_datetime():
    try:
        import jdatetime
        from datetime import datetime
        now = datetime.now()
        persian_now = jdatetime.datetime.fromgregorian(datetime=now)
        return persian_now.strftime('%Y/%m/%d %H:%M:%S')
    except:
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

class RobotIntegrationThread(threading.Thread):
    """اجرای ربات در ترد جداگانه با نمایش لحظه‌ای"""
    
    def __init__(self, data_manager, status_callback=None, progress_callback=None, finish_callback=None, refresh_callback=None):
        super().__init__()
        self.daemon = True
        self.data_manager = data_manager
        self.status_callback = status_callback
        self.progress_callback = progress_callback
        self.finish_callback = finish_callback
        self.refresh_callback = refresh_callback
        self.error = None
        self.total_letters = 0
    
    def run(self):
        try:
            if self.status_callback:
                self.status_callback("🔄 در حال اجرای ربات...")
            
            from main import main
            main()
            
            if self.status_callback:
                self.status_callback("🔄 همگام‌سازی داده‌ها...")
            
            total = sync_data_to_gui(self.data_manager)
            
            if self.refresh_callback:
                self.refresh_callback()
            
            if self.finish_callback:
                self.finish_callback(total, None)
            
        except Exception as e:
            self.error = str(e)
            if self.finish_callback:
                self.finish_callback(0, str(e))
