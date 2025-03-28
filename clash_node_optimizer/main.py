import yaml
import copy
import re  # 导入正则表达式模块
import html  # 导入html模块
from .modules.find_invalid import find_invalid_nodes
from .modules.remove_invalid import remove_invalid_nodes
from .modules.clean_groups import clean_proxy_groups
from .modules.fill_groups import fill_empty_groups
from .modules.save_config import save_config

def process_config(config_path: str, output_path: str = 'config.new.yaml'):
    with open(config_path, 'r', encoding='utf-8') as file:
        config_data = file.read()
    
    # 使用正则表达式去除HTML标签
    config_data = re.sub(r'<[^>]+>', '', config_data)

    # 解码HTML转义字符
    config_data = html.unescape(config_data)

    # 删除包含HTML标签的行
    config_lines = config_data.split('\n')
    config_lines = [line for line in config_lines if not re.search(r'<[^>]+>', line)]
    config_data = '\n'.join(config_lines)

    # 加载去除HTML标签后的yaml内容
    config_data = yaml.safe_load(config_data)

    invalid_criteria = lambda x: x.get('cipher') == 'ss'
    invalid_nodes = find_invalid_nodes(config_data.get('proxies', []), invalid_criteria)
    updated_proxies = remove_invalid_nodes(config_data.get('proxies', []), invalid_nodes)
    updated_proxy_groups = clean_proxy_groups(config_data.get('proxy-groups', []), updated_proxies, invalid_nodes)
    updated_proxy_groups = fill_empty_groups(updated_proxy_groups, updated_proxies)
    
    new_config = copy.deepcopy(config_data)
    new_config['proxies'] = updated_proxies
    new_config['proxy-groups'] = updated_proxy_groups
    save_config(new_config, output_path)