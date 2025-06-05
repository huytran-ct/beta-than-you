from langfuse.decorators import langfuse_context
from llm_trace_log.base import LangFuseGenerationDataModel, LangFuseSpanDataModel
from threading import Lock
from langfuse import Langfuse
from langfuse.model import PromptClient

import os

class SingletonMeta(type):
    _instances = {}
    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]

class LangfuseClient(metaclass=SingletonMeta):
    def __init__(self, langfuse_host: str="http://localhost:3000", 
                 langfuse_public_key: str="", 
                 langfuse_secret_key: str=""):
        if "LANGFUSE_PUBLIC_KEY" not in os.environ:
            os.environ["LANGFUSE_PUBLIC_KEY"] = langfuse_public_key
        if "LANGFUSE_SECRET_KEY" not in os.environ:
            os.environ["LANGFUSE_SECRET_KEY"] = langfuse_secret_key
        if "LANGFUSE_HOST" not in os.environ:
            os.environ["LANGFUSE_HOST"] = langfuse_host

        self._langfuse = Langfuse()

    @classmethod
    def update_trace_metadata(self, data: LangFuseGenerationDataModel):
        langfuse_context.update_current_trace(metadata=data.metadata)

    @classmethod
    def update_trace_input_output(self, data: LangFuseGenerationDataModel):
        langfuse_context.update_current_trace(input=data.input, output=data.output, tags=data.tag, user_id=data.user_id)

    @classmethod
    def update_generation_observation(self, data: LangFuseGenerationDataModel):
        if data.metadata is not None:
            langfuse_context.update_current_trace(tags=data.tag, metadata=data.metadata)
        else:
            langfuse_context.update_current_trace(tags=data.tag)
        langfuse_context.update_current_observation(usage=data.usage, 
                                                    model=data.model,
                                                    input=data.input,
                                                    output=data.output,
                                                    name=data.name)
    
    @classmethod
    def update_span_observation(self, data: LangFuseSpanDataModel):
        if data.metadata is not None:
            langfuse_context.update_current_trace(tags=data.tag, metadata=data.metadata)
        else:
            langfuse_context.update_current_trace(tags=data.tag)
        langfuse_context.update_current_observation(input=data.input,
                                                    output=data.output,
                                                    tags=data.tag)
        
    def get_prompt(self, name: str, version: int=None) -> PromptClient:
        if not version:
            return self._langfuse.get_prompt(name, label="latest")
        else:
            return self._langfuse.get_prompt(name, version)
        