"""RAG service for document processing and semantic search."""

import os
import hashlib
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from pypdf import PdfReader
import re
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
import logging

try:
    import pytesseract
    from pdf2image import convert_from_path
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("OCR libraries not installed. Scanned PDFs will be skipped.")

logger = logging.getLogger(__name__)


class RAGService:
    """RAG service for document processing and retrieval."""
    
    def __init__(self):
        """Initialize ChromaDB and embedding model."""
        chroma_db_path = Path(settings.BASE_DIR) / "chroma_db"
        chroma_db_path.mkdir(exist_ok=True)
        
        self.client = chromadb.PersistentClient(
            path=str(chroma_db_path),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        self.collection_name = "baseera_documents"
        try:
            self.collection = self.client.get_collection(name=self.collection_name)
            logger.info(f"Loaded existing collection: {self.collection_name}")
        except Exception:
            self.collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"description": "Baseera AI Materials Failure Analysis Documents"}
            )
            logger.info(f"Created new collection: {self.collection_name}")
        
        try:
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Loaded embedding model: all-MiniLM-L6-v2")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise ImproperlyConfigured(f"Could not load embedding model: {e}")
    
    def _is_likely_scanned_pdf(self, pdf_path: Path, extracted_text: str) -> bool:
        """Check if PDF is likely scanned."""
        path_str = str(pdf_path).lower()
        scanned_indicators = ['unsearchable', 'scanned', 'mostlyunsearchable', 'image', 'scan']
        
        for indicator in scanned_indicators:
            if indicator in path_str:
                logger.info(f"PDF {pdf_path.name} is in a scanned folder, forcing OCR")
                return True
        
        text_length = len(extracted_text.strip())
        try:
            reader = PdfReader(str(pdf_path))
            num_pages = len(reader.pages)
            if num_pages > 0:
                avg_chars_per_page = text_length / num_pages
                if avg_chars_per_page < 50:
                    logger.info(f"PDF {pdf_path.name} has low text density ({avg_chars_per_page:.1f} chars/page), likely scanned")
                    return True
        except:
            pass
        
        if text_length < 200:
            return True
        
        return False
    
    def extract_text_from_pdf(self, pdf_path: Path, use_ocr: bool = True) -> Tuple[str, int, bool]:
        """Extract text from PDF, using OCR if needed."""
        try:
            reader = PdfReader(str(pdf_path))
            num_pages = len(reader.pages)
            
            text_parts = []
            for page in reader.pages:
                try:
                    text = page.extract_text()
                    if text and text.strip():
                        text_parts.append(text.strip())
                except Exception as e:
                    logger.warning(f"Error extracting text from page in {pdf_path}: {e}")
                    continue
            
            full_text = "\n\n".join(text_parts)
            
            is_scanned = self._is_likely_scanned_pdf(pdf_path, full_text)
            
            if (is_scanned or len(full_text.strip()) < 200) and use_ocr and OCR_AVAILABLE:
                logger.info(f"PDF {pdf_path.name} appears to be scanned. Attempting OCR...")
                try:
                    ocr_text, ocr_pages = self._extract_text_with_ocr(pdf_path)
                    if ocr_text and len(ocr_text.strip()) > 100:
                        logger.info(f"Successfully extracted {len(ocr_text)} characters using OCR")
                        return ocr_text, ocr_pages, True
                    else:
                        logger.warning(f"OCR extraction returned little text for {pdf_path.name}")
                        if ocr_text and len(ocr_text.strip()) > len(full_text.strip()):
                            return ocr_text, ocr_pages, True
                except Exception as ocr_error:
                    logger.error(f"OCR extraction failed for {pdf_path.name}: {ocr_error}")
            
            return full_text, num_pages, False
            
        except Exception as e:
            logger.error(f"Error reading PDF {pdf_path}: {e}")
            if use_ocr and OCR_AVAILABLE:
                try:
                    logger.info(f"Regular extraction failed for {pdf_path.name}. Attempting OCR as last resort...")
                    ocr_text, ocr_pages = self._extract_text_with_ocr(pdf_path)
                    if ocr_text:
                        return ocr_text, ocr_pages, True
                except Exception as ocr_error:
                    logger.error(f"OCR also failed for {pdf_path.name}: {ocr_error}")
            raise
    
    def _extract_text_with_ocr(self, pdf_path: Path) -> Tuple[str, int]:
        """Extract text using OCR."""
        if not OCR_AVAILABLE:
            raise ImportError("OCR libraries not installed.")
        
        try:
            images = convert_from_path(
                str(pdf_path),
                dpi=200,
                first_page=None,
                last_page=None,
                thread_count=1
            )
            
            num_pages = len(images)
            text_parts = []
            
            logger.info(f"Processing {num_pages} pages with OCR for {pdf_path.name}...")
            
            for i, image in enumerate(images, 1):
                try:
                    page_text = pytesseract.image_to_string(image, lang='eng')
                    
                    if page_text and page_text.strip():
                        text_parts.append(page_text.strip())
                        logger.debug(f"Extracted {len(page_text)} chars from page {i}/{num_pages}")
                    
                except Exception as e:
                    logger.warning(f"Error during OCR on page {i} of {pdf_path.name}: {e}")
                    continue
            
            full_text = "\n\n".join(text_parts)
            return full_text, num_pages
            
        except Exception as e:
            logger.error(f"OCR extraction failed for {pdf_path}: {e}")
            raise
    
    def chunk_text(self, text: str, chunk_size: int = 1000, chunk_overlap: int = 200) -> List[str]:
        """Split text into overlapping chunks."""
        if not text or len(text.strip()) == 0:
            return []
        
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        if len(text) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(text):
            end = start + chunk_size
            
            if end < len(text):
                sentence_endings = re.finditer(r'[.!?]\s+', text[max(start, end - 200):end])
                sentence_ends = list(sentence_endings)
                
                if sentence_ends:
                    last_match = sentence_ends[-1]
                    end = start + (end - 200) + last_match.end()
            
            chunk = text[start:end].strip()
            if chunk:
                chunks.append(chunk)
            
            start = end - chunk_overlap
            if start >= len(text):
                break
        
        return chunks
    
    def process_document(self, pdf_path: Path, collection_name: str = "unknown") -> Dict:
        """Process PDF: extract, chunk, and store embeddings."""
        try:
            text, num_pages, used_ocr = self.extract_text_from_pdf(pdf_path, use_ocr=True)
            
            if not text or len(text.strip()) < 50:
                return {
                    'success': False,
                    'error': 'Document too short or no text extracted (may be scanned PDF without OCR)',
                    'num_pages': num_pages,
                    'used_ocr': used_ocr
                }
            
            chunks = self.chunk_text(text, chunk_size=1000, chunk_overlap=200)
            
            if not chunks:
                return {
                    'success': False,
                    'error': 'No chunks created',
                    'num_pages': num_pages
                }
            
            embeddings = self.embedding_model.encode(
                chunks,
                show_progress_bar=False,
                convert_to_numpy=True
            )
            
            file_hash = hashlib.md5(str(pdf_path).encode()).hexdigest()[:8]
            chunk_ids = [f"{file_hash}_{i}" for i in range(len(chunks))]
            
            file_name = pdf_path.name
            metadata_list = [
                {
                    'file_path': str(pdf_path),
                    'file_name': file_name,
                    'collection': collection_name,
                    'chunk_index': i,
                    'total_chunks': len(chunks),
                    'num_pages': num_pages,
                    'used_ocr': str(used_ocr)
                }
                for i in range(len(chunks))
            ]
            
            self.collection.add(
                ids=chunk_ids,
                embeddings=embeddings.tolist(),
                documents=chunks,
                metadatas=metadata_list
            )
            
            logger.info(f"Processed {file_name}: {len(chunks)} chunks, {num_pages} pages (OCR: {used_ocr})")
            
            return {
                'success': True,
                'num_chunks': len(chunks),
                'num_pages': num_pages,
                'file_name': file_name,
                'used_ocr': used_ocr
            }
            
        except Exception as e:
            logger.error(f"Error processing document {pdf_path}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def search(self, query: str, n_results: int = 5, collection_filter: Optional[str] = None) -> List[Dict]:
        """Search for relevant document chunks."""
        try:
            query_embedding = self.embedding_model.encode(
                query,
                show_progress_bar=False,
                convert_to_numpy=True
            )
            
            where_clause = None
            if collection_filter:
                where_clause = {"collection": collection_filter}
            
            results = self.collection.query(
                query_embeddings=[query_embedding.tolist()],
                n_results=n_results,
                where=where_clause
            )
            
            formatted_results = []
            if results['ids'] and len(results['ids'][0]) > 0:
                for i in range(len(results['ids'][0])):
                    formatted_results.append({
                        'chunk_id': results['ids'][0][i],
                        'text': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i],
                        'distance': results['distances'][0][i] if 'distances' in results else None
                    })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error during search: {e}")
            return []
    
    def build_query_from_failure_data(self, failure_data: Dict) -> str:
        """Build search query from failure case data."""
        query_parts = []
        
        if failure_data.get('metal_type'):
            query_parts.append(f"metal type {failure_data['metal_type']}")
        
        if failure_data.get('environment'):
            query_parts.append(f"environment {failure_data['environment']}")
        
        if failure_data.get('temperature'):
            query_parts.append(f"temperature {failure_data['temperature']}")
        
        if failure_data.get('mechanical_load'):
            query_parts.append(f"mechanical load {failure_data['mechanical_load']}")
        
        if failure_data.get('service_time'):
            query_parts.append(f"service time {failure_data['service_time']}")
        
        if failure_data.get('notes'):
            query_parts.append(failure_data['notes'])
        
        base_query = " ".join(query_parts)
        enhanced_query = f"failure analysis {base_query} root cause corrosion fatigue stress cracking"
        
        return enhanced_query
    
    def format_context_for_prompt(self, search_results: List[Dict], max_chunks: int = 5) -> str:
        """Format retrieved chunks for AI prompt."""
        if not search_results:
            return "No similar cases found in the knowledge base."
        
        context_parts = ["## Similar Cases from Knowledge Base\n"]
        
        by_document = {}
        for result in search_results[:max_chunks]:
            file_name = result['metadata'].get('file_name', 'Unknown')
            if file_name not in by_document:
                by_document[file_name] = []
            by_document[file_name].append(result)
        
        for file_name, chunks in list(by_document.items())[:3]:
            collection = chunks[0]['metadata'].get('collection', 'Unknown')
            context_parts.append(f"\n### From: {file_name} ({collection})\n")
            
            for chunk in chunks[:2]:
                text = chunk['text']
                if len(text) > 800:
                    text = text[:800] + "..."
                context_parts.append(f"{text}\n")
        
        return "\n".join(context_parts)
    
    def get_collection_stats(self) -> Dict:
        """Get collection statistics."""
        try:
            count = self.collection.count()
            return {
                'total_chunks': count,
                'collection_name': self.collection_name
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {'total_chunks': 0, 'error': str(e)}


_rag_service = None

def get_rag_service() -> RAGService:
    """Get singleton RAG service instance."""
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service

