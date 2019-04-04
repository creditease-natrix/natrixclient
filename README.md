# 关于Natrix

Natrix是开源混合云拨测系统

# 关于Natrixclient

natrixclient是配合Natrix的功能，安装在终端上的客户端软件，本软件具备如下功能

- 命令行命令，用于单机调试
- API接口，作为pip库，用于第三方调用
- 接入Natrix系统，提供数据， 现阶段主要支持 RabbitMQ

# 安装

## 必要条件

1. 必须是root用户
2. 目前只支持 python >= 3.4

## 测试矩阵



| 操作系统 \| 硬件 | 树梅派3B | X86-64 |
| ---------------- | -------- | ------ |
| raspbian jessie  | Y        |        |
| raspbian strech  | Y        |        |
| ubuntu 18        |          | Y      |
| centos 7         | Y        |        |
| windows 7        |          |        |
| windows 10       |          |        |

## 安装

**必须使用root权限**

```
pip3 install natrixclient
```

## 初始化

```
natrix service init
```

初始化主要完成如下事项

- 创建配置文件目录 /etc/natrix
- 拷贝配置文件模版和脚本到配置文件目录
- 创建日志文件目录 /var/log/natrix
- 创建systemctl服务

## 配置文件修改

根据自己公司实际，修改配置文件 /etc/natrix/natrix.ini

### RabbitMQ配置

配置如下

```
[RABBITMQ]
host = rabbitmq.natrix.com
port = 5672
username = natrix
password = natrix
vhost = /natrix
```

根据部署情况进行修改

### 访问配置

主要是访问外网, 企业内网，局域网三种情况，例如

```
[NETWORK]
internet_websites = ["www.baidu.com.com", "www.alibaba.com", "www.qq.com"]
corporate_websites = ["test1.natrix.com", "test2.natrix.com"]
intranet_ips = ["192.168.31.166", "192.168.31.188"]
```

internet_websites 检测终端是否能够访问互联网，简易输入几个典型的互联网网址

corporate_websites 检测终端是否能够访问企业网，简易输入几个典型的企业内网网址，例.com网址

intranet_ips 检测终端是否能够访问局域网，简易输入几个典型的内网IP地址

## 启动客户端

```
natrix service start
```

主要有2个作用

1. 启动natrixclient systemd服务
2. 设置natrixclient crontab周期性命令

### 停止

```
natrix service stop
```

主要有2个作用

1. 关闭natrixclient systemd服务
2. 清除natrixclient crontab周期性命令

### 查看状态

```
natrix service status
```

### 设置开机启动

```
natrix service enable
```

主要有2个作用

1. 设置natrixclient systemd服务开机启动
2. 设置natrixclient crontab周期性命令

### 取消开机启动

```
natrix service disable
```

主要有2个作用

1. 取消natrixclient systemd服务开机启动
2. 清除natrixclient crontab周期性命令

## 日志

日志文件位于 /var/log/natrix

### console.log

使用命令行方式调用natrixclient生成的日志

### api.log

使用api方式调用的时候生成的日志

### rabbitmq.log

开启systemd服务，使用rabbitmq方式交互生成的日志

# 使用

natrixclient 支持3种使用方式

- 命令行调用
- API调用
- RabbitMQ交互

## 命令行

natrix提供可以单独使用的命令行， 可以使用类似语句找寻帮助

```
$ natrix -h
usage: natrix [-h] [-d] [--log-file LOG_FILE]
              {ping,http,performance,dns,traceroute,check,keepalive} ...

Natrix Command Line Interface

optional arguments:
  -h, --help            show this help message and exit

Natrix Sub Commands:
  natrix sub commands.

  {ping,http,performance,dns,traceroute,check,keepalive}
                        help information about the natrix sub commands
    ping                natrix sub command - ping.
    http                natrix sub command - http
    dns                 natrix sub command - dns.
    traceroute          natrix sub command - traceroute.
    check               natrix sub command - check
    report              natrix sub command - report

Natrix Command Line interface. 
This tool is used to send network detective command such as ping, traceroute, dns and
etc.
```

```
$ natrix http -h
usage: natrix http [-h] [--http-version HTTP_VERSION] [-i INTERFACE]
                   [-t TIMEOUT] [-R ALLOW_REDIRECTS] [-r MAX_REDIRECTS]
                   [-a AUTHENTICATION_TYPE] [-c AUTHENTICATION_CONTENT]
                   {get,post,put,delete} ... destination

positional arguments:
  destination           natrix http command destination, url or ip.

optional arguments:
  -h, --help            show this help message and exit
  --http-version HTTP_VERSION
                        HTTP version, support 1.0 / 1.1 / 2.0
  -i INTERFACE, --interface INTERFACE
                        user can use dedicated network interface.
  -t TIMEOUT, --timeout TIMEOUT
                        Set an expiration time.
  -R ALLOW_REDIRECTS, --allow-redirects ALLOW_REDIRECTS
                        Allow Redirects, Default is True.
  -r MAX_REDIRECTS, --max-redirects MAX_REDIRECTS
                        Set Max Redirects. Default is 10
  -a AUTHENTICATION_TYPE, --authentication-type AUTHENTICATION_TYPE
                        Authentication Type. support basic_auth /digest_auth /
                        oauth1.0 / oauth2.0, if authentication-content is set,
                        authentication-type is basic_auth
  -c AUTHENTICATION_CONTENT, --authentication-content AUTHENTICATION_CONTENT
                        Authentication Content, for basic_auth, use
                        username:password, like guest:guest

Natrix HTTP Sub Commands:
  Natrix HTTP Sub Commands.

  {get,post,put,delete}
                        Help Information About the Natrix HTTP sub commands
    get                 Natrix HTTP Sub Command - GET.
    post                Natrix HTTP Sub Command - POST.
    put                 Natrix HTTP Sub Command - PUT.
    delete              Natrix HTTP Sub Command - DELETE.
```

### 命令列表

natrix包含如下子命令

- ping

  相关的PING操作命令

- traceroute

  相关的路由命令

- dns

  相关的DNS命令

- http

  相关HTTP协议的命令，例如 GET, PUT, POST, DELETE等

- check

  检测本设备信息的命令

- report

  通过rabbitmq汇报本机数据给natrix server

## API

通过pip安装natrixclient包之后，可以直接通过API对其功能进行调用，例如

```
from natrixclient.api import NatrixClientAPI

api = NatrixClientAPI()

destination = "www.baidu.com"

parameters = dict()
parameters["count"] = 1
parameters["timeout"] = 30

result = self.api.ping(destination=destination, parameters=parameters)
```

相关的参数定义请参考具体的命令

## RabbitMQ

客户端与服务端通过RabbitMQ等进行交流, 需要进行相关配置

# PING

## 命令行

**natrix ping <u>parameters</u>  destination**

### destination

url or ip

### parameters

请参考 参数 章节

## API

```
from natrixclient.api import NatrixClientAPI

api = NatrixClientAPI()

destination = "www.baidu.com"

parameters = dict()
parameters["count"] = 1
parameters["timeout"] = 30

result = api.ping(destination=destination, parameters=parameters)
```

parameters项请参考 参数 章节

## RabbitMQ

### 启动服务



### producer_ping.py

```
#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json
import pika
import time
from natrixclient.common import const
from natrixclient.common.config import NatrixConfig
from natrixclient.command.check.network import NetInfo


host = "rabbitmq.natrix.com"
port = 5672
vhost = "/natrix"
username = "natrix"
password = "natrix"
credentials = pika.PlainCredentials(username, password)
parameters = pika.ConnectionParameters(host, int(port), vhost, credentials=credentials)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()

macs = NetInfo().get_macs()
for mac in macs:
    queue_name = const.QUEUE_COMMAND_PREFIX + mac.lower()
    print(queue_name)
    channel.queue_declare(queue=queue_name,
                              durable=True,
                              arguments={
                                  'x-message-ttl': 120000,
                                  'x-dead-letter-exchange': const.EXCHANGE_COMMAND_DEAD,
                                  'x-dead-letter-routing-key': 'dead_command'
                              })
    request = dict()
    request["generate_timestamp"] = time.time()
    request["terminal"] = mac.lower()
    request["uuid"] = mac.lower()
    request["protocol"] = "PING"
    request["destination"] = "www.baidu.com"
    request_json = json.dumps(request)
    print(request_json)
    channel.basic_publish(exchange='', routing_key=queue_name, body=request_json)
```

### consumer_ping.py

```
#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json
import pika
from natrixclient.common.const import REQUEST_STORAGE_QUEUE_NAME

def callback(ch, method, properties, body):
    print("[x] Received: {}".format(body))
    print("")

host = "rabbitmq.natrix.com"
port = 5672
vhost = "/natrix"
username = "natrix"
password = "natrix"
queue_name = REQUEST_STORAGE_QUEUE_NAME

credentials = pika.PlainCredentials(username, password)
parameters = pika.ConnectionParameters(host, port, vhost, credentials=credentials)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()
channel = connection.channel()
queue = channel.queue_declare(queue=queue_name, auto_delete=True)
channel.basic_consume(callback, queue=queue_name, no_ack=True)

try:
    channel.start_consuming()
except KeyboardInterrupt:
    channel.stop_consuming()
finally:
    connection.close()
```

parameters项请参考 参数 章节

## 输入参数

| console long key  | console short key | api & rabbitmq parameter | type    | comments                                                     | milestone |
| ----------------- | ----------------- | ------------------------ | ------- | ------------------------------------------------------------ | --------- |
| --count           | -c                | count                    | int     | ping的次数, Stop after sending count ECHO_REQUEST packets    |           |
| --interface       | -i                | interface                | string  | interface  is  either  an address, or an interface name.  If interface is an address, it sets source address to specified interface address.  If interface in an interface name, it sets source interface to specified interface |           |
| --timeout         | -t                | timeout                  | int     | Time to wait for a response, in seconds. Default is five seconds. | 2         |
|                   |                   | packet_size              |         |                                                              | 2         |
|                   |                   | udp                      |         |                                                              | 2         |
|                   |                   | verbose                  |         |                                                              | 2         |
| --dns             | -d                |                          | string  | 指定DNS进行ping                                              | 2         |
| --capture-packets | -C                |                          | boolean | (现阶段不支持)是否抓包, 默认false, 如果true, 保存成pcap文件,采用对象存储 | 3         |
|                   |                   |                          |         | 指定包大小                                                   | 3         |

## 返回数据

### 数据格式

```
{
    'command': {
        'uuid': 'aaaaa',  //来自终端接收到的command信息
        'terminal': 'mac_address', //来自终端接收到的command信息
    }
    'status': status_code,
    'data': data_json,
    'stamp': stamp_json
}
```

### command

command项只是 rabbitmq 才有

| 字段       | 类型     | 说明                     | 备注   |
| -------- | ------ | ---------------------- | ---- |
| uuid     | string | 命令的UUID                |      |
| terminal | string | 终端的唯一号, 一般是mac address |      |

### status_code

status_code有如下值

| 值    | 说明     |
| ---- | ------ |
| 0    | 正确返回数据 |
| 1    | 状态错误   |
|      |        |

### stamp_json

```
{
    "server_request_generate_time": 12345678,
    "terminal_request_receive_time": 123456,
    "terminal_request_send_time": 123456,
    "terminal_response_receive_time": 123456,
    "terminal_response_return_time": 123456,
}
```

| 字段                             | 类型   | 说明                                       | 备注   |
| ------------------------------ | ---- | ---------------------------------------- | ---- |
| server_request_generate_time   | time | 服务器向终端发送请求的时间戳                           |      |
| terminal_request_receive_time  | time | 终端(树莓派)接收到服务器请求的时间戳                      |      |
| terminal_request_send_time     | time | 终端(树莓派) 向 目的地址 发起请求的时间                   |      |
| terminal_response_receive_time | time | 终端(树莓派) 接收到 目的地址 response 的时间            |      |
| terminal_response_return_time  | time | 终端(树莓派) 接收到 处理完response, 发送给 natrix服务器 的时间 |      |

### data_json

data_json是返回的数据类型，有正确返回和错误返回2种

### data_json正确返回

命令正确执行，得到正确的返回数据

#### data_json格式

```
{
	"destination": "www.baidu.com",
	"destination_ip": "10.10.10.13"，
	"destination_location": location_info,
	"packet_send": 3,
    "packet_receive": 3,
    "packet_loss": 0,
    "packet_size": 1233456,
    "avg_time": 1233456
    "max_time": 1233456,
    "min_time": 1233456
}
```

| 字段                   | 类型     | 说明        | 备注   |
| -------------------- | ------ | --------- | ---- |
| destination          | string | 目的地址      |      |
| destination_ip       | string | 目的地址IP    |      |
| destination_location | json   | 目的地址的区域信息 |      |
| packet_send          | int    | ping包发送数量 |      |
| packet_receive       | int    | ping包接收数量 |      |
| packet_loss          | int    | ping包丢弃数量 |      |
| packet_size          | int    | ping包大小   |      |
| avg_time             | time   | 平均时间      |      |
| max_time             | time   | 最大时间      |      |
| min_time             | time   | 最小时间      |      |

#### location_json格式

```
{
        "country": "中国",
        "region": "华北",
        "province": "北京",
        "city": "北京",
        "county": "朝阳区",
        "isp": "移动"
}
```

| 字段       | 类型     | 说明   |
| -------- | ------ | ---- |
| country  | string | 国家   |
| region   | string | 区域   |
| province | string | 省    |
| city     | string | 市    |
| country  | string | 县    |
| isp      | string | 运营商  |

### data_json错误返回

#### data_json格式

| 字段        | 说明   |
| --------- | ---- |
| errorcode |      |
| errorinfo |      |
|           |      |

# Traceroute

## 命令行

natrix traceroute <u>parameters</u>  destination

### destination

url or ip

### parameters

请参考 参数 章节

## API

```
from natrixclient.api import NatrixClientAPI

api = NatrixClientAPI()

destination = "www.baidu.com"
parameters = dict()
parameters["protocol"] = "icmp"

result = api.traceroute(destination=destination, parameters=parameters)
```

parameters 请参考 参数 章节

## RabbitMQ

### 启动服务



### producer_traceroute.py

```
#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json
import pika
import time
from natrixclient.common import const
from natrixclient.common.config import NatrixConfig
from natrixclient.command.check.network import NetInfo


host = "rabbitmq.natrix.com"
port = 5672
vhost = "/natrix"
username = "natrix"
password = "natrix"
credentials = pika.PlainCredentials(username, password)
parameters = pika.ConnectionParameters(host, int(port), vhost, credentials=credentials)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()

macs = NetInfo().get_macs()
for mac in macs:
    queue_name = const.QUEUE_COMMAND_PREFIX + mac.lower()
    print(queue_name)
    channel.queue_declare(queue=queue_name,
                              durable=True,
                              arguments={
                                  'x-message-ttl': 120000,
                                  'x-dead-letter-exchange': const.EXCHANGE_COMMAND_DEAD,
                                  'x-dead-letter-routing-key': 'dead_command'
                              })
    request = dict()
    request["generate_timestamp"] = time.time()
    request["terminal"] = mac.lower()
    request["uuid"] = mac.lower()
    request["protocol"] = "TRACEROUTE"
    request["destination"] = "www.baidu.com"
    request_json = json.dumps(request)
    print(request_json)
    channel.basic_publish(exchange='', routing_key=queue_name, body=request_json)
```

### consumer_traceroute.py

```
#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json
import pika
from natrixclient.common.const import REQUEST_STORAGE_QUEUE_NAME

def callback(ch, method, properties, body):
    print("[x] Received: {}".format(body))
    print("")

host = "rabbitmq.natrix.com"
port = 5672
vhost = "/natrix"
username = "natrix"
password = "natrix"
queue_name = REQUEST_STORAGE_QUEUE_NAME

credentials = pika.PlainCredentials(username, password)
parameters = pika.ConnectionParameters(host, port, vhost, credentials=credentials)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()
channel = connection.channel()
queue = channel.queue_declare(queue=queue_name, auto_delete=True)
channel.basic_consume(callback, queue=queue_name, no_ack=True)

try:
    channel.start_consuming()
except KeyboardInterrupt:
    channel.stop_consuming()
finally:
    connection.close()
```

parameters项请参考 参数 章节

## 输入参数

| console long key  | console short key | api & rabbitmq parameter | type    | comments                                 | milestone |
| ----------------- | ----------------- | ------------------------ | ------- | ---------------------------------------- | --------- |
| --interface       | -i                | interface                | string  | 接口名称                                     | 2         |
| --icmp            | -I                | protocol="icmp"          | boolean | 缺省值, Use ICMP ECHO for probes            |           |
| --tcp             | -T                | protocol="tcp"           | boolean | Use TCP SYN for probes                   |           |
| --udp             | -U                | protocol="udp"           | boolean | Use UDP to particular destination port for tracerouting (instead of increasing the port per each probe). Default port is 53 (dns). |           |
| --max-hops        | -m                | max_hops                 | int     | 最大跳数                                     |           |
| --dns             | -d                |                          | DNS     | 使用指定DNS                                  | 2         |
| --capture packets | -C                |                          | boolean | (现阶段不支持)是否抓包, 默认false, 如果true, 保存成pcap文件,采用对象存储 | 3         |

## 返回数据

### 数据格式

```
{
    'command': {
        'uuid': 'aaaaa',  //来自终端接收到的command信息
        'terminal': 'mac_address', //来自终端接收到的command信息
    }
    'status': status_code,
    'data': data_json
}
```

### command

command项只是 rabbitmq 才有

| 字段                 | 类型     | 说明                     | 备注   |
| ------------------ | ------ | ---------------------- | ---- |
| uuid               | string | 命令的UUID                |      |
| terminal           | string | 终端的唯一号, 一般是mac address |      |
| generate_timestamp | int    | 命令生成时的时间戳              |      |

### status_code

status_code有如下值

| 值    | 说明     |
| ---- | ------ |
| 0    | 正确返回数据 |
| 1    | 状态错误   |
|      |        |

### stamp_json

```
{
    "server_request_generate_time": 12345678,
    "terminal_request_receive_time": 123456,
    "terminal_request_send_time": 123456,
    "terminal_response_receive_time": 123456,
    "terminal_response_return_time": 123456,
}
```

| 字段                             | 类型   | 说明                                       | 备注   |
| ------------------------------ | ---- | ---------------------------------------- | ---- |
| server_request_generate_time   | time | 服务器向终端发送请求的时间戳                           |      |
| terminal_request_receive_time  | time | 终端(树莓派)接收到服务器请求的时间戳                      |      |
| terminal_request_send_time     | time | 终端(树莓派) 向 目的地址 发起请求的时间                   |      |
| terminal_response_receive_time | time | 终端(树莓派) 接收到 目的地址 response 的时间            |      |
| terminal_response_return_time  | time | 终端(树莓派) 接收到 处理完response, 发送给 natrix服务器 的时间 |      |

### data_json

data_json是返回的数据类型，有正确返回和错误返回2种

### data_json正确返回

#### data_json格式

```
{
    traceroute_list
}
```

| 字段              | 类型   | 说明      | 备注   |
| --------------- | ---- | ------- | ---- |
| traceroute_list | list | 每次路由项列表 |      |
|                 |      |         |      |

#### traceroute_list格式

```
[
    traceroute_item1,
    traceroute_item2,
    traceroute_item3,
    ...
]
```

#### traceroute_item格式

```
{
	"seq": 1,
	"routes": route_list
}
```

| 字段             | 类型     | 说明   | 备注   |
| -------------- | ------ | ---- | ---- |
| seq            | int    | 序列号  |      |
| ip             | string | IP   |      |
| hostname       | string | 主机名  |      |
| location       | json   | 位置信息 |      |
| response_times | float  | 返回时间 |      |

#### route_list格式

```
[
    route_item1,
    route_item2,
    route_item3,
]
```

#### route_item格式

```
{
	"ip": "10.10.36.1",
	"hostname": "bogon",
	"location": location_json,
	"response_times": 1.475
}
```

| 字段             | 类型     | 说明   | 备注   |
| -------------- | ------ | ---- | ---- |
| ip             | string | IP   |      |
| location       | json   | 位置信息 |      |
| hostname       | string | 主机名  |      |
| response_times | float  | 返回时间 |      |

#### location_json格式

```
{
        "country": "中国",
        "region": "华北",
        "province": "北京",
        "city": "北京",
        "county": "朝阳区",
        "isp": "移动"
}
```

| 字段       | 类型     | 说明   |
| -------- | ------ | ---- |
| country  | string | 国家   |
| region   | string | 区域   |
| province | string | 省    |
| city     | string | 市    |
| country  | string | 县    |
| isp      | string | 运营商  |

### data_json错误返回

#### data_json格式

| 字段        | 说明   |
| --------- | ---- |
| errorcode | 错误代码 |
| errorinfo | 错误信息 |
|           |      |

# DNS

## 命令行

natrix dns <u>parameters</u>  destination

### destination

url or ip

### parameters

请参考 参数 定义

## API

```
from natrixclient.api import NatrixClientAPI

api = NatrixClientAPI()

destination = "www.baidu.com"

parameters = dict()
parameters["dns_method"] = "a"

result = api.dns(destination=destination, parameters=parameters)
```

parameters 请参考 参数 章节

## RabbitMQ

### 启动服务



### producer_dns.py

```
#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json
import pika
import time
from natrixclient.common import const
from natrixclient.common.config import NatrixConfig
from natrixclient.command.check.network import NetInfo


host = "rabbitmq.natrix.com"
port = 5672
vhost = "/natrix"
username = "natrix"
password = "natrix"
credentials = pika.PlainCredentials(username, password)
parameters = pika.ConnectionParameters(host, int(port), vhost, credentials=credentials)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()

macs = NetInfo().get_macs()
for mac in macs:
    queue_name = const.QUEUE_COMMAND_PREFIX + mac.lower()
    print(queue_name)
    channel.queue_declare(queue=queue_name,
                              durable=True,
                              arguments={
                                  'x-message-ttl': 120000,
                                  'x-dead-letter-exchange': const.EXCHANGE_COMMAND_DEAD,
                                  'x-dead-letter-routing-key': 'dead_command'
                              })
    request = dict()
    request["generate_timestamp"] = time.time()
    request["terminal"] = mac.lower()
    request["uuid"] = mac.lower()
    request["protocol"] = "DNS"
    request["destination"] = "www.baidu.com"
    request_json = json.dumps(request)
    print(request_json)
    channel.basic_publish(exchange='', routing_key=queue_name, body=request_json)
```

### consumer_dns.py

```
#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json
import pika
from natrixclient.common.const import REQUEST_STORAGE_QUEUE_NAME

def callback(ch, method, properties, body):
    print("[x] Received: {}".format(body))
    print("")

host = "rabbitmq.natrix.com"
port = 5672
vhost = "/natrix"
username = "natrix"
password = "natrix"
queue_name = REQUEST_STORAGE_QUEUE_NAME

credentials = pika.PlainCredentials(username, password)
parameters = pika.ConnectionParameters(host, port, vhost, credentials=credentials)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()
channel = connection.channel()
queue = channel.queue_declare(queue=queue_name, auto_delete=True)
channel.basic_consume(callback, queue=queue_name, no_ack=True)

try:
    channel.start_consuming()
except KeyboardInterrupt:
    channel.stop_consuming()
finally:
    connection.close()
```

parameters项请参考 参数 章节

## 输入参数

| console long key  | console short key | api & rabbitmq parameter | type    | comments                                 | milestone |
| ----------------- | ----------------- | ------------------------ | ------- | ---------------------------------------- | --------- |
| --server          | -s                | dns_server               | string  | (optional) 指定dns server                  |           |
| --method          | -m                | dns_method               | string  | (optional) Change the type of the information query. default A |           |
| --timeout         | -t                | dns_timeout              | int     | (optional) The number of seconds to wait before the query times out. If None, the default, wait forever |           |
| --capture-packets | -C                |                          | boolean | (现阶段不支持)是否抓包, 默认false, 如果true, 保存成pcap文件,采用对象存储 | 3         |

### 输入参数 - method

method取值如下

| value | comments |
| ----- | -------- |
| a     | 地址记录     |
| cname | 别名记录     |
| mx    | 邮件服务器记录  |
| ns    | 名字服务器记录  |
|       |          |

## 返回数据

### 数据格式

```
{
    'command': {
        'uuid': 'aaaaa',  //来自终端接收到的command信息
        'terminal': 'mac_address', //来自终端接收到的command信息
     }
    'status': status_code,
    'data': data_json
}
```

### command

command项只是 rabbitmq 才有

| 字段                 | 类型     | 说明                     | 备注   |
| ------------------ | ------ | ---------------------- | ---- |
| uuid               | string | 命令的UUID                |      |
| terminal           | string | 终端的唯一号, 一般是mac address |      |
| generate_timestamp | int    | 命令生成时的时间戳              |      |

### status_code

status_code有如下值

| 值    | 说明     |
| ---- | ------ |
| 0    | 正确返回数据 |
| 1    | 状态错误   |
|      |        |

### stamp_json

```
{
    "server_request_generate_time": 12345678,
    "terminal_request_receive_time": 123456,
    "terminal_request_send_time": 123456,
    "terminal_response_receive_time": 123456,
    "terminal_response_return_time": 123456,
}
```

| 字段                             | 类型   | 说明                                       | 备注   |
| ------------------------------ | ---- | ---------------------------------------- | ---- |
| server_request_generate_time   | time | 服务器向终端发送请求的时间戳                           |      |
| terminal_request_receive_time  | time | 终端(树莓派)接收到服务器请求的时间戳                      |      |
| terminal_request_send_time     | time | 终端(树莓派) 向 目的地址 发起请求的时间                   |      |
| terminal_response_receive_time | time | 终端(树莓派) 接收到 目的地址 response 的时间            |      |
| terminal_response_return_time  | time | 终端(树莓派) 接收到 处理完response, 发送给 natrix服务器 的时间 |      |

### data_json

data_json是返回的数据类型，有正确返回和错误返回2种

### data_json正确返回 

#### 数据格式

```
{
	"ips": ips_list,
	"destination": "www.baidu.com",
	"ptime": 8.700132369995117,
	"dns_server": dns_server_json
}
```

| 字段          | 类型     | 说明            | 备注   |
| ----------- | ------ | ------------- | ---- |
| ips         | list   | 返回的IP列表       |      |
| destination | string | 请求的URL或IP     |      |
| ptime       | float  | dns解析时间, 单位毫秒 |      |
| dns_server  | json   | dns服务器IP      |      |

#### ips_list格式

```
[
    ip_item,
    ip_item,
    ...
]
```

#### ip_item格式

```
{
	"ip": "220.181.112.244",
	"location": location_json
}
```

| 字段       | 类型     | 说明    |
| -------- | ------ | ----- |
| ip       | string | IP    |
| location | json   | 位置等信息 |

#### dns_server格式

```
{
	"ip": "220.181.112.244",
	"location": location_json
}
```

| 字段       | 类型     | 说明   |
| -------- | ------ | ---- |
| ip       | string | IP   |
| location | json   | 位置信息 |
|          |        |      |

#### location_json格式

```
{
        "country": "中国",
        "region": "华北",
        "province": "北京",
        "city": "北京",
        "county": "朝阳区",
        "isp": "移动"
}
```



| 字段       | 类型     | 说明   |
| -------- | ------ | ---- |
| country  | string | 国家   |
| region   | string | 区域   |
| province | string | 省    |
| city     | string | 市    |
| country  | string | 县    |
| isp      | string | 运营商  |



#### data_json错误返回

#### data_json格式

| 字段        | 说明   |
| --------- | ---- |
| errorcode | 错误代码 |
| errorinfo | 错误信息 |
|           |      |

# HTTP

## 命令行

**natrix http <u>operation</u> <u>parameters</u>  destination**

### destination

url or ip

### operation

| VALUE   | COMMENTS | MILESTONE |
| ------- | -------- | --------- |
| get     | GET      |           |
| post    | POST     |           |
| put     | PUT      |           |
| delete  | DELETE   |           |
| head    | HEAD     | 2         |
| patch   | PATCH    | 2         |
| options | OPTIONS  | 2         |

### parameters

请参考 参数 定义

## API

```
from natrixclient.api import NatrixClientAPI

api = NatrixClientAPI()

destination = "www.baidu.com"

result = api.get(destination=destination)
```

parameters 请参考 参数 章节

## RabbitMQ

### 启动服务



### producer_http.py

```
#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json
import pika
import time
from natrixclient.common import const
from natrixclient.common.config import NatrixConfig
from natrixclient.command.check.network import NetInfo


host = "rabbitmq.natrix.com"
port = 5672
vhost = "/natrix"
username = "natrix"
password = "natrix"
credentials = pika.PlainCredentials(username, password)
parameters = pika.ConnectionParameters(host, int(port), vhost, credentials=credentials)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()

macs = NetInfo().get_macs()
for mac in macs:
    queue_name = const.QUEUE_COMMAND_PREFIX + mac.lower()
    print(queue_name)
    channel.queue_declare(queue=queue_name,
                              durable=True,
                              arguments={
                                  'x-message-ttl': 120000,
                                  'x-dead-letter-exchange': const.EXCHANGE_COMMAND_DEAD,
                                  'x-dead-letter-routing-key': 'dead_command'
                              })
    request = dict()
    request["generate_timestamp"] = time.time()
    request["terminal"] = mac.lower()
    request["uuid"] = mac.lower()
    request["protocol"] = "HTTP"
    request["destination"] = "www.baidu.com"
    request["parameters"] = dict()
    request["parameters"]["operation"] = "get"
    request_json = json.dumps(request)
    print(request_json)
    channel.basic_publish(exchange='', routing_key=queue_name, body=request_json)
```

### consumer_http.py

```
#!/usr/bin/env python
# -*- coding: utf-8 -*-


import json
import pika
from natrixclient.common.const import REQUEST_STORAGE_QUEUE_NAME

def callback(ch, method, properties, body):
    print("[x] Received: {}".format(body))
    print("")

host = "rabbitmq.natrix.com"
port = 5672
vhost = "/natrix"
username = "natrix"
password = "natrix"
queue_name = REQUEST_STORAGE_QUEUE_NAME

credentials = pika.PlainCredentials(username, password)
parameters = pika.ConnectionParameters(host, port, vhost, credentials=credentials)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()
channel = connection.channel()
queue = channel.queue_declare(queue=queue_name, auto_delete=True)
channel.basic_consume(callback, queue=queue_name, no_ack=True)

try:
    channel.start_consuming()
except KeyboardInterrupt:
    channel.stop_consuming()
finally:
    connection.close()
```

parameters项请参考 参数 章节

## 参数

通过命令行执行的时候需要那些输入参数

| console long key       | console short key | api & rabbitmq parameter | type    | comments                                 | milestone |
| ---------------------- | ----------------- | ------------------------ | ------- | ---------------------------------------- | --------- |
|                        |                   | operation                | string  | (required) http协议, get/post/put/delete   |           |
| --interface            | -i                | interface                | string  | (optional) 接口, 允许用户指定网络接口                |           |
| --allow-redirects      |                   | allow_redirects          | boolean | (optional) 是否允许重定向, 默认允许。使用范围 GET / HEAD / POST / PUT / OPTIONS / PATCH / DELETE |           |
| --max-redirects        |                   | max_redirects            | int     | (optional) 最大重定向数                        |           |
| --timeout              | -t                | timeout                  | float   | (optional) 超时时间,   Timeout for the entire request. 超时时间, 经过以 `timeout` 参数设定的秒数时间之后停止等待响应. `timeout` 仅对连接过程有效，与响应体的下载无关。 `timeout` 并不是整个下载响应的时间限制，而是如果服务器在 `timeout` 秒内没有应答，将会引发一个异常（更精确地说，是在 `timeout` 秒内没有从基础套接字上接收到任何字节的数据时）   **连接**超时指的是在你的客户端实现到远端机器端口的连接时（对应的是`connect()`_），Request 会等待的秒数.      **读取**超时指的就是客户端等待服务器发送请求的时间.  命令行只支持设置超时时间，不支持单独设置连接超时和读取超时 |           |
| --connect-timeout      |                   | connect_timeout          | int     | (optional) 连接超时时间                        |           |
| --dns-cache-timeout    |                   | dns_cache_timeout        | int     | (optional) DNS信息保存时间                     |           |
| --fresh-connect        |                   | fresh_connect            | bool    | (optional) 强制获取新的连接，即替代缓存中的连接, 缺省是0, 代表可以使用老的连接, natrix默认每次强制获取新连接 |           |
| --auth-type            | -a                | auth_type                | string  | (optional) 安全验证类型, 目前支持basic             |           |
| --auth-user            | -u                | auth_user                | String  | (optional) 安全验证内容, 支持安全验证，格式根据类型不同而不同, 以basic_auth来说, guest:guest |           |
| --dns-servers          |                   |                          | string  | (optional) DNS服务器, servers 按照逗号分割，按照顺序使用dns server | 2         |
| --capture-packets      |                   |                          | boolean | (optional) 是否抓包, 默认false, 如果true, 保存成pcap文件,采用对象存储 | 3         |
| --protocol             |                   |                          | string  | (optional) 协议类型, 支持HTTP里的各种协议, 例如HTTP, HTTPS， FTP，RTSP， RTSPU， 默认HTTP | 3         |
| --http-version         |                   |                          | string  | (optional) HTTP版本， 对于HTTP来说，有HTTP 1.0/HTTP 1.1/HTTP 2.0 | 2         |
| --use-cookies          |                   |                          | boolean | (optional) 是否使用缓存                        | 3         |
| --cookies              |                   |                          | json    | (optional) 缓存内容                          | 3         |
| --http-header          | -H                | http_header              | string  | (optional) 头部信息支持, 信息参考文档 parameters-header |           |
| --http-body            | -D                | http_body                | string  | (optional) body                          |           |
| --save-response-header |                   | save_response_header     | boolean | (optional) 返回结果是否包含response_header信息,  默认false |           |
| --save-response-body   |                   | save_response_body       | boolean | (optional) 返回结果是否包含response_body信息, 默认false |           |

### parameters - header

| 名称           | 说明   | Sample           |
| ------------ | ---- | ---------------- |
| Accept       |      | application/json |
| Content-Type |      | application/json |
| charset      |      | UTF-8            |
## 示例

### GET

#### CURL

```
$ curl -i -u guest:guest http://localhost:15672/api/vhosts
HTTP/1.1 200 OK
cache-control: no-cache
content-length: 77
content-security-policy: default-src 'self'
content-type: application/json
date: Tue, 22 Jan 2019 03:25:58 GMT
server: Cowboy
vary: accept, accept-encoding, origin

[{"cluster_state":{"rabbit@localhost":"running"},"name":"/","tracing":false}]
```

#### Natrix命令行

```
$ natrix http -u guest:guest get http://localhost:15672/api/vhosts
==================HTTP EXECUTE========================
{"status": 0, "data": {"url": "http://localhost:15672/api/vhosts", "last_url": "http://localhost:15672/api/vhosts", "status_code": 200, "redirect_count": 0, "redirect_time": 0.0, "remote_ip": "127.0.0.1", "remote_port": 15672, "local_ip": "127.0.0.1", "local_port": "127.0.0.1", "total_time": 6.225, "period_nslookup": 5.197, "period_tcp_connect": 0.25099999999999945, "period_ssl_connect": 0, "period_request": 0.03700000000000081, "period_response": 0.7139999999999995, "period_transfer": 0.0259999999999998, "header_size": 233, "size_upload": 0.0, "size_download": 77.0, "speed_upload": 0.0, "speed_download": 12369.0}}
======================================================
```

```
$ natrix http -u guest:guest --save-response-header --save-response-body get http://localhost:15672/api/vhosts
==================HTTP EXECUTE========================
{"status": 0, "data": {"url": "http://localhost:15672/api/vhosts", "last_url": "http://localhost:15672/api/vhosts", "status_code": 200, "redirect_count": 0, "redirect_time": 0.0, "remote_ip": "127.0.0.1", "remote_port": 15672, "local_ip": "127.0.0.1", "local_port": "127.0.0.1", "total_time": 6.759, "period_nslookup": 5.125, "period_tcp_connect": 0.3489999999999993, "period_ssl_connect": 0, "period_request": 0.3210000000000006, "period_response": 0.9260000000000002, "period_transfer": 0.038000000000000256, "header_size": 233, "size_upload": 0.0, "size_download": 77.0, "speed_upload": 0.0, "speed_download": 11392.0}, "response_header": "HTTP/1.1 200 OK\r\ncache-control: no-cache\r\ncontent-length: 77\r\ncontent-security-policy: default-src 'self'\r\ncontent-type: application/json\r\ndate: Tue, 22 Jan 2019 03:28:32 GMT\r\nserver: Cowboy\r\nvary: accept, accept-encoding, origin\r\n\r\n", "response_body": "[{\"cluster_state\":{\"rabbit@localhost\":\"running\"},\"name\":\"/\",\"tracing\":false}]"}
======================================================
```

#### Natrix API

```
from natrixclient.api import NatrixClientAPI

api = NatrixClientAPI()

destination = "www.baidu.com"

result = api.get(destination=destination)
```



#### Natrix RabbitMQ

```
import json
import pika

queue_name = "natrix_request_xxxxxxxxxxxx"
credentials = pika.PlainCredentials("natrix", "natrix")
parameters = pika.ConnectionParameters("127.0.0.1", 5672, "/natrix", credentials=credentials)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()
queue = channel.queue_declare(queue=queue_name, auto_delete=True)

request = dict()
request["generate_timestamp"] = "222222"
request["terminal"] = "080027683719"
request["uuid"] = "333333"
request["protocol"] = "HTTP"
request["destination"] = "www.baidu.com"
request["parameters"] = dict()
request["parameters"]["operation"] = "get"

channel.basic_publish(exchange='', routing_key=queue_name, body=json.dumps(request))

```



### PUT

#### CURL

```
$ curl -i -u guest:guest -H "content-type:application/json" -XPUT http://localhost:15672/api/vhosts/foo
HTTP/1.1 201 Created
content-length: 0
content-security-policy: default-src 'self'
date: Tue, 22 Jan 2019 03:31:20 GMT
server: Cowboy
vary: accept, accept-encoding, origin

```

```
$ curl -i -u guest:guest -H "content-type:application/json" -XPUT -d'{"type":"direct","durable":true}' http://localhost:15672/api/exchanges/foo/my-new-exchange
HTTP/1.1 201 Created
content-length: 0
content-security-policy: default-src 'self'
date: Tue, 22 Jan 2019 06:58:05 GMT
server: Cowboy
vary: accept, accept-encoding, origin

```

#### Natrix命令行

```
$ natrix http -u guest:guest -H "content-type:application/json" put http://localhost:15672/api/vhosts/foo2
==================HTTP EXECUTE========================
{"status": 0, "data": {"url": "http://localhost:15672/api/vhosts/foo2", "last_url": "http://localhost:15672/api/vhosts/foo2", "status_code": 201, "redirect_count": 0, "redirect_time": 0.0, "remote_ip": "127.0.0.1", "remote_port": 15672, "local_ip": "127.0.0.1", "local_port": "127.0.0.1", "total_time": 177.95, "period_nslookup": 5.176, "period_tcp_connect": 0.20999999999999996, "period_ssl_connect": 0, "period_request": 0.28300000000000036, "period_response": 172.25799999999998, "period_transfer": 0.022999999999996135, "header_size": 180, "size_upload": 0.0, "size_download": 0.0, "speed_upload": 0.0, "speed_download": 0.0}}
======================================================
```

```
$ natrix http -u guest:guest -H "content-type:application/json" -D '{"type":"direct","durable":true}' put http://localhost:15672/api/exchanges/foo/my-new-exchange2
==================HTTP EXECUTE========================
{"status": 0, "data": {"url": "http://localhost:15672/api/exchanges/foo/my-new-exchange2", "last_url": "http://localhost:15672/api/exchanges/foo/my-new-exchange2", "status_code": 201, "redirect_count": 0, "redirect_time": 0.0, "remote_ip": "127.0.0.1", "remote_port": 15672, "local_ip": "127.0.0.1", "local_port": "127.0.0.1", "total_time": 17.46, "period_nslookup": 4.432, "period_tcp_connect": 0.1979999999999995, "period_ssl_connect": 0, "period_request": 0.04900000000000038, "period_response": 12.758999999999999, "period_transfer": 0.022000000000002018, "header_size": 180, "size_upload": 32.0, "size_download": 0.0, "speed_upload": 1832.0, "speed_download": 0.0}}
======================================================
```

#### Natrix API

```
from natrixclient.api import NatrixClientAPI

api = NatrixClientAPI()

destination = "http://localhost:15672/api/vhosts/foo6"

parameters = dict()
parameters["auth_user"] = "guest:guest"
parameters["http_header"] = "content-type:application/json"

result = api.put(destination=destination, parameters=parameters)
```

```
from natrixclient.api import NatrixClientAPI

api = NatrixClientAPI()

destination = "http://localhost:15672/api/vhosts/foo7"

parameters = dict()
parameters["auth_user"] = "guest:guest"
parameters["http_header"] = "content-type:application/json"
parameters["http_body"] = '{"type":"direct","durable":true}'

result = api.put(destination=destination, parameters=parameters)
```



#### Natrix RabbitMQ

```
import json
import pika

queue_name = "natrix_request_xxxxxxxxxxxx"
credentials = pika.PlainCredentials("natrix", "natrix")
parameters = pika.ConnectionParameters("127.0.0.1", 5672, "/natrix", credentials=credentials)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()
queue = channel.queue_declare(queue=queue_name, auto_delete=True)

request = dict()
request["generate_timestamp"] = "222222"
request["terminal"] = "080027683719"
request["uuid"] = "333333"
request["protocol"] = "HTTP"
request["destination"] = "http://localhost:15672/api/vhosts/foo8"
request["parameters"] = dict()
request["parameters"]["operation"] = "put"
request["parameters"]["auth_user"] = "guest:guest"
request["parameters"]["http_header"] = "content-type:application/json"
request["parameters"]["http_body"] = '{"type":"direct","durable":true}'

channel.basic_publish(exchange='', routing_key=queue_name, body=json.dumps(request))

```

### POST

#### CURL

```
$ curl -i -u guest:guest -H "content-type:application/json" -XPOST -d'{"properties":{},"routing_key":"my key","payload":"my body","payload_encoding":"string"}' http://localhost:15672/api/exchanges/foo/my-new-exchange/publish
HTTP/1.1 200 OK
cache-control: no-cache
content-length: 16
content-security-policy: default-src 'self'
content-type: application/json
date: Wed, 23 Jan 2019 02:01:42 GMT
server: Cowboy
vary: accept, accept-encoding, origin

{"routed":false}
```

#### Natrix命令行

```
$ natrix http -u guest:guest -H "content-type:application/json" -d '{"properties":{},"routing_key":"my key","payload":"my body","payload_encoding":"string"}' post http://localhost:15672/api/exchanges/foo/my-new-exchange/publish
==================HTTP EXECUTE========================
{"status": 0, "data": {"url": "http://localhost:15672/api/exchanges/foo/my-new-exchange/publish", "last_url": "http://localhost:15672/api/exchanges/foo/my-new-exchange/publish", "status_code": 200, "redirect_count": 0, "redirect_time": 0.0, "remote_ip": "127.0.0.1", "remote_port": 15672, "local_ip": "127.0.0.1", "local_port": "127.0.0.1", "total_time": 8.468, "period_nslookup": 5.221, "period_tcp_connect": 0.1980000000000004, "period_ssl_connect": 0, "period_request": 0.04299999999999926, "period_response": 2.9810000000000016, "period_transfer": 0.02499999999999858, "header_size": 233, "size_upload": 88.0, "size_download": 16.0, "speed_upload": 10392.0, "speed_download": 1889.0}}
======================================================
```

#### Natrix API

```
from natrixclient.api import NatrixClientAPI

api = NatrixClientAPI()

destination = "http://localhost:15672/api/vhosts/foo7"

parameters = dict()
parameters["auth_user"] = "guest:guest"
parameters["http_header"] = "content-type:application/json"
parameters["http_body"] = '{"type":"direct","durable":true}'

result = api.post(destination=destination, parameters=parameters)
```



#### Natrix RabbitMQ

```
import json
import pika

queue_name = "natrix_request_xxxxxxxxxxxx"
credentials = pika.PlainCredentials("natrix", "natrix")
parameters = pika.ConnectionParameters("127.0.0.1", 5672, "/natrix", credentials=credentials)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()
queue = channel.queue_declare(queue=queue_name, auto_delete=True)

request = dict()
request["generate_timestamp"] = "222222"
request["terminal"] = "080027683719"
request["uuid"] = "333333"
request["protocol"] = "HTTP"
request["destination"] = "http://localhost:15672/api/vhosts/foo8"
request["parameters"] = dict()
request["parameters"]["operation"] = "post"
request["parameters"]["auth_user"] = "guest:guest"
request["parameters"]["http_header"] = "content-type:application/json"
request["parameters"]["http_body"] = '{"type":"direct","durable":true}'

channel.basic_publish(exchange='', routing_key=queue_name, body=json.dumps(request))
```

### DELETE

#### CURL

```
$ curl -i -u guest:guest -H "content-type:application/json" -XDELETE http://localhost:15672/api/exchanges/foo/my-new-exchange
HTTP/1.1 204 No Content
content-security-policy: default-src 'self'
date: Tue, 22 Jan 2019 08:26:54 GMT
server: Cowboy
vary: accept, accept-encoding, origin
```

#### Natrix命令行

```
$ natrix http -u guest:guest -H "content-type:application/json" delete http://localhost:15672/api/exchanges/foo/my-new-exchange1
==================HTTP EXECUTE========================
{"status": 0, "data": {"url": "http://localhost:15672/api/exchanges/foo/my-new-exchange1", "last_url": "http://localhost:15672/api/exchanges/foo/my-new-exchange1", "status_code": 204, "redirect_count": 0, "redirect_time": 0.0, "remote_ip": "127.0.0.1", "remote_port": 15672, "local_ip": "127.0.0.1", "local_port": "127.0.0.1", "total_time": 47.851, "period_nslookup": 4.64, "period_tcp_connect": 0.18799999999999972, "period_ssl_connect": 0, "period_request": 0.038000000000000256, "period_response": 42.961, "period_transfer": 0.02400000000000091, "header_size": 164, "size_upload": 0.0, "size_download": 0.0, "speed_upload": 0.0, "speed_download": 0.0}}
======================================================
```

#### Natrix API

```
from natrixclient.api import NatrixClientAPI

api = NatrixClientAPI()

destination = "http://localhost:15672/api/vhosts/foo7"

parameters = dict()
parameters["auth_user"] = "guest:guest"
parameters["http_header"] = "content-type:application/json"
parameters["http_body"] = '{"type":"direct","durable":true}'

result = api.delete(destination=destination, parameters=parameters)
```



#### Natrix RabbitMQ

```
import json
import pika

queue_name = "natrix_request_xxxxxxxxxxxx"
credentials = pika.PlainCredentials("natrix", "natrix")
parameters = pika.ConnectionParameters("127.0.0.1", 5672, "/natrix", credentials=credentials)
connection = pika.BlockingConnection(parameters)
channel = connection.channel()
queue = channel.queue_declare(queue=queue_name, auto_delete=True)

request = dict()
request["generate_timestamp"] = "222222"
request["terminal"] = "080027683719"
request["uuid"] = "333333"
request["protocol"] = "HTTP"
request["destination"] = "http://localhost:15672/api/vhosts/foo8"
request["parameters"] = dict()
request["parameters"]["operation"] = "delete"
request["parameters"]["auth_user"] = "guest:guest"
request["parameters"]["http_header"] = "content-type:application/json"
request["parameters"]["http_body"] = '{"type":"direct","durable":true}'
request["parameters"]["save_response_header"] = True
request["parameters"]["save_response_body"] = True

channel.basic_publish(exchange='', routing_key=queue_name, body=json.dumps(request))
```

## 返回数据

### 数据格式

```
{
    'command': {
        'uuid': 'aaaaa',  //来自终端接收到的command信息
        'terminal': 'mac_address', //来自终端接收到的command信息
    }
    'status': status_code,
    'data': data_json
}
```

### command

command项只是 rabbitmq 才有

| 字段                 | 类型     | 说明                     | 备注   |
| ------------------ | ------ | ---------------------- | ---- |
| uuid               | string | 命令的UUID                |      |
| terminal           | string | 终端的唯一号, 一般是mac address |      |
| generate_timestamp | int    | 命令生成时的时间戳              |      |

### status_code

status_code有如下值

| 值    | 说明     |
| ---- | ------ |
| 0    | 正确返回数据 |
| 1    | 状态错误   |
|      |        |

### stamp_json

```
{
    "server_request_generate_time": 12345678,
    "terminal_request_receive_time": 123456,
    "terminal_request_send_time": 123456,
    "terminal_response_receive_time": 123456,
    "terminal_response_return_time": 123456,
}
```

| 字段                             | 类型   | 说明                                       | 备注   |
| ------------------------------ | ---- | ---------------------------------------- | ---- |
| server_request_generate_time   | time | 服务器向终端发送请求的时间戳                           |      |
| terminal_request_receive_time  | time | 终端(树莓派)接收到服务器请求的时间戳                      |      |
| terminal_request_send_time     | time | 终端(树莓派) 向 目的地址 发起请求的时间                   |      |
| terminal_response_receive_time | time | 终端(树莓派) 接收到 目的地址 response 的时间            |      |
| terminal_response_return_time  | time | 终端(树莓派) 接收到 处理完response, 发送给 natrix服务器 的时间 |      |



### data_json

data_json是返回的数据类型，有正确返回和错误返回2种

### data_json正确返回

#### data_json格式

```
{
	"url": "http://localhost:15672/api/vhosts",
	"last_url": "http://localhost:15672/api/vhosts",
	"status_code": 200,
	"redirect_count": 0,
	"redirect_time": 0.0,
	"remote_ip": "127.0.0.1",
	"remote_location": location_json,
	"remote_port": 15672,
	"local_ip": "127.0.0.1",
	"local_location": location_json,
	"local_port": "127.0.0.1",
	"total_time": 6.759,
	"period_nslookup": 5.125,
	"period_tcp_connect": 0.3489999999999993,
	"period_ssl_connect": 0,
	"period_request": 0.3210000000000006,
	"period_response": 0.9260000000000002,
	"period_transfer": 0.038000000000000256,
	"header_size": 233,
	"size_upload": 0.0,
	"size_download": 77.0,
	"speed_upload": 0.0,
	"speed_download": 11392.0,
	"response_header": "HTTP/1.1 404 Not Found\r\nserver: Cowboy\r\ndate: Thu, 14 Mar 2019 08:47:04 GMT\r\ncontent-length: 49\r\ncontent-type: application/json\r\nvary: accept, accept-encoding, origin\r\n\r\n",
	"response_body": "{\"error\":\"Object Not Found\",\"reason\":\"Not Found\"}"
}
```

| 字段                 | 类型     | 说明              |
| ------------------ | ------ | --------------- |
| url                | string | 请求URL           |
| last_url           | string | 最后一次请求的URL      |
| status_code        | int    | HTTP 响应代码       |
| redirect_count     | int    | 重定向次数           |
| redirect_time      | float  | 重定向所消耗的时间       |
| remote_ip          | string | 最后一次连接的远程IP地址   |
| remote_location    | json   | 远程IP的位置信息       |
| remote_port        | int    | 最后一次连接的远程端口号    |
| local_ip           | string | 最后一次连接的本地IP地址   |
| local_location     | json   | 本地IP的位置信息       |
| local_port         | int    | 最后一次连接的本地端口号    |
| total_time         | float  | 请求总的时间          |
| namelookup_time    | float  | DNS解析所消耗的时间     |
| period_tcp_connect | float  | TCP连接耗时         |
| period_ssl_connect | float  | SSL连接耗时         |
| period_request     | float  | Request请求耗时     |
| period_response    | float  | Response处理耗时    |
| period_transfer    | float  | Response传输耗时    |
| size_upload        | float  | 上传数据包大小         |
| size_download      | float  | 下载数据包大小         |
| speed_upload       | float  | 上传速度            |
| speed_download     | float  | 下载速度            |
| response_header    | string | response头部信息    |
| response_body      | string | response body信息 |

#### location_json格式

```
{
        "country": "中国",
        "region": "华北",
        "province": "北京",
        "city": "北京",
        "county": "朝阳区",
        "isp": "移动"
}
```

| 字段       | 类型     | 说明   |
| -------- | ------ | ---- |
| country  | string | 国家   |
| region   | string | 区域   |
| province | string | 省    |
| city     | string | 市    |
| country  | string | 县    |
| isp      | string | 运营商  |

#### data_json错误返回

#### data_json格式

| 字段        | 说明   |
| --------- | ---- |
| errorcode | 错误代码 |
| errorinfo | 错误信息 |
|           |      |

# Check

## 命令行

natrix check type

type有如下几种

| 类型     | 备注                                           |
| -------- | ---------------------------------------------- |
| basic    | 基础上报功能                                   |
| advance  | 所有的信息都上报                               |
| hardware | 硬件信息                                       |
| network  | 网络信息                                       |
| system   | 系统信息, 包含操作系统信息, natrixclient的信息 |

## API

```
from natrixclient.api import NatrixClientAPI

api = NatrixClientAPI()
parameters = dict()
parameters["type"] = "system"
result = api.check(parameters)
```

parameters 请参考 参数 章节

## RabbitMQ

无

## 返回数据

### 高级返回信息 advanced_information

check the current client information, the result information including
需要包含如下信息：

采用 json 格式

```
{
    "system": system_json,
    "hardware": hardware_json,
    "networks": network_json,
    "heartbeat": 1234567,
}
```

heatbeat属于心跳时间, 是从客户端发出的时间

#### 系统信息 system_json

```
{
	"operating": operating_json,
	"natrixclient": natrixclient_json,
},
```

##### 操作系统信息 operating_json



| 名称                      | 类型   | 备注                                                         | 必须 | 空值 | 里程碑 |
| ------------------------- | ------ | ------------------------------------------------------------ | ---- | ---- | ------ |
| type                      | string | 操作系统类型, 例如Linux或Windows                             | Y    | N    |        |
| series                    | string | 操作系统系列, 例如debian或redhat                             | Y    | N    |        |
| name                      | string | 操作系统名称，例如ubuntu或centos或raspbian                   | Y    | N    |        |
| codename                  | string | 操作系统发行代号, 例如strech或'Bionic Beaver'                | Y    | N    |        |
| major_version             | string | 操作系统主版本号                                             | Y    | N    |        |
| minor_version             | string | 操作系统次版本号, 可以为空或空值                             | Y    | N    |        |
| kernel_version            | string | 操作系统内核版本信息, 例如linux kernel的版本信息             | Y    | N    |        |
| architecture              | string | 操作系统架构信息, 32bit 或 64bit                             | Y    | N    |        |
| platform                  | string | 综合平台信息，例如 'Linux-4.15.0-42-generic-x86_64-with-Ubuntu-18.04-bionic' | Y    | N    |        |
| python_version            | string | 默认python版本                                               | Y    | N    |        |
| python2_version           | string | python2的版本                                                |      |      | 2      |
| python3_version           | string | python3的版本                                                |      |      | 2      |
| desktop_version           | string | 桌面版本信息                                                 | Y    | N    |        |
| selenium_version          | string | selenium版本信息, 0代表未安装                                | Y    | N    |        |
| chrome_version            | string | chrome版本信息, 0代表未安装                                  | Y    | N    |        |
| chrome_webdriver_path     | string | chrome webdriver路径信息, 空代表未找到                       | Y    | Y    |        |
| chrome_webdriver_version  | string | chrome webdriver版本信息, 0代表未安装                        | Y    | N    |        |
| firefox_version           | string | firefox版本信息, 0代表未安装                                 | Y    | N    |        |
| firefox_webdriver_path    | string | firefox webdriver路径信息, 空代表未找到                      | Y    | Y    |        |
| firefox_webdriver_version | string | firefox webdriver版本信息, 0代表未安装                       | Y    | N    |        |

##### natrixclient软件信息 natrixclient_json

| 名称                 | 类型   | 说明                   | 必须 | 空值 | 里程碑 |
| -------------------- | ------ | ---------------------- | ---- | ---- | ------ |
| natrixclient_version | string | natrixclient的版本信息 | Y    | N    |        |

#### 硬件信息 hardware_json

硬件信息主要包含如下内容

```
{
	"sn": "xxxxxxx",
	"hostname": "pi-xxxxxx",
	"product": "Raspberry Pi 3 Model B Rev 1.2",
	"boot_time": 113456,
	"cpu_info": cpu_json,
	"memory_info": memory_json,
	"disk_info": disk_json,
},
```

| 名称        | 类型   | 说明     | 必须 | 空值 | 里程碑 |
| ----------- | ------ | -------- | ---- | ---- | ------ |
| sn          | sting  | 序列号   | Y    | N    |        |
| hostname    | string | 主机名   | Y    | N    |        |
| product     | string | 产品型号 | Y    | N    |        |
| boot_time   | float  | 开机时长 | Y    | N    |        |
| cpu_info    | json   | cpu信息  | Y    | N    |        |
| memory_info | json   | 内存信息 | Y    | N    |        |
| disk_info   | json   | 磁盘信息 | Y    | N    |        |



##### sn

终端设备的序列号

对于树梅派设备, 使用cpu serial number

```
cat /proc/cpuinfo | grep -i Serial | cut -d ' ' -f 2
```

对于ubuntu设备

```
sudo dmidecode -t system | grep -i serial | cut -d ':' -f 2
```

if serial number is 0, using

```
sudo dmidecode -t system | grep uuid
```

##### hostname

主机名

##### product

终端设备的产品型号信息

对于linux终端设备

```
sudo dmidecode -t system | grep "Product Name"  
```

对于raspbian终端设备

```
cat /sys/firmware/devicetree/base/model
```

##### boot_time

启动时间

##### cpu_json

| 名称        | 类型   | 说明                                    | 必须 | 空值 | 里程碑 |
| ----------- | ------ | --------------------------------------- | ---- | ---- | ------ |
| cpu_model   | string | CPU型号                                 | Y    | N    |        |
| cpu_core    | int    | CPU核数                                 | Y    | N    |        |
| cpu_percent | float  | CPU使用率, 默认是一秒钟的使用率, 百分比 | Y    | N    |        |

##### memory _info

| 名称           | 类型  | 说明               | 必须 | 空值 | 里程碑 |
| -------------- | ----- | ------------------ | ---- | ---- | ------ |
| memory_total   | float | 总的内存           | Y    | N    |        |
| memory_used    | float | 已经使用的内存     | Y    | N    |        |
| memory_percent | float | 内存使用率, 百分比 | Y    | N    |        |
|                |       |                    |      |      |        |

##### disk_info

| 名称         | 类型  | 说明       | 必须 | 空值 | 里程碑 |
| ------------ | ----- | ---------- | ---- | ---- | ------ |
| disk_percent | float | 磁盘使用率 | Y    | N    |        |

#### 网络信息 network_json

##### 所有网络接口信息 interfaces_json

网络接口信息是一个列表信息, 里面的信息如下

```
{
	"eth0": interface_json, 
	"wlan0": interface_json
}
```

##### 单个网络接口信息 interface_json

```
{
    "type": "wired",
    "name": "eth0",
    "macaddress": "xxxxxxxxx",
    "localip": "10.10.10.10",
    "netmask": "255.255.255.0",
    "braodcast": "10.10.10.255",
    "gateway": "10.10.10.1,
    "is_default": true,
    "public_ip": "10.10.10.10",
    "location_info": location_json,
    "access_intranet": true,
    "access_coporate": true,
    "access_internet": true
}
```

| 名称            | 类型    | 说明                              | 必须 | 空值 | 里程碑 |
| --------------- | ------- | --------------------------------- | ---- | ---- | ------ |
| type            | string  | 网卡类型(有线,无线,4G)            | Y    | N    |        |
| name            | string  | 网卡名称, 例如eth0等              | Y    | N    |        |
| macaddress      | string  | MACADDRESS, 网卡物理地址          | Y    | Y    |        |
| local_ip        | string  | 本地IP地址                        | Y    | Y    |        |
| local_location  | json    | location_json                     | Y    | Y    |        |
| netmask         | string  | 子网掩码                          | Y    | Y    |        |
| broadcast       | string  | 广播地址                          | Y    | Y    |        |
| gateway         | string  | 网关                              | Y    | Y    |        |
| is_default      | boolean | 是否是缺省使用的网卡, 默认是false | Y    | Y    |        |
|                 |         |                                   |      |      |        |
| public_ip       | string  | 检测公网IP                        | Y    | Y    |        |
| public_location | json    | location_json                     | Y    | Y    |        |
|                 |         |                                   |      |      |        |
| access_intranet | boolean | 是否能访问局域网, 默认False       | Y    | N    |        |
| access_coporate | boolean | 是否能访问企业网, 默认False       | Y    | N    |        |
| access_internet | boolean | 是否能访问互联网, 默认为False     | Y    | N    |        |
|                 |         |                                   |      |      |        |

对于一个接口来说，有可能存在好几个IP地址的情况, 这种情况下，need to throw exception, natrix do not support this situation

##### 地域与运营商信息 location_json

| 名称     | 类型   | 说明              | 必须 | 空值 | 里程碑 |
| -------- | ------ | ----------------- | ---- | ---- | ------ |
| country  | string | 国家              | Y    | N    |        |
| region   | string | 区域, 0代表没有   | Y    | N    |        |
| province | string | 省, 0代表没有     | Y    | N    |        |
| city     | string | 城市, 0代表没有   | Y    | N    |        |
| isp      | string | 运营商, 0代表没有 | Y    | N    |        |
|          |        |                   |      |      |        |



### 基础返回信息 basic_infomation

check the current client information, the result information including
需要包含如下信息：

采用 json 格式

```
{
    "system": system_basic_json,
    "hardware": hardware_basic_json,
    "networks": network_json,
    "heartbeat": 1234567,
}
```

heatbeat属于心跳时间, 是从客户端发出的时间

#### 系统简单信息 system_basic_json

| 名称                             | 类型     | 说明                          | 里程碑  |
| ------------------------------ | ------ | --------------------------- | ---- |
| natrixclient_version           | string | natrixclient的版本信息           |      |
| natrixclient_crontab_version   | string | natrixclient crontab的版本信息   |      |
| natrixclient_dashboard_version | string | natrixclient dashboard的版本信息 |      |
|                                |        |                             |      |
|                                |        |                             |      |
|                                |        |                             |      |
|                                |        |                             |      |

#### 硬件简单信息 hardware_simple_json

| 名称             | 类型     | 说明                      | 里程碑  |
| -------------- | ------ | ----------------------- | ---- |
| sn             | string |                         |      |
| hostname       | string |                         |      |
| cpu_percent    | float  | CPU使用率, 默认是一秒钟的使用率, 百分比 |      |
| memory_percent | float  | 内存使用率, 百分比              |      |
| disk_percent   | float  | 磁盘使用率, 百分比              |      |
|                |        |                         |      |
|                |        |                         |      |
|                |        |                         |      |
|                |        |                         |      |

#### 网络信息  network_json

同高级返回信息中的network_json

# Report

report命令用来手动进行信息上报

## 命令行

natrix report type 

type包含如下2种类

| 类型    | 说明                                 |
| ------- | ------------------------------------ |
| basic   | 基础信息上报, 具体参考 check basic   |
| advance | 高级信息上报，具体参考 check advance |
|         |                                      |

## API

不支持

## RabbitMQ

不支持


# Performance(In progressing...)

**natrix performance <u>parameters</u> destination**

## 命令行

### destination

url or ip

## 输入参数

| long key          | short key | value       | comments                                                     | milestone |
| ----------------- | --------- | ----------- | ------------------------------------------------------------ | --------- |
| --browser         | -b        | web browser | 浏览器选择, the webbrowser, values curl/firefox/chrome, by default is curl |           |
| --dns-server      | -d        | dns-server  | dns server                                                   |           |
| --snapshot        | -S        | boolean     | (现阶段不支持)是否保存快照, 默认false, 如果true, 保存返回html, 以文件形式存在, 采用对象存储 | 2         |
| --capture packets | -C        | boolean     | (现阶段不支持)是否抓包, 默认false, 如果true, 保存成pcap文件,采用对象存储 | 3         |
| --keep-alive      | -K        | boolean     | (现阶段不支持)是否保持常连接                                 | 2         |
| --cache           | -C        | boolean     | (现阶段不支持)是否使用缓存                                   | 2         |

## 返回数据

```
{
    "timing": {},
    "resources": {}
}
```

| 名称      | 类型 | 说明           |
| --------- | ---- | -------------- |
| timing    | json | 时间信息       |
| resources | json | 资源的返回列表 |

#### timing

| name                       | 名称                | 说明                                                         | 显示        |
| -------------------------- | ------------------- | ------------------------------------------------------------ | ----------- |
| statusCode                 | 状态码              | 暂时得不到相关信息                                           |             |
| resourceSize               | 资源大小            | 暂时得不到相关信息                                           |             |
| navigationStart            | 开始时间            | 准备加载新页面的起始时间                                     |             |
| redirectStart              | 重定向开始时        | 如果发生了HTTP重定向，并且从导航开始，中间的每次重定向，都和当前文档同域的话，就返回开始重定向的timing.fetchStart的值。其他情况，则返回0 |             |
| redirectEnd                | 重定向结束时间      | 如果发生了HTTP重定向，并且从导航开始，中间的每次重定向，都和当前文档同域的话，就返回最后一次重定向，接收到最后一个字节数据后的那个时间.其他情况则返回0 |             |
| fetchStart                 | 资源获取开始时间    | 如果一个新的资源获取被发起，则 fetchStart必须返回用户代理开始检查其相关缓存的那个时间，其他情况则返回开始获取该资源的时间 |             |
| domainLookupStart          | 域名解析开始时间    | 返回用户代理对当前文档所属域进行DNS查询开始的时间。如果此请求没有DNS查询过程，如长连接，资源cache,甚至是本地资源等。 那么就返回 fetchStart的值 |             |
| domainLookupEnd            | 域名检测结束时间    | 返回用户代理对结束对当前文档所属域进行DNS查询的时间。如果此请求没有DNS查询过程，如长连接，资源cache，甚至是本地资源等。那么就返回 fetchStart的值 |             |
| connectStart               | 连接开始时间        | 返回用户代理向服务器服务器请求文档，开始建立连接的那个时间，如果此连接是一个长连接，又或者直接从缓存中获取资源（即没有与服务器建立连接）。则返回domainLookupEnd的值 |             |
| secureConnectionStart      | 安全连接开始时间    | 可选特性。用户代理如果没有对应的东东，就要把这个设置为undefined。如果有这个东东，并且是HTTPS协议，那么就要返回开始SSL握手的那个时间。 如果不是HTTPS， 那么就返回0 | HTTPS才统计 |
| connectEnd                 | 连接结束时间        | 返回用户代理向服务器服务器请求文档，建立连接成功后的那个时间，如果此连接是一个长连接，又或者直接从缓存中获取资源（即没有与服务器建立连接）。则返回domainLookupEnd的值 |             |
| requestStart               | 请求开始时间        | 返回从服务器、缓存、本地资源等，开始请求文档的时间           |             |
| responseStart              | 回复开始时间        | 返回用户代理从服务器、缓存、本地资源中，接收到第一个字节数据的时间 |             |
| responseEnd                | 回复结束时间        | 返回用户代理接收到最后一个字符的时间，和当前连接被关闭的时间中，更早的那个。同样，文档可能来自服务器、缓存、或本地资源 |             |
| domLoading                 | DOM开始时间         | 开始渲染dom的时间 , 返回用户代理把其文档的 "current document readiness" 设置为 "loading"的时候 |             |
| domInteractive             | DOM交互时间         | 开始可以进行dom交互的时间，返回用户代理把其文档的 "current document readiness" 设置为 "interactive"的时候. |             |
| domContentLoadedEventStart | DOM内容加载开始时间 | 返回文档发生 DOMContentLoaded 事件的时间                     |             |
| domContentLoadedEventEnd   | DOM内容加载结束时间 | 返回文档 DOMContentLoaded 事件的结束时间                     |             |
| domComplete                | DOM结束时间         | 返回用户代理把其文档的 "current document readiness" 设置为 "complete"的时候 |             |
| loadEventStart             | LOAD开始时间        | 文档触发load事件的时间。如果load事件没有触发，那么该接口就返回0 |             |
| loadEventEnd               | LOAD结束时间        | 文档触发load事件结束后的时间。如果load事件没有触发，那么该接口就返回0 |             |

#### timing 计算公式

客户端只返回原始的数据，服务器端对结果进行计算，并存储到ES中

| 时间         | 计算公式                              | 说明                                                         |
| ------------ | ------------------------------------- | ------------------------------------------------------------ |
| 总时间       | loadEventEnd - navigationStart        |                                                              |
| 重定向时间   | redirectEnd - redirectStart           |                                                              |
| 域名解析时间 | domainLookupEnd - domainLookupStart   |                                                              |
| TCP连接时间  | connectEnd - connectStart             |                                                              |
| SSL连接时间  | connectEnd - secureConnectionStart    | 只对HTTTPS有效                                               |
| 请求时间     | responseStart - requestStart          |                                                              |
| 回复时间     | responseEnd - responseStart           |                                                              |
| DOM解析时间  | domContentLoadedEventEnd - domLoading |                                                              |
| LOAD事件时间 | loadEventEnd - loadEventStart         |                                                              |
|              |                                       |                                                              |
| 首字节时间   | responseStart - navigationStart       | TTFB 即 Time To First Byte 的意思, 读取页面第一个字节的时间, 也叫做白屏时间 |

##### 甘特图说明

总时间 = 重定向时间 + 域名解析时间 + TCP连接时间 + 请求时间 + 回复时间 + DOM解析时间 + LOAD事件时间

#### resources

返回所有的资源信息，格式式json，定义如下

```
{
    "resource1": {},
    "resource2": {},
    ...
}
```

每个单独的资源信息如下

| name                  | 名称             | 说明                                                         | 显示          |
| --------------------- | ---------------- | ------------------------------------------------------------ | ------------- |
| statusCode            | 状态码           | 暂时得不到相关信息                                           |               |
| initiatorType         | 资源类型         | 代表了资源类型                                               |               |
| startTime             | 开始时间         | 获取资源的开始时间                                           |               |
| fetchStart            | 开始时间         | 与startTime相同                                              |               |
| redirectStart         | 重定向开始时间   |                                                              |               |
| redirectEnd           | 重定向结束时间   |                                                              |               |
| domainLookupStart     | 域名解析开始时间 |                                                              |               |
| domainLookupEnd       | 域名解析结束时间 |                                                              |               |
| connectStart          | 连接开始时间     | 浏览器开始和服务器建立连接的时间                             |               |
| secureConnectionStart | 安全连接开始时间 | 浏览器在当前连接下，开始与服务器建立安全握手的时间           | 仅对HTTPS有效 |
| requestStart          | 请求开始时间     |                                                              |               |
| responseStart         | 回复开始时间     |                                                              |               |
| responseEnd           | 回复结束时间     |                                                              |               |
| transferSize          | 资源大小         | 获取资源的大小(采用八进制, 请注意转换), 大小包含了response头部和实体 |               |
| encodedBodySize       |                  | 表示从 HTTP 网络或缓存中接收到的有效内容主体 (Payload Body) 的大小(在删除所有应用内容编码之前) |               |
| decodedBodySize       |                  | 表示从 HTTP 网络或缓存中接收到的消息主体 (Message Body) 的大小(在删除所有应用内容编码之后) |               |

##### resource 计算公式

客户端只返回原始的数据，服务器端对结果进行计算，并存储到ES中

| 时间         | 计算公式                            | 说明           |
| ------------ | ----------------------------------- | -------------- |
| 总时间       | responseEnd- navigationStart        | 或者 duration  |
| 重定向时间   | redirectEnd - redirectStart         |                |
| 域名解析时间 | domainLookupEnd - domainLookupStart |                |
| TCP连接时间  | connectEnd - connectStart           |                |
| SSL连接时间  | connectEnd - secureConnectionStart  | 只对HTTTPS有效 |
| 请求时间     | responseStart - requestStart        |                |
| 回复时间     | responseEnd - responseStart         |                |
|              |                                     |                |

##### 甘特图说明

总时间 = 重定向时间 + 域名解析时间 + TCP连接时间 + 请求时间 + 回复时间