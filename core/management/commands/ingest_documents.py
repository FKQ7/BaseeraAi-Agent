"""Management command to ingest PDF documents."""

from django.core.management.base import BaseCommand
from django.conf import settings
from pathlib import Path
from core.rag_service import get_rag_service
from core.models import Document
from tqdm import tqdm
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Ingest PDF documents from RAG_DATA directory into the vector database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--path',
            type=str,
            default=None,
            help='Specific path to process (relative to RAG_DATA or absolute)',
        )
        parser.add_argument(
            '--reprocess',
            action='store_true',
            help='Reprocess documents that were already processed',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=None,
            help='Limit the number of documents to process (for testing)',
        )

    def handle(self, *args, **options):
        rag_service = get_rag_service()
        base_dir = Path(settings.BASE_DIR)
        if options['path']:
            if Path(options['path']).is_absolute():
                rag_data_path = Path(options['path'])
            else:
                rag_data_path = base_dir / options['path']
        else:
            rag_data_path = base_dir / "RAG_DATA"
        
        if not rag_data_path.exists():
            self.stdout.write(self.style.ERROR(f"Path does not exist: {rag_data_path}"))
            return
        
        self.stdout.write(self.style.SUCCESS(f"Scanning for PDFs in: {rag_data_path}"))
        
        pdf_files = list(rag_data_path.rglob("*.pdf")) + list(rag_data_path.rglob("*.PDF"))
        
        if not pdf_files:
            self.stdout.write(self.style.WARNING("No PDF files found!"))
            return
        
        self.stdout.write(self.style.SUCCESS(f"Found {len(pdf_files)} PDF files"))
        
        if options['limit']:
            pdf_files = pdf_files[:options['limit']]
            self.stdout.write(self.style.WARNING(f"Processing limited to {len(pdf_files)} files"))
        
        processed_count = 0
        skipped_count = 0
        error_count = 0
        
        with tqdm(total=len(pdf_files), desc="Processing PDFs") as pbar:
            for pdf_path in pdf_files:
                try:
                    try:
                        relative_path = pdf_path.relative_to(base_dir)
                    except ValueError:
                        relative_path = str(pdf_path)
                    
                    doc_record, created = Document.objects.get_or_create(
                        file_path=str(relative_path),
                        defaults={
                            'file_name': pdf_path.name,
                            'collection_name': self._get_collection_name(pdf_path, rag_data_path),
                            'file_size': pdf_path.stat().st_size,
                        }
                    )
                    
                    if not created and doc_record.is_processed and not options['reprocess']:
                        skipped_count += 1
                        pbar.set_postfix({
                            'processed': processed_count,
                            'skipped': skipped_count,
                            'errors': error_count
                        })
                        pbar.update(1)
                        continue
                    
                    result = rag_service.process_document(
                        pdf_path,
                        collection_name=doc_record.collection_name
                    )
                    
                    if result['success']:
                        doc_record.num_pages = result.get('num_pages', 0)
                        doc_record.num_chunks = result.get('num_chunks', 0)
                        doc_record.used_ocr = result.get('used_ocr', False)
                        doc_record.is_processed = True
                        doc_record.error_message = None
                        doc_record.save()
                        processed_count += 1
                    else:
                        doc_record.is_processed = False
                        doc_record.error_message = result.get('error', 'Unknown error')
                        doc_record.save()
                        error_count += 1
                        self.stdout.write(
                            self.style.WARNING(f"Failed to process {pdf_path.name}: {result.get('error')}")
                        )
                    
                except Exception as e:
                    error_count += 1
                    logger.error(f"Error processing {pdf_path}: {e}")
                        self.stdout.write(
                            self.style.ERROR(f"Exception processing {pdf_path.name}: {str(e)}")
                        )
                
                pbar.set_postfix({
                    'processed': processed_count,
                    'skipped': skipped_count,
                    'errors': error_count
                })
                pbar.update(1)
        
        self.stdout.write(self.style.SUCCESS("\n" + "="*60))
        self.stdout.write(self.style.SUCCESS("Ingestion Summary:"))
        self.stdout.write(self.style.SUCCESS(f"  Processed: {processed_count}"))
        self.stdout.write(self.style.SUCCESS(f"  Skipped: {skipped_count}"))
        self.stdout.write(self.style.SUCCESS(f"  Errors: {error_count}"))
        self.stdout.write(self.style.SUCCESS("="*60))
        
        stats = rag_service.get_collection_stats()
        self.stdout.write(self.style.SUCCESS(f"\nTotal chunks in vector DB: {stats.get('total_chunks', 0)}"))
    
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

