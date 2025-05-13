import json
import asyncio
from typing import Type
from loguru import logger
from mcp import ClientSession
from pydantic import BaseModel
from crewai.tools import BaseTool
from mcp.client.sse import sse_client

from multi_agents.config.schemas import CreateOrderInput


class CreateOrderTool(BaseTool):
    name: str = "Create order"
    description: str = "Saves order data to a file in the 'orders' subdirectory with a standardized format. Input is a JSON string from SaveOrderInput model."
    args_schema: Type[BaseModel] = CreateOrderInput

    async def _arun(self, order_details: str) -> str:
        async with sse_client(url="http://localhost:8000/sse") as streams:
            async with ClientSession(*streams) as session:
                await session.initialize()
                try:
                    logger.debug(f"Sending order_details : {order_details} (type: {type(order_details)})")

                    result = await session.call_tool("create_order", {"order_details": order_details})
                    return str(result) if result is not None else "Error: No result from server"
                except Exception as e:
                    logger.error(f"Error creating order: {str(e)}")
                    return f"Error creating order: {str(e)}"

    def _run(self, order_details: str) -> str:
        return asyncio.run(self._arun(order_details))
    
if __name__ == "__main__":
    tool = CreateOrderTool()
    input = {"order_details": {"order_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef", "product": "iPhone 15 Pro Max", "color": "Black", "storage": "256GB", "quantity": 1, "total_price": 32990000, "customer_info": {"conversation_id": "12345", "customer_name": "Nguyễn Văn A", "previous_interactions": "Đã từng hỏi về iPad Air."}}, "message": ""}
    result = tool._run(json.dumps(input))
    print(result)