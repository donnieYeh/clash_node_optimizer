from typing import List, Dict, Any

def remove_invalid_nodes(proxies: List[Dict[str, Any]], invalid_node_names: List[str]) -> List[Dict[str, Any]]:
    """
    Remove proxies that match the invalid_node_names.
    
    Args:
    - proxies: List of proxy definitions.
    - invalid_node_names: List of proxy names to remove.

    Returns:
    - Updated list of proxies without the invalid nodes.
    """
    return [proxy for proxy in proxies if proxy['name'] not in invalid_node_names]
