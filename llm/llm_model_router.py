from typing import List, Dict
from config import config
from dotenv import load_dotenv


import openai
import asyncio
import os

load_dotenv()  # Load environment variables from .env file
LITELLM_API_KEY = os.getenv("LITELLM_API_KEY", "")


class LLMModelRouter:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(LLMModelRouter, cls).__new__(cls)
        return cls._instance

    def __init__(self, host: str, api_key: str, system_role_instruction: str = ""):
        if not hasattr(self, 'initialized'):
            self.router = openai.AsyncOpenAI(
                # base_url=host,
                # api_key=api_key
            )
            self.system_role_instruction = system_role_instruction
            self.initialized = True

    def prepare_message(self, message: str = "") -> List[Dict[str, str]]:
        messages = []
        if self.system_role_instruction is not None and self.system_role_instruction != "":
            messages.append({"role": "system", "content": self.system_role_instruction})
        messages.append({"role": "user", "content": message})
        return messages

    async def async_completion(self, model: str, messages: List[Dict[str, str]] = [], safety_settings: Dict = {}) -> str:
        if safety_settings != {}:
            response = await self.router.chat.completions.create(model=model, 
                                                                 messages=messages, 
                                                                 safety_settings=safety_settings)
       
        else:
            response = await self.router.chat.completions.create(model=model, messages=messages)
        return response.choices[0].message.content if response.choices else ""


if __name__ == "__main__":
    from llm.llm_config import LLMModels
    import json

    ad_performance_prompt = """Bạn là một chuyên gia trong việc phân tích dữ liệu hiệu quả quảng cáo. Nhiệm vụ của bạn là tóm tắt hiệu suất của một quảng cáo cụ thể dựa trên dữ liệu được cung cấp.
Dữ liệu bao gồm ID quảng cáo, tiêu đề, nội dung, ngày chạy và số lượt xem quảng cáo.
Hãy đưa ra một bản tóm tắt ngắn gọn nêu bật các chỉ số quan trọng và xu hướng, đồng thời đưa ra gợi ý cải thiện nếu cần.
Phản hồi nên ở định dạng JSON:
{"performance_insight": "string", "suggestions": []}
- performance_insight: Một đoạn tóm tắt ngắn gọn về hiệu suất quảng cáo.
- suggestions: Danh sách các gợi ý cụ thể để cải thiện hiệu quả quảng cáo.
Kết quả cần được viết bằng tiếng Việt, giọng văn tự nhiên, không quá trang trọng và tránh dùng các thuật ngữ kỹ thuật. Cách viết nên thân thiện và dễ hiểu với người dùng.
"""
    executor = LLMModelRouter(
            host=config["litellm"]["host"],
            api_key=config["litellm"]["api_key"], 
            system_role_instruction=ad_performance_prompt
        )
    
    ad = {"id": 168007238, "title": "\\u0110\\u1ea5t th\\u1ed5 c\\u01b0 122m2 MT \\u0111\\u01b0\\u1eddng 10m B\\u1ea1ch Mai, \\u0110\\u1ed3ng Th\\u00e1i 2,8 t\\u1ef7", "body": "C\\u1ea7n b\\u00e1n m\\u1ea3nh \\u0111\\u1ea5t \\u0111\\u1eb9p 122m2 ngang 5m d\\u00e0i 20,4m, full th\\u1ed5 c\\u01b0 t\\u1ea1i th\\u00f4n B\\u1ea1ch Mai, x\\u00e3 \\u0110\\u1ed3ng Th\\u00e1i, An D\\u01b0\\u01a1ng, H\\u1ea3i Ph\\u00f2ng.\\n\\u0110\\u1ea5t thu\\u1ed9c khu ph\\u00e2n l\\u00f4, \\u0110\\u01b0\\u1eddng tr\\u01b0\\u1edbc \\u0111\\u1ea5t r\\u1ed9ng 10m, c\\u1ea3 v\\u1ec9a h\\u00e8. Khu v\\u1ef1c \\u0111ang x\\u00e2y d\\u1ef1ng m\\u1ea1nh, d\\u00e2n c\\u01b0 v\\u1ec1 \\u1edf ng\\u00e0y m\\u1ed9t \\u0111\\u00f4ng \\u0111\\u00fac, g\\u1ea7n \\u0110\\u01b0\\u1eddng An Kim H\\u1ea3i, g\\u1ea7n ch\\u1ee3 An \\u0110\\u1ed3ng, g\\u1ea7n ch\\u00f9a B\\u1ee5t M\\u1ecdc, c\\u00e1ch PG An \\u0110\\u1ed3ng ch\\u1ec9 h\\u01a1n 1km. \\nXung quanh nhi\\u1ec1u ti\\u1ec7n \\u00edch, khu nh\\u00e0 \\u1edf d\\u00e2n \\u0111\\u00e3 x\\u00e2y k\\u00edn, an ninh an to\\u00e0n, h\\u00e0ng x\\u00f3m th\\u00e2n thi\\u1ec7n.\\n\\u0110\\u1ea5t \\u0111\\u00e3 c\\u00f3 s\\u1ed5 \\u0111\\u1ecf ri\\u00eang, mua b\\u00e1n sang t\\u00ean ngay.\\nGi\\u00e1 b\\u00e1n 23 tri\\u1ec7u \\u0111\\u1ed3ng/1m2 t\\u1ea7m 2,8 t\\u1ef7 \\u0111\\u1ed3ng, c\\u00f3 th\\u01b0\\u01a1ng l\\u01b0\\u1ee3ng.", "category": 1040, "price": 22950820.0, "location": "Unknown", "postedDate": "Unknown", "image": "/default-image.png", "clicks": 0, "spend": 0.0, "qualifiedCriteria": 0, "totalCriteria": 5, "criteriaDetails": {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5}, "status": "Active", "performanceData": []}
    message = executor.prepare_message(message=json.dumps(ad))
    response = asyncio.run(
        executor.async_completion(model=LLMModels.VERTEXAI_GEMINI_15_FLASH.value.lower(), messages=message)
    )
    print(response)