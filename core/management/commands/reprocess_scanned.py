"""
Django management command to reprocess scanned PDFs with OCR.

This command specifically targets the "MostlyUnsearchable" folder and
forces OCR processing for all PDFs in that folder.

Usage:
    python manage.py reprocess_scanned
    python manage.py reprocess_scanned --path RAG_DATA/ASM\ Failure\ Analisys\ Cases/MostlyUnsearchable
"""

from django.core.management.base import BaseCommand
from django.conf import settings
from pathlib import Path
from core.rag_service import get_rag_service
from core.models import Document
from tqdm import tqdm
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Reprocess scanned PDFs from MostlyUnsearchable folder with OCR'

    def add_arguments(self, parser):
        parser.add_argument(
            '--path',
            type=str,
            default=None,
            help='Specific path to process (default: searches for MostlyUnsearchable folder)',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force reprocessing even if already processed',
        )

    def handle(self, *args, **options):
        rag_service = get_rag_service()
        
        # Check if OCR is available
        try:
            import pytesseract
            from pdf2image import convert_from_path
            OCR_AVAILABLE = True
        except ImportError:
            OCR_AVAILABLE = False
        
        if not OCR_AVAILABLE:
            self.stdout.write(self.style.ERROR(
                "OCR libraries are not installed!\n"
                "Please install: pip install pytesseract pdf2image Pillow\n"
                "And install Tesseract OCR engine (see OCR_SETUP.md)"
            ))
            return
        
        base_dir = Path(settings.BASE_DIR)
        
        # Find the MostlyUnsearchable folder
        if options['path']:
            if Path(options['path']).is_absolute():
                target_path = Path(options['path'])
            else:
                target_path = base_dir / options['path']
        else:
            # Search for MostlyUnsearchable folder
            rag_data_path = base_dir / "RAG_DATA"
            target_path = None
            
            for folder in rag_data_path.rglob("*MostlyUnsearchable*"):
                if folder.is_dir():
                    target_path = folder
                    break
            
            if not target_path:
                self.stdout.write(self.style.ERROR(
                    "Could not find 'MostlyUnsearchable' folder in RAG_DATA.\n"
                    "Please specify path with --path option."
                ))
                return
        
        if not target_path.exists():
            self.stdout.write(self.style.ERROR(f"Path does not exist: {target_path}"))
            return
        
        self.stdout.write(self.style.SUCCESS(f"Processing scanned PDFs in: {target_path}"))
        
        # Find all PDF files
        pdf_files = list(target_path.rglob("*.pdf")) + list(target_path.rglob("*.PDF"))
        
        if not pdf_files:
            self.stdout.write(self.style.WARNING("No PDF files found!"))
            return
        
        self.stdout.write(self.style.SUCCESS(f"Found {len(pdf_files)} PDF files"))
        self.stdout.write(self.style.WARNING(
            "Note: OCR processing is slow (~10-30 seconds per page).\n"
            "This may take a while for large documents..."
        ))
        
        # Process each PDF
        processed_count = 0
        ocr_count = 0
        skipped_count = 0
        error_count = 0
        
        with tqdm(total=len(pdf_files), desc="Processing with OCR") as pbar:
            for pdf_path in pdf_files:
                try:
                    # Get relative path for database
                    try:
                        relative_path = pdf_path.relative_to(base_dir)
                    except ValueError:
                        relative_path = str(pdf_path)
                    
                    # Check if already processed
                    doc_record, created = Document.objects.get_or_create(
                        file_path=str(relative_path),
                        defaults={
                            'file_name': pdf_path.name,
                            'collection_name': self._get_collection_name(pdf_path, base_dir / "RAG_DATA"),
                            'file_size': pdf_path.stat().st_size,
                        }
                    )
                    
                    if not created and doc_record.is_processed and not options['force']:
                        if doc_record.used_ocr:
                            self.stdout.write(self.style.WARNING(
                                f"Skipping {pdf_path.name} (already processed with OCR)"
                            ))
                            skipped_count += 1
                        else:
                            self.stdout.write(self.style.WARNING(
                                f"Reprocessing {pdf_path.name} (was processed without OCR)"
                            ))
                    elif not created and doc_record.is_processed and options['force']:
                        self.stdout.write(self.style.WARNING(
                            f"Force reprocessing {pdf_path.name}"
                        ))
                    
                    # Process the document (will force OCR for files in this folder)
                    result = rag_service.process_document(
                        pdf_path,
                        collection_name=doc_record.collection_name
                    )
                    
                    if result['success']:
                        # Update document record
                        doc_record.num_pages = result.get('num_pages', 0)
                        doc_record.num_chunks = result.get('num_chunks', 0)
                        doc_record.used_ocr = result.get('used_ocr', False)
                        doc_record.is_processed = True
                        doc_record.error_message = None
                        doc_record.save()
                        processed_count += 1
                        
                        if result.get('used_ocr', False):
                            ocr_count += 1
                            self.stdout.write(self.style.SUCCESS(
                                f"✓ {pdf_path.name}: {result.get('num_chunks', 0)} chunks (OCR used)"
                            ))
                        else:
                            self.stdout.write(self.style.WARNING(
                                f"⚠ {pdf_path.name}: OCR was not used (may need manual check)"
                            ))
                    else:
                        doc_record.is_processed = False
                        doc_record.error_message = result.get('error', 'Unknown error')
                        doc_record.save()
                        error_count += 1
                        self.stdout.write(
                            self.style.ERROR(f"✗ Failed: {pdf_path.name}: {result.get('error')}")
                        )
                    
                except Exception as e:
                    error_count += 1
                    logger.error(f"Error processing {pdf_path}: {e}")
                    self.stdout.write(
                        self.style.ERROR(f"✗ Exception: {pdf_path.name}: {str(e)}")
                    )
                
                pbar.set_postfix({
                    'processed': processed_count,
                    'ocr': ocr_count,
                    'skipped': skipped_count,
                    'errors': error_count
                })
                pbar.update(1)
        
        # Print summary
        self.stdout.write(self.style.SUCCESS("\n" + "="*60))
        self.stdout.write(self.style.SUCCESS("Reprocessing Summary:"))
        self.stdout.write(self.style.SUCCESS(f"  Processed: {processed_count}"))
        self.stdout.write(self.style.SUCCESS(f"  Used OCR: {ocr_count}"))
        self.stdout.write(self.style.SUCCESS(f"  Skipped: {skipped_count}"))
        self.stdout.write(self.style.SUCCESS(f"  Errors: {error_count}"))
        self.stdout.write(self.style.SUCCESS("="*60))
        
        if ocr_count < processed_count:
            self.stdout.write(self.style.WARNING(
                f"\n⚠ Warning: {processed_count - ocr_count} files were processed but OCR was not used.\n"
                "This may indicate:\n"
                "  1. OCR libraries are not properly installed\n"
                "  2. Tesseract OCR is not in PATH\n"
                "  3. Files are not actually scanned (have extractable text)\n"
                "\nCheck logs for more details."
            ))
    
    def _get_collection_name(self, pdf_path: Path, base_path: Path) -> str:
        """Extract collection name from file path."""
        try:
            rel_path = pdf_path.relative_to(base_path)
            parts = rel_path.parts
            if len(parts) > 1:
                return parts[0]
            return "root"
        except ValueError:
            return pdf_path.parent.name or "unknown"

