from openai import OpenAI
from loguru import logger
from typing import Dict, Optional

from multi_agents.config.settings import llm_config, Role


class BaseAgent:
    def __init__(
        self,
        llm: Optional[OpenAI] = None,
        system_prompt: Optional[str] = None,
        prompt_template: Optional[str] = None,
    ):
        if llm is None:
            llm = OpenAI(api_key=llm_config.api_key, base_url=llm_config.base_url)
        self.llm = llm
        self.system_prompt = system_prompt
        self.prompt_template = prompt_template

    def call_llm(self, prompt: str) -> dict:
        logger.info("=== Prompt ===")
        print(prompt)
        
        response = self.llm.chat.completions.create(
            seed=llm_config.seed,
            temperature=llm_config.temperature,
            top_p=llm_config.top_p,
            model=llm_config.model,
            messages=[
                {"role": Role.SYSTEM, "content": self.system_prompt},
                {"role": Role.USER, "content": prompt},
            ],
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content
        return content

    def process_input(self, input_data: str, context: Optional[Dict] = None) -> Dict:
        """Xử lý input và tạo prompt từ template."""
        prompt = self.prompt_template.format(input=input_data, context=context or {})
        return self.call_llm(prompt)

# if __name__ == "__main__":
#     agent = BaseAgent(
#         system_prompt="Bạn là một trợ lý bán hàng thông minh, trả lời câu hỏi khách hàng một cách thân thiện và chính xác.",
#         prompt_template="Khách hàng: {input}\nBối cảnh: {context}\nTrả lời:"
#     )
#     customer_input = "iPhone 13 còn hàng không? Giá bao nhiêu?"
#     context = {"conversation_id": "context_1", "khách_hàng": "Nguyễn Văn A", "sản_phẩm": "iPhone 13"}
#     result = agent.process_input(customer_input, context)
#     print(result)