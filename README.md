# 1Forma Documentation Vectorization

Semantic search for 1Forma manuals using OpenAI embeddings and ChromaDB.

## Overview

This project enables semantic search across 1Forma's extensive documentation:
- **Admin Manual**: 6331 pages
- **User Guide**: 855 pages

Instead of keyword search, ask questions in natural language and get relevant sections with page numbers.

## Features

- ✅ OpenAI text-embedding-3-small for high-quality embeddings
- ✅ ChromaDB for local vector storage (no cloud dependency)
- ✅ Batch processing for rate limit safety
- ✅ CLI tools for easy querying
- ✅ Metadata tracking (source, page numbers)

## Prerequisites

- Python 3.8+
- OpenAI API key
- PDFs: `Admin.pdf` and `User_Guide.pdf` from https://help.1forma.ru/pdf/

## Quick Start

### 1. Installation

```bash
# Clone repository
git clone https://github.com/SmartestBotEver/1forma-vectorization.git
cd 1forma-vectorization

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Download PDFs

```bash
# Download manuals
curl -O https://help.1forma.ru/pdf/Admin.pdf
curl -O https://help.1forma.ru/pdf/User_Guide.pdf
```

### 3. Set API Key

```bash
export OPENAI_API_KEY='your-api-key-here'
```

### 4. Vectorize Documents

```bash
python3 vectorize_manuals.py
# Takes ~20-25 minutes
# Cost: ~$0.50-1.00
```

### 5. Search

```bash
# Search admin manual
python3 query_docs.py "как настроить дополнительные поля"

# Search user guide
python3 query_docs.py "создание задачи" user_manual

# Get more results
python3 query_docs.py "виджеты портала" admin_manual 10
```

## Usage Examples

### Basic Search
```bash
python3 query_docs.py "настройка пользователей"
```

Output:
```
🔍 Поиск в admin_manual: 'настройка пользователей'
============================================================

📄 Результат #1 (релевантность: 87.3%)
   Источник: Admin
   Страница: 42/6331
   --------------------------------------------------------
   Настройка пользователей в системе 1Forma...
```

### Status Check
```bash
python3 check_status.py
```

### Python API

```python
import chromadb
from chromadb.utils import embedding_functions
import os

# Connect
ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=os.environ['OPENAI_API_KEY'],
    model_name="text-embedding-3-small"
)
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_collection(name="admin_manual", embedding_function=ef)

# Search
results = collection.query(
    query_texts=["настройка дополнительных полей"],
    n_results=5
)

for doc, meta in zip(results['documents'][0], results['metadatas'][0]):
    print(f"Page {meta['page']}: {doc[:200]}...")
```

## Architecture

```
┌─────────────────┐
│  PDF Documents  │
│  Admin.pdf      │
│  User_Guide.pdf │
└────────┬────────┘
         │ PyMuPDF
         ▼
┌─────────────────┐
│  Text Chunks    │
│  (page-level)   │
└────────┬────────┘
         │ OpenAI API
         │ text-embedding-3-small
         ▼
┌─────────────────┐
│  Vector DB      │
│  ChromaDB       │
│  (local)        │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Search CLI     │
│  query_docs.py  │
└─────────────────┘
```

## Performance

**Vectorization:**
- Admin.pdf (6331 pages): ~20 minutes
- User_Guide.pdf (855 pages): ~5 minutes
- Total: ~25 minutes

**Search:**
- Latency: 100-300ms per query
- Throughput: ~5-10 queries/sec

**Storage:**
- Vector DB: ~2-3 GB

**Cost:**
- Initial vectorization: ~$0.50-1.00
- Searches: ~$0.0001 per query

## Files

- `vectorize_manuals.py` - Main vectorization script
- `query_docs.py` - Search interface
- `check_status.py` - Status checker
- `requirements.txt` - Python dependencies
- `README.md` - This file

## Configuration

### Change Batch Size

Edit `vectorize_manuals.py`:
```python
batch_size = 50  # Reduce if hitting rate limits
```

### Change Embedding Model

```python
ef = embedding_functions.OpenAIEmbeddingFunction(
    api_key=api_key,
    model_name="text-embedding-3-large"  # Higher quality, more expensive
)
```

## Troubleshooting

### Rate Limit Errors
Reduce `batch_size` in `vectorize_manuals.py` and add longer `time.sleep()` delays.

### Out of Memory
Process PDFs one at a time by commenting out files in the script.

### Collection Not Found
Run `vectorize_manuals.py` first to create the database.

## Contributing

Pull requests welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a PR

## License

MIT License - see LICENSE file

## Credits

- 1Forma documentation: https://help.1forma.ru/
- OpenAI embeddings: https://openai.com/
- ChromaDB: https://www.trychroma.com/
- PyMuPDF: https://pymupdf.readthedocs.io/

## Support

For issues or questions:
- GitHub Issues: https://github.com/SmartestBotEver/1forma-vectorization/issues
- 1Forma docs: https://help.1forma.ru/

---

Made with ❤️ for better documentation search
