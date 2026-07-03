#!/usr/bin/env bash
# Render 部署构建脚本
set -o errexit

pip install -r requirements.txt
python manage.py collectstatic --no-input
python manage.py migrate
