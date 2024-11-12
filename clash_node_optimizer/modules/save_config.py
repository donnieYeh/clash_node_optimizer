import yaml
from typing import Dict, Any


class _Proxy(dict):
    """用于标记 proxies 节点的特殊类型"""

    pass


class _CompactDumper(yaml.SafeDumper):
    def represent_proxies(self, data):
        # 在此处对 Proxies 类型的数据应用紧凑格式
        return self.represent_mapping("tag:yaml.org,2002:map", data, flow_style=True)


# 为 Proxies 类型注册紧凑表示
_CompactDumper.add_representer(_Proxy, _CompactDumper.represent_proxies)


def save_config(config_data: Dict[str, Any], output_path: str = "xxx.new.yaml"):
    """
    Save the configuration data to a YAML file, applying compact format only to the /proxies node.

    Args:
    - config_data: The processed configuration dictionary.
    - output_path: Path to save the new YAML file.
    """
    # 手动将 /proxies 节点转换为 Proxies 类型，其他节点保持不变
    if "proxies" in config_data:
        for index, proxy in enumerate(config_data["proxies"]):
            # if len(proxy) < 8:
            config_data["proxies"][index] = _Proxy(proxy)

    with open(output_path, "w", encoding="utf-8") as file:
        yaml.dump(
            config_data,
            file,
            Dumper=_CompactDumper,
            allow_unicode=True,
            width=1000,
            sort_keys=False,
        )
