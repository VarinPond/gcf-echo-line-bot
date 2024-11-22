import yaml
import os


# Load YAML and set environment variables
def load_yaml_to_env(yaml_file):
    try:
        with open(yaml_file, "r") as file:
            data = yaml.safe_load(file)
            if isinstance(data, dict):  # Ensure the YAML file has key-value pairs
                for key, value in data.items():
                    os.environ[key] = str(
                        value
                    )  # Convert all values to strings for the environment
                    # print(f"Set ENV {key} = {value}")
            else:
                print("Error: YAML content is not a valid dictionary.")
    except FileNotFoundError:
        print(f"Error: The file '{yaml_file}' was not found.")
    except yaml.YAMLError as exc:
        print(f"Error parsing YAML: {exc}")
