import json
from pydantic import BaseModel
from typing import Type, Optional
from crewai.tools import BaseTool

from multi_agents.db.connector import MongoDBClient
from multi_agents.utils.logging import setup_logger
from multi_agents.config.schemas import CheckInventoryInput

logger = setup_logger()


class GetDetailTool(BaseTool):
    name: str = "Check inventory detail"
    description: str = (
        "Retrieves inventory details from storage based on the product. "
        "Input is a JSON string or object with product name, and optionally storage and color."
    )
    args_schema: Type[BaseModel] = CheckInventoryInput
    db_client: Optional[MongoDBClient] = None
    
    def __init__(self):
        super().__init__()
        try:
            self.db_client = MongoDBClient()
            logger.info("GetDetailTool initialized with MongoDB client")
        except Exception as e:
            logger.error(f"Failed to initialize MongoDB client: {str(e)}")
            self.db_client = None

    def _run(self, **kwargs) -> str:
        """
        Retrieves product details from inventory based on input.
        Args:
            **kwargs: Input arguments from CheckInventoryInput (e.g., product, storage, color).
        Returns:
            str: JSON string containing product details or error message.
        """
        try:
            if self.db_client is None:
                logger.error("MongoDB client not initialized")
                return json.dumps({"error": "Cannot connect to MongoDB database"})
            
            input_data = kwargs
            if not input_data.get("product"):
                return json.dumps({"error": "Product name is required"})

            product_name = input_data["product"]
            storage = input_data.get("storage")
            color = input_data.get("color")

            matching_products = self.db_client.get_products(
                product_name=product_name,
                storage=storage,
                color=color
            )

            if not matching_products:
                logger.warning(f"No product found for: {input_data}")
                return json.dumps({
                    "error": f"No product found matching product='{product_name}', "
                             f"storage='{storage or 'any'}', color='{color or 'any'}'"
                })

            result = {
                "status": "success",
                "products": matching_products
            }
            logger.debug(f"Found products: {result}")
            return json.dumps(result, ensure_ascii=False)

        except json.JSONDecodeError as e:
            logger.error(f"Error decoding inventory JSON: {str(e)}")
            return json.dumps({"error": f"Error decoding inventory JSON: {str(e)}"})
        except Exception as e:
            logger.error(f"Error in GetDetailTool: {str(e)}")
            return json.dumps({"error": f"Error retrieving product details: {str(e)}"})


if __name__ == "__main__":
    tool = GetDetailTool()
    input_data = {
        "product": "iPhone 15 Pro Max",
        "storage": "256GB",
        "color": "Titan tự nhiên"
    }
    result = tool._run(**input_data)
    print(result)