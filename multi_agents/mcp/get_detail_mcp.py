import json
import asyncio
from typing import Type
from mcp import ClientSession
from pydantic import BaseModel
from crewai.tools import BaseTool
from mcp.client.sse import sse_client

from multi_agents.config.schemas import CheckInventoryInput


class GetDetailTool(BaseTool):
    name: str = "Check inventory detail"
    description: str = (
        "Retrieves inventory details from storage based on the product. "
        "Input is a JSON string or object with product name, and optionally storage and color."
    )
    args_schema: Type[BaseModel] = CheckInventoryInput

    async def _arun(self, **kwargs) -> str:
        async with sse_client(url="http://localhost:8000/sse") as streams:
            async with ClientSession(*streams) as session:
                await session.initialize()
                try:
                    result = await session.call_tool("get_product_info", kwargs)
                    return result
                except Exception as e:
                    return json.dumps({"error": f"Failed to retrieve product info: {str(e)}", "status": "error"})

    def _run(self, **kwargs) -> str:
        return asyncio.run(self._arun(**kwargs))

if __name__ == "__main__":
    tool = GetDetailTool()
    input_data = {
        "product": "iPhone 15 Pro Max",
        "storage": "256GB",
        "color": "Titan tự nhiên"
    }
    result = tool._run(**input_data)
    print(result)