**[فارسی](README.fa.md) · [English](README.md)**

---

<div align="center">

# 🖥️پَـــــرنا

### سامانه‌ی هوشمند پردازش نامه‌ها

*یک برنامه‌ی دسکتاپ ویندوزی برای استخراج خودکار، خلاصه‌سازی با هوش مصنوعی و پیگیری مهلت نامه‌های سازمانی.*

[![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?style=flat-square&logo=windows&logoColor=white)](#)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)](#)
[![PyQt5](https://img.shields.io/badge/PyQt5-5.15-41CD52?style=flat-square&logo=qt&logoColor=white)](#)
[![Ollama](https://img.shields.io/badge/AI-Ollama-000000?style=flat-square)](#)
[![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)](#license)

</div>

---

<div dir="rtl" align="right">

<a id="about"></a>

## درباره

پَـــــرنا یک برنامه‌ی دسکتاپ ویندوزی برای مشاهده و پردازش نامه‌ها در سامانه‌ی مدیریت مکاتبات سازمانی است. این برنامه با استفاده از Selenium به سامانه متصل می‌شود، محتوای نامه‌ها را استخراج می‌کند و با مدل `qwen3.5:latest` از طریق Ollama، خلاصه‌ی نامه و مهلت انجام کار را به‌صورت محلی تولید می‌کند.

> **پردازش هوش مصنوعی با تمرکز بر حریم خصوصی:** محتوای نامه‌ها به‌صورت محلی از طریق Ollama پردازش می‌شود و به‌صورت عمدی برای تحلیل به سرویس هوش مصنوعی ابری ارسال نمی‌گردد. اتصال اینترنت برای دسترسی به سامانه‌ی مکاتبات و دریافت اولیه‌ی مدل هوش مصنوعی لازم است.

---

## فهرست مطالب

<ul dir="rtl" style="list-style-position: inside; padding-right: 25px; padding-left: 0; text-align: right;">
<li><a href="#about">درباره</a></li>
<li><a href="#features">قابلیت‌ها</a></li>
<li><a href="#technologies">فناوری‌های استفاده‌شده</a></li>
<li><a href="#achievements">دستاوردهای کلیدی</a></li>
<li><a href="#structure">ساختار پروژه</a></li>
<li><a href="#external-dependencies">وابستگی‌های خارجی</a></li>
<li><a href="#prerequisites">پیش‌نیازها</a></li>
<li><a href="#installation">نصب و اجرا از سورس</a></li>
<li><a href="#ollama-setup">راه‌اندازی هوش مصنوعی با Ollama</a></li>
<li><a href="#building">ساخت فایل اجرایی ویندوز</a></li>
<li><a href="#standalone">اجرای نسخه‌ی مستقل</a></li>
<li><a href="#data-files">فایل‌های داده‌ی محلی</a></li>
<li><a href="#privacy">حریم خصوصی و پردازش داده</a></li>
<li><a href="#developers">توسعه‌دهندگان</a></li>
<li><a href="#license">لایسنس</a></li>
</ul>

---

<a id="features"></a>

## قابلیت‌ها

### پردازش مکاتبات

<ul dir="rtl" style="list-style-position: inside; padding-right: 25px; padding-left: 0; text-align: right;">
<li>استخراج خودکار نامه‌ها از سامانه‌ی مدیریت مکاتبات پیکربندی‌شده.</li>
<li>استخراج و پردازش جزئیات نامه — موضوع، تاریخ، شماره، شرح و اطلاعات مرتبط.</li>
<li>جستجو و فیلتر لحظه‌ای در تمام ستون‌های جدول.</li>
<li>مرتب‌سازی انعطاف‌پذیر بر اساس تاریخ نامه یا ددلاین.</li>
<li>تنظیم خودکار اندازه‌ی ستون‌ها و نمایش زنده‌ی پیشرفت.</li>
<li>مدیریت دستورات ارجاع و پیگیری مکاتبات.</li>
<li>امکان توقف ایمن عملیات در حال اجرا.</li>
<li>مدیریت خطاهای شبکه و بررسی سازگاری درایور مرورگر.</li>
</ul>

### استخراج متن و OCR

<ul dir="rtl" style="list-style-position: inside; padding-right: 25px; padding-left: 0; text-align: right;">
<li>استخراج متن از اسناد PDF از طریق لایه‌ی متنی PDF.js.</li>
<li>تشخیص متن مبتنی بر OCR برای نامه‌های تصویری.</li>
<li>پشتیبانی از زبان فارسی و انگلیسی از طریق Tesseract.</li>
</ul>

### پردازش هوش مصنوعی محلی

<ul dir="rtl" style="list-style-position: inside; padding-right: 25px; padding-left: 0; text-align: right;">
<li>خلاصه‌سازی خودکار نامه با مدل زبانی محلی.</li>
<li>تشخیص و استخراج ددلاین‌های احتمالی از محتوای نامه.</li>
<li>محتوای نامه به‌صورت محلی از طریق Ollama پردازش می‌شود و به‌صورت عمدی برای تحلیل به سرویس هوش مصنوعی ابری ارسال نمی‌گردد.</li>
<li>نمایش اطلاعات ددلاین برای اولویت‌بندی.</li>
</ul>

### مدیریت داده و خروجی

<ul dir="rtl" style="list-style-position: inside; padding-right: 25px; padding-left: 0; text-align: right;">
<li>ذخیره‌سازی محلی وضعیت برنامه و اطلاعات استخراج‌شده.</li>
<li>خروجی به فرمت Excel (`.xlsx`) و PDF.</li>
<li>پیگیری نامه‌های پردازش‌شده و حذف‌شده.</li>
<li>حفظ فایل‌های وضعیت بین اجراهای مختلف برنامه.</li>
</ul>

### مرتب‌سازی و نمایش ددلاین

| گزینه‌ی مرتب‌سازی | توضیح |
|-------------------|-------|
| ترتیب پیش‌فرض | ترتیب طبیعی برنامه |
| تاریخ نامه: صعودی | قدیمی ← جدید |
| تاریخ نامه: نزولی | جدید ← قدیمی |
| ددلاین: صعودی | زودترین ← دیرترین |
| ددلاین: نزولی | دیرترین ← زودترین |

تاریخ‌های خالی یا نامعتبر بعد از موارد معتبر قرار می‌گیرند. مرتب‌سازی فقط ترتیب نمایش را تغییر می‌دهد و داده‌های اصلی دست‌نخورده می‌مانند.

**رنگ‌بندی ددلاین:**

| رنگ | معنا |
|-----|-------|
| قرمز | ددلاین‌های گذشته |
| زرد | ددلاین از امروز تا سه روز آینده |

---

<a id="technologies"></a>

## فناوری‌های استفاده‌شده

| دسته | فناوری | کاربرد |
|------|--------|--------|
| **هسته** | Python | منطق اصلی برنامه |
| | PyQt5 | رابط کاربری گرافیکی دسکتاپ |
| | Selenium | خودکارسازی مرورگر و تعامل وب |
| **هوش مصنوعی و محتوا** | Ollama | محیط اجرای محلی مدل هوش مصنوعی |
| | Qwen3.5 | مدل زبانی محلی برای خلاصه‌سازی و تشخیص ددلاین |
| | Tesseract OCR | تشخیص نویسه‌ی نوری (فارسی + انگلیسی) |
| | PDF.js | استخراج متن از لایه‌ی متنی PDF |
| **محیط اجرا** | Google Chrome | دسترسی به سامانه‌ی مکاتبات |
| | ChromeDriver | درایور خودکارسازی مرورگر |
| | PyInstaller | بسته‌بندی فایل اجرایی ویندوز |
| **کتابخانه‌های کمکی** | pandas | پردازش داده‌های جدولی |
| | openpyxl | عملیات فایل Excel |
| | jdatetime | مدیریت تاریخ شمسی |
| | Pillow | پردازش تصویر |
| | requests | ارتباط HTTP با Ollama |
| **توسعه** | Git & GitHub | کنترل نسخه و میزبانی کد |

---

<a id="achievements"></a>

## دستاوردهای کلیدی

<ul dir="rtl" style="list-style-position: inside; padding-right: 25px; padding-left: 0; text-align: right;">
<li><strong>یکپارچه‌سازی هوش مصنوعی محلی:</strong> یکپارچه‌سازی مدل Qwen3.5 از طریق Ollama برای انجام خلاصه‌سازی و تشخیص ددلاین به‌صورت محلی. محتوای نامه به‌صورت محلی از طریق Ollama پردازش می‌شود و به‌صورت عمدی برای تحلیل به سرویس هوش مصنوعی ابری ارسال نمی‌گردد.</li>
<li><strong>پردازش اسناد فارسی:</strong> ترکیب استخراج متن PDF از لایه‌ی متنی PDF.js با Tesseract OCR با پشتیبانی از داده‌های زبانی فارسی و انگلیسی.</li>
<li><strong>معماری ماژولار:</strong> سازمان‌دهی کد در ماژول‌های اختصاصی برای خودکارسازی مرورگر، استخراج محتوا، پردازش هوش مصنوعی، مدیریت داده و ابزارهای مشترک.</li>
<li><strong>رابط دسکتاپ تعاملی:</strong> طراحی رابط فارسی (RTL) با جستجوی لحظه‌ای، مرتب‌سازی انعطاف‌پذیر، گزارش پیشرفت، رنگ‌بندی ددلاین و کنترل توقف.</li>
<li><strong>خودکارسازی مقاوم مرورگر:</strong> تشخیص خودکار ناسازگاری ChromeDriver و مدیریت مؤثر خطاهای شبکه با پشتیبانی از تلاش مجدد.</li>
<li><strong>مدیریت داده و خروجی:</strong> ذخیره‌سازی محلی داده‌ها، پیگیری وضعیت پردازش و خروجی Excel/PDF با قالب‌بندی تقویم شمسی.</li>
</ul>

---

<a id="structure"></a>

## ساختار پروژه

```text
Parna/
├── ai/
│   ├── __init__.py
│   ├── ai_service.py
│   ├── runtime_setup.py
│   └── ollama/                    # در Git نیست
│       ├── OllamaSetup.exe
│       └── models/
├── core/
│   ├── __init__.py
│   └── browser_manager.py
├── extractors/
│   ├── __init__.py
│   ├── image_ocr.py
│   ├── pdf_extractor.py
│   └── text_extractor.py
├── handlers/
│   ├── __init__.py
│   ├── file_menu.py
│   ├── iframe_handlers.py
│   ├── letter_operations.py
│   └── tracker.py
├── installer/
│   └── build.bat
├── ocr/                            # در Git نیست
│   ├── tesseract.exe
│   └── tessdata/
│       ├── fas.traineddata
│       └── eng.traineddata
├── processor/
│   ├── __init__.py
│   └── processor.py
├── utils/
│   ├── __init__.py
│   ├── helpers.py
│   ├── json_storage.py
│   ├── progress_control.py
│   ├── result_saver.py
│   └── stop_control.py
├── PyQt.py
├── main.py
├── config.py
├── data_bridge.py
├── icon.ico
├── __init__.py
├── پَـــــرنا.spec
├── .gitignore
├── requirements.txt
├── LICENSE
├── README.md
└── README.fa.md
```

> **توجه:** پوشه‌هایی که با `در Git نیست` علامت خورده‌اند، بخشی از ساختار اجرایی پروژه هستند اما به‌دلیل حجم بالا یا ماهیت اجرایی در مخزن Git نگهداری نمی‌شوند. برای اطلاعات بیشتر به بخش [وابستگی‌های خارجی](#external-dependencies) مراجعه کنید.

---

<a id="external-dependencies"></a>

## وابستگی‌های خارجی

برخی ابزارهای اجرایی و فایل‌های جانبی **در مخزن Git نگهداری نمی‌شوند** — یا به‌دلیل حجم بالا یا ماهیت اجرایی. باید جداگانه تهیه شده و قبل از اجرا از سورس، در مسیرهای صحیح قرار گیرند.

```text
Parna/
├── chromedriver.exe          ← موردنیاز برای اجرا از سورس
├── ocr/
│   ├── tesseract.exe
│   └── tessdata/
│       ├── fas.traineddata
│       └── eng.traineddata
└── ai/
    └── ollama/
        ├── OllamaSetup.exe   ← فقط در صورت نصب نبودن Ollama
        └── models/           ← فایل‌های مدل دانلودشده
```

| فایل / پوشه | نیازمندی |
|-------------|-----------|
| `chromedriver.exe` | باید با نسخه‌ی نصب‌شده‌ی Chrome مطابقت داشته باشد |
| `ocr/tesseract.exe` | موتور OCR، موردنیاز برای اجرا از سورس |
| `ocr/tessdata/*.traineddata` | داده‌های زبانی فارسی و انگلیسی |
| `ai/ollama/OllamaSetup.exe` | فقط در صورت نصب نبودن Ollama |
| `ai/ollama/models/` | فایل‌های مدل دانلودشده برای Ollama |

> **توجه:** فایل `icon.ico` در مخزن ردیابی می‌شود و نیازی به تهیه‌ی جداگانه ندارد.

**فایل اجرایی مستقل:** فایل اجرایی ویندوز به‌صورت محلی در طول فرآیند ساخت تولید می‌شود و در مخزن ثبت نمی‌گردد.

---

<a id="prerequisites"></a>

## پیش‌نیازها

| نیازمندی | توضیحات |
|----------|---------|
| **سیستم‌عامل** | Windows 10 (64-bit) یا بالاتر |
| **Python** | نسخه‌ی 3.11 (پیشنهادی) — برای اجرا از سورس |
| **مرورگر** | Google Chrome + ChromeDriver سازگار |
| **OCR** | Tesseract با داده‌های فارسی و انگلیسی *(در نسخه‌ی مستقل لازم نیست)* |
| **هوش مصنوعی** | Ollama + مدل `qwen3.5:latest` *(فقط در صورت نیاز به AI)* |

برخی قابلیت‌ها به دسترسی شبکه به سامانه‌ی مکاتبات نیاز دارند. دریافت اولیه‌ی مدل هوش مصنوعی نیز به دسترسی شبکه نیاز دارد.

---

<a id="installation"></a>

## نصب و اجرا از سورس

دستورات زیر را در **PowerShell** و از ریشه‌ی پروژه اجرا کنید.

### ۱. ایجاد محیط مجازی

```powershell
python -m venv .venv
```

### ۲. فعال‌سازی محیط مجازی

```powershell
.\.venv\Scripts\Activate.ps1
```

> اگر PowerShell از اجرای اسکریپت جلوگیری کرد، خط‌مشی اجرا را برای جلسه‌ی فعلی مطابق نیازهای امنیتی خود تنظیم کنید.

### ۳. به‌روزرسانی pip

```powershell
python -m pip install --upgrade pip
```

### ۴. نصب وابستگی‌ها

```powershell
python -m pip install -r requirements.txt
```

### ۵. اجرای برنامه

```powershell
python PyQt.py
```

پس از باز شدن Chrome، وارد سامانه‌ی مدیریت مکاتبات شوید و به صفحه‌ی نامه‌های دریافتی بروید. نشانی‌های ورود و کارتابل در `config.py` تنظیم شده‌اند.

---

<a id="ollama-setup"></a>

## راه‌اندازی هوش مصنوعی با Ollama

پَرنا از مدل `qwen3.5:latest` از طریق Ollama برای تولید خلاصه و تشخیص ددلاین استفاده می‌کند.

### ۱. نصب Ollama

اگر Ollama روی سیستم شما نصب نیست، آن را نصب کنید.

### ۲. دانلود مدل

```powershell
ollama pull qwen3.5:latest
```

### ۳. تأیید

```powershell
ollama list
```

مدل موردنیاز باید در خروجی نمایش داده شود.

### ۴. اجرای پَرنا

پس از راه‌اندازی Ollama و در دسترس بودن مدل، پردازش هوش مصنوعی به‌صورت محلی انجام می‌شود. محتوای نامه به‌صورت محلی از طریق Ollama پردازش می‌شود و به‌صورت عمدی برای تحلیل به سرویس هوش مصنوعی ابری ارسال نمی‌گردد.

> **نکته:** در صورت اهمیت دقت، نتایج تولیدشده توسط هوش مصنوعی باید بازبینی شوند — به‌ویژه برای تاریخ‌ها، ددلاین‌ها یا دستورالعمل‌های استخراج‌شده.

---

<a id="building"></a>

## ساخت فایل اجرایی ویندوز

پس از فعال‌سازی محیط مجازی و نصب وابستگی‌ها:

```powershell
.\installer\build.bat
```

| مسیر | محتوا |
|------|--------|
| `پَـــــرنا.spec` | تنظیمات بسته‌بندی PyInstaller |
| `build/` | فایل‌های موقت ساخت |
| `dist/` | فایل اجرایی تولیدشده (`پَـــــرنا.exe`) |

---

<a id="standalone"></a>

## اجرای نسخه‌ی مستقل

فایل مستقل `پَـــــرنا.exe` شامل موتور Tesseract OCR و داده‌های فارسی/انگلیسی است — پوشه‌ی جداگانه‌ی `ocr/` **لازم نیست**.

### قبل از اجرا

<ul dir="rtl" style="list-style-position: inside; padding-right: 25px; padding-left: 0; text-align: right;">
<li>Chrome نصب باشد.</li>
<li><code>chromedriver.exe</code> کنار فایل اجرایی قرار گیرد.</li>
<li><code>icon.ico</code> کنار <code>پَـــــرنا.exe</code> قرار گیرد (برای آیکون Taskbar).</li>
<li>Ollama نصب باشد و مدل در دسترس باشد <em>(در صورت نیاز به AI)</em>.</li>
</ul>

---

<a id="data-files"></a>

## فایل‌های داده‌ی محلی

برنامه ممکن است فایل‌های زیر را برای ذخیره‌ی اطلاعات و سوابق پردازش ایجاد یا به‌روزرسانی کند:

| فایل | کاربرد |
|------|--------|
| `data_storage.json` | داده‌های محلی برنامه |
| `letter_state.json` | وضعیت پردازش مکاتبات |
| `all_extracted_letters.txt` | متن استخراج‌شده‌ی مکاتبات |
| `deleted_letters.log` | سوابق مکاتبات حذف/ارجاع‌شده |

هر چهار فایل در `.gitignore` قرار دارند تا از ثبت تصادفی داده‌های محلی جلوگیری شود.

> **مکاتبات واقعی، اطلاعات شخصی، اعتبارنامه‌ها یا داده‌های محرمانه‌ی سازمانی را به مخزن عمومی ارسال نکنید.**

---

<a id="privacy"></a>

## حریم خصوصی و پردازش داده

پَرنا از **Ollama** برای اجرای محلی مدل هوش مصنوعی استفاده می‌کند. محتوای نامه به‌صورت محلی از طریق Ollama پردازش می‌شود و به‌صورت عمدی برای تحلیل به سرویس هوش مصنوعی ابری ارسال نمی‌گردد.

اما این بدان معنا نیست که تمام بخش‌های برنامه آفلاین کار می‌کنند:

<ul dir="rtl" style="list-style-position: inside; padding-right: 25px; padding-left: 0; text-align: right;">
<li>Selenium با سامانه‌ی مدیریت مکاتبات در ارتباط است.</li>
<li>دسترسی شبکه ممکن است برای دریافت مکاتبات لازم باشد.</li>
<li>دانلود مدل هوش مصنوعی در اولین راه‌اندازی نیازمند دسترسی شبکه است.</li>
</ul>

برای استقرارهای سازمانی، مجوزهای دسترسی به داده، امنیت فایل‌های محلی و خط‌مشی‌های امنیت اطلاعات را قبل از پردازش مکاتبات محرمانه بررسی کنید.

---

<a id="developers"></a>

## 👥توسعه‌دهندگان

<table>
  <tr>
    <td align="center">
      <strong>مهدیس صادقی</strong><br>
      <a href="https://github.com/SadeghiCE2004">@SadeghiCE2004</a>
    </td>
    <td align="center">
      <strong>محدثه محمدی</strong><br>
      <a href="https://github.com/Mohadeseh-Mohammadi">@Mohadeseh-Mohammadi</a>
    </td>
  </tr>
</table>

---

<a id="license"></a>

## 📄لایسنس

این پروژه تحت شرایط ذکرشده در فایل [LICENSE](LICENSE) منتشر شده است.

</div>

---

<div align="center">

پَـــــرنا — *مدیریت هوشمندتر مکاتبات و ددلاین‌ها*

</div>
