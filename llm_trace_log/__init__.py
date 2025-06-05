from .log import LangfuseClient
from config import config

langfuse_client = LangfuseClient(config["langfuse"]["host"])