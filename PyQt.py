import sys
import os
import json
import subprocess
import re
import webbrowser
import socket
import io
from contextlib import redirect_stdout, redirect_stderr
import pandas as pd
from datetime import datetime
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
import jdatetime
from PyQt5.QtPrintSupport import QPrinter, QPrintPreviewDialog, QPrintDialog
from openpyxl.styles import Alignment

def get_base_dir():
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

try:
    import winreg
    WINREG_AVAILABLE = True
except ImportError:
    WINREG_AVAILABLE = False

from data_bridge import sync_data_to_gui
from utils.json_storage import write_json_atomic

try:
    from config import STATE_FILE
except ImportError:
    STATE_FILE = "processed_letters.json"

class Theme:
    PRIMARY = "#3B82F6"
    PRIMARY_DARK = "#2563EB"
    PRIMARY_LIGHT = "#93C5FD"
    PRIMARY_SOFT = "#DBEAFE"
    
    SECONDARY = "#14B8A6"
    SECONDARY_DARK = "#0D9488"
    SECONDARY_SOFT = "#CCFBF1"
    
    DANGER = "#EF4444"
    DANGER_DARK = "#DC2626"
    
    WARNING = "#F59E0B"
    WARNING_DARK = "#D97706"
    
    INFO = "#0EA5E9"
    INFO_DARK = "#0284C7"
    
    HEADER_FROM = "#60A5FA"
    HEADER_TO = "#3B82F6"
    
    BG_MAIN = "#F0F4F8"
    BG_CARD = "#FFFFFF"
    BG_TOOLBAR = "#FFFFFF"
    BG_HEADER = "#EFF6FF"
    BG_ALT_ROW = "#F8FAFC"
    
    TEXT_PRIMARY = "#1E293B"
    TEXT_SECONDARY = "#64748B"
    TEXT_MUTED = "#94A3B8"
    
    BORDER = "#E2E8F0"
    BORDER_LIGHT = "#F1F5F9"
    
    SELECTION_BG = "#DBEAFE"
    SELECTION_TEXT = "#1E3A8A"
    
    HIGHLIGHT_NEW = "#BBF7D0"

class TeeOutput:
    def __init__(self, original_stdout):
        self.terminal = original_stdout
        self.captured = io.StringIO()
    
    def write(self, text):
        try:
            self.terminal.write(text)
            self.terminal.flush()
        except Exception:
            pass
        self.captured.write(text)
    
    def flush(self):
        try:
            self.terminal.flush()
        except Exception:
            pass
    
    def getvalue(self):
        return self.captured.getvalue()

def get_persian_datetime():
    try:
        now = datetime.now()
        persian_now = jdatetime.datetime.fromgregorian(datetime=now)
        return persian_now.strftime('%Y/%m/%d %H:%M:%S')
    except:
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def get_icon_path():
    base_dir = get_base_dir()
    return os.path.join(base_dir, "icon.ico")

def is_network_error(error_text):
    if not error_text:
        return False
    error_lower = str(error_text).lower()
    network_keywords = [
        "timeout", "timed out", "time out", "readtimeout",
        "connectionerror", "connection error", "connection refused",
        "connection reset", "connection aborted", "connection broken",
        "network", "internet", "no internet",
        "unreachable", "no route", "host unreachable",
        "socket", "urlerror", "httperror", "max retries",
        "failed to establish", "name or service not known",
        "temporary failure", "proxy", "dns",
        "sslerror", "ssl error", "handshake",
        "requests.exceptions", "urllib3",
        "read timed out", "connect timeout",
        "خظای شبکه", "خطای شبکه", "اتصال", "اینترنت", "شبکه",
        "تایم اوت", "تایم‌اوت", "پاسخ نداد", "قطع",
    ]
    for keyword in network_keywords:
        if keyword in error_lower:
            return True
    return False

def check_internet(timeout=3):
    test_hosts = [
        ("8.8.8.8", 53),
        ("1.1.1.1", 53),
        ("www.google.com", 80),
        ("www.microsoft.com", 80),
    ]
    for host, port in test_hosts:
        try:
            socket.setdefaulttimeout(timeout)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((host, port))
            sock.close()
            return True
        except Exception:
            continue
    return False

def get_chrome_version():
    if not WINREG_AVAILABLE:
        return _get_chrome_version_from_exe()
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Google\Chrome\BLBeacon")
        version, _ = winreg.QueryValueEx(key, "version")
        winreg.CloseKey(key)
        if version:
            return version
    except Exception:
        pass
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Google\Update\Clients\{8A69D345-D564-463c-AFF1-A69D9E530F96}")
        version, _ = winreg.QueryValueEx(key, "pv")
        winreg.CloseKey(key)
        if version:
            return version
    except Exception:
        pass
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Wow6432Node\Google\Update\Clients\{8A69D345-D564-463c-AFF1-A69D9E530F96}")
        version, _ = winreg.QueryValueEx(key, "pv")
        winreg.CloseKey(key)
        if version:
            return version
    except Exception:
        pass
    return _get_chrome_version_from_exe()

def _get_chrome_version_from_exe():
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe"),
    ]
    for path in chrome_paths:
        if os.path.exists(path):
            try:
                result = subprocess.run([path, "--version"], capture_output=True,
                    text=True, timeout=5,
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
                match = re.search(r"(\d+\.\d+\.\d+\.\d+)", result.stdout)
                if match:
                    return match.group(1)
            except Exception:
                pass
    return None

def get_chromedriver_version(driver_path):
    if not os.path.exists(driver_path):
        return None
    try:
        result = subprocess.run([driver_path, "--version"], capture_output=True,
            text=True, timeout=5,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
        match = re.search(r"(\d+\.\d+\.\d+\.\d+)", result.stdout)
        if match:
            return match.group(1)
    except Exception:
        pass
    return None

def get_driver_path():
    base_dir = get_base_dir()
    return os.path.join(base_dir, "chromedriver.exe")

def format_worksheet(worksheet):
    worksheet.sheet_view.rightToLeft = True
    for row in worksheet.iter_rows():
        for cell in row:
            cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
    column_widths = {"A": 18, "B": 15, "C": 12, "D": 40, "E": 30, "F": 40, "G": 60, "H": 18, "I": 40}
    for col, width in column_widths.items():
        worksheet.column_dimensions[col].width = width

def save_to_excel_custom(records, filename):
    try:
        if not records:
            return False, "هیچ داده‌ای وجود ندارد!"
        columns = ["شماره", "تاریخ", "ساعت", "موضوع", "امضاکننده",
                   "شرح ارجاع", "خلاصه", "ددلاین", "دستور ارجاع"]
        df = pd.DataFrame(records)
        for col in columns:
            if col not in df.columns:
                df[col] = ""
        df = df[columns]
        with pd.ExcelWriter(filename, engine="openpyxl") as writer:
            df.to_excel(writer, index=False, sheet_name="Sheet1")
            worksheet = writer.sheets["Sheet1"]
            format_worksheet(worksheet)
        return True, f"✅ {len(df)} رکورد در اکسل ذخیره شد!"
    except Exception as e:
        return False, f"❌ خطا: {str(e)}"

class DataManager:
    
    def __init__(self):
        self.data_file = os.path.join(get_base_dir(), "data_storage.json")
        self.records = []
        self.load_data()

    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    self.records = json.load(f)
                print(f"✅ {len(self.records)} رکورد بارگذاری شد")
            except:
                self.records = []
        else:
            print("📄 فایل داده جدید ساخته می‌شود")
            self.records = []
    
    def save_data(self):
        try:
            write_json_atomic(self.data_file, self.records)
            print(f"✅ {len(self.records)} رکورد ذخیره شد")
            return True
        except Exception as e:
            print(f"❌ خطا: {e}")
            return False
    
    def delete_records(self, indices):
        for idx in sorted(indices, reverse=True):
            if 0 <= idx < len(self.records):
                del self.records[idx]
        self.save_data()
    
    def update_command(self, index, command):
        if 0 <= index < len(self.records):
            self.records[index]['دستور ارجاع'] = command
            self.save_data()
            return True
        return False
    
    def clear_all(self):
        self.records = []
        self.save_data()

class TableModel(QAbstractTableModel):
    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        self.headers = ['ردیف', 'شماره', 'تاریخ', 'ساعت', 'موضوع', 'امضاکننده', 'شرح ارجاع', 'خلاصه', 'ددلاین', 'دستور ارجاع']
        self.persian_headers = ['ردیف', 'شماره', 'تاریخ', 'ساعت', 'موضوع', 'امضاکننده', 'شرح ارجاع', 'خلاصه', 'ددلاین', 'دستور ارجاع']
        self.filtered_indices = []
        self.filter_text = ""
        self.sort_field = None
        self.sort_descending = False
        
        self._highlighted_numbers = set()
        
        self._rebuild_filter()
    
    def mark_new_numbers(self, numbers_list):
        """علامت‌گذاری شماره‌های جدید برای هایلایت"""
        self._highlighted_numbers.update(str(n).strip() for n in numbers_list if str(n).strip())
        if self._highlighted_numbers:
            if self.rowCount() > 0:
                top_left = self.index(0, 0)
                bottom_right = self.index(self.rowCount() - 1, self.columnCount() - 1)
                self.dataChanged.emit(top_left, bottom_right)
    
    def clear_highlights(self):
        """پاک کردن همه هایلایت‌ها"""
        if self._highlighted_numbers:
            self._highlighted_numbers.clear()
            if self.rowCount() > 0:
                top_left = self.index(0, 0)
                bottom_right = self.index(self.rowCount() - 1, self.columnCount() - 1)
                self.dataChanged.emit(top_left, bottom_right)
    
    def _rebuild_filter(self):
        if not self.filter_text:
            self.filtered_indices = list(range(len(self.data_manager.records)))
        else:
            needle = self.filter_text.lower()
            self.filtered_indices = []
            for i, rec in enumerate(self.data_manager.records):
                for v in rec.values():
                    if needle in str(v).lower():
                        self.filtered_indices.append(i)
                        break

        if self.sort_field:
            dated_rows = []
            undated_rows = []
            for record_index in self.filtered_indices:
                record = self.data_manager.records[record_index]
                date_value = self._parse_sort_date(record.get(self.sort_field, ""))
                if date_value is None:
                    undated_rows.append(record_index)
                else:
                    dated_rows.append((date_value, record_index))

            dated_rows.sort(key=lambda item: item[0], reverse=self.sort_descending)
            self.filtered_indices = [index for _, index in dated_rows] + undated_rows

    @staticmethod
    def _parse_sort_date(value):
        if not value:
            return None

        normalized = str(value).strip().translate(str.maketrans(
            "۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩",
            "01234567890123456789"
        ))
        match = re.match(r"^(\d{4})[/-](\d{1,2})[/-](\d{1,2})", normalized)
        if not match:
            return None

        year, month, day = (int(part) for part in match.groups())
        try:
            if 1200 <= year < 1600:
                return jdatetime.date(year, month, day).togregorian().toordinal()
            return datetime(year, month, day).date().toordinal()
        except ValueError:
            return None

    def set_sort(self, field=None, descending=False):
        self.beginResetModel()
        self.sort_field = field
        self.sort_descending = descending
        self._rebuild_filter()
        self.endResetModel()
    
    def set_filter(self, text):
        self.beginResetModel()
        self.filter_text = text.strip()
        self._rebuild_filter()
        self.endResetModel()
    
    def rowCount(self, parent=None):
        return len(self.filtered_indices)
    
    def columnCount(self, parent=None):
        return len(self.headers)
    
    def data(self, index, role):
        if not index.isValid():
            return None
        
        if index.column() == 0:
            if role == Qt.DisplayRole:
                return str(index.row() + 1)
            elif role == Qt.TextAlignmentRole:
                return Qt.AlignCenter | Qt.AlignVCenter
            elif role == Qt.ForegroundRole:
                return QColor(Theme.TEXT_MUTED)
            return None
        
        real_row = self.filtered_indices[index.row()]
        record = self.data_manager.records[real_row]
        key = self.headers[index.column()]
        value = record.get(key, '')
        
        if role == Qt.DisplayRole or role == Qt.EditRole:
            return str(value) if value else ''
        
        elif role == Qt.BackgroundRole:
            # Deadline colors take priority over the new-record highlight.
            if index.column() == 8:
                try:
                    deadline_str = str(value)
                    if deadline_str and deadline_str != 'nan':
                        today = jdatetime.datetime.now().date()
                        deadline_date = jdatetime.datetime.strptime(deadline_str.strip(), '%Y/%m/%d').date()
                        diff = (deadline_date - today).days
                        if diff < 0:
                            return QColor(254, 226, 226)
                        elif diff <= 3:
                            return QColor(254, 243, 199)
                        return QColor(209, 250, 229)
                except (TypeError, ValueError):
                    pass

            current_number = str(record.get('شماره', '')).strip()
            if current_number and current_number in self._highlighted_numbers:
                return QColor(Theme.HIGHLIGHT_NEW)
            
            if index.column() == 9:
                command = record.get('دستور ارجاع', '')
                if command and command.strip():
                    return QColor(219, 234, 254)
            
            return None
        
        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter | Qt.AlignVCenter
        
        return None
    
    def setData(self, index, value, role):
        if role == Qt.EditRole:
            real_row = self.filtered_indices[index.row()]
            key = self.headers[index.column()]
            self.data_manager.records[real_row][key] = value
            self.data_manager.save_data()
            self.dataChanged.emit(index, index)
            return True
        return False
    
    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.persian_headers[section]
        elif orientation == Qt.Horizontal and role == Qt.TextAlignmentRole:
            return Qt.AlignCenter | Qt.AlignVCenter
        return None
    
    def flags(self, index):
        return Qt.ItemIsSelectable | Qt.ItemIsEnabled | Qt.ItemIsEditable
    
    def refresh(self):
        self.beginResetModel()
        self._rebuild_filter()
        self.endResetModel()
    
    def get_real_row(self, view_row):
        if 0 <= view_row < len(self.filtered_indices):
            return self.filtered_indices[view_row]
        return -1

class RobotThread(QThread):
    progress = pyqtSignal(int, str, str, str)
    
    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        self.error_message = ""
        self.letter_errors = []

    def _capture_letter_error(self, number, message):
        self.letter_errors.append((str(number), str(message)))

    def _emit_progress(self, percent, message, letter_number="", title=""):
        value = -1 if percent is None else max(0, min(100, int(percent)))
        self.progress.emit(value, message, letter_number or "", title or "")
    
    def run(self):
        try:
            self._emit_progress(None, "در حال بررسی اتصال اینترنت...")
            if not check_internet(timeout=3):
                self.error_message = "NETWORK_OFFLINE"
                return
            
            driver_path = get_driver_path()
            
            if not os.path.exists(driver_path):
                self.error_message = "DRIVER_MISSING"
                return
            
            self._emit_progress(None, "در حال بررسی نسخه‌های Chrome و ChromeDriver...")
            chrome_ver = get_chrome_version()
            driver_ver = get_chromedriver_version(driver_path)
            
            if chrome_ver and driver_ver:
                chrome_major = chrome_ver.split('.')[0]
                driver_major = driver_ver.split('.')[0]
                if chrome_major != driver_major:
                    self.error_message = f"DRIVER_MISMATCH|{chrome_ver}|{driver_ver}"
                    return
            
            captured_output = TeeOutput(sys.__stdout__)
            error_caught = None
            
            try:
                from main import main
                import builtins
                previous_progress_callback = getattr(builtins, 'BOT_PROGRESS_CALLBACK', None)
                previous_error_callback = getattr(builtins, 'BOT_LETTER_ERROR_CALLBACK', None)
                builtins.BOT_PROGRESS_CALLBACK = self._emit_progress
                builtins.BOT_LETTER_ERROR_CALLBACK = self._capture_letter_error
                try:
                    with redirect_stdout(captured_output), redirect_stderr(captured_output):
                        main()
                finally:
                    if previous_progress_callback is None:
                        try:
                            del builtins.BOT_PROGRESS_CALLBACK
                        except AttributeError:
                            pass
                    else:
                        builtins.BOT_PROGRESS_CALLBACK = previous_progress_callback
                    if previous_error_callback is None:
                        try:
                            del builtins.BOT_LETTER_ERROR_CALLBACK
                        except AttributeError:
                            pass
                    else:
                        builtins.BOT_LETTER_ERROR_CALLBACK = previous_error_callback
            except Exception as e:
                error_caught = f"{type(e).__name__}: {str(e)}"
            
            import builtins
            user_stopped = getattr(builtins, 'STOP_BOT', False)
            
            if user_stopped:
                try:
                    sync_data_to_gui(self.data_manager)
                except Exception:
                    pass
                return
            
            if error_caught and is_network_error(error_caught):
                self.error_message = f"NETWORK_ERROR|{error_caught[:500]}"
                return

            if error_caught:
                self.error_message = error_caught[:500]
                return
            
            try:
                sync_data_to_gui(self.data_manager)
            except Exception:
                pass
            
        except Exception as e:
            error_str = f"{type(e).__name__}: {str(e)}"
            if is_network_error(error_str):
                self.error_message = f"NETWORK_ERROR|{error_str[:500]}"
            else:
                self.error_message = error_str

class SavedLettersDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(" شماره نامه‌های ذخیره شده")
        self.setLayoutDirection(Qt.RightToLeft)
        self.setMinimumSize(600, 650)
        
        icon_path = get_icon_path()
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        self.setStyleSheet(f"""
            QDialog {{ background-color: {Theme.BG_MAIN}; }}
            QLabel#header {{
                font-size: 15px; font-weight: bold; color: {Theme.PRIMARY_DARK};
                padding: 16px;
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {Theme.PRIMARY_SOFT}, stop:1 {Theme.SECONDARY_SOFT});
                border-radius: 12px;
            }}
            QLabel#count {{
                font-size: 11px; color: {Theme.TEXT_SECONDARY};
                padding: 8px; background-color: {Theme.BG_CARD};
                border-radius: 8px; border: 1px solid {Theme.BORDER_LIGHT};
            }}
            QListWidget {{
                background-color: {Theme.BG_CARD};
                border: 1px solid {Theme.BORDER};
                border-radius: 12px; font-size: 12px;
                padding: 8px; outline: none;
            }}
            QListWidget::item {{
                padding: 10px; border-bottom: 1px solid {Theme.BORDER_LIGHT};
                border-radius: 6px; margin: 2px 0px;
            }}
            QListWidget::item:hover {{ background-color: {Theme.BG_HEADER}; }}
            QListWidget::item:selected {{
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {Theme.PRIMARY_SOFT}, stop:1 {Theme.SECONDARY_SOFT});
                color: {Theme.SELECTION_TEXT}; font-weight: bold;
            }}
            QPushButton {{
                border: none; border-radius: 8px; padding: 8px 16px;
                font-weight: bold; font-size: 11px; min-height: 30px;
            }}
            QPushButton#delete_btn {{
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {Theme.DANGER}, stop:1 {Theme.DANGER_DARK});
                color: white;
            }}
            QPushButton#delete_btn:hover {{ background-color: {Theme.DANGER_DARK}; }}
            QPushButton#delete_all_btn {{
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {Theme.WARNING}, stop:1 {Theme.WARNING_DARK});
                color: white;
            }}
            QPushButton#delete_all_btn:hover {{ background-color: {Theme.WARNING_DARK}; }}
            QPushButton#close_btn {{
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #94A3B8, stop:1 #64748B);
                color: white;
            }}
            QPushButton#close_btn:hover {{ background-color: #64748B; }}
            QScrollBar:vertical {{
                background: transparent; width: 10px;
                border-radius: 5px; margin: 0;
            }}
            QScrollBar::handle:vertical {{
                background: {Theme.BORDER}; border-radius: 5px; min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{ background: {Theme.PRIMARY_LIGHT}; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(16, 16, 16, 16)
        
        header = QLabel("شماره نامه‌های پردازش شده تا الان")
        header.setObjectName("header")
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)
        
        self.count_label = QLabel("")
        self.count_label.setObjectName("count")
        self.count_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.count_label)
        
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QListWidget.ExtendedSelection)
        layout.addWidget(self.list_widget, 1)
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)
        
        self.delete_btn = QPushButton(" حذف انتخاب شده")
        self.delete_btn.setObjectName("delete_btn")
        self.delete_btn.clicked.connect(self.delete_selected)
        btn_layout.addWidget(self.delete_btn)
        
        self.delete_all_btn = QPushButton(" حذف همه")
        self.delete_all_btn.setObjectName("delete_all_btn")
        self.delete_all_btn.clicked.connect(self.delete_all)
        btn_layout.addWidget(self.delete_all_btn)
        
        btn_layout.addStretch()

        layout.addLayout(btn_layout)
        
        self.load_letters()
    
    def get_state_file(self):
        if os.path.isabs(STATE_FILE):
            return STATE_FILE
        base_dir = get_base_dir()
        return os.path.join(base_dir, STATE_FILE)

    def load_letters(self):
        self.list_widget.clear()
        state_file = self.get_state_file()
        
        if not os.path.exists(state_file):
            self.count_label.setText(" فایل حافظه وجود ندارد")
            return
        
        try:
            with open(state_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            processed = data.get("processed", [])
            
            if not processed:
                self.count_label.setText(" هیچ شماره نامه‌ای ذخیره نشده است")
                return
            
            try:
                processed_sorted = sorted(processed, key=lambda x: str(x), reverse=True)
            except:
                processed_sorted = processed
            
            for number in processed_sorted:
                item = QListWidgetItem(f"📄  {number}")
                item.setData(Qt.UserRole, str(number))
                self.list_widget.addItem(item)
            
            self.count_label.setText(f"📊 تعداد: {len(processed)} شماره نامه")
        except Exception as e:
            self.count_label.setText(f"❌ خطا در خواندن فایل: {e}")
    
    def save_letters(self, numbers_list):
        state_file = self.get_state_file()
        try:
            data = {"processed": sorted([str(n) for n in numbers_list])}
            temp_file = state_file + ".tmp"
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            os.replace(temp_file, state_file)
            return True
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در ذخیره فایل:\n{e}")
            return False
    
    def delete_selected(self):
        selected_items = self.list_widget.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "خطا", "لطفاً حداقل یک شماره را انتخاب کنید!")
            return
        
        reply = QMessageBox.question(
            self, "🗑️ تأیید حذف",
            f"آیا از حذف {len(selected_items)} شماره نامه مطمئن هستید؟\n\n"
            f"⚠️ بعد از حذف، اگر این نامه‌ها در کارتابل باشند، دوباره پردازش خواهند شد.",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return
        
        state_file = self.get_state_file()
        try:
            with open(state_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            current_numbers = set(str(n) for n in data.get("processed", []))
        except:
            current_numbers = set()
        
        for item in selected_items:
            number = str(item.data(Qt.UserRole))
            current_numbers.discard(number)
        
        if self.save_letters(list(current_numbers)):
            self.load_letters()
            QMessageBox.information(self, "✅ موفق", "شماره‌های انتخاب شده حذف شدند!")
    
    def delete_all(self):
        if self.list_widget.count() == 0:
            QMessageBox.information(self, "اطلاع", "لیست خالی است!")
            return
        
        reply = QMessageBox.question(
            self, "⚠️ تأیید حذف همه",
            f"آیا از حذف همه {self.list_widget.count()} شماره نامه مطمئن هستید؟\n\n"
            f"⚠️ هشدار: بعد از حذف، همه نامه‌های کارتابل دوباره پردازش خواهند شد!",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return
        
        if self.save_letters([]):
            self.load_letters()
            QMessageBox.information(self, "✅ موفق", "همه شماره‌ها حذف شدند!")

class LetterProgressDialog(QDialog):
    stop_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("پردازش نامه")
        self.setLayoutDirection(Qt.RightToLeft)
        self.setFixedSize(460, 290)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        
        icon_path = get_icon_path()
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        self.setStyleSheet(f"""
            QDialog {{ background-color: {Theme.BG_CARD}; }}
            QLabel#title {{
                font-size: 14px; font-weight: bold;
                color: {Theme.PRIMARY_DARK}; padding: 4px;
            }}
            QLabel#letter_info {{
                font-size: 12px; color: {Theme.TEXT_PRIMARY}; padding: 2px 4px;
            }}
            QLabel#stage {{
                font-size: 12px; color: {Theme.INFO_DARK};
                padding: 6px; background-color: {Theme.PRIMARY_SOFT};
                border-radius: 6px;
            }}
            QProgressBar {{
                border: 1px solid {Theme.BORDER};
                border-radius: 8px;
                background-color: {Theme.BG_MAIN};
                text-align: center;
                height: 26px; font-size: 12px; font-weight: bold;
                color: {Theme.TEXT_PRIMARY};
            }}
            QProgressBar::chunk {{
                background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {Theme.PRIMARY}, stop:1 {Theme.SECONDARY});
                border-radius: 7px;
            }}
            QPushButton#stop_btn {{
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {Theme.DANGER}, stop:1 {Theme.DANGER_DARK});
                color: white; font-weight: bold; font-size: 11px;
                padding: 6px 16px; border-radius: 8px;
                min-height: 30px; border: none;
            }}
            QPushButton#stop_btn:hover {{ background-color: {Theme.DANGER_DARK}; }}
            QPushButton#hide_btn {{
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #94A3B8, stop:1 #64748B);
                color: white; font-weight: bold; font-size: 11px;
                padding: 6px 16px; border-radius: 8px;
                min-height: 30px; border: none;
            }}
            QPushButton#hide_btn:hover {{ background-color: #64748B; }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(16, 14, 16, 14)
        
        title = QLabel("در حال پردازش نامه")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        self.letter_label = QLabel("📄 شماره نامه: —")
        self.letter_label.setObjectName("letter_info")
        layout.addWidget(self.letter_label)
        
        self.subject_label = QLabel("📌 موضوع: —")
        self.subject_label.setObjectName("letter_info")
        layout.addWidget(self.subject_label)
        
        layout.addSpacing(4)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("%p%")
        layout.addWidget(self.progress_bar)
        
        self.stage_label = QLabel("⏳ در حال آماده‌سازی...")
        self.stage_label.setObjectName("stage")
        self.stage_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.stage_label)
        
        layout.addStretch()
        
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)
        
        self.stop_btn = QPushButton("⏹️ توقف")
        self.stop_btn.setObjectName("stop_btn")
        self.stop_btn.setCursor(Qt.PointingHandCursor)
        self.stop_btn.clicked.connect(self._on_stop)
        btn_layout.addWidget(self.stop_btn)
        
        self.hide_btn = QPushButton("👁️ پنهان")
        self.hide_btn.setObjectName("hide_btn")
        self.hide_btn.setCursor(Qt.PointingHandCursor)
        self.hide_btn.clicked.connect(self.hide)
        btn_layout.addWidget(self.hide_btn)
        
        layout.addLayout(btn_layout)
    
    def set_letter_info(self, number, title=""):
        self.letter_label.setText(f"📄 شماره نامه: {number}")
        if title:
            display_title = title if len(title) <= 45 else title[:45] + "..."
            self.subject_label.setText(f" موضوع: {display_title}")
        else:
            self.subject_label.setText(" موضوع: —")
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setFormat("%p%")
        self.progress_bar.setValue(0)
        self.stage_label.setText(" شروع پردازش...")
    
    def set_progress(self, percent, message=""):
        if percent is None:
            self.progress_bar.setRange(0, 0)
            self.progress_bar.setFormat("")
        else:
            self.progress_bar.setRange(0, 100)
            self.progress_bar.setFormat("%p%")
            self.progress_bar.setValue(int(percent))
        if message:
            self.stage_label.setText(f"🔄 {message}")
    
    def _on_stop(self):
        self.stop_requested.emit()
        self.hide()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("پَـــــرنا | سیستم هوشمند پردازش نامه‌ها")
        screen = QApplication.primaryScreen()
        if screen:
            available = screen.availableGeometry()
            window_width = min(
                available.width(), max(800, min(1800, int(available.width() * 0.92)))
            )
            window_height = min(
                available.height(), max(600, min(1000, int(available.height() * 0.90)))
            )
            window_x = available.x() + (available.width() - window_width) // 2
            window_y = available.y() + (available.height() - window_height) // 2
            self.setGeometry(window_x, window_y, window_width, window_height)
        else:
            self.resize(1200, 720)
        self.setLayoutDirection(Qt.RightToLeft)
        
        icon_path = get_icon_path()
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
        
        self.data_manager = DataManager()
        self.model = TableModel(self.data_manager)
        self.robot_thread = None
        
        self._highlighted_numbers = []
        
        self.init_ui()
        
        settings = QSettings("MyApp", "LetterManager")
        saved_size = settings.value("font_size", 12, type=int)
        
        if hasattr(self, 'font_size_combo'):
            self.font_size_combo.blockSignals(True)
            self.font_size_combo.setCurrentText(str(saved_size))
            self.font_size_combo.blockSignals(False)
        
        self.change_font_size(saved_size)
        self.update_status()
        
        self.watch_timer = QTimer()
        self.watch_timer.timeout.connect(self.check_for_new_data)
        self.watch_timer.start(1500)
        self._last_record_count = len(self.data_manager.records)
        
        self.progress_dialog = LetterProgressDialog(self)
        self.progress_dialog.stop_requested.connect(self._on_progress_stop)
        self._current_letter_number = ""
        self._initial_column_fit_pending = True

    def showEvent(self, event):
        super().showEvent(event)
        if self._initial_column_fit_pending:
            self._initial_column_fit_pending = False
            QTimer.singleShot(100, self._fit_initial_column_widths)

    def _fit_initial_column_widths(self):
        available_width = self.table_view.viewport().width()
        if available_width <= 0:
            return

        base_column_widths = self._base_column_widths
        minimum_column_widths = self._minimum_column_widths
        base_total = sum(base_column_widths)
        minimum_total = sum(minimum_column_widths)

        if available_width >= base_total:
            target_width = min(available_width, round(base_total * 1.25))
            scale = target_width / base_total
            column_widths = [round(width * scale) for width in base_column_widths]
        elif available_width >= minimum_total:
            scale = (available_width - minimum_total) / (base_total - minimum_total)
            column_widths = [
                minimum + round((base - minimum) * scale)
                for base, minimum in zip(base_column_widths, minimum_column_widths)
            ]
        else:
            scale = available_width / minimum_total
            column_widths = [round(minimum * scale) for minimum in minimum_column_widths]

        target_width = min(available_width, round(base_total * 1.25))
        if column_widths:
            column_widths[-1] += target_width - sum(column_widths)

        for index, width in enumerate(column_widths):
            self.table_view.setColumnWidth(index, width)

        horizontal_scrollbar = self.table_view.horizontalScrollBar()
        horizontal_scrollbar.setValue(horizontal_scrollbar.minimum())
    
    def _make_button_style(self, color_from, color_to, color_hover, text_color="white"):
        return f"""
            QPushButton {{
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {color_from}, stop:1 {color_to});
                color: {text_color};
                font-weight: 600; font-size: 11px;
                padding: 6px 16px; border: none;
                border-radius: 8px; min-height: 30px;
            }}
            QPushButton:hover {{ background-color: {color_hover}; }}
            QPushButton:pressed {{
                background-color: {color_to};
                padding-top: 8px; padding-bottom: 4px;
            }}
            QPushButton:disabled {{
                background-color: #CBD5E1; color: #94A3B8;
            }}
        """
    
    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(12, 12, 12, 12)
        
        toolbar_frame = QFrame()
        toolbar_frame.setObjectName("toolbar_frame")
        toolbar_frame.setStyleSheet(f"""
            QFrame#toolbar_frame {{
                background-color: {Theme.BG_TOOLBAR};
                border-radius: 12px;
                border: 1px solid {Theme.BORDER_LIGHT};
            }}
        """)
        toolbar = QHBoxLayout(toolbar_frame)
        toolbar.setSpacing(8)
        toolbar.setContentsMargins(12, 10, 12, 10)
        
        self.menu_btn = QToolButton()
        self.menu_btn.setText("☰")
        self.menu_btn.setPopupMode(QToolButton.InstantPopup)
        self.menu_btn.setFixedSize(38, 34)
        self.menu_btn.setToolTip("منو")
        self.menu_btn.setCursor(Qt.PointingHandCursor)
        self.menu_btn.setStyleSheet(f"""
            QToolButton {{
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {Theme.PRIMARY}, stop:1 {Theme.PRIMARY_DARK});
                color: white; font-size: 18px; font-weight: bold;
                border: none; border-radius: 8px; padding: 0px;
            }}
            QToolButton:hover {{ background-color: {Theme.PRIMARY_DARK}; }}
            QToolButton::menu-indicator {{ image: none; width: 0px; }}
        """)
        
        menu = QMenu(self)
        menu.setLayoutDirection(Qt.RightToLeft)
        menu.setStyleSheet(f"""
            QMenu {{
                background-color: {Theme.BG_CARD};
                border: 1px solid {Theme.BORDER};
                border-radius: 10px; padding: 6px; font-size: 12px;
            }}
            QMenu::item {{
                padding: 10px 24px 10px 16px;
                border-radius: 6px; text-align: right;
                color: {Theme.TEXT_PRIMARY};
            }}
            QMenu::item:selected {{
                background-color: {Theme.BG_HEADER};
                color: {Theme.PRIMARY_DARK};
            }}
            QMenu::separator {{
                height: 1px; background: {Theme.BORDER_LIGHT};
                margin: 6px 10px;
            }}
            QWidgetAction {{ background: transparent; }}
        """)
        
        saved_letters_action = QAction("  شماره نامه‌های ذخیره شده", self)
        saved_letters_action.triggered.connect(self.open_saved_letters)
        menu.addAction(saved_letters_action)
        
        menu.addSeparator()
        
        font_size_widget = QWidget()
        font_size_widget.setLayoutDirection(Qt.RightToLeft)
        font_layout = QHBoxLayout(font_size_widget)
        font_layout.setContentsMargins(16, 8, 16, 8)
        font_layout.setSpacing(10)
        
        font_label = QLabel(" اندازه متن:")
        font_label.setStyleSheet(f"font-size: 12px; color: {Theme.TEXT_PRIMARY}; font-weight: 500;")
        font_layout.addWidget(font_label)
        
        self.font_size_combo = QComboBox()
        self.font_size_combo.addItems(['8', '9', '10', '11', '12', '13', '14', '15', '16', '18', '20'])
        settings = QSettings("MyApp", "LetterManager")
        saved_size = settings.value("font_size", 12, type=int)
        self.font_size_combo.setCurrentText(str(saved_size))
        self.font_size_combo.currentTextChanged.connect(self.change_font_size_from_combo)
        self.font_size_combo.setStyleSheet(f"""
            QComboBox {{
                font-size: 11px; padding: 4px 10px;
                min-height: 22px; border: 1px solid {Theme.BORDER};
                border-radius: 6px; background-color: white;
                min-width: 70px; color: {Theme.TEXT_PRIMARY};
            }}
            QComboBox:hover {{ border-color: {Theme.PRIMARY_LIGHT}; }}
            QComboBox::drop-down {{ border: none; width: 20px; }}
        """)
        font_layout.addWidget(self.font_size_combo)
        font_layout.addStretch()
        
        font_widget_action = QWidgetAction(self)
        font_widget_action.setDefaultWidget(font_size_widget)
        menu.addAction(font_widget_action)

        menu.addSeparator()
        sort_menu = menu.addMenu("مرتب‌سازی جدول")
        sort_menu.setLayoutDirection(Qt.RightToLeft)
        sort_group = QActionGroup(sort_menu)
        sort_group.setExclusive(True)
        sort_options = [
            ("ترتیب اصلی", None, False),
            ("تاریخ نامه: جدیدترین اول", "تاریخ", True),
            ("تاریخ نامه: قدیمی‌ترین اول", "تاریخ", False),
            ("ددلاین: زودترین تاریخ اول", "ددلاین", False),
            ("ددلاین: دیرترین تاریخ اول", "ددلاین", True),
        ]
        for option_index, (label, field, descending) in enumerate(sort_options):
            action = QAction(label, self)
            action.setCheckable(True)
            action.setChecked(option_index == 0)
            sort_group.addAction(action)
            action.triggered.connect(
                lambda _checked=False, sort_field=field, reverse=descending:
                    self.model.set_sort(sort_field, reverse)
            )
            sort_menu.addAction(action)
        
        self.menu_btn.setMenu(menu)
        toolbar.addWidget(self.menu_btn)
        
        toolbar.addSpacing(6)
        
        bot_btn = QPushButton("  اجرای ربات")
        bot_btn.setCursor(Qt.PointingHandCursor)
        bot_btn.clicked.connect(self.run_bot)
        bot_btn.setStyleSheet(self._make_button_style(
            Theme.PRIMARY, Theme.PRIMARY_DARK, Theme.PRIMARY_DARK
        ))
        toolbar.addWidget(bot_btn)
        
        self.stop_btn = QPushButton(" توقف")
        self.stop_btn.setCursor(Qt.PointingHandCursor)
        self.stop_btn.clicked.connect(self.stop_bot)
        self.stop_btn.setEnabled(False)
        self.stop_btn.setStyleSheet(self._make_button_style(
            Theme.WARNING, Theme.WARNING_DARK, Theme.WARNING_DARK, "#FFFFFF"
        ))
        toolbar.addWidget(self.stop_btn)
        
        sep1 = QFrame()
        sep1.setFrameShape(QFrame.VLine)
        sep1.setStyleSheet(f"color: {Theme.BORDER};")
        sep1.setFixedHeight(28)
        toolbar.addWidget(sep1)
        
        for icon, tooltip, callback, color_from, color_to in [
            ("🖨️", "پرینت", self.print_table, Theme.INFO, Theme.INFO_DARK),
            ("📄", "ذخیره PDF", self.save_to_pdf, Theme.INFO, Theme.INFO_DARK),
            ("💾", "ذخیره اکسل", self.save_to_excel, Theme.SECONDARY, Theme.SECONDARY_DARK),
        ]:
            btn = QPushButton(icon)
            btn.setFixedSize(36, 34)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setToolTip(tooltip)
            btn.clicked.connect(callback)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 {color_from}, stop:1 {color_to});
                    color: white; font-size: 15px;
                    border: none; border-radius: 8px;
                }}
                QPushButton:hover {{ background-color: {color_to}; }}
                QPushButton:pressed {{ background-color: {color_to}; }}
            """)
            toolbar.addWidget(btn)
        
        toolbar.addStretch()
        
        search_container = QFrame()
        search_container.setStyleSheet(f"""
            QFrame {{
                background-color: {Theme.BG_MAIN};
                border: 1px solid {Theme.BORDER};
                border-radius: 8px;
            }}
        """)
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(10, 0, 10, 0)
        search_layout.setSpacing(6)
        
        search_icon = QLabel("🔍")
        search_icon.setStyleSheet("font-size: 13px; border: none; background: transparent;")
        search_layout.addWidget(search_icon)
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("جستجو در همه ستون‌ها...")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.setFixedWidth(240)
        self.search_input.textChanged.connect(self.on_search_changed)
        self.search_input.setStyleSheet(f"""
            QLineEdit {{
                font-size: 11px; padding: 6px 4px;
                min-height: 20px; border: none;
                background: transparent; color: {Theme.TEXT_PRIMARY};
            }}
        """)
        search_layout.addWidget(self.search_input)
        toolbar.addWidget(search_container)
        
        toolbar.addSpacing(6)
        
        for icon, tooltip, callback in [
            ("🗑️", "حذف انتخاب شده‌ها", self.delete_selected),
            ("🔄", "پاک کردن همه", self.clear_all),
        ]:
            btn = QPushButton(icon)
            btn.setFixedSize(36, 34)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setToolTip(tooltip)
            btn.clicked.connect(callback)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 {Theme.DANGER}, stop:1 {Theme.DANGER_DARK});
                    color: white; font-size: 15px;
                    border: none; border-radius: 8px;
                }}
                QPushButton:hover {{ background-color: {Theme.DANGER_DARK}; }}
                QPushButton:pressed {{ background-color: {Theme.DANGER_DARK}; }}
            """)
            toolbar.addWidget(btn)
        
        main_layout.addWidget(toolbar_frame)
        
        table_container = QFrame()
        table_container.setStyleSheet(f"""
            QFrame {{
                background-color: {Theme.BG_CARD};
                border-radius: 12px;
                border: 1px solid {Theme.BORDER_LIGHT};
            }}
        """)
        table_layout = QVBoxLayout(table_container)
        table_layout.setContentsMargins(2, 2, 2, 2)
        
        self.table_view = QTableView()
        self.table_view.setModel(self.model)
        self.table_view.setSelectionMode(QTableView.ExtendedSelection)
        self.table_view.setSelectionBehavior(QTableView.SelectRows)
        self.table_view.setAlternatingRowColors(True)
        self.table_view.verticalHeader().setDefaultSectionSize(60)
        self.table_view.verticalHeader().setVisible(True)
        self.table_view.setShowGrid(False)
        self.table_view.setWordWrap(True)
        self.table_view.setTextElideMode(Qt.ElideNone)
        self.table_view.resizeRowsToContents()
        self.table_view.setStyleSheet(f"""
            QTableView {{
                background-color: {Theme.BG_CARD};
                alternate-background-color: {Theme.BG_ALT_ROW};
                gridline-color: transparent;
                font-size: 12px; color: {Theme.TEXT_PRIMARY};
                border: none; border-radius: 10px;
                selection-background-color: {Theme.SELECTION_BG};
                selection-color: {Theme.SELECTION_TEXT};
                outline: none;
            }}
            QTableView::item {{
                padding: 6px 4px;
                border-bottom: 1px solid {Theme.BORDER_LIGHT};
            }}
            QTableView::item:selected {{
                background-color: {Theme.SELECTION_BG};
                color: {Theme.SELECTION_TEXT};
            }}
            QTableView::item:hover {{ background-color: {Theme.BG_HEADER}; }}
            QHeaderView {{
                background-color: transparent; border: none;
            }}
            QHeaderView::section {{
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {Theme.HEADER_FROM}, stop:1 {Theme.HEADER_TO});
                color: white; padding: 10px 6px;
                border: none; font-weight: 600; font-size: 11px;
            }}
            QHeaderView::section:first {{ border-top-right-radius: 10px; }}
            QHeaderView::section:last {{ border-top-left-radius: 10px; }}
            QHeaderView::section:horizontal {{
                border-left: 1px solid rgba(255, 255, 255, 0.2);
            }}
            QScrollBar:vertical {{
                background: transparent; width: 10px;
                border-radius: 5px; margin: 0;
            }}
            QScrollBar::handle:vertical {{
                background: {Theme.BORDER}; border-radius: 5px; min-height: 30px;
            }}
            QScrollBar::handle:vertical:hover {{ background: {Theme.PRIMARY_LIGHT}; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
            QScrollBar:horizontal {{
                background: transparent; height: 10px;
                border-radius: 5px; margin: 0;
            }}
            QScrollBar::handle:horizontal {{
                background: {Theme.BORDER}; border-radius: 5px; min-width: 30px;
            }}
            QScrollBar::handle:horizontal:hover {{ background: {Theme.PRIMARY_LIGHT}; }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; }}
        """)
        
        header = self.table_view.horizontalHeader()
        self._base_column_widths = (40, 90, 100, 90, 180, 160, 220, 280, 100, 180)
        self._minimum_column_widths = (36, 65, 70, 60, 130, 115, 150, 180, 75, 125)
        base_column_widths = self._base_column_widths
        minimum_column_widths = self._minimum_column_widths
        available_width = max(1, self.width() - 54)
        base_total = sum(base_column_widths)
        minimum_total = sum(minimum_column_widths)

        if available_width >= base_total:
            target_width = min(available_width, round(base_total * 1.25))
            scale = target_width / base_total
            column_widths = [round(width * scale) for width in base_column_widths]
        elif available_width >= minimum_total:
            scale = (available_width - minimum_total) / (base_total - minimum_total)
            column_widths = [
                minimum + round((base - minimum) * scale)
                for base, minimum in zip(base_column_widths, minimum_column_widths)
            ]
        else:
            scale = available_width / minimum_total
            column_widths = [round(minimum * scale) for minimum in minimum_column_widths]

        target_width = min(available_width, round(base_total * 1.25))
        if column_widths:
            column_widths[-1] += target_width - sum(column_widths)

        header.setStretchLastSection(False)
        header.setMinimumSectionSize(32)
        for i, width in enumerate(column_widths):
            header.setSectionResizeMode(i, QHeaderView.Interactive)
            self.table_view.setColumnWidth(i, width)
        
        table_layout.addWidget(self.table_view)
        main_layout.addWidget(table_container, 1)
        
        bottom_frame = QFrame()
        bottom_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {Theme.BG_CARD};
                border-radius: 12px;
                border: 1px solid {Theme.BORDER_LIGHT};
            }}
        """)
        bottom_layout = QVBoxLayout(bottom_frame)
        bottom_layout.setSpacing(4)
        bottom_layout.setContentsMargins(10, 6, 10, 6)
        
        command_header = QHBoxLayout()
        command_header.setSpacing(4)
        command_icon = QLabel("✏️")
        command_icon.setStyleSheet("font-size: 12px; border: none; background: transparent;")
        command_header.addWidget(command_icon)
        
        command_label = QLabel("دستور ارجاع")
        command_label.setStyleSheet(f"""
            font-size: 11px; font-weight: 600; 
            color: {Theme.PRIMARY_DARK};
            border: none; background: transparent;
        """)
        command_header.addWidget(command_label)
        command_header.addStretch()
        bottom_layout.addLayout(command_header)
        
        self.command_text = QTextEdit()
        self.command_text.setPlaceholderText("متن دستور ارجاع را وارد کنید...")
        self.command_text.setMaximumHeight(26)
        self.command_text.setStyleSheet(f"""
            QTextEdit {{
                border: 1.5px solid {Theme.BORDER};
                border-radius: 6px; padding: 2px 8px;
                font-size: 11px; min-height: 18px; max-height: 26px;
                background-color: {Theme.BG_MAIN};
                color: {Theme.TEXT_PRIMARY};
            }}
            QTextEdit:focus {{
                border-color: {Theme.PRIMARY};
                background-color: white;
            }}
        """)
        bottom_layout.addWidget(self.command_text)
        
        command_buttons = QHBoxLayout()
        command_buttons.setSpacing(6)
        
        save_command_btn = QPushButton("ذخیره")
        save_command_btn.setCursor(Qt.PointingHandCursor)
        save_command_btn.clicked.connect(self.save_command)
        save_command_btn.setFixedHeight(26)
        save_command_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {Theme.SECONDARY}, stop:1 {Theme.SECONDARY_DARK});
                color: white; font-weight: 600; font-size: 10px;
                padding: 2px 12px; border: none;
                border-radius: 6px; min-height: 22px;
            }}
            QPushButton:hover {{ background-color: {Theme.SECONDARY_DARK}; }}
        """)
        command_buttons.addWidget(save_command_btn)
        
        edit_command_btn = QPushButton("ویرایش")
        edit_command_btn.setCursor(Qt.PointingHandCursor)
        edit_command_btn.clicked.connect(self.edit_command)
        edit_command_btn.setFixedHeight(26)
        edit_command_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {Theme.INFO}, stop:1 {Theme.INFO_DARK});
                color: white; font-weight: 600; font-size: 10px;
                padding: 2px 12px; border: none;
                border-radius: 6px; min-height: 22px;
            }}
            QPushButton:hover {{ background-color: {Theme.INFO_DARK}; }}
        """)
        command_buttons.addWidget(edit_command_btn)
        
        clear_command_btn = QPushButton("حذف")
        clear_command_btn.setCursor(Qt.PointingHandCursor)
        clear_command_btn.clicked.connect(self.clear_command)
        clear_command_btn.setFixedHeight(26)
        clear_command_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {Theme.DANGER}, stop:1 {Theme.DANGER_DARK});
                color: white; font-weight: 600; font-size: 10px;
                padding: 2px 12px; border: none;
                border-radius: 6px; min-height: 22px;
            }}
            QPushButton:hover {{ background-color: {Theme.DANGER_DARK}; }}
        """)
        command_buttons.addWidget(clear_command_btn)
        
        command_buttons.addStretch()
        bottom_layout.addLayout(command_buttons)
        
        main_layout.addWidget(bottom_frame)
        
        self.status_label = QLabel("✨ آماده")
        self.status_label.setStyleSheet(f"""
            padding: 8px 16px; 
            background-color: {Theme.BG_CARD};
            border: 1px solid {Theme.BORDER_LIGHT};
            border-radius: 10px; font-size: 11px;
            min-height: 20px; color: {Theme.TEXT_SECONDARY};
            font-weight: 500;
        """)
        main_layout.addWidget(self.status_label)
        
        self.setStyleSheet(f"""
            QMainWindow {{ background-color: {Theme.BG_MAIN}; }}
            QLabel {{ font-size: 11px; color: {Theme.TEXT_PRIMARY}; }}
            QToolTip {{
                background-color: {Theme.TEXT_PRIMARY};
                color: white; border: none;
                padding: 6px 10px; border-radius: 6px; font-size: 11px;
            }}
        """)

    def show_network_error_dialog(self, error_details=""):
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Warning)
        msg.setWindowTitle("🌐 خطای اینترنت")
        msg.setLayoutDirection(Qt.RightToLeft)
        msg.setTextFormat(Qt.RichText)
        
        icon_path = get_icon_path()
        if os.path.exists(icon_path):
            msg.setWindowIcon(QIcon(icon_path))
        
        msg.setStyleSheet(f"""
            QMessageBox {{ background-color: {Theme.BG_CARD}; }}
            QMessageBox QLabel {{ color: {Theme.TEXT_PRIMARY}; }}
            QPushButton {{
                background-color: {Theme.PRIMARY};
                color: white; font-weight: bold; font-size: 11px;
                padding: 6px 16px; border-radius: 6px;
                min-height: 26px; border: none;
            }}
            QPushButton:hover {{ background-color: {Theme.PRIMARY_DARK}; }}
        """)
        
        msg.setText(
            f"<div style='direction:rtl; text-align:right; font-family:Tahoma;'>"
            f"<p style='color:{Theme.WARNING_DARK}; font-size:14pt; font-weight:bold;'>"
            f"🌐 اینترنت ضعیف است!</p>"
            f"<p style='font-size:11pt; color:{Theme.TEXT_PRIMARY};'>"
            f"ارتباط با سرور برقرار نشد یا قطع شده است."
            f"<br>لطفاً چند لحظه صبر کنید و دوباره امتحان کنید.</p></div>"
        )
        
        details = (
            f"<div style='direction:rtl; text-align:right; font-family:Tahoma; font-size:10pt;'>"
            f"<b style='color:{Theme.INFO};'> پیشنهادات:</b>"
            f"<ul style='line-height:1.9; color:{Theme.TEXT_PRIMARY};'>"
            f"<li>اتصال اینترنت خود را بررسی کنید</li>"
            f"<li>چند دقیقه دیگر دوباره امتحان کنید</li>"
            f"<li>صفحه مرورگر را رفرش کنید (F5)</li>"
            f"</ul>"
        )
        
        if error_details:
            error_display = error_details.replace("NETWORK_ERROR|", "").replace("NETWORK_OFFLINE", "اینترنت قطع است")
            error_display = error_display[:400]
            details += (
                f"<hr style='border:none; border-top:1px solid {Theme.BORDER};'>"
                f"<b style='color:{Theme.TEXT_SECONDARY};'>جزئیات فنی:</b>"
                f"<br><span style='font-family:monospace; font-size:9pt; color:{Theme.DANGER};'>"
                f"{error_display}</span>"
            )
        
        details += "</div>"
        msg.setInformativeText(details)
        
        retry_btn = msg.addButton("🔄 دوباره امتحان کن", QMessageBox.ActionRole)
        msg.addButton("باشه", QMessageBox.AcceptRole)
        
        msg.exec_()
        
        if msg.clickedButton() == retry_btn:
            for btn in self.findChildren(QPushButton):
                if "اجرای ربات" in btn.text():
                    btn.setEnabled(True)
                    btn.click()
                    break
    
    def open_saved_letters(self):
        dialog = SavedLettersDialog(self)
        dialog.exec_()

    def show_driver_error_dialog(self, title, main_message, details_html, driver_path):
        download_url = "https://googlechromelabs.github.io/chrome-for-testing/"
        chrome_version = get_chrome_version()
        chrome_ver_short = chrome_version.split('.')[0] if chrome_version else "???"
        
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle(f"❌ {title}")
        msg.setLayoutDirection(Qt.RightToLeft)
        msg.setTextFormat(Qt.RichText)
        
        icon_path = get_icon_path()
        if os.path.exists(icon_path):
            msg.setWindowIcon(QIcon(icon_path))
        
        msg.setStyleSheet(f"""
            QMessageBox {{ background-color: {Theme.BG_CARD}; }}
            QPushButton {{
                background-color: {Theme.PRIMARY};
                color: white; font-weight: bold; font-size: 11px;
                padding: 6px 16px; border-radius: 6px;
                min-height: 26px; border: none;
            }}
            QPushButton:hover {{ background-color: {Theme.PRIMARY_DARK}; }}
        """)
        
        msg.setText(
            f"<div style='direction:rtl; text-align:right; font-family:Tahoma;'>"
            f"<p style='color:{Theme.DANGER}; font-size:12pt; font-weight:bold;'>{main_message}</p></div>"
        )

        info_html = f"""
        <div dir="rtl" style="direction:rtl; text-align:right; font-family:Tahoma; font-size:10pt;">

        {details_html}

        <hr style="border:none; border-top:1px solid {Theme.BORDER};">

        <p style="color:{Theme.INFO}; font-weight:bold; font-size:11pt; text-align:right; margin:8px 0;">
            راهنمای دانلود
        </p>

        <ul style="line-height:1.9; list-style:none; padding:0; margin:0; text-align:right;">
            <li style="text-align:right;">
            <bdi>chromedriver</bdi> هم‌نسخه با کروم خود را از لینک زیر دانلود کنید
            </li>
        </ul>

        <p style="font-size:9pt; color:{Theme.INFO}; text-align:right; direction:ltr; word-break:break-all;">
            {download_url}
        </p>

        <ul style="line-height:1.9; list-style:none; padding:0; margin:0; text-align:right;">
            <li style="text-align:right;">
            فایل <code dir="ltr">chromedriver.exe</code> را در مسیر زیر قرار دهید
            <br>
            <span dir="ltr" style="color:{Theme.SECONDARY}; font-family:monospace; font-size:9pt; display:inline-block; text-align:left;">
                {driver_path}
            </span>
            </li>
        </ul>

        </div>
        """

        if chrome_version:
            info_html += f"""
        <p style='background:{Theme.PRIMARY_SOFT}; padding:10px; border-radius:6px; border-right:4px solid {Theme.INFO};'>
            <b>کروم شما:</b> نسخه <b style='color:{Theme.INFO}; font-size:11pt;'>{chrome_version}</b><br>
            در صفحه دانلود، نسخه <b>{chrome_ver_short}.x.x.x</b> را انتخاب کنید.
        </p>
        """
        else:
            info_html += f"""
        <p style='background:#FEF3C7; padding:10px; border-radius:6px; border-right:4px solid {Theme.WARNING};'>
            ⚠️ نسخه کروم شما به‌صورت خودکار پیدا نشد.<br>
            لطفاً کروم را باز کنید، به <code>chrome://version/</code> بروید و نسخه را ببینید.
        </p>
        """
        
        info_html += "</div>"
        msg.setInformativeText(info_html)
        
        copy_btn = msg.addButton("کپی لینک", QMessageBox.ActionRole)
        open_btn = msg.addButton("باز کردن صفحه دانلود", QMessageBox.ActionRole)
        msg.addButton("باشه", QMessageBox.AcceptRole)
        
        msg.exec_()
        
        clicked = msg.clickedButton()
        if clicked == copy_btn:
            QApplication.clipboard().setText(download_url)
            QMessageBox.information(self, "✅ موفق", "لینک در کلیپ‌بورد کپی شد!")
        elif clicked == open_btn:
            webbrowser.open(download_url)

    def on_search_changed(self, text):
        self.model.set_filter(text)
        self.table_view.resizeRowsToContents()
        self.update_status()

    def check_for_new_data(self):
        """چک خودکار فایل JSON — آپدیت جدول + پیشرفت + هایلایت"""
        try:
            if not os.path.exists(self.data_manager.data_file):
                return
            
            with open(self.data_manager.data_file, 'r', encoding='utf-8') as f:
                file_records = json.load(f)
            
            file_count = len(file_records)
            
            if file_count != self._last_record_count:
                if file_count > self._last_record_count:
                    new_indices = list(range(self._last_record_count, file_count))

                    for i in new_indices:
                        if i < len(file_records):
                            num = str(file_records[i].get("شماره", "")).strip()
                            if num:
                                self._highlighted_numbers.append(num)
                
                self.data_manager.records = file_records
                self._last_record_count = file_count
                self.model.refresh()
                self.table_view.resizeRowsToContents()
                self.update_status()
                
                if self._highlighted_numbers:
                    self.model.mark_new_numbers(self._highlighted_numbers)
                    
                    if self.model.rowCount() > 0:
                        last_index = self.model.index(self.model.rowCount() - 1, 0)
                        self.table_view.scrollTo(last_index, QTableView.PositionAtBottom)
                
                if self.search_input.text().strip():
                    self.model.set_filter(self.search_input.text())
        except Exception as e:
            print(f"⚠️ خطا در check_for_new_data: {e}")
    
    def update_progress(self, percent, message, number="", title=""):
        if number and number != self._current_letter_number:
            self._current_letter_number = number
            self.progress_dialog.set_letter_info(number, title)
            if not self.progress_dialog.isVisible():
                self.progress_dialog.show()

        actual_percent = None if percent < 0 else percent
        self.progress_dialog.set_progress(actual_percent, message)

    def _on_progress_stop(self):
        """توقف از توی پنجره پیشرفت"""
        import builtins
        builtins.STOP_BOT = True
        self.status_label.setText("ربات در حال پردازش نهایی است لطفا منتظر بمانید ...")
        print("⏹️ درخواست توقف از پنجره پیشرفت ارسال شد...")

    def run_bot(self):
        self._highlighted_numbers = []
        self.model.clear_highlights()
        
        self.status_label.setText("🔄 در حال اجرای ربات...")
        self.status_label.setStyleSheet(f"""
            padding: 8px 16px; 
            background-color: #FEF3C7;
            border: 1px solid {Theme.WARNING};
            border-radius: 10px; font-size: 11px;
            min-height: 20px; color: {Theme.WARNING_DARK};
            font-weight: 600;
        """)
        
        sender = self.sender()
        if sender:
            sender.setEnabled(False)
        
        self.stop_btn.setEnabled(True)
        
        import builtins
        builtins.STOP_BOT = False
        
        self.progress_dialog.set_letter_info("—", "در حال آماده‌سازی...")
        self.progress_dialog.set_progress(None, "در انتظار شروع پردازش...")
        self.progress_dialog.show()
        
        self._current_letter_number = ""
        
        self.robot_thread = RobotThread(self.data_manager)
        self.robot_thread.finished.connect(self.bot_finished)
        self.robot_thread.progress.connect(self.update_progress)
        self.robot_thread.start()
    
    def stop_bot(self):
        reply = QMessageBox.question(
            self, "⏹️ تأیید توقف",
            "آیا از توقف ربات مطمئن هستید؟\n\nنامه‌های پردازش‌شده تا الان نمایش داده میشن.",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            import builtins
            builtins.STOP_BOT = True
            self.status_label.setText("⏹️ در حال توقف ربات...")
            print("⏹️ درخواست توقف ربات ارسال شد...")
    
    def bot_finished(self):
        error = self.robot_thread.error_message if self.robot_thread else ""
        for btn in self.findChildren(QPushButton):
            if "اجرای ربات" in btn.text():
                btn.setEnabled(True)
                break
        
        self.stop_btn.setEnabled(False)
        
        if self.progress_dialog.isVisible():
            QTimer.singleShot(800, self.progress_dialog.hide)
        
        actual_total = len(self._highlighted_numbers)
        
        if error:
            driver_path = get_driver_path()
            
            if error == "NETWORK_OFFLINE":
                self.status_label.setText("🌐 اینترنت قطع است! لطفاً بعداً امتحان کنید.")
                self.show_network_error_dialog("اتصال اینترنت شما قطع است.")
                return
            
            if error.startswith("NETWORK_ERROR|"):
                details = error.replace("NETWORK_ERROR|", "")
                self.status_label.setText("🌐 اینترنت ضعیف است! لطفاً بعداً امتحان کنید.")
                self.show_network_error_dialog(details)
                return
            
            if error == "DRIVER_MISSING":
                self.status_label.setText("❌ chromedriver.exe پیدا نشد!")
                self.show_driver_error_dialog(
                    title="chromedriver پیدا نشد",
                    main_message="فایل chromedriver.exe در پوشه برنامه وجود ندارد!",
                    details_html=(  "لطفاً <b>chromedriver.exe</b> را دانلود و کنار فایل اجرایی برنامه قرار دهید."),
                    driver_path=driver_path
                )
                return
            
            if error.startswith("DRIVER_MISMATCH|"):
                parts = error.split("|")
                chrome_ver = parts[1] if len(parts) > 1 else "نامشخص"
                driver_ver = parts[2] if len(parts) > 2 else "نامشخص"
                self.status_label.setText("❌ نسخه chromedriver ناسازگار است!")
                details = (
                    f"<b>نسخه کروم سیستم:</b> "
                    f"<span style='color:{Theme.INFO}; font-size:11pt;'>{chrome_ver}</span><br>"
                    f"<b>نسخه chromedriver فعلی:</b> "
                    f"<span style='color:{Theme.DANGER}; font-size:11pt;'>{driver_ver}</span><br><br>"
                    f"<b>این دو نسخه باید یکسان باشند.</b>"
                )
                self.show_driver_error_dialog(
                    title="نسخه chromedriver ناسازگار",
                    main_message="نسخه chromedriver با کروم سیستم شما هماهنگ نیست!",
                    details_html=details,
                    driver_path=driver_path
                )
                return
            
            if is_network_error(error):
                self.status_label.setText("🌐 اینترنت ضعیف است! لطفاً بعداً امتحان کنید.")
                self.show_network_error_dialog(error)
                return
            
            self.status_label.setText(f"❌ خطا: {error[:80]}")
            QMessageBox.critical(self, "خطا", f"خطا در اجرای ربات:\n{error}")
        
        else:
            self.status_label.setText(f" ربات متوقف شد! {actual_total} نامه پردازش شد.")
            self.status_label.setStyleSheet(f"""
                padding: 8px 16px; 
                background-color: {Theme.SECONDARY_SOFT};
                border: 1px solid {Theme.SECONDARY};
                border-radius: 10px; font-size: 11px;
                min-height: 20px; color: {Theme.SECONDARY_DARK};
                font-weight: 600;
            """)
            self.model.refresh()
            self.update_status()
            self.table_view.resizeRowsToContents()
            self._last_record_count = len(self.data_manager.records)
            
            if actual_total > 0:
                if self.robot_thread and self.robot_thread.letter_errors:
                    details = "\n".join(
                        f"{number}: {message}"
                        for number, message in self.robot_thread.letter_errors[:5]
                    )
                    QMessageBox.warning(
                        self,
                        "پایان پردازش با خطا",
                        f"{actual_total} نامه پردازش شد؛ "
                        f"{len(self.robot_thread.letter_errors)} نامه ناموفق بود.\n\n{details}",
                    )
                else:
                    QMessageBox.information(self, "موفق",
                        f"✅ ربات متوقف شد!\n{actual_total} نامه پردازش و ذخیره شد.")
            else:
                if self.robot_thread and self.robot_thread.letter_errors:
                    details = "\n".join(
                        f"{number}: {message}"
                        for number, message in self.robot_thread.letter_errors[:5]
                    )
                    self.status_label.setText("❌ هیچ نامه‌ای پردازش نشد؛ جزئیات خطا نمایش داده شد.")
                    QMessageBox.warning(
                        self,
                        "پردازش نامه ناموفق بود",
                        f"هیچ نامه‌ای پردازش نشد. علت‌های ثبت‌شده:\n\n{details}",
                    )
                else:
                    QMessageBox.information(self, "اطلاع", "📭 هیچ نامه‌ای پردازش نشد.")

    def save_command(self):
        selected = self.table_view.selectionModel().selectedRows()
        if not selected:
            QMessageBox.warning(self, "خطا", "لطفاً یک ردیف را انتخاب کنید!")
            return
        if len(selected) > 1:
            QMessageBox.warning(self, "خطا", "لطفاً فقط یک ردیف را انتخاب کنید!")
            return
        
        command_text = self.command_text.toPlainText().strip()
        if not command_text:
            QMessageBox.warning(self, "خطا", "لطفاً متن دستور ارجاع را وارد کنید!")
            return
        
        view_row = selected[0].row()
        real_row = self.model.get_real_row(view_row)
        if real_row >= 0 and self.data_manager.update_command(real_row, command_text):
            self.model.refresh()
            self.command_text.clear()
            self.update_status()
            self.table_view.resizeRowsToContents()
            QMessageBox.information(self, "موفق", "دستور ارجاع ذخیره شد!")
    
    def edit_command(self):
        selected = self.table_view.selectionModel().selectedRows()
        if not selected:
            QMessageBox.warning(self, "خطا", "لطفاً یک ردیف را انتخاب کنید!")
            return
        if len(selected) > 1:
            QMessageBox.warning(self, "خطا", "لطفاً فقط یک ردیف را انتخاب کنید!")
            return
        
        view_row = selected[0].row()
        real_row = self.model.get_real_row(view_row)
        if real_row < 0:
            return
        
        current_command = self.data_manager.records[real_row].get('دستور ارجاع', '')
        text, ok = QInputDialog.getMultiLineText(
            self, "✏️ ویرایش دستور ارجاع", "متن جدید را وارد کنید:", current_command
        )
        if ok:
            if self.data_manager.update_command(real_row, text):
                self.model.refresh()
                self.update_status()
                self.table_view.resizeRowsToContents()
                QMessageBox.information(self, "موفق", "✅ دستور ارجاع ویرایش شد!")
    
    def clear_command(self):
        selected = self.table_view.selectionModel().selectedRows()
        if not selected:
            QMessageBox.warning(self, "خطا", "لطفاً یک ردیف را انتخاب کنید!")
            return
        if len(selected) > 1:
            QMessageBox.warning(self, "خطا", "لطفاً فقط یک ردیف را انتخاب کنید!")
            return
        
        view_row = selected[0].row()
        real_row = self.model.get_real_row(view_row)
        if real_row < 0:
            return
        
        current_command = self.data_manager.records[real_row].get('دستور ارجاع', '')
        if not current_command:
            QMessageBox.information(self, "اطلاع", "این ردیف دستور ارجاعی ندارد!")
            return
        
        reply = QMessageBox.question(self, '🗑️ تأیید حذف',
            'آیا از حذف دستور ارجاع این ردیف مطمئن هستید؟',
            QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            if self.data_manager.update_command(real_row, ""):
                self.model.refresh()
                self.update_status()
                self.table_view.resizeRowsToContents()
                QMessageBox.information(self, "موفق", "🗑️ دستور ارجاع با موفقیت حذف شد!")

    def delete_selected(self):
        selected = self.table_view.selectionModel().selectedRows()
        if not selected:
            QMessageBox.warning(self, "خطا", "لطفاً یک ردیف را انتخاب کنید!")
            return
        
        reply = QMessageBox.question(self, 'تأیید حذف',
            f'آیا از حذف {len(selected)} ردیف مطمئن هستید؟',
            QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            real_rows = sorted([self.model.get_real_row(idx.row()) for idx in selected], reverse=True)
            self.data_manager.delete_records(real_rows)
            self.model.clear_highlights()
            self._highlighted_numbers = []
            self.model.refresh()
            self.update_status()
            self.table_view.resizeRowsToContents()
    
    def clear_all(self):
        if not self.data_manager.records:
            QMessageBox.warning(self, "خطا", "هیچ رکوردی وجود ندارد!")
            return
        
        reply = QMessageBox.question(self, 'تأیید پاک کردن',
            'آیا از پاک کردن همه رکوردها مطمئن هستید؟',
            QMessageBox.Yes | QMessageBox.No)
        
        if reply == QMessageBox.Yes:
            self.data_manager.clear_all()
            self.model.clear_highlights()
            self._highlighted_numbers = []
            self.model.refresh()
            self.update_status()
            self.table_view.resizeRowsToContents()

    def save_to_excel(self):
        try:
            if not self.data_manager.records:
                QMessageBox.warning(self, "خطا", "هیچ داده‌ای وجود ندارد!")
                return
            
            filename = QFileDialog.getSaveFileName(
                self, "ذخیره به اکسل", "", "Excel Files (*.xlsx)")[0]
            if not filename:
                return
            if not filename.endswith('.xlsx'):
                filename += '.xlsx'
            
            success, message = save_to_excel_custom(self.data_manager.records, filename)
            if success:
                QMessageBox.information(self, "موفق", message)
                self.status_label.setText(f"💾 {message}")
            else:
                QMessageBox.warning(self, "خطا", message)
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا: {str(e)}")
    
    def save_to_pdf(self):
        try:
            if not self.data_manager.records:
                QMessageBox.warning(self, "خطا", "هیچ داده‌ای برای ذخیره وجود ندارد!")
                return
            
            filename = QFileDialog.getSaveFileName(
                self, "ذخیره به PDF", "", "PDF Files (*.pdf)")[0]
            if not filename:
                return
            if not filename.endswith('.pdf'):
                filename += '.pdf'
            
            selected_rows = self.table_view.selectionModel().selectedRows()
            if selected_rows:
                view_rows = sorted([index.row() for index in selected_rows])
                rows_to_print = [self.model.get_real_row(vr) for vr in view_rows]
                rows_to_print = [r for r in rows_to_print if r >= 0]
                print_type = f"ردیف‌های انتخاب شده ({len(rows_to_print)} ردیف)"
            else:
                rows_to_print = list(range(len(self.data_manager.records)))
                print_type = f"همه ردیف‌ها ({len(rows_to_print)} ردیف)"
            
            printer = QPrinter(QPrinter.HighResolution)
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(filename)
            printer.setPageOrientation(QPageLayout.Landscape)
            printer.setPageSize(QPrinter.A3)
            printer.setFullPage(True)
            printer.setPageMargins(0, 0, 0, 0, QPrinter.Millimeter)
            
            doc = self.create_pdf_document(rows_to_print, print_type)
            doc.print_(printer)
            
            QMessageBox.information(self, "موفق", f"✅ فایل PDF با موفقیت ذخیره شد!")
            self.status_label.setText(f"📄 فایل PDF ذخیره شد")
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در ذخیره PDF: {str(e)}")
    
    def create_pdf_document(self, rows_to_print, print_type):
        doc = QTextDocument()
        doc.setDefaultTextOption(QTextOption(Qt.AlignVCenter))
        cursor = QTextCursor(doc)
        doc.setDocumentMargin(0)
        font = QFont("B Yekan", 12)
        doc.setDefaultFont(font)
        
        title_format = QTextCharFormat()
        title_format.setFontPointSize(13)
        title_format.setFontWeight(QFont.Bold)
        title_format.setForeground(QColor(0, 51, 102))
        cursor.insertText("📋 گزارش نامه‌های اداری\n", title_format)
        cursor.blockFormat().setAlignment(Qt.AlignCenter)
        
        info_format = QTextCharFormat()
        info_format.setFontPointSize(10)
        cursor.blockFormat().setAlignment(Qt.AlignRight)
        cursor.insertText(f"📅 تاریخ چاپ: {get_persian_datetime()}\n", info_format)
        cursor.insertText(f"📊 نوع گزارش: {print_type}\n", info_format)
        cursor.insertText(f"📌 تعداد کل نامه‌ها: {len(self.data_manager.records)} ردیف\n", info_format)
        
        headers = ['دستور ارجاع', 'ددلاین', 'خلاصه', 'شرح ارجاع', 'امضاکننده', 'موضوع', 'ساعت', 'تاریخ', 'شماره', 'ردیف']
        cols = len(headers)
        
        table_format = QTextTableFormat()
        table_format.setAlignment(Qt.AlignCenter)
        table_format.setCellPadding(2)
        table_format.setCellSpacing(0)
        table_format.setBorder(1)
        table_format.setBorderStyle(QTextTableFormat.BorderStyle_Solid)
        table_format.setWidth(QTextLength(QTextLength.PercentageLength, 100))
        
        column_widths = [15, 5, 25, 15, 5, 15, 5, 5, 5, 5]
        table_format.setColumnWidthConstraints([
            QTextLength(QTextLength.PercentageLength, w) for w in column_widths
        ])
        
        table = cursor.insertTable(len(rows_to_print) + 1, cols, table_format)
        
        header_format = QTextCharFormat()
        header_format.setFontPointSize(11)
        header_format.setFontWeight(QFont.Bold)
        header_format.setForeground(QColor(0, 51, 102))
        
        for col in range(cols):
            cell = table.cellAt(0, col)
            cell_cursor = cell.firstCursorPosition()
            cell_cursor.insertText(headers[col], header_format)
        
        data_format = QTextCharFormat()
        data_format.setFontPointSize(10)
        
        col_map = {
            0: 'دستور ارجاع', 1: 'ددلاین', 2: 'خلاصه', 3: 'شرح ارجاع', 4: 'امضاکننده',
            5: 'موضوع', 6: 'ساعت', 7: 'تاریخ', 8: 'شماره', 9: 'ردیف'
        }
        
        for i, row_index in enumerate(rows_to_print):
            record = self.data_manager.records[row_index]
            for col in range(cols):
                cell = table.cellAt(i + 1, col)
                cell_cursor = cell.firstCursorPosition()
                key = col_map.get(col, '')
                
                if col == 9:
                    value = str(row_index + 1)
                else:
                    value = str(record.get(key, ''))
                
                if col == 1:
                    try:
                        deadline_str = value
                        if deadline_str and deadline_str != 'nan':
                            today = jdatetime.datetime.now().date()
                            deadline_date = jdatetime.datetime.strptime(deadline_str.strip(), '%Y/%m/%d').date()
                            diff = (deadline_date - today).days
                            color_format = QTextCharFormat()
                            color_format.setFontPointSize(10)
                            if diff < 0:
                                color_format.setForeground(QColor(255, 0, 0))
                                color_format.setFontWeight(QFont.Bold)
                            elif diff <= 3:
                                color_format.setForeground(QColor(156, 101, 0))
                            else:
                                color_format.setForeground(QColor(0, 128, 0))
                            cell_cursor.insertText(value, color_format)
                            continue
                    except:
                        pass
                
                if col == 0 and value:
                    command_format = QTextCharFormat()
                    command_format.setFontPointSize(10)
                    command_format.setForeground(QColor(0, 102, 204))
                    command_format.setFontWeight(QFont.Bold)
                    cell_cursor.insertText(value, command_format)
                    continue
                
                cell_cursor.insertText(value, data_format)
        
        cursor.movePosition(QTextCursor.End)
        cursor.insertText("\n\n")
        
        footer_format = QTextCharFormat()
        footer_format.setFontPointSize(9)
        footer_format.setFontWeight(QFont.Bold)
        cursor.insertText("✅ امضا: ____________________\n", footer_format)
        cursor.insertText(f"📅 تاریخ: {jdatetime.datetime.now().strftime('%Y/%m/%d')}\n", footer_format)
        
        return doc
    
    def print_table(self):
        try:
            if not self.data_manager.records:
                QMessageBox.warning(self, "خطا", "هیچ داده‌ای برای پرینت وجود ندارد!")
                return
            
            selected_rows = self.table_view.selectionModel().selectedRows()
            if selected_rows:
                view_rows = sorted([index.row() for index in selected_rows])
                rows_to_print = [self.model.get_real_row(vr) for vr in view_rows]
                rows_to_print = [r for r in rows_to_print if r >= 0]
                print_type = f"ردیف‌های انتخاب شده ({len(rows_to_print)} ردیف)"
            else:
                rows_to_print = list(range(len(self.data_manager.records)))
                print_type = f"همه ردیف‌ها ({len(rows_to_print)} ردیف)"
            
            doc = self.create_pdf_document(rows_to_print, print_type)
            printer = QPrinter(QPrinter.HighResolution)
            preview = QPrintPreviewDialog(printer, self)
            preview.paintRequested.connect(lambda p: doc.print_(p))
            preview.exec_()
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در پرینت: {str(e)}")

    def change_font_size(self, size):
        try:
            size = int(size)
            
            font = QFont(self.table_view.font())
            font.setPointSize(size)
            self.table_view.setFont(font)
            
            header_font = QFont(self.table_view.horizontalHeader().font())
            header_font.setPointSize(size)
            self.table_view.horizontalHeader().setFont(header_font)
            
            vheader_font = QFont(self.table_view.verticalHeader().font())
            vheader_font.setPointSize(size)
            self.table_view.verticalHeader().setFont(vheader_font)
            
            row_height = size + 48
            self.table_view.verticalHeader().setDefaultSectionSize(row_height)
            
            self.table_view.setStyleSheet(f"""
                QTableView {{
                    background-color: {Theme.BG_CARD};
                    alternate-background-color: {Theme.BG_ALT_ROW};
                    gridline-color: transparent;
                    font-size: {size}px;
                    color: {Theme.TEXT_PRIMARY};
                    border: none;
                    border-radius: 10px;
                    selection-background-color: {Theme.SELECTION_BG};
                    selection-color: {Theme.SELECTION_TEXT};
                    outline: none;
                }}
                QTableView::item {{
                    padding: 6px 4px;
                    border-bottom: 1px solid {Theme.BORDER_LIGHT};
                }}
                QTableView::item:selected {{
                    background-color: {Theme.SELECTION_BG};
                    color: {Theme.SELECTION_TEXT};
                }}
                QTableView::item:hover {{
                    background-color: {Theme.BG_HEADER};
                }}
                QHeaderView {{
                    background-color: transparent;
                    border: none;
                }}
                QHeaderView::section {{
                    background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 {Theme.HEADER_FROM}, stop:1 {Theme.HEADER_TO});
                    color: white;
                    padding: 10px 6px;
                    border: none;
                    font-weight: 600;
                    font-size: {size}px;
                }}
                QHeaderView::section:first {{
                    border-top-right-radius: 10px;
                }}
                QHeaderView::section:last {{
                    border-top-left-radius: 10px;
                }}
                QHeaderView::section:horizontal {{
                    border-left: 1px solid rgba(255, 255, 255, 0.2);
                }}
                QScrollBar:vertical {{
                    background: transparent;
                    width: 10px;
                    border-radius: 5px;
                    margin: 0;
                }}
                QScrollBar::handle:vertical {{
                    background: {Theme.BORDER};
                    border-radius: 5px;
                    min-height: 30px;
                }}
                QScrollBar::handle:vertical:hover {{
                    background: {Theme.PRIMARY_LIGHT};
                }}
                QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                    height: 0;
                }}
                QScrollBar:horizontal {{
                    background: transparent;
                    height: 10px;
                    border-radius: 5px;
                    margin: 0;
                }}
                QScrollBar::handle:horizontal {{
                    background: {Theme.BORDER};
                    border-radius: 5px;
                    min-width: 30px;
                }}
                QScrollBar::handle:horizontal:hover {{
                    background: {Theme.PRIMARY_LIGHT};
                }}
                QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                    width: 0;
                }}
            """)
            
            settings = QSettings("MyApp", "LetterManager")
            settings.setValue("font_size", size)
            
            self.model.refresh()
            self.table_view.resizeRowsToContents()
            self.status_label.setText(f"اندازه متن: {size}")
        except Exception as e:
            print(f"خطا در تغییر اندازه متن: {e}")
    
    def change_font_size_from_combo(self, size_str):
        try:
            size = int(size_str)
            self.change_font_size(size)
        except Exception as e:
            print(f"خطا: {e}")
    
    def update_status(self):
        total = len(self.data_manager.records)
        shown = len(self.model.filtered_indices)
        if self.model.filter_text:
            self.status_label.setText(f"🔍 نمایش {shown} از {total} نامه (جستجو فعال)")
        else:
            self.status_label.setText(f" تعداد کل نامه‌ها: {total}")

try:
    import ctypes
    myappid = 'letterbot.management.app.1.0'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except Exception:
    pass

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setLayoutDirection(Qt.RightToLeft)
    app.setStyle('Fusion')
    
    icon_path = get_icon_path()
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))
        print(f"✅ آیکون بارگذاری شد: {icon_path}")
    else:
        print(f"⚠️ فایل آیکون پیدا نشد: {icon_path}")
    
    font = QFont("B Yekan", 10)
    app.setFont(font)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
