from llm.base import BaseLLMModel
from utils.utils import process_json_format

class AdPerformanceSummary(BaseLLMModel):
    def __init__(self, system_prompt: str, model_name: str):
        super().__init__(model_name=model_name, system_role_instruction=system_prompt)

    async def generate_content(self, message: str):
        # message = self.model_router.prepare_message(
        #         message=message
        #     )
        # print(message)
        response = await self.model_router.async_completion(
            model=self.model_name,
            messages=self.model_router.prepare_message(
                message=message
            )
        )
        return process_json_format(response)