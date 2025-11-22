from django.db import models
from pathlib import Path
import os


class Document(models.Model):
    """Tracks processed PDF documents."""
    
    file_path = models.CharField(max_length=1000, unique=True)
    file_name = models.CharField(max_length=500)
    collection_name = models.CharField(max_length=200, help_text="Source collection/folder")
    file_size = models.BigIntegerField(help_text="File size in bytes")
    num_pages = models.IntegerField(null=True, blank=True)
    num_chunks = models.IntegerField(default=0, help_text="Number of text chunks created")
    used_ocr = models.BooleanField(default=False, help_text="Whether OCR was used to extract text")
    processed_at = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    is_processed = models.BooleanField(default=False)
    error_message = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-processed_at']
        indexes = [
            models.Index(fields=['file_path']),
            models.Index(fields=['is_processed']),
        ]
    
    def __str__(self):
        return f"{self.file_name} ({self.collection_name})"


class QueryLog(models.Model):
    """Logs user queries."""
    
    query_text = models.TextField()
    metal_type = models.CharField(max_length=200, blank=True)
    environment = models.CharField(max_length=200, blank=True)
    temperature = models.CharField(max_length=100, blank=True)
    num_results_retrieved = models.IntegerField(default=0)
    response_time_ms = models.IntegerField(help_text="Response time in milliseconds")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"Query at {self.created_at}"
