# NetSerial

# 简介

NetSerial是一款可以通过TCP连接传输串口通讯的工具，支持`Windows` 以及 `Linux`。

多会话连接同时可以操作一个Serial。

当连接[服务器端](https://github.com/Elinpf/NetSerial_Server)后，远端设备可以通过服务器端连接到Client端串口。

# 安装方法
```
git clone https://github.com/Elinpf/NetSerial_Client.git
cd NetSerial_Client
pip install -r requirements.txt
```

# 配置

打开`custom.json`文件，修改所需配置。

- "SERIAL_DEVICE": "COM3"  # 串口名
- "SSH_SERVER_IP_ADDRESS": "127.0.0.1"  # 修改为连接服务器地址
- "SSH_SERVER_PORT": 2200  # 服务器连接端口
- "SSH_SERVER_USERNAME": "bar"  # 连接服务器用户名
- "SSH_SERVER_PASSWORD": "foo"  # 连接服务器密码

# 使用方法
```
cd NetSerial_Client
python ./start.py
```

使用`ctrl-m`可以打开菜单


# TODO
