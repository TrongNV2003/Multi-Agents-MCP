from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from typing import List, Dict, Any, Optional

from multi_agents.config.settings import db_config
from multi_agents.utils.logging import setup_logger

logger = setup_logger()

class MongoDBClient:
    def __init__(self, uri: str = db_config.mongo_uri, db_name: str = db_config.db_name):
        """
        Initialize MongoDB client.
        Args:
            uri (str): MongoDB connection URI.
            db_name (str): Database name.
        """
        try:
            self.client = MongoClient(uri)
            self.db = self.client[db_name]

            self.client.admin.command("ping")
            logger.info(f"Connected to MongoDB at {uri}, database: {db_name}")
        except ConnectionFailure as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            raise

    def insert_product(self, product: Dict[str, Any]) -> str:
        """
        Insert a product into MongoDB.

        Args:
            product (Dict[str, Any]): Product data to insert.

        Returns:
            str: Inserted product ID.
        """
        try:
            required_fields = ["product_id", "product", "storage", "color", "price", "quantity"]
            missing_fields = [field for field in required_fields if field not in product]
            if missing_fields:
                raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

            result = self.db.products.insert_one(product)
            logger.info(f"Inserted product with ID: {result.inserted_id}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error inserting product: {str(e)}")
            raise

    def get_products(
        self,
        product_name: str,
        storage: Optional[str] = None,
        color: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve products from MongoDB based on name, storage, and color.

        Args:
            product_name (str): Name of the product (case-insensitive).
            storage (Optional[str]): Storage capacity (e.g., '256GB').
            color (Optional[str]): Color of the product (e.g., 'Titan tự nhiên').

        Returns:
            List[Dict[str, Any]]: List of matching products.
        """
        try:
            query = {"product": {"$regex": product_name, "$options": "i"}}
            if storage:
                query["storage"] = {"$regex": storage, "$options": "i"}
            if color:
                query["color"] = {"$regex": color, "$options": "i"}

            products = self.db.products.find(query)
            result = []
            for product in products:
                if "_id" in product:
                    product["_id"] = str(product["_id"])
                result.append(product)
            logger.debug(f"Query: {query}, Found: {len(result)} products")
            return result
        except Exception as e:
            logger.error(f"Error querying products: {str(e)}")
            raise
