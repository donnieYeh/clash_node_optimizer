import yaml
import copy
from .modules.find_invalid import find_invalid_nodes
from .modules.remove_invalid import remove_invalid_nodes
from .modules.clean_groups import clean_proxy_groups
from .modules.fill_groups import fill_empty_groups
from .modules.save_config import save_config

def process_config(config_path: str, output_path: str = 'config.new.yaml'):
    with open(config_path, 'r', encoding='utf-8') as file:
        config_data = yaml.safe_load(file)

    invalid_criteria = lambda x: x.get('cipher') == 'ss'
    invalid_nodes = find_invalid_nodes(config_data.get('proxies', []), invalid_criteria)
    updated_proxies = remove_invalid_nodes(config_data.get('proxies', []), invalid_nodes)
    updated_proxy_groups = clean_proxy_groups(config_data.get('proxy-groups', []), updated_proxies, invalid_nodes)
    updated_proxy_groups = fill_empty_groups(updated_proxy_groups, updated_proxies)
    
    new_config = copy.deepcopy(config_data)
    new_config['proxies'] = updated_proxies
    new_config['proxy-groups'] = updated_proxy_groups
    save_config(new_config, output_path)
