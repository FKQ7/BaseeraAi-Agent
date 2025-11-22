# RAG System Implementation Guide

This document explains the complete RAG (Retrieval-Augmented Generation) system that has been implemented for Baseera AI.

## Overview

The RAG system enables Baseera to:
- Process and index all PDF documents in the `RAG_DATA` directory
- Perform semantic search to find relevant context from the knowledge base
- Use retrieved context to provide more accurate and informed failure analysis

## Architecture

### Components

1. **RAG Service** (`core/rag_service.py`)
   - Handles PDF text extraction
   - Chunks documents intelligently (1000 chars with 200 char overlap)
   - Generates embeddings using `sentence-transformers` (all-MiniLM-L6-v2 model)
   - Stores embeddings in ChromaDB (persistent vector database)
   - Performs semantic search to retrieve relevant chunks

2. **Database Models** (`core/models.py`)
   - `Document`: Tracks processed PDFs and their metadata
   - `QueryLog`: Logs user queries for analytics

3. **Management Command** (`core/management/commands/ingest_documents.py`)
   - Processes all PDFs in `RAG_DATA` directory
   - Extracts text, chunks, and creates embeddings
   - Stores results in ChromaDB and Django database

4. **Updated Views** (`core/views.py`)
   - `chat_api`: Now retrieves relevant context before calling Gemini
   - Builds enhanced prompts with knowledge base context
   - Logs queries for analytics

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

**Note:** The first time you run this, it will download the embedding model (~80MB). This is a one-time download.

### 2. Run Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

This creates the `Document` and `QueryLog` tables.

### 3. Ingest Documents

Process all PDFs in the `RAG_DATA` directory:

```bash
python manage.py ingest_documents
```

**Options:**
- `--path PATH`: Process a specific subdirectory (e.g., `--path RAG_DATA/ASMHandbook`)
- `--reprocess`: Reprocess documents that were already processed
- `--limit N`: Process only the first N documents (useful for testing)

**Example:**
```bash
# Process all documents
python manage.py ingest_documents

# Process only ASM Handbook documents
python manage.py ingest_documents --path RAG_DATA/ASMHandbook

# Reprocess failed documents
python manage.py ingest_documents --reprocess

# Test with first 10 documents
python manage.py ingest_documents --limit 10
```

### 4. Verify Ingestion

Check the Django admin to see processed documents:
```bash
python manage.py createsuperuser  # If you haven't already
python manage.py runserver
```

Visit `http://localhost:8000/admin/core/document/` to see all processed documents.

## How It Works

### Document Processing Flow

1. **PDF Extraction**: Uses `pypdf` to extract text from each page
2. **Text Chunking**: Splits documents into overlapping chunks (1000 chars, 200 overlap)
   - Preserves sentence boundaries when possible
   - Ensures context continuity between chunks
3. **Embedding Generation**: Creates vector embeddings using sentence-transformers
4. **Storage**: Stores embeddings in ChromaDB with metadata (file name, collection, chunk index)

### Query Flow

1. **User submits failure case** with structured data (metal type, environment, etc.)
2. **Query Building**: System builds a natural language query from the failure data
3. **Semantic Search**: Searches ChromaDB for the 5 most relevant document chunks
4. **Context Formatting**: Formats retrieved chunks into a context section
5. **Enhanced Prompt**: Combines context + failure case into a comprehensive prompt
6. **AI Analysis**: Gemini analyzes with full context from knowledge base
7. **Response**: Returns analysis with citations to source documents

## File Structure

```
project_root/
├── core/
│   ├── rag_service.py          # Core RAG functionality
│   ├── models.py                # Document and QueryLog models
│   ├── views.py                 # Updated with RAG integration
│   └── management/
│       └── commands/
│           └── ingest_documents.py  # Document ingestion command
├── RAG_DATA/                    # PDF documents directory
├── chroma_db/                   # ChromaDB storage (auto-created)
└── requirements.txt             # Python dependencies
```

## Configuration

### ChromaDB Storage

ChromaDB data is stored in `chroma_db/` directory (created automatically). This directory contains:
- Vector embeddings
- Document metadata
- Collection information

**Note:** Add `chroma_db/` to `.gitignore` if using version control.

### Embedding Model

The system uses `all-MiniLM-L6-v2` from sentence-transformers:
- Fast and efficient
- Good performance on technical documents
- ~80MB download (one-time)
- 384-dimensional embeddings

### Chunking Strategy

- **Chunk Size**: 1000 characters
- **Overlap**: 200 characters
- **Rationale**: Balances context preservation with embedding quality

## Monitoring & Analytics

### Query Logs

All queries are logged in the `QueryLog` model:
- Query text
- Failure case parameters
- Number of results retrieved
- Response time

View in Django admin: `/admin/core/querylog/`

### Document Status

Track document processing status:
- Processed count
- Failed documents
- Chunk counts
- Processing errors

View in Django admin: `/admin/core/document/`

## Troubleshooting

### Documents Not Processing

1. Check file permissions
2. Verify PDFs are not corrupted
3. Check logs for specific error messages
4. Some scanned PDFs may have no extractable text

### Low Quality Results

1. Ensure documents are properly ingested
2. Try reprocessing with `--reprocess` flag
3. Check that search is finding relevant chunks (view query logs)
4. Consider adjusting chunk size or overlap in `rag_service.py`

### Performance Issues

1. First query may be slow (model loading)
2. Large document sets take time to process initially
3. Consider using `--limit` for testing
4. ChromaDB queries are fast once indexed

## Advanced Usage

### Custom Collection Filtering

You can filter searches by collection in `rag_service.py`:

```python
search_results = rag_service.search(
    query=search_query,
    n_results=5,
    collection_filter="ASMHandbook"  # Only search in this collection
)
```

### Adjusting Chunk Parameters

Modify in `rag_service.py`:

```python
chunks = self.chunk_text(
    text,
    chunk_size=1500,      # Larger chunks
    chunk_overlap=300     # More overlap
)
```

### Using Different Embedding Models

Change in `rag_service.py`:

```python
# For better quality (slower, larger)
self.embedding_model = SentenceTransformer('all-mpnet-base-v2')

# For faster processing
self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
```

## Best Practices

1. **Regular Ingestion**: Re-run ingestion when new documents are added
2. **Monitor Logs**: Check query logs to understand usage patterns
3. **Error Handling**: Review failed documents periodically
4. **Backup**: ChromaDB data is in `chroma_db/` - back it up regularly
5. **Testing**: Use `--limit` flag to test with small subsets first

## Performance Metrics

Expected performance:
- **Document Processing**: ~1-5 seconds per PDF (depending on size)
- **Query Time**: ~100-500ms (including embedding + search)
- **Storage**: ~1-2KB per chunk (embeddings + metadata)

For 500 documents with ~10 chunks each:
- Total chunks: ~5,000
- Storage: ~10-20MB
- Processing time: ~1-2 hours (one-time)

## Next Steps

The RAG system is now fully integrated. To use it:

1. Run `python manage.py ingest_documents` to process your PDFs
2. Start the server: `python manage.py runserver`
3. Submit failure cases through the web interface
4. The system will automatically retrieve relevant context and provide informed analysis

Enjoy your enhanced Baseera AI system! 🚀

