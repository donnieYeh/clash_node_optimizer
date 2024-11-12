# 打包
python setup.py sdist bdist_wheel

# 安装本地包
pip install .

# 使用
```python
from clash_node_optimizer import (
    find_invalid_nodes,
    remove_invalid_nodes,
    clean_proxy_groups,
    fill_empty_groups,
    save_config
)
```

# 命令行执行
```
clash-node-optimizer --config config.yaml --output config.new.yaml
```