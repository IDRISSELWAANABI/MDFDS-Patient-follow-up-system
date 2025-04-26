import yaml

def read_config_file(file_path: str, BASE_CONFIG_FOLDER: str = "./config/") -> dict:
    """
    Reads a configuration file and returns its contents as a dictionary.

    Args:
        file_path (str): The path to the configuration file.

    Returns:
        dict: A dictionary containing the configuration settings.
    """
    file_path = BASE_CONFIG_FOLDER + file_path
    try:
        with open(file_path, 'r') as file:
            config = yaml.safe_load(file)
        return config
    except FileNotFoundError:
        print(f"Configuration file not found: {file_path}")
        return {}
    except yaml.YAMLError as e:
        print(f"Error parsing YAML file: {e}")
        return {}
    except Exception as e:
        print(f"An unexpected error occurred while reading from {file_path}: {e}")
        return {}
    
if __name__ == "__main__":
    # Example usage
    config = read_config_file("ollama_config.yaml")
    print(config)
    print(type((config)))
    print(config.get("url"))