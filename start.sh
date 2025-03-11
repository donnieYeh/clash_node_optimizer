# !/bin/bash
source .venv/bin/activate
pip install -r requirements.txt
# 杀掉已有的web_service/app.py进程
pkill -f web_service/app.py
nohup python web_service/app.py > info.log 2>&1 &
echo app startup! please check info.log
deactivate