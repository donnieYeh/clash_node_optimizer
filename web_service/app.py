from flask import Flask, request, jsonify, send_file, send_from_directory
from clash_node_optimizer.main import process_config
import os
import requests
import tempfile
import threading

app = Flask(__name__, static_folder="static")

# 全局变量，用于存储进度信息
progress = {"status": "idle", "percent": 0}
output_filename = None  # 存储结果文件路径

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/upload', methods=['POST'])
def upload():
    global progress, output_filename
    config_source = request.form.get('config_source')
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=".yaml") as temp_config_file:
        temp_filename = temp_config_file.name
        
        progress["status"] = "Preparing configuration file"
        progress["percent"] = 10

        if config_source == "url":
            config_url = request.form.get('config_url')
            if not config_url:
                progress["status"] = "Error: URL is required"
                return jsonify({"error": "URL is required"}), 400
            response = requests.get(config_url)
            if response.status_code != 200:
                progress["status"] = "Error: Failed to fetch the file from URL"
                return jsonify({"error": "Failed to fetch the file from URL"}), 400
            temp_config_file.write(response.content)
        
        elif config_source == "file":
            config_file = request.files.get('config_file')
            if not config_file:
                progress["status"] = "Error: File is required"
                return jsonify({"error": "File is required"}), 400
            config_file.save(temp_filename)
        
        else:
            progress["status"] = "Error: Invalid config source"
            return jsonify({"error": "Invalid config source"}), 400
    
    output_filename = tempfile.mktemp(suffix=".yaml")
    
    def process_and_prepare_file():
        global progress
        try:
            progress["status"] = "Processing configuration"
            progress["percent"] = 50

            process_config(temp_filename, output_filename)

            progress["status"] = "Completed"
            progress["percent"] = 100
            
        except Exception as e:
            progress["status"] = f"Error: {str(e)}"
        finally:
            os.remove(temp_filename)

    thread = threading.Thread(target=process_and_prepare_file)
    thread.start()

    return jsonify({"message": "File upload started"}), 202

@app.route('/progress', methods=['GET'])
def get_progress():
    return jsonify(progress)

@app.route('/download', methods=['GET'])
def download_file():
    if output_filename and os.path.exists(output_filename):
        return send_file(output_filename, as_attachment=True, download_name="optimized_config.yaml", mimetype="application/x-yaml")
    else:
        return jsonify({"error": "File not available"}), 404

if __name__ == '__main__':
    app.run(debug=True)
