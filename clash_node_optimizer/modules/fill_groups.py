from typing import List, Dict, Any

def fill_empty_groups(proxy_groups: List[Dict[str, Any]], proxies: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Fill any empty proxy group with the first available proxy.
    
    Args:
    - proxy_groups: List of proxy groups from the config.
    - proxies: List of all proxies to get a fallback proxy.

    Returns:
    - List of updated proxy groups.
    """
    if not proxies:
        return proxy_groups  # No proxies available, return groups as is
    
    default_proxy = proxies[0]['name']
    for group in proxy_groups:
        if not group['proxies']:  # Fill group if empty
            group['proxies'].append(default_proxy)
    return proxy_groups
