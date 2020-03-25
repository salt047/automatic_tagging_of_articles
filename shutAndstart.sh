#!/bin/bash
#运维测试部署代码和调试日志输出
#添加启动时候的日志输出地址，防止jenkins脚本启动被弹出日志拖延失去连接。
port=10000
netstat -apn | grep $port
sleep 1s
kill -9 $(netstat -nlp | grep :${port} | awk '{print $7}' | awk -F"/" '{ print $1 }')

nohup python3 main.py >logs/server.log 2>&1 &
echo "====================start success======================================="
netstat -apn | grep :${port}
echo "------------------------------------------------------------------------"
echo "success"


