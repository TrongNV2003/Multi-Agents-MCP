import json
from multi_agents.db.connector import MongoDBClient


def init_mongodb(data_path: str):
    with open(data_path, "r", encoding="utf-8") as f:
        products = json.load(f)
    try:
        db_client = MongoDBClient()
        for product in products:
            try:
                db_client.insert_product(product)
                print(f"Inserted: {product['product']}")
            except ValueError as e:
                print(f"Skipping {product['product']}: {str(e)}")
    except Exception as e:
        print(f"Error initializing MongoDB: {str(e)}")


if __name__ == "__main__":
    data_path = "storage/inventory.json"
    init_mongodb(data_path)