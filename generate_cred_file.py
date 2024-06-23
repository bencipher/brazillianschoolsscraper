from configs.env_config import EnvironmentConfig

# Initialize environment configuration
dotenv_path = ".env"  # Adjust this path if your dotenv file is elsewhere
env_config = EnvironmentConfig(dotenv_path)


# Function to save credentials to file
def save_credentials_to_file(env_var_name, file_name):
    credentials_json = env_config.get_env_variable(env_var_name)
    if credentials_json:
        with open(file_name, 'w') as f:
            f.write(credentials_json)
        print(f"Credentials successfully saved to {file_name}")
    else:
        print(f"Error: Environment variable {env_var_name} not set or empty.")
