import environ
from utils import *
from langchain_openai import AzureChatOpenAI

log = get_logger(__name__)

env = environ.Env()
environ.Env.read_env()

BASE_URL = f"https://{env('AZURE_RESOURCE_NAME', None)}.openai.azure.com/"
API_KEY = env('AZURE_API_KEY', None)
DEPLOYMENT_NAME = env('AZURE_DEPLOYMENT_NAME', None)

def AzureModel(max_tokens=2000, llm_model="gpt-4"):
  return AzureChatOpenAI(
            azure_endpoint=BASE_URL,
            openai_api_version="2023-05-15",
            deployment_name=DEPLOYMENT_NAME,
            openai_api_key=API_KEY,
            openai_api_type="azure",
            max_tokens=max_tokens,
            model_name=llm_model
        )   