# Training Details and Model Configuration

## Overview

I built the Baseera AI system using **pre-trained models**, so it doesn't require traditional machine learning training. This document describes the models, embeddings, and configuration I used in the system.

## Models Used

### 1. Embedding Model: sentence-transformers/all-MiniLM-L6-v2

**Purpose**: Convert text chunks and queries into vector embeddings for semantic search

**Model Details**:
- **Model Name**: `all-MiniLM-L6-v2`
- **Provider**: sentence-transformers (Hugging Face)
- **Type**: Pre-trained transformer model
- **Embedding Dimension**: 384
- **Model Size**: ~80MB
- **Download**: Automatic on first use

**Configuration**:
```python
# Location: core/rag_service.py
self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
```

**Why I Chose This Model**:
- Fast inference (~100-500ms per query)
- Good performance on technical documents
- Balanced accuracy and speed
- Widely used in production RAG systems

**No Training Required**: This is a pre-trained model that works out-of-the-box.

### 2. Large Language Model: Google Gemini 2.5 Flash

**Purpose**: Generate detailed failure analysis responses

**Model Details**:
- **Model Name**: `gemini-2.5-flash-preview-09-2025`
- **Provider**: Google
- **Type**: Large Language Model (LLM)
- **Access**: Via API
- **API Version**: v1beta

**Configuration**:
```python
# Location: core/views.py (line 161)
api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-09-2025:generateContent?key={api_key}"
```

**No Training Required**: This is a pre-trained API-based model that I'm calling directly.

## System Architecture

### RAG (Retrieval-Augmented Generation) Pipeline

```
User Query
    ↓
Query Embedding (all-MiniLM-L6-v2)
    ↓
Semantic Search (ChromaDB)
    ↓
Retrieve Top-K Chunks (K=5)
    ↓
Build Enhanced Prompt
    ↓
LLM Generation (Gemini 2.5 Flash)
    ↓
Response with Citations
```

## Configuration Parameters

### Chunking Parameters

**Location**: `core/rag_service.py`

```python
chunk_size = 1000        # Characters per chunk
chunk_overlap = 200      # Overlap between chunks
```

**Why I Chose These Values**:
- 1000 characters balances context preservation with embedding quality
- 200-character overlap ensures continuity across chunk boundaries

### Retrieval Parameters

**Location**: `core/views.py`

```python
n_results = 5            # Number of document chunks to retrieve
```

**Why I Use 5 Chunks**:
- 5 chunks provide sufficient context without overwhelming the LLM
- Balances relevance and token usage

### Embedding Model Parameters

**Model**: `all-MiniLM-L6-v2`
- **Max Sequence Length**: 256 tokens
- **Normalize Embeddings**: Yes (default)
- **Device**: CPU (I'm using CPU, but it can use GPU if available)

## Vector Database Configuration

### ChromaDB Settings

**Location**: `core/rag_service.py`

```python
chroma_db_path = Path(settings.BASE_DIR) / "chroma_db"
self.client = chromadb.PersistentClient(
    path=str(chroma_db_path),
    settings=Settings(
        anonymized_telemetry=False,
        allow_reset=True
    )
)
```

**Storage**:
- **Type**: Persistent client (disk-based)
- **Location**: `chroma_db/` directory
- **Format**: SQLite + embeddings storage

## Performance Metrics

### Document Processing

- **Processing Speed**: ~1-5 seconds per PDF (searchable)
- **OCR Processing**: ~10-30 seconds per page (scanned PDFs)
- **Embedding Generation**: ~100-200ms per chunk
- **Total Ingestion Time**: ~1-2 hours for 500+ documents (one-time)

### Query Processing

- **Query Embedding**: ~50-100ms
- **Semantic Search**: ~10-50ms
- **LLM Response**: ~500ms-2s (depends on Gemini API)
- **Total Query Time**: ~100-500ms (excluding LLM)

### Storage

- **Embedding Size**: ~1-2KB per chunk
- **Total Storage**: ~10-20MB for 500 documents
- **Database Size**: ~5-10MB (SQLite)

## Evaluation Results

### Accuracy Metrics

**Location**: `evaluation_results/`

Recent evaluation (2025-11-12):
- **Average Accuracy**: 100.0%
- **Primary Mode Identification**: 100.0%
- **Test Cases**: 16 failure scenarios

**Evaluation Methodology**:
- Weighted scoring system:
  - Primary failure mode: 40%
  - Keyword relevance: 30%
  - Metal type mention: 10%
  - Source sufficiency: 10%
  - Root cause analysis: 5%
  - Recommendations: 5%

See `ACCURACY_EVALUATION_SUMMARY.md` for detailed methodology.

## Model Alternatives I Considered

### Embedding Models

1. **all-MiniLM-L6-v2** (What I Selected)
   - Fast, efficient, good for technical documents

2. **all-mpnet-base-v2** (Alternative I Considered)
   - Better quality but slower
   - Larger model size (~420MB)

3. **all-MiniLM-L12-v2** (Alternative I Considered)
   - Better quality than L6, still fast
   - Medium model size (~130MB)

### LLM Models

1. **Gemini 2.5 Flash** (Selected)
   - Fast response time
   - Good performance on technical content
   - Multimodal (text + images)

2. **Gemini Pro** (Alternative)
   - Better quality but slower
   - Higher cost

## Fine-Tuning Considerations

### Current Approach: Zero-Shot Learning

I'm using pre-trained models without fine-tuning:
- **Advantages**: No training data needed, works immediately
- **Disadvantages**: May not be optimized for specific domain

### Potential Improvements

If I were to improve this further, I could:

1. **Fine-tune Embedding Model**:
   - Train on domain-specific failure analysis text
   - Requires labeled data pairs
   - Would improve retrieval accuracy

2. **Fine-tune LLM**:
   - Train Gemini on failure analysis examples
   - Requires extensive training data
   - Would improve response quality

3. **Hybrid Approach**:
   - Use fine-tuned embeddings + pre-trained LLM
   - Balance between customization and cost

## Configuration Files

### No Separate Config Files

I'm currently using:
- **Django Settings**: `BaseeraAi/settings.py`
- **Hardcoded Parameters**: In Python code (could be moved to config)
- **Environment Variables**: Not currently used (could be added)

### Future Configuration Options

If I were to refactor, I'd consider creating `config.py` for:
- Chunk size and overlap
- Number of retrieval results
- Embedding model selection
- LLM parameters (temperature, max tokens)

## Logs and Monitoring

### Query Logs

**Location**: Django database (`QueryLog` model)

Tracks:
- Query text
- Failure case parameters
- Number of sources retrieved
- Response time
- Timestamp

### Document Processing Logs

**Location**: Django database (`Document` model)

Tracks:
- Processing status
- Error messages
- Chunk counts
- OCR usage

### Access Logs

View in Django admin:
- `/admin/core/querylog/` - Query logs
- `/admin/core/document/` - Document status

## Model Updates

### Updating Embedding Model

To use a different model:

```python
# In core/rag_service.py
self.embedding_model = SentenceTransformer('all-mpnet-base-v2')
```

Then re-run document ingestion:
```bash
python manage.py ingest_documents --reprocess
```

### Updating LLM Model

Change API endpoint in `core/views.py`:
```python
api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}"
```

## Training Data (Not Applicable)

**No Training Data Required**: The system uses pre-trained models that work out-of-the-box.

**Knowledge Base**: The `RAG_DATA/` documents serve as the knowledge base, not training data. They are used for retrieval, not model training.

## Summary

Here's what I built:
- **Embedding Model**: Pre-trained `all-MiniLM-L6-v2` (no training needed)
- **LLM Model**: Pre-trained `Gemini 2.5 Flash` via API (no training needed)
- **Vector Database**: ChromaDB (no training, just storage)
- **Configuration**: Hardcoded parameters (could be moved to config files)
- **Performance**: Excellent accuracy (100% on test cases) with fast response times

---

**Note**: This system does not require any model training. All models are pre-trained and ready to use. The "training" phase is actually the document ingestion process, which creates embeddings and indexes the knowledge base.

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

