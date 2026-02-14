#!/usr/bin/env python3
"""
Векторизация PDF-документов для 1Forma с использованием OpenAI embeddings
Обрабатывает Admin.pdf и User_Guide.pdf постранично
"""

import fitz  # PyMuPDF
import chromadb
from chromadb.utils import embedding_functions
import sys
import time
import os
from pathlib import Path

def extract_text_from_pdf(pdf_path, batch_size=100):
    """Извлекает текст постранично с батчингом"""
    print(f"📄 Открываю {pdf_path}...")
    doc = fitz.open(pdf_path)
    total_pages = len(doc)
    print(f"📊 Всего страниц: {total_pages}")
    
    documents = []
    metadatas = []
    ids = []
    
    doc_name = Path(pdf_path).stem
    
    for page_num in range(total_pages):
        page = doc[page_num]
        text = page.get_text("text")
        
        # Пропускаем пустые страницы
        if not text.strip():
            continue
        
        # Ограничиваем размер (OpenAI embeddings: max 8191 tokens, ~32k chars)
        text = text[:32000]
        
        documents.append(text)
        metadatas.append({
            "source": doc_name,
            "page": page_num + 1,
            "total_pages": total_pages
        })
        ids.append(f"{doc_name}_page_{page_num + 1}")
        
        # Прогресс
        if (page_num + 1) % batch_size == 0:
            print(f"   ✓ Обработано {page_num + 1}/{total_pages} страниц...")
    
    doc.close()
    print(f"✅ Извлечено {len(documents)} непустых страниц из {total_pages}")
    return documents, metadatas, ids

def create_vector_store(documents, metadatas, ids, collection_name):
    """Создаёт векторную базу Chroma с OpenAI embeddings"""
    print(f"\n🔧 Создаю векторную базу '{collection_name}'...")
    
    # Проверяем API ключ
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("❌ OPENAI_API_KEY не найден в переменных окружения!")
    
    # OpenAI embeddings (text-embedding-3-small - быстрее и дешевле)
    ef = embedding_functions.OpenAIEmbeddingFunction(
        api_key=api_key,
        model_name="text-embedding-3-small"
    )
    
    client = chromadb.PersistentClient(path="./chroma_db")
    
    # Удаляем старую коллекцию если есть
    try:
        client.delete_collection(name=collection_name)
        print(f"   ♻️  Удалена старая коллекция")
    except:
        pass
    
    collection = client.create_collection(
        name=collection_name,
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"}
    )
    
    # Добавляем документы батчами (для OpenAI API rate limits)
    batch_size = 50  # Меньше батч для API
    total = len(documents)
    
    for i in range(0, total, batch_size):
        end = min(i + batch_size, total)
        batch_docs = documents[i:end]
        batch_metas = metadatas[i:end]
        batch_ids = ids[i:end]
        
        try:
            collection.add(
                documents=batch_docs,
                metadatas=batch_metas,
                ids=batch_ids
            )
            print(f"   ✓ Векторизовано {end}/{total} документов...")
            time.sleep(0.5)  # Пауза между батчами для rate limit
        except Exception as e:
            print(f"   ⚠️  Ошибка на батче {i}-{end}: {e}")
            print(f"   Пауза 2 секунды и повтор...")
            time.sleep(2)
            # Повторная попытка
            collection.add(
                documents=batch_docs,
                metadatas=batch_metas,
                ids=batch_ids
            )
    
    print(f"✅ Векторная база создана: {total} документов")
    return collection

def main():
    print("=" * 60)
    print("🚀 Векторизация руководств 1Forma (OpenAI embeddings)")
    print("=" * 60)
    
    # Проверяем API ключ
    if not os.environ.get('OPENAI_API_KEY'):
        print("❌ OPENAI_API_KEY не найден!")
        print("   Установите: export OPENAI_API_KEY='your-key'")
        sys.exit(1)
    
    print(f"✅ OpenAI API ключ найден")
    print(f"📊 Модель: text-embedding-3-small")
    print()
    
    # Проверяем наличие файлов
    files = {
        "Admin.pdf": "admin_manual",
        "User_Guide.pdf": "user_manual"
    }
    
    for pdf_file, collection_name in files.items():
        if not Path(pdf_file).exists():
            print(f"⚠️  Файл {pdf_file} не найден, пропускаю...")
            continue
        
        print(f"\n{'='*60}")
        print(f"📚 Обрабатываю: {pdf_file}")
        print(f"{'='*60}")
        
        try:
            # Извлекаем текст
            documents, metadatas, ids = extract_text_from_pdf(pdf_file, batch_size=100)
            
            # Векторизуем
            collection = create_vector_store(documents, metadatas, ids, collection_name)
            
            print(f"\n✨ {pdf_file} успешно векторизован!")
            
        except Exception as e:
            print(f"❌ Ошибка при обработке {pdf_file}: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    print(f"\n{'='*60}")
    print("🎉 Векторизация завершена!")
    print(f"{'='*60}")
    print(f"\n📁 База данных сохранена в: ./chroma_db/")
    print(f"💰 Стоимость: ~$0.50-1.00 (зависит от объёма текста)")
    print(f"\n📖 Использование:")
    print(f"   python3 query_docs.py 'ваш вопрос'")

if __name__ == "__main__":
    main()
