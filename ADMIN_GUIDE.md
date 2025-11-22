# Django Admin Panel Guide for Documents

## Adding Documents from Admin Panel

### Step 1: Access Admin Panel
1. Start your Django server: `python manage.py runserver`
2. Go to: `http://localhost:8000/admin`
3. Login with your superuser credentials
4. Navigate to **Core → Documents**

### Step 2: Add New Document
1. Click the **"Add Document"** button (top right)
2. Fill in the form:

#### Required Fields:
- **File path**: 
  - Relative path: `RAG_DATA/ASMHandbook/file.pdf`
  - Absolute path: `C:/path/to/file.pdf`
  - The file_name will be auto-extracted

- **Collection name**: 
  - Name of the collection/folder (e.g., "ASM Handbook", "CSB Reports")
  - Used for organizing documents

#### Optional Fields:
- **File name**: Auto-extracted from path, but you can override
- **File size**: Auto-detected if file exists
- **Is processed**: Uncheck if you want to process later
- **Used OCR**: Check if document was processed with OCR

3. Click **"Save"** or **"Save and add another"**

### Step 3: Process Documents
After adding documents, you can process them:

1. **Select documents** in the list view (checkboxes)
2. **Choose action** from dropdown: "Process selected documents with RAG"
3. Click **"Go"**
4. Documents will be processed and added to the vector database

## Admin Features

### List View Features:
- **Search**: Search by file name, path, or collection
- **Filters**: Filter by:
  - Is processed
  - Used OCR
  - Collection name
  - Processed date
- **Sorting**: Click column headers to sort

### Bulk Actions:
1. **Process selected documents with RAG**
   - Processes documents through the RAG system
   - Extracts text, creates chunks, generates embeddings
   - Updates num_pages, num_chunks, used_ocr fields

2. **Mark selected documents as unprocessed**
   - Resets processing status
   - Useful for reprocessing

3. **Mark selected documents as processed**
   - Marks as processed without actually processing
   - Use with caution

### Form Fieldsets:

#### File Information:
- File path (required)
- File name (auto-extracted)
- Collection name (required)
- File size (auto-detected)
- File size display (read-only, human-readable)

#### Processing Status:
- Is processed (checkbox)
- Used OCR (checkbox)
- Number of pages
- Number of chunks
- Error message (if processing failed)

#### Metadata (collapsed by default):
- Processed at (read-only)
- Last updated (read-only)

## Tips

### Adding Multiple Documents:
1. Use **"Save and add another"** button
2. Or use the bulk import via management command:
   ```bash
   python manage.py ingest_documents
   ```

### Processing Workflow:
1. **Add documents** manually or via command
2. **Select unprocessed documents**
3. **Run "Process selected documents"** action
4. **Check results** - num_chunks should be > 0 if successful

### Troubleshooting:
- **File not found**: Check that file_path is correct
- **Processing fails**: Check error_message field for details
- **No chunks created**: Document might be empty or corrupted
- **OCR not used**: Check if OCR libraries are installed

## Example: Adding a Single Document

1. Go to Admin → Documents → Add Document
2. Enter:
   - **File path**: `RAG_DATA/ASMHandbook/Volume 11/Fatigue Failures.pdf`
   - **Collection name**: `ASM Handbook`
3. Click **Save**
4. Select the document in list view
5. Choose action: **"Process selected documents with RAG"**
6. Click **Go**
7. Wait for processing (check messages at top)
8. Document should now show:
   - Is processed: ✓
   - Num chunks: > 0
   - Num pages: > 0

## Quick Reference

| Action | Location | Description |
|--------|----------|-------------|
| Add Document | Documents → Add Document | Add new document manually |
| Process | Select → Actions → Process | Process documents with RAG |
| Search | Top search bar | Search by name/path/collection |
| Filter | Right sidebar | Filter by status/collection |
| Edit | Click document name | Edit document details |

