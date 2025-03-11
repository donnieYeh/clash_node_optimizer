import configparser
from flask import Blueprint, Flask, request, jsonify, send_file, send_from_directory

import sys
# 计算项目的根目录路径
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)  # 添加根目录到 sys.path

from clash_node_optimizer import process_config
from werkzeug.middleware.proxy_fix import ProxyFix
import os
import requests
import tempfile
import threading
import hashlib
import json
from datetime import datetime

# 读取配置文件
config = configparser.ConfigParser()
PROPERTIES_DIR = os.path.join(os.path.dirname(__file__), "config.properties")
config.read(PROPERTIES_DIR)
port = int(config.get("DEFAULT", "web_service_port", fallback="5000"))

app = Flask(__name__, static_folder="static")

# 创建蓝图
cno = Blueprint("cno", __name__, static_folder="static", static_url_path="/static")

# 添加 ProxyFix 中间件来处理代理头信息
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1)

# 缓存目录，存放于 /web_service/cache
CACHE_DIR = os.path.join(os.path.dirname(__file__), "cache")
os.makedirs(CACHE_DIR, exist_ok=True)

# 全局变量，用于存储进度信息
progress = {"status": "idle", "percent": 0}
output_filename = None  # 存储结果文件路径


def get_file_key(content: bytes) -> str:
    """
    生成内容的 MD5 哈希值作为唯一标识
    """
    return hashlib.md5(content).hexdigest()


def get_cached_file(file_key: str) -> str:
    """
    检查缓存目录中是否有已解析的文件
    """
    cached_path = os.path.join(CACHE_DIR, f"{file_key}.yaml")
    return cached_path if os.path.exists(cached_path) else None


def save_cache_info(file_key: str, file_path: str, source: str):
    """
    保存缓存文件的信息到缓存目录
    """
    cache_info = {
        "key": file_key,
        "path": file_path,
        "source": source,  # 数据来源
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    # 读取现有缓存信息
    cache_file_path = os.path.join(CACHE_DIR, "cache_info.json")
    cache_list = []
    if os.path.exists(cache_file_path):
        with open(cache_file_path, "r") as f:
            cache_list = json.load(f)

    # 添加新缓存项
    cache_list.append(cache_info)

    # 写回到 JSON 文件
    with open(cache_file_path, "w") as f:
        json.dump(cache_list, f, indent=4)


@cno.route("/")
def index():
    """
    返回前端 HTML 页面
    """
    return send_from_directory(cno.static_folder, "index.html")


@cno.route("/upload", methods=["POST"])
def upload():
    global progress, output_filename
    config_source = request.form.get("config_source")
    progress = {"status": "idle", "percent": 0}  # 重置进度条

    # 获取唯一文件标识
    if config_source == "url":
        config_url = request.form.get("config_url")
        if not config_url:
            return jsonify({"error": "URL is required"}), 400
        response = requests.get(config_url)
        if response.status_code != 200:
            return jsonify({"error": "Failed to fetch the file from URL"}), 400
        file_content = response.content
        source = config_url  # 数据来源为 URL
    elif config_source == "file":
        config_file = request.files.get("config_file")
        if not config_file:
            return jsonify({"error": "File is required"}), 400
        file_content = config_file.read()
        source = config_file.filename  # 数据来源为文件名
    else:
        return jsonify({"error": "Invalid config source"}), 400

    file_key = get_file_key(file_content)  # 生成文件的唯一 key
    cached_file = get_cached_file(file_key)

    # 如果缓存文件已存在，则立即返回并更新进度条
    if cached_file:
        progress["status"] = "File already processed, loading from cache"
        progress["percent"] = 100
        return jsonify({"message": "File already processed", "new_file": False}), 200

    # 如果缓存文件不存在，则继续处理
    with tempfile.NamedTemporaryFile(delete=False, suffix=".yaml") as temp_config_file:
        temp_filename = temp_config_file.name
        temp_config_file.write(file_content)

    output_filename = os.path.join(CACHE_DIR, f"{file_key}.yaml")

    # 启动一个新线程执行处理和缓存
    def process_and_cache_file():
        global progress
        try:
            progress["status"] = "wait latency test finish"
            progress["percent"] = 30
            # 直到latencyTestResults非NONE时，才推进进度

            progress["status"] = "Processing configuration"
            progress["percent"] = 60

            process_config(temp_filename, output_filename)  # 确保文件保存到 cache 目录

            progress["status"] = "Completed"
            progress["percent"] = 100

            save_cache_info(file_key, output_filename, source)  # 记录缓存信息
        except Exception as e:
            progress["status"] = f"Error: {str(e)}"
        finally:
            os.remove(temp_filename)

    thread = threading.Thread(target=process_and_cache_file)
    thread.start()

    return jsonify({"message": "File processing started", "new_file": True}), 202


@cno.route("/progress", methods=["GET"])
def get_progress():
    """
    返回当前进度信息
    """
    return jsonify(progress)


@cno.route("/cache-list", methods=["GET"])
def list_cache():
    """
    返回缓存的文件列表，按日期倒序
    """
    cache_list = []
    cache_file_path = os.path.join(CACHE_DIR, "cache_info.json")
    if os.path.exists(cache_file_path):
        with open(cache_file_path, "r") as f:
            cache_list = json.load(f)
    # 按日期倒序排序
    cache_list.sort(key=lambda x: x["date"], reverse=True)
    return jsonify(cache_list)


@cno.route("/download/<file_key>", methods=["GET"])
def download_cached_file(file_key):
    """
    提供缓存文件的下载
    """
    cached_file = get_cached_file(file_key)
    if cached_file:
        return send_file(
            cached_file,
            as_attachment=True,
            download_name=f"{file_key}.yaml",
            mimetype="application/x-yaml",
        )
    else:
        return jsonify({"error": "File not available"}), 404


@cno.route("/delete-cache", methods=["POST"])
def delete_cache():
    data = request.get_json()
    keys = data.get("keys", [])

    deleted_keys = []
    for key in keys:
        # 生成缓存文件路径并验证是否位于CACHE_DIR内
        cache_file_path = os.path.join(CACHE_DIR, f"{key}.yaml")
        if os.path.commonpath([CACHE_DIR, cache_file_path]) != CACHE_DIR:
            continue  # 跳过不在CACHE_DIR目录内的路径

        if os.path.exists(cache_file_path):
            os.remove(cache_file_path)
            deleted_keys.append(key)

    # 更新缓存列表
    cache_info_path = os.path.join(CACHE_DIR, "cache_info.json")
    if os.path.exists(cache_info_path):
        with open(cache_info_path, "r") as f:
            cache_list = json.load(f)

        # 过滤掉被删除的文件
        cache_list = [item for item in cache_list if item["key"] not in deleted_keys]

        with open(cache_info_path, "w") as f:
            json.dump(cache_list, f, indent=4)

    return jsonify({"success": True, "deleted_keys": deleted_keys})


if __name__ == "__main__":
    # 注册蓝图，设置url_prefix
    app.register_blueprint(cno, url_prefix="/cno")
    app.run(debug=True, port=port)
