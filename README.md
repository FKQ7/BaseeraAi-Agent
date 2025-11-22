# Baseera AI - Materials Failure Analysis Agent

This is my implementation of a comprehensive RAG (Retrieval-Augmented Generation) system for materials failure analysis. I built this system using Google Gemini AI combined with semantic search over a knowledge base of failure analysis documents to provide intelligent failure analysis assistance.

## ⚠️ IMPORTANT - Data Download Required

**The `RAG_DATA/` directory with PDF documents is NOT included in the ZIP submission** due to file size limitations. 

**You must download the required data files from Aramco** and place them in the `RAG_DATA/` directory structure before running the system. See the [Data Used](#-data-used) section and `DATA_USED.md` for details.

## 📋 Table of Contents

- [Overview](#overview)
- [System Requirements](#system-requirements)
- [Installation](#installation)
- [Setup Instructions](#setup-instructions)
- [Running the Application](#running-the-application)
- [Tools and Technologies](#tools-and-technologies)
- [API Keys](#api-keys)
- [Project Structure](#project-structure)
- [Usage Examples](#usage-examples)
- [Testing](#testing)
- [Evaluation](#evaluation)
- [Troubleshooting](#troubleshooting)

## 🎯 Overview

I developed Baseera AI as an intelligent failure analysis assistant that:
- Analyzes materials failure cases using structured input (metal type, environment, temperature, etc.)
- Processes images of failure surfaces
- Retrieves relevant context from a comprehensive knowledge base (500+ PDF documents)
- Provides detailed failure analysis with source citations
- Generates PDF reports

## 💻 System Requirements

### Python Version
- **Python 3.12.0** - This is what I used for development
- Python 3.10+ should also work

### Operating System
- **Windows 10/11** - This is my primary development environment
- macOS and Linux should also work, though I haven't tested them extensively

### Additional Requirements
- **Tesseract OCR** (optional, for scanned PDFs):
  - Windows: Download from [UB-Mannheim/tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
  - macOS: `brew install tesseract`
  - Linux: `sudo apt-get install tesseract-ocr`

## 📦 Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd BaseeraAi-Agent-main
```

### 2. Create a Virtual Environment (Recommended)

I recommend using a virtual environment to avoid conflicts:

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 3. Install Required Packages

```bash
pip install -r requirements.txt
```

**Note:** When you first run the application, it will automatically download the embedding model (~80MB). This is a one-time download.

### 4. Install Node.js Dependencies (for Tailwind CSS)

```bash
cd theme/static_src
npm install
cd ../..
```

## 🚀 Setup Instructions

### Step 1: Run Database Migrations

First, you need to set up the database:

```bash
python manage.py makemigrations
python manage.py migrate
```

This creates the necessary database tables for documents and query logs that I use to track the system.

### Step 2: Download Required Data

**⚠️ IMPORTANT:** I couldn't include the `RAG_DATA/` directory with PDF documents in the ZIP file because it's too large. 

**You'll need to download the required data from Aramco** and place it in the `RAG_DATA/` directory structure before proceeding.

I've documented the data structure in `DATA_USED.md` - check that file for details.

### Step 3: Ingest Documents into RAG System

Once you have the data, process all PDF documents:

```bash
python manage.py ingest_documents
```

I've included several options you can use:
- `--path PATH`: Process a specific subdirectory (e.g., `--path RAG_DATA/ASMHandbook`)
- `--reprocess`: Reprocess documents that were already processed
- `--limit N`: Process only the first N documents (useful for testing)

**Example:**
```bash
# Process all documents (this takes ~1-2 hours for 500+ documents)
python manage.py ingest_documents

# Or test with first 10 documents
python manage.py ingest_documents --limit 10
```

### Step 4: Create Admin User (Optional)

If you want to monitor the system through the admin interface:

```bash
python manage.py createsuperuser
```

This lets you access the Django admin to see document processing status and query logs.

## ▶️ Running the Application

**⚠️ Prerequisite:** Ensure you have downloaded and placed the `RAG_DATA/` files from Aramco before running the application.

### Start the Development Server

```bash
python manage.py runserver
```

The application will be available at: `http://localhost:8000`

### Access Points

- **Main Interface**: `http://localhost:8000`
- **API Endpoint**: `http://localhost:8000/api/chat`
- **Admin Interface**: `http://localhost:8000/admin`

## 🛠️ Tools and Technologies

Here's what I used to build this system:

### Core Framework
- **Django 5.2.8** - I used Django for the web framework and backend
- **Django Tailwind 4.2.0** - For UI styling

### RAG System
- **ChromaDB 0.5.15** - I chose ChromaDB as the vector database for semantic search
- **sentence-transformers 2.7.0** - Using the `all-MiniLM-L6-v2` embedding model
- **pypdf 5.1.0** - For extracting text from PDFs
- **PyTorch 2.4.1** - Required for sentence-transformers
- **transformers 4.46.3** - Hugging Face transformers library

### OCR (Optional)
- **pytesseract 0.3.13** - Python wrapper for Tesseract OCR
- **pdf2image 1.17.0** - Converts PDF pages to images for OCR
- **Pillow 10.4.0** - Image processing

### AI/ML
- **Google Gemini 2.5 Flash** - I'm using Gemini as the LLM for generating responses
- **sentence-transformers** - Pre-trained embedding model for semantic search

### Utilities
- **requests 2.31.0** - For making API calls to Gemini
- **python-dotenv 1.0.1** - Environment variable management
- **tqdm 4.66.5** - Progress bars during document processing
- **reportlab 4.2.5** - For generating PDF reports
- **numpy 1.26.4** - Numerical computing

### How I Applied These Tools

1. **ChromaDB**: I use this to store vector embeddings of document chunks, which enables fast semantic search over my 500+ PDF documents
2. **sentence-transformers**: This converts text chunks and queries into 384-dimensional embeddings for similarity matching
3. **Django**: I built REST API endpoints, database models, and an admin interface with Django
4. **Google Gemini API**: I call this to generate detailed failure analysis responses using the retrieved context
5. **OCR (pytesseract)**: I added this to handle scanned PDFs that don't have extractable text
6. **pypdf**: I use this to extract text from searchable PDF documents

## 🔑 API Keys

### Google Gemini API Key

I'm using a hardcoded API key for Google Gemini 2.5 Flash API:

```
AIzaSyDXPPROy_wZe6m0BNAj-6-uso3h1Mu7hE8
```

You can find this in `core/views.py` (line 160).

**Note:** This API key was provided as per project instructions, so I left it as-is. For production use, you'd want to move this to an environment variable.

### No Other API Keys Required

Everything else runs locally - ChromaDB and sentence-transformers don't need any API keys.

## 📁 Project Structure

```
BaseeraAi-Agent-main/
├── BaseeraAi/              # Django project settings
│   ├── settings.py         # Django configuration
│   └── urls.py            # URL routing
├── core/                   # Main application
│   ├── models.py          # Database models (Document, QueryLog)
│   ├── views.py           # API endpoints and Gemini integration
│   ├── rag_service.py     # RAG system core functionality
│   ├── pdf_service.py     # PDF processing utilities
│   ├── admin.py           # Django admin configuration
│   └── management/
│       └── commands/
│           ├── ingest_documents.py  # Document ingestion command
│           ├── reprocess_scanned.py # OCR reprocessing
│           └── update_ocr_flags.py # OCR flag updates
├── theme/                  # Frontend (Tailwind CSS)
│   ├── templates/
│   │   └── index.html     # Main UI
│   └── static_src/        # Tailwind source files
├── RAG_DATA/              # Knowledge base PDFs
│   ├── ASM Failure Analisys Cases/
│   ├── ASMHandbook for Failure Analysis and Fractography/
│   ├── CSBInvestigation Reports/
│   └── FailureAnalysis Publications/
├── evaluation_results/    # Accuracy evaluation reports
├── test_images/           # Sample failure images
├── chroma_db/            # ChromaDB vector database (auto-created)
├── requirements.txt      # Python dependencies
├── manage.py             # Django management script
├── test_api.py           # API testing script
├── evaluate_accuracy.py  # Accuracy evaluation script
├── setup_rag.py          # Setup verification script
└── test_parameters.json  # Test case definitions
```

## 💡 Usage Examples

### Using the Web Interface

1. Start the server: `python manage.py runserver`
2. Open `http://localhost:8000` in your browser
3. Fill in the failure case form:
   - Metal type (e.g., "316L Stainless Steel")
   - Service time
   - Environment
   - Temperature
   - Mechanical load
   - Notes/observations
   - Upload images (optional)
4. Click "Analyze Failure" to get AI-powered analysis

### Using the API Directly

```python
import requests
import json

url = "http://localhost:8000/api/chat"
data = {
    "metal_type": "316L Stainless Steel",
    "service_time": "3 years",
    "environment": "High-chloride environment",
    "temperature": "60-80°C",
    "mechanical_load": "Static with residual stress",
    "notes": "Cracks observed in weld heat-affected zone"
}

response = requests.post(url, json=data)
result = response.json()
print(result['response'])
```

### Testing with Provided Scripts

```bash
# Quick test
python test_api.py quick

# Run all test cases
python test_api.py all

# Run specific test case
python test_api.py 1
```

## 🧪 Testing

### Run Accuracy Evaluation

```bash
# Full evaluation
python evaluate_accuracy.py

# Quick evaluation (first 5 cases)
python evaluate_accuracy.py --quick

# Generate HTML report only
python evaluate_accuracy.py --output html
```

Evaluation results are saved in `evaluation_results/` directory.

## 📊 Evaluation

The system includes a comprehensive accuracy evaluation framework:

- **Metrics**: Primary failure mode identification, keyword relevance, source sufficiency
- **Test Cases**: 16 predefined failure scenarios
- **Output Formats**: JSON, CSV, and HTML reports

See `ACCURACY_EVALUATION_SUMMARY.md` for detailed evaluation methodology.

## 🔧 Troubleshooting

### Common Issues

1. **ChromaDB errors**: Delete `chroma_db/` directory and re-run `ingest_documents`
2. **OCR not working**: Install Tesseract OCR (see System Requirements)
3. **Model download slow**: First run downloads ~80MB embedding model (one-time)
4. **Port already in use**: Change port with `python manage.py runserver 8001`

### Verify Setup

Run the setup verification script:

```bash
python setup_rag.py
```

### Check Document Processing Status

Visit Django admin: `http://localhost:8000/admin/core/document/`

## 📚 Additional Documentation

I've included several documentation files:

- `RAG_README.md` - Detailed documentation about the RAG system I built
- `IMPLEMENTATION_SUMMARY.md` - Overview of what I implemented
- `ACCURACY_EVALUATION_SUMMARY.md` - How I evaluated the system's accuracy
- `EVALUATION_GUIDE.md` - Guide on running evaluations
- `OCR_SETUP.md` - How to set up OCR for scanned PDFs
- `TEST_CASES.md` - Description of the test cases I created

## 📝 Data Used

See `DATA_USED.md` for detailed information about the knowledge base documents.

**⚠️ IMPORTANT - Data Download Required:**

Some data files could not be compressed into the ZIP file due to size limitations. **You must download the required data from Aramco** and place it in the `RAG_DATA/` directory structure as described in `DATA_USED.md` before running the document ingestion process.

## 🎓 Training Details

See `TRAINING_DETAILS.md` for information about models, embeddings, and configuration.

## 📹 Demo Video

**⚠️ IMPORTANT:** A recorded demo video with voice explanation is required for submission. The video should demonstrate:
- System setup and installation
- Document ingestion process
- Failure case analysis workflow
- API usage examples
- Evaluation results

---

## 👥 Team

**Name and Credits:**

- **Abdulrahman Al-Ghamdi**: Team Lead + Software Engineer
- **Fayez Al-Shawayaa**: Software Engineer - Built the website and RAG
- **Hadi Al-Jader**: AI Engineer
- **Rashid Al-Gharib**: UI Designer
- **Abdulwahab Al-Abdulhadi**: Industrial Engineer

---

## 📄 Copyright

Copyright © 2024 Baseera AI Team

All rights reserved.

---

**Last Updated:** November 2024

