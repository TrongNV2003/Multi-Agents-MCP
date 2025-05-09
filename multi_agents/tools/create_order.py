import os
import json
import time
from typing import Type
from pydantic import BaseModel
from crewai.tools import BaseTool

from multi_agents.config.schemas import CreateOrderInput

class CreateOrderTool(BaseTool):
    name: str = "Create order"
    description: str = "Saves order data to a file in the 'orders' subdirectory with a standardized format. Input is a JSON string from SaveOrderInput model."
    args_schema: Type[BaseModel] = CreateOrderInput
    
    def _run(self, order_details: str) -> str:
        """
        Saves the given order data (JSON string) to a file in the 'orders' subdirectory, with a standardized format.
        Returns a success message with the filename or an error message.
        Input is a JSON string from SaveOrderInput model.
        """
        try:
            orders_dir = "orders"
            if not os.path.exists(orders_dir):
                os.makedirs(orders_dir)

            input_data = json.loads(order_details) if isinstance(order_details, str) else order_details

            if not isinstance(input_data, dict):
                return f"Error: Input data is not a valid dictionary, received: {type(input_data)}"

            if "order_details" in input_data:
                input_data = input_data["order_details"]

            required_fields = ["order_id", "product", "quantity", "total_price", "customer_info"]
            missing_fields = [field for field in required_fields if field not in input_data]
            if missing_fields:
                return f"Error: Missing required fields: {', '.join(missing_fields)}"

            standard_order = {
                "order_details": {
                    "order_id": input_data.get("order_id", f"{int(time.time())}"),
                    "product": input_data.get("product", "Unknown Product"),
                    "quantity": input_data.get("quantity", 1),
                    "total_price": input_data.get("total_price", 0),
                    "customer_info": {
                        "customer_name": input_data.get("customer_info", {}).get("customer_name", "Guest"),
                        "conversation_id": input_data.get("customer_info", {}).get("conversation_id", f"{int(time.time())}")
                    }
                },
                "message": input_data.get("message", "Đơn hàng đã được tạo.")
            }

            order_id = standard_order["order_details"]["order_id"]
            conversation_id = standard_order["order_details"]["customer_info"]["conversation_id"]
            
            filename_base = f"order_{order_id}_{conversation_id}"
            filename = f"{filename_base}.json"
            filepath = os.path.join(orders_dir, filename)

            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(standard_order, f, ensure_ascii=False, indent=4)

            return f"Order data successfully saved to file: {filepath}"
        except json.JSONDecodeError as e:
            return f"Error decoding JSON data: {str(e)}"
        except Exception as e:
            return f"Error saving order to file: {str(e)}"
    
    
if __name__ == "__main__":
    tool = CreateOrderTool()
    input = {"order_details": {"order_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef", "product": "iPhone 15 Pro Max 256GB màu Titan tự nhiên", "quantity": 1, "total_price": 32990000, "customer_info": {"conversation_id": "12345", "customer_name": "Nguyễn Văn A", "previous_interactions": "Đã từng hỏi về iPad Air."}}, "message": ""}
    result = tool._run(json.dumps(input))
    print(result)
