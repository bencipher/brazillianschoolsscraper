from dotenv import load_dotenv
import os


class EnvironmentConfig:
    def __init__(self, dotenv_path):
        self.dotenv_path = dotenv_path
        self.loaded = False

    def load_env(self):
        if not self.loaded:
            load_dotenv(self.dotenv_path)
            self.loaded = True

    def get_env_variable(self, key):
        self.load_env()
        print('loading {key=}')
        return os.getenv(key)
