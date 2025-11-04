from crewai import Agent, LLM

from multi_agents.config.settings import api_config


class ConsultantAgent:
    def __init__(self, tools=None):
        self.llm = LLM(
            model="openai/Qwen/Qwen3-8B",
            base_url=api_config.base_url_llm,
            api_key=api_config.api_key,
            temperature=0.5,
        )
        
        self.crewai_agent = Agent(
            role="Tư vấn khách hàng",
            goal="Trả lời câu hỏi khách hàng và cung cấp thông tin sản phẩm",
            backstory="Bạn là một trợ lý bán hàng tận tâm, luôn hỗ trợ khách hàng tốt nhất.",
            llm=self.llm,
            tools=tools or [],
            verbose=True,
        )

class InventoryAgent:
    def __init__(self, tools=None):
        self.llm = LLM(
            model="openai/Qwen/Qwen3-8B",
            base_url=api_config.base_url_llm,
            api_key=api_config.api_key,
            temperature=0.5,
        )
        
        self.crewai_agent = Agent(
            role="Kiểm tra kho",
            goal="Kiểm tra tồn kho và giá sản phẩm",
            backstory="Bạn là chuyên viên quản lý kho, cung cấp thông tin chính xác về tồn kho.",
            llm=self.llm,
            tools=tools or [],
            verbose=True
        )

class OrderAgent:
    def __init__(self, tools=None):
        self.llm = LLM(
            model="openai/Qwen/Qwen3-8B",
            base_url=api_config.base_url_llm,
            api_key=api_config.api_key,
            temperature=0.5,
        )
        
        self.crewai_agent = Agent(
            role="Lên đơn hàng",
            goal="Tạo đơn hàng dựa trên yêu cầu khách hàng",
            backstory="Bạn xử lý đơn hàng nhanh chóng và chính xác.",
            llm=self.llm,
            tools=tools or [],
            verbose=True
        )
