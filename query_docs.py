#!/usr/bin/env python3
"""
Поиск по векторизованным руководствам 1Forma (OpenAI embeddings)
"""

import chromadb
from chromadb.utils import embedding_functions
import sys
import os

def search_docs(query, collection_name="admin_manual", n_results=5):
    """Выполняет семантический поиск"""
    
    api_key = os.environ.get('OPENAI_API_KEY')
    if not api_key:
        print("❌ OPENAI_API_KEY не найден в переменных окружения!")
        return None
    
    ef = embedding_functions.OpenAIEmbeddingFunction(
        api_key=api_key,
        model_name="text-embedding-3-small"
    )
    
    client = chromadb.PersistentClient(path="./chroma_db")
    
    try:
        collection = client.get_collection(
            name=collection_name,
            embedding_function=ef
        )
    except:
        print(f"❌ Коллекция '{collection_name}' не найдена!")
        print(f"   Доступные коллекции: {[c.name for c in client.list_collections()]}")
        return None
    
    results = collection.query(
        query_texts=[query],
        n_results=n_results
    )
    
    return results

def main():
    if len(sys.argv) < 2:
        print("Использование: python3 query_docs.py 'ваш вопрос' [manual_type] [num_results]")
        print("\nmanual_type: admin_manual (по умолчанию) или user_manual")
        print("num_results: количество результатов (по умолчанию 5)")
        print("\nПример:")
        print("  python3 query_docs.py 'как настроить пользователей'")
        print("  python3 query_docs.py 'виджеты портала' admin_manual 3")
        print("  python3 query_docs.py 'создание задачи' user_manual 5")
        sys.exit(1)
    
    query = sys.argv[1]
    collection_name = sys.argv[2] if len(sys.argv) > 2 else "admin_manual"
    n_results = int(sys.argv[3]) if len(sys.argv) > 3 else 5
    
    print(f"🔍 Поиск в {collection_name}: '{query}'")
    print("=" * 60)
    
    results = search_docs(query, collection_name, n_results)
    
    if not results or not results['documents'][0]:
        print("❌ Ничего не найдено")
        return
    
    documents = results['documents'][0]
    metadatas = results['metadatas'][0]
    distances = results['distances'][0]
    
    for i, (doc, meta, dist) in enumerate(zip(documents, metadatas, distances), 1):
        relevance = (1 - dist) * 100  # Косинусная близость в проценты
        
        print(f"\n📄 Результат #{i} (релевантность: {relevance:.1f}%)")
        print(f"   Источник: {meta['source']}")
        print(f"   Страница: {meta['page']}/{meta['total_pages']}")
        print(f"   {'-' * 56}")
        
        # Показываем первые 500 символов
        preview = doc[:500].replace('\n', ' ').strip()
        if len(doc) > 500:
            preview += "..."
        print(f"   {preview}")
        print()

if __name__ == "__main__":
    main()
