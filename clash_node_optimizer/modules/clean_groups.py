from typing import List, Dict, Any
import copy

def clean_proxy_groups(proxy_groups: List[Dict[str, Any]], proxies: List[Dict[str, Any]], invalid_node_names: List[str]) -> List[Dict[str, Any]]:
    """
    Clean each proxy group by removing invalid nodes and nodes not in proxies.
    
    Args:
    - proxy_groups: List of proxy groups from the config.
    - proxies: List of all proxies to determine valid nodes.
    - invalid_node_names: List of invalid proxy names to remove from groups.

    Returns:
    - Updated list of proxy groups.
    """
    # Determine valid node names from proxies
    valid_node_names = [proxy['name'] for proxy in proxies]
    
    # Clean each group
    updated_groups = copy.deepcopy(proxy_groups)
    for group in updated_groups:
        group['proxies'] = [
            proxy for proxy in group['proxies'] 
            if proxy not in invalid_node_names and proxy in valid_node_names
        ]
    return updated_groups
