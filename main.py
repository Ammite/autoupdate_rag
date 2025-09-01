import requests
import config
import chromadb
from chromadb.utils import embedding_functions

# 🔹 API с товарами (замени на свой)
API_URL = "https://loshadka.tomsk.ru/wp-json/wc/v3/products"

# 🔹 Chroma клиент (локально или через chromadb-server)
chroma_client = chromadb.PersistentClient(path="./chroma_db")

# 🔹 Создаем/получаем коллекцию
collection = chroma_client.get_or_create_collection(
    name="products",
    embedding_function=embedding_functions.DefaultEmbeddingFunction()
)

def fetch_products():
    """Получаем товары из API"""
    response = requests.get(API_URL, timeout=10)
    response.raise_for_status()
    return response.json()  # список словарей

def update_chroma():
    """Обновляем товары в Chroma"""
    products = fetch_products()
    ids, docs, metas = [], [], []

    for product in products:
        ids.append(str(product["id"]))  # id товара как уникальный ключ
        docs.append(product["name"])    # векторизуем название
        metas.append({
            "url": product.get("link"),
            "price": product.get("price"),
            "name": product["name"]
        })

    collection.upsert(
        ids=ids,
        documents=docs,
        metadatas=metas
    )

    print(f"✅ Обновлено {len(products)} товаров в Chroma")

if __name__ == "__main__":
    update_chroma()
