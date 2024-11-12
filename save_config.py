import yaml
from typing import Dict, Any

def save_config(config_data: Dict[str, Any], output_path: str = 'xxx.new.yaml'):
    """
    Save the configuration data to a YAML file.
    
    Args:
    - config_data: The processed configuration dictionary.
    - output_path: Path to save the new YAML file.
    """
    with open(output_path, 'w', encoding='utf-8') as file:
        yaml.dump(config_data, file, allow_unicode=True)
