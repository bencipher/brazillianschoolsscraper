from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.embeddings import HuggingFaceInstructEmbeddings

from configs.env_config import EnvironmentConfig


class GoogleGenerativeAIService:
    def __init__(self, env_config: EnvironmentConfig):
        self.env_config = env_config
        self.google_api_key = None
        self.llm_instance = None
        self.huggingface_embeddings = None
        self.initialize()

    def initialize(self):
        self.huggingface_embeddings = HuggingFaceInstructEmbeddings(model_name="hkunlp/instructor-large")
        self.google_api_key = self.env_config.get_env_variable('GEMINI_API_KEY')
        self.llm_instance = ChatGoogleGenerativeAI(model="gemini-1.5-pro", google_api_key=self.google_api_key)

    def get_llm_instance(self):
        if not self.llm_instance:
            self.initialize()
        return self.llm_instance

    def get_huggingface_embeddings(self):
        if not self.huggingface_embeddings:
            self.initialize()
        return self.huggingface_embeddings
