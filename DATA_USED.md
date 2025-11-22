# Data Used in Baseera AI Project

## 📥 Data Download Required

**⚠️ CRITICAL:** The `RAG_DATA/` directory containing PDF documents is **NOT included in the ZIP submission** due to file size limitations. 

**You must download the required data files from Aramco** and place them in the `RAG_DATA/` directory structure before running the system. The ZIP file contains only the code, configuration files, and documentation.

## Overview

I built the Baseera AI system to use a comprehensive knowledge base of materials failure analysis documents stored in the `RAG_DATA/` directory. This document describes the data sources and structure that you'll need to download separately.

## ⚠️ Important Note

**DO NOT re-upload any Aramco-provided datasets.** I'm using publicly available and project-specific data sources only.

**⚠️ IMPORTANT:** I couldn't compress some data files into the submission ZIP file due to size limitations. 

**You must download the required data from Aramco** and place the files in the `RAG_DATA/` directory structure as I've described below before running the document ingestion process (`python manage.py ingest_documents`).

The ZIP file submission does NOT include the actual PDF documents - only the code, configuration, and documentation. You'll need to get the data separately from Aramco.

## Data Sources

### 1. ASM Failure Analysis Cases
**Location:** `RAG_DATA/ASM Failure Analisys Cases/`

- **Searchable PDFs**: 42 documents
- **Scanned PDFs**: 37 documents (processed with OCR)
- **Content**: Real-world failure analysis case studies
- **Coverage**: Various failure modes, materials, and environments

### 2. ASM Handbook for Failure Analysis and Fractography
**Location:** `RAG_DATA/ASMHandbook for Failure Analysis and Fractography (120+ Chapters)20251112185224/`

- **Volume 11 - Failure Analysis and Prevention**: 14 chapters
- **Volume 11A**: 40+ chapters (scanned PDFs)
- **Volume 12 - Fractography**: 23 chapters
- **Volume 12A - Atlas of Fractographs**: 5 chapters
- **Content**: Comprehensive reference material on failure analysis methodologies, failure modes, and fractographic analysis

### 3. CSB Investigation Reports
**Location:** `RAG_DATA/CSBInvestigation Reports (50+ Detailed Report)20251112190040/`

- **Count**: 53 PDF documents
- **Content**: Chemical Safety Board investigation reports
- **Coverage**: Real industrial incidents and failure analyses

### 4. Failure Analysis Publications
**Location:** `RAG_DATA/FailureAnalysis Publications (300+ Papers)20251112190009/`

- **Count**: 100+ PDF documents (subset of 300+ papers)
- **Content**: Academic and industry research papers on failure analysis
- **Coverage**: Various failure mechanisms, materials science, and analysis techniques

## Data Statistics

- **Total PDF Documents**: ~500+ documents
- **Total Pages**: Estimated 10,000+ pages
- **Total Chunks**: ~5,000+ text chunks (after processing)
- **Storage Size**: ~10-20MB (vector embeddings)

## Data Processing

### Document Types

I handle two types of PDFs:
1. **Searchable PDFs**: I extract text directly using `pypdf`
2. **Scanned PDFs**: I process these using OCR (Tesseract) when text extraction yields less than 100 characters

### Processing Pipeline

Here's how I process the documents:

1. **Text Extraction**: Extract text from PDF pages
2. **Chunking**: Split documents into 1000-character chunks with 200-character overlap
3. **Embedding**: Generate 384-dimensional vectors using the `all-MiniLM-L6-v2` model
4. **Storage**: Store embeddings and metadata in ChromaDB

### Chunking Strategy

- **Chunk Size**: 1000 characters
- **Overlap**: 200 characters
- **Rationale**: Preserves context while maintaining embedding quality

## Data Quality

### Document Status Tracking

I've set up the system to track:
- Processed vs. unprocessed documents
- OCR usage (scanned vs. searchable PDFs)
- Processing errors
- Chunk counts per document

### Quality Metrics

I monitor:
- **Processing Success Rate**: Tracked in Django admin
- **OCR Usage**: Documents requiring OCR are flagged
- **Error Handling**: Failed documents are logged with error messages

## Data Access

### Viewing Processed Documents

You can view processed documents through the Django admin:
1. Access Django admin: `http://localhost:8000/admin/core/document/`
2. Filter by:
   - Collection name
   - Processing status
   - OCR usage
   - Date processed

### Query Logs

I log all queries in the `QueryLog` model:
- Query text
- Failure case parameters
- Number of sources retrieved
- Response time

Access at: `http://localhost:8000/admin/core/querylog/`

## Data Updates

### Adding New Documents

If you want to add new documents:
1. Place PDF files in the appropriate `RAG_DATA/` subdirectory
2. Run: `python manage.py ingest_documents`
3. New documents will be processed and indexed automatically

### Reprocessing Documents

I've included commands for reprocessing:

```bash
# Reprocess all documents
python manage.py ingest_documents --reprocess

# Reprocess only scanned PDFs
python manage.py reprocess_scanned
```

## Data Privacy and Security

- All documents are stored locally
- No external data transmission except Gemini API calls
- ChromaDB data stored in `chroma_db/` directory (excluded from version control)

## Test Data

### Test Images
**Location:** `test_images/`

Sample failure images for testing:
- `scc_cracks.jpg` - Stress corrosion cracking
- `fatigue_beach_marks.jpg` - Fatigue failure
- `creep_deformation.jpg` - Creep deformation
- `pitting_corrosion.jpg` - Pitting corrosion
- `hydrogen_embrittlement.jpg` - Hydrogen embrittlement
- `erosion_wear.jpg` - Erosive wear
- `thermal_fatigue.jpg` - Thermal fatigue
- `brittle_fracture.jpg` - Brittle fracture

### Test Parameters
**Location:** `test_parameters.json`

16 predefined test cases covering various failure modes:
- Stress Corrosion Cracking (SCC)
- Fatigue Failure
- High-Temperature Creep
- Pitting Corrosion
- Hydrogen Embrittlement
- Erosive Wear
- Intergranular Corrosion
- Thermal Fatigue
- Galvanic Corrosion
- Brittle Fracture
- Fretting Wear
- And more...

## Data Citation

When my system retrieves relevant documents, it provides citations in the response:
- Document name
- Collection/source
- Relevant chunk information

## Future Data Additions

If you want to add new data sources:
1. Create a new subdirectory in `RAG_DATA/`
2. Add PDF documents
3. Run the ingestion command
4. The system will automatically process and index new documents

---

**Note**: This project does NOT include any Aramco-provided datasets. All data sources are publicly available materials or project-specific test data.

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

