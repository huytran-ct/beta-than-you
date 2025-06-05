from llm.llm_model import AdPerformanceSummary
from llm.llm_config import LLMModels

ad_performance_prompt = """You are an expert in analyzing ad performance data. Your task is to summarize the performance of a specific ad based on the provided data. 
The data includes ad ID, title, body, date, and adview count. Provide a concise summary highlighting key performance metrics and trends and give suggestions for improvement if applicable. The response should be in JSON format with the following keys:
{"performance_insight": "string", "suggestions": []}
- performance_insight: A brief summary of the ad's performance. Should be less than 100 character, concrete and easy to understand.
- suggestions: A list of actionable suggestions to improve ad performance. Each suggesttion should be less than 100 character, concrete and easy to understand, call to action.
The result should be written by Vietnamese language. Use the normal tone, not too formal, and avoid using technical terms, friendly and easy to understand for the user.
"""


LLM_MODELS = {
    "ad_performance_summary": AdPerformanceSummary(system_prompt=ad_performance_prompt, model_name=LLMModels.VERTEXAI_GEMINI_15_FLASH.value.lower())}

def get_llm_model(model_name: str):
    """
    Factory function to get the LLM model instance based on the model name.
    """
    if model_name in LLM_MODELS:
        return LLM_MODELS[model_name]
    else:
        raise ValueError(f"Model {model_name} is not supported.")