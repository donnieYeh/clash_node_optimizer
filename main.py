import yaml
import copy
from find_invalid import find_invalid_nodes
from remove_invalid import remove_invalid_nodes
from clean_groups import clean_proxy_groups
from fill_groups import fill_empty_groups
from save_config import save_config
from typing import Dict, Any

def process_config(config_data: Dict[str, Any], output_path: str = 'config.new.yaml'):
    """
    Process the Clash configuration file based on the requirements and save the output.
    
    Args:
    - config_data: Original configuration data loaded from YAML.
    - output_path: Path to save the processed configuration.
    """
    # Step 1: Find invalid nodes based on 'cipher' == 'ss'
    invalid_criteria = lambda x: x.get('cipher') == 'ss'
    invalid_nodes = find_invalid_nodes(config_data.get('proxies', []), invalid_criteria)

    # Step 2: Remove invalid nodes from proxies
    updated_proxies = remove_invalid_nodes(config_data.get('proxies', []), invalid_nodes)
    
    # Step 3: Clean invalid nodes from proxy groups
    updated_proxy_groups = clean_proxy_groups(config_data.get('proxy-groups', []), invalid_nodes)
    
    # Step 4: Fill any empty proxy groups
    updated_proxy_groups = fill_empty_groups(updated_proxy_groups, updated_proxies)
    
    # Update config with the modified proxies and proxy groups
    new_config = copy.deepcopy(config_data)
    new_config['proxies'] = updated_proxies
    new_config['proxy-groups'] = updated_proxy_groups
    
    # Step 5: Save the updated config to file
    save_config(new_config, output_path)

# Load the configuration file
with open('config.yaml', 'r', encoding='utf-8') as file:
    config_data = yaml.safe_load(file)

# Process and save the new configuration
process_config(config_data)
