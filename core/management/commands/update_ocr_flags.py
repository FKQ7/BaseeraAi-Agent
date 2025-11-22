"""
Django management command to update used_ocr flags for scanned PDFs.

This command finds all documents in scanned/unsearchable folders and
updates their used_ocr field to True in the database.

Usage:
    python manage.py update_ocr_flags
    python manage.py update_ocr_flags --dry-run  # Preview changes without saving
"""

from django.core.management.base import BaseCommand
from core.models import Document
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Update used_ocr flags for documents in scanned folders'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview changes without saving to database',
        )
        parser.add_argument(
            '--collection',
            type=str,
            default=None,
            help='Only update documents in specific collection (e.g., "ASM Failure Analisys Cases")',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        collection_filter = options.get('collection')
        
        # Keywords that indicate scanned PDFs
        scanned_keywords = [
            'unsearchable',
            'scanned',
            'mostlyunsearchable',
            'image',
            'scan'
        ]
        
        # Find all documents
        queryset = Document.objects.all()
        
        if collection_filter:
            queryset = queryset.filter(collection_name__icontains=collection_filter)
        
        # Filter documents that are likely scanned
        scanned_docs = []
        for doc in queryset:
            file_path_lower = doc.file_path.lower()
            file_name_lower = doc.file_name.lower()
            
            # Check if path or filename contains scanned indicators
            is_scanned = any(keyword in file_path_lower or keyword in file_name_lower 
                          for keyword in scanned_keywords)
            
            if is_scanned:
                scanned_docs.append(doc)
        
        if not scanned_docs:
            self.stdout.write(self.style.WARNING("No scanned documents found."))
            return
        
        self.stdout.write(self.style.SUCCESS(f"Found {len(scanned_docs)} documents in scanned folders"))
        
        # Count how many need updating
        needs_update = [doc for doc in scanned_docs if not doc.used_ocr]
        already_updated = [doc for doc in scanned_docs if doc.used_ocr]
        
        self.stdout.write(f"  - Already marked as OCR: {len(already_updated)}")
        self.stdout.write(f"  - Need update: {len(needs_update)}")
        
        if not needs_update:
            self.stdout.write(self.style.SUCCESS("All scanned documents already have used_ocr=True"))
            return
        
        # Show preview
        self.stdout.write(self.style.WARNING("\nDocuments to update:"))
        for doc in needs_update[:10]:  # Show first 10
            self.stdout.write(f"  - {doc.file_name} ({doc.collection_name})")
        if len(needs_update) > 10:
            self.stdout.write(f"  ... and {len(needs_update) - 10} more")
        
        if dry_run:
            self.stdout.write(self.style.WARNING(
                f"\n[DRY RUN] Would update {len(needs_update)} documents."
                "\nRun without --dry-run to apply changes."
            ))
            return
        
        # Confirm
        self.stdout.write(self.style.WARNING(
            f"\nAbout to update {len(needs_update)} documents."
        ))
        confirm = input("Continue? (yes/no): ").strip().lower()
        
        if confirm not in ['yes', 'y']:
            self.stdout.write(self.style.ERROR("Cancelled."))
            return
        
        # Update documents
        updated_count = 0
        for doc in needs_update:
            doc.used_ocr = True
            doc.save(update_fields=['used_ocr'])
            updated_count += 1
        
        self.stdout.write(self.style.SUCCESS(
            f"\n✅ Successfully updated {updated_count} documents!"
        ))
        
        # Show summary
        self.stdout.write(self.style.SUCCESS("\n" + "="*60))
        self.stdout.write(self.style.SUCCESS("Update Summary:"))
        self.stdout.write(self.style.SUCCESS(f"  Total scanned documents: {len(scanned_docs)}"))
        self.stdout.write(self.style.SUCCESS(f"  Updated: {updated_count}"))
        self.stdout.write(self.style.SUCCESS(f"  Already correct: {len(already_updated)}"))
        self.stdout.write(self.style.SUCCESS("="*60))
        
        # Show collection breakdown
        from collections import Counter
        collections = Counter(doc.collection_name for doc in scanned_docs)
        self.stdout.write(self.style.SUCCESS("\nBy Collection:"))
        for collection, count in collections.most_common():
            self.stdout.write(f"  - {collection}: {count} documents")

