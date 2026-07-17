#!/usr/bin/env python3
"""安装依赖"""
import subprocess
import sys

deps = ['requests', 'beautifulsoup4', 'lxml']
for dep in deps:
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', dep, '-q'])
print('[OK] 依赖安装完成')
