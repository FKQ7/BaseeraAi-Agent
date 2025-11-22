from django.contrib import admin
from django.contrib import messages
from django.conf import settings
from core.models import Document, QueryLog
from core.rag_service import get_rag_service
from pathlib import Path
import os


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['file_name', 'collection_name', 'num_chunks', 'num_pages', 'used_ocr', 'is_processed', 'processed_at']
    list_filter = ['is_processed', 'used_ocr', 'collection_name', 'processed_at']
    search_fields = ['file_name', 'file_path', 'collection_name']
    readonly_fields = ['processed_at', 'last_updated', 'file_size_display']
    list_per_page = 50
    
    fieldsets = (
        ('File Information', {
            'fields': ('file_path', 'file_name', 'collection_name', 'file_size', 'file_size_display')
        }),
        ('Processing Status', {
            'fields': ('is_processed', 'used_ocr', 'num_pages', 'num_chunks', 'error_message')
        }),
        ('Metadata', {
            'fields': ('processed_at', 'last_updated'),
            'classes': ('collapse',)
        }),
    )
    
    def file_size_display(self, obj):
        """Display file size in human-readable format."""
        if obj.file_size:
            size = float(obj.file_size)
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024.0:
                    return f"{size:.2f} {unit}"
                size /= 1024.0
            return f"{size:.2f} TB"
        return "N/A"
    file_size_display.short_description = "File Size (Human Readable)"
    
    def get_form(self, request, obj=None, **kwargs):
        """Customize form for add vs change."""
        form = super().get_form(request, obj, **kwargs)
        
        # When adding a new document, make file_path more helpful
        if obj is None:  # Adding new document
            form.base_fields['file_path'].help_text = (
                "Enter the path to the PDF file. Can be:\n"
                "- Relative to project root (e.g., 'RAG_DATA/ASMHandbook/file.pdf')\n"
                "- Absolute path (e.g., 'C:/path/to/file.pdf')\n"
                "The file_name will be auto-extracted from the path."
            )
            form.base_fields['file_name'].help_text = (
                "File name will be auto-extracted from file_path, but you can override it."
            )
            form.base_fields['collection_name'].help_text = (
                "Collection/folder name (e.g., 'ASM Handbook', 'CSB Reports'). "
                "Used for organizing documents."
            )
            form.base_fields['is_processed'].help_text = (
                "Uncheck this if you want to process the document later using the 'Process Documents' action."
            )
        else:  # Editing existing document
            form.base_fields['file_path'].help_text = (
                "Path to the PDF file. Changing this will not reprocess the document."
            )
        
        return form
    
    def save_model(self, request, obj, form, change):
        """Override save to auto-extract file_name and file_size if not set."""
        # Auto-extract file_name from file_path if not set
        if obj.file_path and not obj.file_name:
            obj.file_name = Path(obj.file_path).name
        
        # Try to get file size if file exists
        if obj.file_path and not obj.file_size:
            # Try relative path first
            base_dir = Path(settings.BASE_DIR)
            full_path = base_dir / obj.file_path if not Path(obj.file_path).is_absolute() else Path(obj.file_path)
            
            if full_path.exists() and full_path.is_file():
                obj.file_size = full_path.stat().st_size
            else:
                # Try absolute path
                if Path(obj.file_path).exists():
                    obj.file_size = Path(obj.file_path).stat().st_size
        
        super().save_model(request, obj, form, change)
    
    actions = ['process_selected_documents', 'mark_as_unprocessed', 'mark_as_processed']
    
    @admin.action(description='Process selected documents with RAG')
    def process_selected_documents(self, request, queryset):
        """Process selected documents through the RAG system."""
        rag_service = get_rag_service()
        processed = 0
        errors = 0
        
        for doc in queryset:
            if not doc.file_path:
                self.message_user(
                    request,
                    f"Document {doc.file_name} has no file_path. Skipping.",
                    level=messages.WARNING
                )
                errors += 1
                continue
            
            # Get full path
            base_dir = Path(settings.BASE_DIR)
            if Path(doc.file_path).is_absolute():
                pdf_path = Path(doc.file_path)
            else:
                pdf_path = base_dir / doc.file_path
            
            if not pdf_path.exists():
                self.message_user(
                    request,
                    f"File not found: {pdf_path}. Skipping {doc.file_name}.",
                    level=messages.ERROR
                )
                errors += 1
                continue
            
            # Process the document
            try:
                result = rag_service.process_document(
                    pdf_path,
                    collection_name=doc.collection_name
                )
                
                if result['success']:
                    doc.num_pages = result.get('num_pages', 0)
                    doc.num_chunks = result.get('num_chunks', 0)
                    doc.used_ocr = result.get('used_ocr', False)
                    doc.is_processed = True
                    doc.error_message = None
                    doc.save()
                    processed += 1
                else:
                    doc.is_processed = False
                    doc.error_message = result.get('error', 'Unknown error')
                    doc.save()
                    errors += 1
                    self.message_user(
                        request,
                        f"Failed to process {doc.file_name}: {result.get('error')}",
                        level=messages.ERROR
                    )
            except Exception as e:
                doc.is_processed = False
                doc.error_message = str(e)
                doc.save()
                errors += 1
                self.message_user(
                    request,
                    f"Error processing {doc.file_name}: {str(e)}",
                    level=messages.ERROR
                )
        
        self.message_user(
            request,
            f"Successfully processed {processed} document(s). {errors} error(s).",
            level=messages.SUCCESS if processed > 0 else messages.WARNING
        )
    
    @admin.action(description='Mark selected documents as unprocessed')
    def mark_as_unprocessed(self, request, queryset):
        """Mark selected documents as not processed."""
        count = queryset.update(is_processed=False, error_message=None)
        self.message_user(
            request,
            f"Marked {count} document(s) as unprocessed.",
            level=messages.SUCCESS
        )
    
    @admin.action(description='Mark selected documents as processed (without actually processing)')
    def mark_as_processed(self, request, queryset):
        """Mark selected documents as processed without actually processing them."""
        count = queryset.update(is_processed=True)
        self.message_user(
            request,
            f"Marked {count} document(s) as processed.",
            level=messages.SUCCESS
        )


@admin.register(QueryLog)
class QueryLogAdmin(admin.ModelAdmin):
    list_display = ['created_at', 'metal_type', 'environment', 'num_results_retrieved', 'response_time_ms']
    list_filter = ['created_at']
    search_fields = ['query_text', 'metal_type', 'environment']
    readonly_fields = ['created_at']
    list_per_page = 50
