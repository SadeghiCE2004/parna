**[English](README.md) · [فارسی](README.fa.md)**

---

<div align="center">

# 🖥️Parna

### Intelligent Correspondence Processing System

*A Windows desktop application for automated extraction, AI-powered summarization, and deadline tracking of organizational correspondence.*

[![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?style=flat-square&logo=windows&logoColor=white)](#)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white)](#)
[![PyQt5](https://img.shields.io/badge/PyQt5-5.15-41CD52?style=flat-square&logo=qt&logoColor=white)](#)
[![Ollama](https://img.shields.io/badge/AI-Ollama-000000?style=flat-square)](#)
[![License](https://img.shields.io/badge/License-MIT-blue?style=flat-square)](#-license)

</div>

---

## About

Parna is a Windows desktop application for viewing and processing correspondence in an organization's letter management system. It uses Selenium to access the system, extract letter content, and generate letter summaries and task deadlines locally using the `qwen3.5:latest` model through Ollama.

> **Privacy-focused AI processing:** Letter content is processed locally through Ollama and is not intentionally sent to a cloud-based AI service for analysis. An internet connection is required to access the correspondence system and download the AI model on first use.

---

## Table of Contents

- [About](#about)
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Key Achievements](#key-achievements)
- [Project Structure](#project-structure)
- [External Dependencies](#external-dependencies)
- [Prerequisites](#prerequisites)
- [Installing and Running from Source](#installing-and-running-from-source)
- [Setting Up AI with Ollama](#setting-up-ai-with-ollama)
- [Building the Windows Executable](#building-the-windows-executable)
- [Running the Standalone Version](#running-the-standalone-version)
- [Local Data Files](#local-data-files)
- [Privacy and Data Processing](#privacy-and-data-processing)
- [Developers](#developers)
- [License](#license)

---

## Features

### Correspondence Processing

- Automated extraction of letters from the configured correspondence management system.
- Extraction and processing of letter details — subjects, dates, numbers, descriptions, and related fields.
- Real-time search and filtering across all table columns.
- Flexible sorting by letter date or deadline.
- Automatic column sizing and live progress reporting.
- Management of referral instructions and correspondence tracking.
- Safe cancellation of ongoing operations.
- Network error handling and browser-driver compatibility checks.

### Text Extraction and OCR

- Text extraction from PDF documents via the PDF.js text layer.
- OCR-based text recognition for image-based letters.
- Persian and English language support through Tesseract.

### Local AI Processing

- Automatic letter summarization using a locally hosted language model.
- Detection and extraction of potential deadlines from correspondence.
- Letter content is processed locally through Ollama and is not intentionally sent to a cloud-based AI service for analysis.
- Deadline information displayed for prioritization.

### Data Management and Export

- Local storage of application state and extracted information.
- Export to Excel (`.xlsx`) and PDF formats.
- Tracking of processed and deleted correspondence.
- Persistent state files across sessions.

### Sorting and Deadline Display

| Sorting Option | Description |
|----------------|-------------|
| Default order | Application's natural ordering |
| Letter date: ascending | Oldest → Newest |
| Letter date: descending | Newest → Oldest |
| Deadline: ascending | Earliest → Latest |
| Deadline: descending | Latest → Earliest |

Missing or invalid dates are placed after valid entries. Sorting only affects display order — the underlying data is never modified.

**Deadline color coding:**

| Color | Meaning |
|-------|---------|
| Red | Past deadlines |
| Yellow | Deadlines from today through the next 3 days |

---

## Technologies Used

| Category | Technology | Purpose |
|----------|------------|---------|
| **Core** | Python | Core application logic |
| | PyQt5 | Desktop graphical user interface |
| | Selenium | Browser automation and web interaction |
| **AI & Content** | Ollama | Local AI model runtime |
| | Qwen3.5 | Local language model for letter summarization and deadline detection |
| | Tesseract OCR | Optical character recognition (Persian + English) |
| | PDF.js | PDF text layer extraction |
| **Runtime** | Google Chrome | Access to the correspondence system |
| | ChromeDriver | Browser automation driver |
| | PyInstaller | Windows executable packaging |
| **Supporting** | pandas | Tabular data processing |
| | openpyxl | Excel file operations |
| | jdatetime | Persian (Jalali) calendar handling |
| | Pillow | Image processing |
| | requests | HTTP communication with Ollama |
| **Development** | Git & GitHub | Version control and source hosting |

---

## Key Achievements

- **Local AI Integration:** Integrated the Qwen3.5 language model through Ollama to perform letter summarization and deadline detection locally. Letter content is processed locally through Ollama and is not intentionally sent to a cloud-based AI service for analysis.
- **Persian Document Processing:** Combined PDF text extraction from the PDF.js text layer with Tesseract OCR supporting both Persian and English language data.
- **Modular Architecture:** Organized the codebase into dedicated modules for browser automation, content extraction, AI processing, data handling, and shared utilities.
- **Interactive Desktop Interface:** Built a Persian (RTL) interface with real-time search, flexible sorting, progress reporting, deadline color highlighting, and cancellation controls.
- **Resilient Browser Automation:** Added automatic ChromeDriver compatibility detection and graceful network error handling with retry support.
- **Data Management and Export:** Implemented local data storage, processing-state tracking, and Excel/PDF export with Persian calendar formatting.

---

## Project Structure

```text
Parna/
├── ai/
│   ├── __init__.py
│   ├── ai_service.py
│   ├── runtime_setup.py
│   └── ollama/                    # Not tracked by Git
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
├── ocr/                            # Not tracked by Git
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

> **Note:** Directories marked as `Not tracked by Git` are part of the runtime structure but are excluded from version control due to their size or executable nature. See the [External Dependencies](#external-dependencies) section for details.

---

## External Dependencies

Some runtime tools and supporting files are **not stored in the Git repository** — either due to their size or their executable nature. They must be obtained separately and placed in the correct locations before running from source.

```text
Parna/
├── chromedriver.exe          ← Required for source execution
├── ocr/
│   ├── tesseract.exe
│   └── tessdata/
│       ├── fas.traineddata
│       └── eng.traineddata
└── ai/
    └── ollama/
        ├── OllamaSetup.exe   ← Only needed if Ollama is not installed
        └── models/           ← Downloaded AI model files
```

| File / Folder | Requirement |
|---------------|-------------|
| `chromedriver.exe` | Must match the installed version of Chrome |
| `ocr/tesseract.exe` | OCR engine, required for source runs |
| `ocr/tessdata/*.traineddata` | Persian and English language data |
| `ai/ollama/OllamaSetup.exe` | Only needed if Ollama is not installed |
| `ai/ollama/models/` | Downloaded model files used by Ollama |

> **Note:** `icon.ico` is already tracked in the repository and does not need to be obtained separately.

**Standalone Executable:** The Windows executable is generated locally during the build process and is not committed to the repository.

---

## Prerequisites

| Requirement | Notes |
|-------------|-------|
| **OS** | Windows 10 (64-bit) or later |
| **Python** | 3.11 (recommended) — for source execution |
| **Browser** | Google Chrome + compatible ChromeDriver |
| **OCR** | Tesseract with Persian and English data *(not needed in standalone build)* |
| **AI** | Ollama + the `qwen3.5:latest` model *(only if AI features are required)* |

Some features depend on network access to the correspondence management system. The initial AI model download also requires network access.

---

## Installing and Running from Source

Run the following commands in **PowerShell** from the project root.

### 1. Create a Virtual Environment

```powershell
python -m venv .venv
```

### 2. Activate the Virtual Environment

```powershell
.\.venv\Scripts\Activate.ps1
```

> If PowerShell prevents script execution, adjust the execution policy for the current session according to your security requirements.

### 3. Upgrade pip

```powershell
python -m pip install --upgrade pip
```

### 4. Install Dependencies

```powershell
python -m pip install -r requirements.txt
```

### 5. Run the Application

```powershell
python PyQt.py
```

Once Chrome opens, log in to the correspondence management system and navigate to the received letters or inbox page. The login and inbox URLs are configured in `config.py`.

---

## Setting Up AI with Ollama

Parna uses the `qwen3.5:latest` model through Ollama to generate letter summaries and identify task deadlines.

### 1. Install Ollama

Install Ollama if it is not already available on your system.

### 2. Download the Model

```powershell
ollama pull qwen3.5:latest
```

### 3. Verify

```powershell
ollama list
```

The required model should appear in the output.

### 4. Run Parna

Once Ollama is running and the model is available, AI processing runs locally. Letter content is processed locally through Ollama and is not intentionally sent to a cloud-based AI service for analysis.

> **Tip:** AI-generated results should always be reviewed when accuracy matters — especially for extracted dates, deadlines, or instructions.

---

## Building the Windows Executable

After activating the virtual environment and installing the dependencies:

```powershell
.\installer\build.bat
```

| Path | Contents |
|------|----------|
| `پَـــــرنا.spec` | PyInstaller packaging configuration |
| `build/` | Temporary build files |
| `dist/` | Generated executable (`پَـــــرنا.exe`) |

---

## Running the Standalone Version

The standalone `پَـــــرنا.exe` includes the Tesseract OCR engine and Persian/English language data — a separate `ocr/` folder is **not** required.

### Before Running

- Chrome is installed.
- `chromedriver.exe` is placed alongside the executable.
- `icon.ico` is placed alongside `پَـــــرنا.exe` (for the taskbar icon).
- Ollama is installed and the model is available *(if AI features are needed)*.

---

## Local Data Files

The application may create or update the following files to store information and processing records:

| File | Purpose |
|------|---------|
| `data_storage.json` | Local application data |
| `letter_state.json` | Correspondence processing state |
| `all_extracted_letters.txt` | Stored extracted correspondence text |
| `deleted_letters.log` | Records of deleted/forwarded correspondence |

All four files are listed in `.gitignore` to prevent local data from being accidentally committed.

> **Do not commit** real correspondence, personal information, credentials, or confidential organizational data to a public repository.

---

## Privacy and Data Processing

Parna uses **Ollama** to run its AI model locally. Letter content is processed locally through Ollama and is not intentionally sent to a cloud-based AI service for analysis.

However, this does not mean that every part of the application runs offline:

- Selenium communicates with the configured correspondence management system.
- Network access may be required to retrieve correspondence.
- Downloading the AI model requires network access on first setup.

For organizational deployments, review data access permissions, local file security, and applicable information-security policies before processing confidential correspondence.

---

## 👥Developers

<table>
  <tr>
    <td align="center">
      <strong>Mahdis Sadeghi</strong><br>
      <a href="https://github.com/SadeghiCE2004">@SadeghiCE2004</a>
    </td>
    <td align="center">
      <strong>Mohadeseh Mohammadi</strong><br>
      <a href="https://github.com/Mohadeseh-Mohammadi">@Mohadeseh-Mohammadi</a>
    </td>
  </tr>
</table>

---

## 📄License

This project is distributed under the terms specified in the [LICENSE](LICENSE) file.

---

<div align="center">

Parna — *Smarter Correspondence and Deadline Management*

</div>
