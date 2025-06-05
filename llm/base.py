from llm.llm_model_router import LLMModelRouter
from typing import List
from config import config

class BaseLLMModel():
    def __init__(self, model_name:str, system_role_instruction: str="") -> None:
        self.model_name = model_name
        self.model_router = LLMModelRouter(
            host=config["litellm"]["host"],
            api_key=config["litellm"]["api_key"],
            system_role_instruction=system_role_instruction
        )
    
    def generate_content(self, contents, generation_name: str, list_image_uris: List[str]=[], list_audio_uris: List[str]=[]) -> str:
        raise ValueError("Method not implemented")
