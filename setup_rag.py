"""
Quick setup script for RAG system.
Run this after installing dependencies to verify everything is working.
"""

import sys
from pathlib import Path

def check_dependencies():
    """Check if all required packages are installed."""
    required_packages = [
        'chromadb',
        'sentence_transformers',
        'pypdf',
        'django',
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✓ {package} is installed")
        except ImportError:
            missing.append(package)
            print(f"✗ {package} is NOT installed")
    
    if missing:
        print(f"\nPlease install missing packages:")
        print(f"pip install {' '.join(missing)}")
        return False
    
    return True

def check_directories():
    """Check if required directories exist."""
    base_dir = Path(__file__).parent
    rag_data = base_dir / "RAG_DATA"
    
    if not rag_data.exists():
        print(f"✗ RAG_DATA directory not found at {rag_data}")
        return False
    
    print(f"✓ RAG_DATA directory found")
    
    # Count PDFs
    pdfs = list(rag_data.rglob("*.pdf")) + list(rag_data.rglob("*.PDF"))
    print(f"✓ Found {len(pdfs)} PDF files")
    
    return True

def main():
    print("=" * 60)
    print("Baseera AI RAG System Setup Check")
    print("=" * 60)
    print()
    
    print("Checking dependencies...")
    deps_ok = check_dependencies()
    print()
    
    print("Checking directories...")
    dirs_ok = check_directories()
    print()
    
    if deps_ok and dirs_ok:
        print("=" * 60)
        print("✓ Setup check passed!")
        print()
        print("Next steps:")
        print("1. Run migrations: python manage.py migrate")
        print("2. Ingest documents: python manage.py ingest_documents")
        print("3. Start server: python manage.py runserver")
        print("=" * 60)
        return 0
    else:
        print("=" * 60)
        print("✗ Setup check failed. Please fix the issues above.")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    sys.exit(main())

