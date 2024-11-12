import argparse
from .main import process_config

def main():
    parser = argparse.ArgumentParser(description="Optimize Clash proxy configuration.")
    parser.add_argument('--config', type=str, required=True, help="Path to the input config YAML file.")
    parser.add_argument('--output', type=str, default='config.new.yaml', help="Path to save the optimized YAML file.")
    args = parser.parse_args()

    # 处理配置文件
    process_config(args.config, args.output)
