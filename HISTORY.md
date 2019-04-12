# 1.0.1
## 预计发布时间
2019-04-30
## 预期功能
- 兼容python2
- 兼容更多硬件和操作系统
- 兼容docker
- 兼容MQTT协议
- 多线程优化
- 功能完善
- 添加测试用例,提高代码测试覆盖率
- 支持具备sudo权限的用户
- 对于高敏感度信息, 例如用户名密码等,做好加密的操作
- 网站支持HTTPS


# 0.1.3
## 主要功能
通过如下操作系统测试
raspbian wheezy
raspbian jessie
raspbian strech
ubuntu 18
centos 7

通过如下Python测试
python 2.7
python 3.4 + 

# 0.1.2
## 主要功能
文档对于每个上报的信息都规定了 必须, 空值 2项信息   
network新增加了一些static method   
static method 增加 logger 传递   
修正 report advance功能   

# 0.1.1
## 发布日期
2019-03-31
## 主要功能
功能
- PING
- DNS
- TRACEROUTE
- HTTP

安装方式
- pip
- systemd

使用方式
- API调用
- SHELL调用
- SYSTEMD服务

CONFIGURATION DIRECTORY     
/etc/natrix/natrix.ini

LOG DIRECTORY   
/var/log/natrix 
