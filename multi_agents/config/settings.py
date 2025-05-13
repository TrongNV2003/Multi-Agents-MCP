from enum import Enum
from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

load_dotenv()

class LLMConfig(BaseSettings):
    gemini_api_key: str = Field(
        ...,
        description="API key for Gemini API",
        alias="GEMINI_API_KEY",
    )
    gemini_model: str = Field(
        default="gemini/gemini-1.5-flash",
        description="Model name to be used (e.g., Gemini-1.5)",
        alias="GEMINI_MODEL",
    )
    temperature: float = Field(
        default=0.0,
        description="Sampling temperature; higher values make output more random",
        alias="TEMPERATURE",
    )
    max_tokens: int = Field(
        default=512,
        alias="MAX_TOKENS",
        description="Maximum number of tokens for API responses",
    )
    top_p: float = Field(
        default=0.95,
        alias="TOP_P",
        description="Nucleus sampling parameter; higher values increase randomness",
    )
    seed: int = Field(default=42, alias="SEED", description="Random seed for sampling")


class MCPConfig(BaseSettings):
    mcp_url: str = Field(
        default="http://localhost:8000/sse",
        description="Base URL for MCP API",
        alias="MCP_SERVER_BASE_URL",
    )


class MongodbConfig(BaseSettings):
    mongo_uri: str = Field(
        default="mongodb://localhost:27017",
        description="MongoDB connection URI",
    )
    db_name: str = Field(
        default="inventory",
        description="Database name for MongoDB",
    )


class Role(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


llm_config = LLMConfig()
mcp_config = MCPConfig()
db_config = MongodbConfig()
