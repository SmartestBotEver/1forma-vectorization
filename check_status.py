#!/usr/bin/env python3
"""
Статус векторизации руководств 1Forma
"""

import chromadb
from pathlib import Path
import sys

def check_status():
    """Проверяет статус векторной базы"""
    
    db_path = Path("./chroma_db")
    
    if not db_path.exists():
        print("❌ База данных не найдена")
        print("   Запустите: python3 vectorize_manuals.py")
        return
    
    print("📊 Статус векторизации")
    print("=" * 60)
    
    client = chromadb.PersistentClient(path="./chroma_db")
    collections = client.list_collections()
    
    if not collections:
        print("⚠️  База данных пуста")
        return
    
    print(f"\n✅ Найдено коллекций: {len(collections)}\n")
    
    for collection in collections:
        coll = client.get_collection(name=collection.name)
        count = coll.count()
        
        # Определяем ожидаемое количество
        expected = {
            "admin_manual": 6331,
            "user_manual": 855
        }
        
        exp_count = expected.get(collection.name, "?")
        progress = (count / exp_count * 100) if exp_count != "?" else 0
        
        print(f"📚 {collection.name}")
        print(f"   Документов: {count}/{exp_count}")
        if exp_count != "?":
            print(f"   Прогресс: {progress:.1f}%")
        
        # Показываем примеры метаданных
        sample = coll.peek(1)
        if sample['metadatas']:
            meta = sample['metadatas'][0]
            print(f"   Источник: {meta.get('source', '?')}")
            print(f"   Страниц обработано: {meta.get('page', '?')}/{meta.get('total_pages', '?')}")
        print()
    
    # Размер базы
    db_size = sum(f.stat().st_size for f in db_path.rglob('*') if f.is_file())
    db_size_mb = db_size / (1024 * 1024)
    print(f"💾 Размер базы: {db_size_mb:.1f} МБ")
    
    print("\n" + "=" * 60)
    print("✨ Готово к использованию!")
    print("\nПример запроса:")
    print("  python3 query_docs.py 'настройка пользователей'")

if __name__ == "__main__":
    check_status()
