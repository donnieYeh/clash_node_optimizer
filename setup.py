from setuptools import setup, find_packages

setup(
    name="clash_node_optimizer",
    version="1.0.0",
    description="A utility to optimize Clash proxy configuration",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(where="."),  # 自动查找包
    install_requires=[
        "pyyaml"
    ],
    entry_points={
        'console_scripts': [
            'clash-node-optimizer=clash_node_optimizer.cli:main',  # 指向 cli.py 的 main 函数
        ]
    }
)
