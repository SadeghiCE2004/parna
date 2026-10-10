# Parna | Intelligent Correspondence Processing System

**Parna** is a Windows desktop application for viewing and processing correspondence in an organization's letter management system. It uses `Selenium` to access the system, extract letter content, and generate letter summaries and task deadlines locally using the `qwen3.5:latest` model through `Ollama`.

Letter content is not sent to a cloud-based AI service for analysis. An internet connection is required to log in to the correspondence system and download the AI model initially.

---

## Features

- **Letter Information Extraction:** Displays letter information and extracted results from the correspondence table.
- **Flexible Sorting:** Sorts the table by letter date or deadline through the sorting menu.
- **Automatic Column Sizing:** Sets initial column widths to fit the available screen space while allowing manual resizing.
- **Processing Progress:** Displays progress based on actual processing stages and highlights past and upcoming deadlines with colors.
- **Live Search:** Searches all table columns in real time.
- **Referral Instruction Management:** Creates, edits, and deletes referral instructions for individual letters.
- **Processing Cancellation:** Allows the user to stop an ongoing processing operation.
- **ChromeDriver Compatibility Detection:** Detects version incompatibility between `ChromeDriver` and `Chrome` and provides guidance for obtaining a compatible version.
- **Network Error Handling:** Displays network errors and allows retrying.
- **PDF Text Extraction:** Extracts text from `PDF` files using the `PDF.js` text layer.
- **Image Text Recognition:** Recognizes text in `JPG` images using `Tesseract OCR` with Persian and English language data.
- **AI-Powered Summarization:** Generates letter summaries locally using `qwen3.5:latest` through `Ollama`.
- **Deadline Detection:** Identifies task deadlines from letter content.
- **Local Data Storage:** Stores processed letter records and application outputs in local files.
- **Excel and PDF Export:** Exports the table and processing results to Excel and PDF files.

---

## Sorting and Deadline Display

The sorting menu provides the following options:

- Default display order
- Letter date, from newest to oldest or oldest to newest
- Deadline, from earliest to latest or latest to earliest

Missing or invalid dates are placed at the end of the table. Sorting changes only the display order and does not modify the stored letter data.

Past deadlines are highlighted in red. Deadlines falling between today and the next three days are highlighted in yellow.

---

## Prerequisites

- Windows operating system
- `Python 3.11`, recommended for running the source code
- `Google Chrome` and a compatible version of `ChromeDriver`
- `Tesseract OCR` and Persian and English language data when running the source code
- `Ollama` and the `qwen3.5:latest` model for AI-powered summarization and deadline detection

In the current standalone executable, the `Tesseract OCR` engine and Persian and English language data are bundled with the application. They do not need to be installed separately to use this version.

### External Dependencies

External runtime tools and supporting files, including `ChromeDriver`, the `icon.ico` application icon, OCR language data, and the Ollama installer, are not stored in the Git repository. To run the source code, obtain the required files separately and place them in the following structure:

```text
project/
├── chromedriver.exe
├── icon.ico
├── ocr/
│   ├── tesseract.exe
│   └── tessdata/
│       ├── fas.traineddata
│       └── eng.traineddata
└── ai/
    └── ollama/
        └── OllamaSetup.exe
```

To run the source code, `chromedriver.exe`, `icon.ico`, and the `ocr` folder must be located in the project root.

The Ollama installer is only required if Ollama is not already installed on the system. To use the AI features, Ollama itself and the required model must be available.

---

## Installing and Running from Source

Run the following commands in `PowerShell` from the project root.

### 1. Create a Virtual Environment

```powershell
python -m venv .venv
```

### 2. Activate the Virtual Environment

```powershell
.\.venv\Scripts\Activate.ps1
```

### 3. Upgrade pip

```powershell
python -m pip install --upgrade pip
```

### 4. Install Project Dependencies

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

Parna uses the `qwen3.5:latest` model through `Ollama` to generate letter summaries and identify task deadlines.

After installing Ollama, run the following command if the model has not already been downloaded:

```powershell
ollama pull qwen3.5:latest
```

The initial model download requires an internet connection. Once the model has been downloaded and the Ollama service is ready, AI processing can run locally. Letter content is not sent to a cloud-based AI service for this analysis.

---

## Building the Windows Executable

After activating the virtual environment and installing the dependencies listed in `requirements.txt`, run the build script:

```powershell
.\installer\build.bat
```

Build settings are defined in `پَـــــرنا.spec`.

The generated executable is placed in the `dist/` directory, while temporary build files are stored in the `build/` directory.

### Running the Standalone Version

The standalone `پَـــــرنا.exe` includes the `Tesseract OCR` engine and Persian and English language data, so it does not require a separate `ocr` folder.

Before running the application, place `chromedriver.exe` alongside the executable.

To display the application icon in the taskbar, place `icon.ico` alongside `پَـــــرنا.exe`.

To use AI-powered summarization and deadline detection, Ollama must be installed and the required model must be available.

---

## Local Data Files

The application may create or update the following files to store information and processing records. These files are listed in `.gitignore` to prevent local data and processing records from being committed to the Git repository.

- `data_storage.json`
- `letter_state.json`
- `all_extracted_letters.txt`
- `deleted_letters.log`

---

## Developers

- [Mahdis Sadeghi](https://github.com/SadeghiCE2004)
- [Mohadeseh Mohammadi](https://github.com/Mohadeseh-Mohammadi)

---

<p align="center">
  <strong>Parna — Smarter Correspondence and Deadline Management</strong>
</p>
