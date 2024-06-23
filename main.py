from generate_cred_file import save_credentials_to_file, env_config
from recommend import start_app


def main():
    env_config.load_env()
    env_var_name = "FIREBASE_CREDENTIALS_JSON"
    file_name = "service_account_key.json"
    save_credentials_to_file(env_var_name, file_name)
    start_app()


if __name__ == '__main__':
    main()
