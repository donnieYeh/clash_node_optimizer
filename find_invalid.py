from typing import List, Dict, Any, Callable

def find_invalid_nodes(proxies: List[Dict[str, Any]], criteria: Callable[[Dict[str, Any]], bool]) -> List[str]:
    """
    Find nodes in proxies that match a given criteria.
    
    Args:
    - proxies: List of proxies from the config file.
    - criteria: A function that takes a proxy and returns True if it's invalid.

    Returns:
    - List of invalid proxy names.
    """
    invalid_nodes = [proxy['name'] for proxy in proxies if criteria(proxy)]
    return invalid_nodes
