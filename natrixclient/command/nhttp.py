# -*- coding: utf-8 -*-


import logging
import pycurl
import re
import time
import threading
from io import BytesIO
from natrixclient.common.const import LOGGING_PATH
from natrixclient.common.const import FILE_MAX_BYTES
from natrixclient.common.const import FILE_BACKUP_COUNTS
from natrixclient.common.const import FILE_LOGGING_DATE_FORMAT
from natrixclient.common.const import HTTP_ALLOW_REDIRECTS
from natrixclient.common.const import HTTP_MAX_REDIRECTS
from natrixclient.common.const import HTTP_AUTH_TYPE
from natrixclient.common.const import HTTP_TIMEOUT
from natrixclient.common.const import HTTP_CONNECT_TIMEOUT
from natrixclient.common.const import HTTP_DNS_CACHE_TIMEOUT
from natrixclient.common.const import HTTP_FRESH_CONNECT
from natrixclient.common.const import HTTP_SAVE_RESPONSE_HEADER
from natrixclient.common.const import HTTP_SAVE_RESPONSE_BODY
from natrixclient.common.const import THREAD_LOGGING_FORMAT
from natrixclient.common.const import AuthType
from natrixclient.common.const import HttpOperation
from natrixclient.command.check.iplocation import IpLocation
from natrixclient.command.storage import storage


"""
#########################################################################################################
请求参数
name                type       comments
==========================================================================================================
http_version        string      HTTP类型, 1.0/1.1/2.0
interface           string      网卡
allow_redirect      boolean     是否允许转发
max_redirect        int         转发最大此书
connect_timeout     int         请求连接超时时间, 单位秒
                                Timeout for the connection phase
                                缺省300秒
accept_timeout      int         请求恢复超时时间, 单位秒
                                Timeout for waiting for the server's connect back to be accepted
                                default 60000 milliseconds
                                只用于FTP协议
request_timeout     int         整个请求超时时间, 单位秒
                                Timeout for the entire request
                                Default timeout is 0 (zero) which means it never times out during transfer
dns_cache_timeout   int         设置保存DNS信息的时间，默认为60秒
header              列表         http头部信息
body                dict        body信息, 用于post和put
user_agent          string      代理浏览器信息
dns_servers         string      dns server列表, 以逗号分割
proxies             json        使用的代理
keep_alive          boolean     TCP保持连接
fresh_connect       boolean     强制获取新的连接，即替代缓存中的连接
                                Use a new connection
save_response_header    boolean     是否保存response的头部信息
save_response_body      boolean     是否保存response的body信息    

#########################################################################################################
得到的原始数据信息
https://curl.haxx.se/libcurl/c/curl_easy_getinfo.html
name                type       comments
==========================================================================================================
url                 string      请求URL
effect_url          string      最后一次请求的URL
                                Last used URL
status_code         string      Last received response code
                                来自 HTTP_CODE 或 RESPONSE_CODE
redirect_count      int         重定向次数
redirect_time       float       Time taken for all redirect steps before the final transfer
                                整个过程重定向的耗时，如果整个过程没有重定向，这个时间为0
primary_ip          string      最后一次连接的IP地址
                                IP address of the last connection
primary_port        int         最后一次连接的端口号
                                Port of the last connection.
local_ip            string      Local-end IP address of last connection
local_port          int         Local-end port of last connection
totoal_time         float       Total time of previous transfer
nslookup_time       float       Time from start until name resolving completed    
connect_time        float       Time from start until remote host or proxy completed
appconnect_time     float       Time from start until SSL/SSH handshake completed
pretransfer_time    float       Time from start until just before the transfer begins
starttransfer_time  float       Time from start until just when the first byte is received.
size_upload         float       Number of bytes uploaded
size_download       float       Number of bytes downloaded
speed_upload        float       Average upload speed
speed_download      float       Average download speed
request_size        float       Number of bytes sent in the issued HTTP requests
                                忽略
response_content_type   string  Content type from the Content-Type header.
                                忽略
response_header_size    float   Number of bytes of all headers received
                                取自HEADER_SIZE
                                忽略

#########################################################################################################
time信息说明
|
|--NAMELOOKUP
|--|--CONNECT
|--|--|--APPCONNECT
|--|--|--|--PRETRANSFER
|--|--|--|--|--STARTTRANSFER
|--|--|--|--|--|--TOTAL
|--|--|--|--|--|--REDIRECT    


#########################################################################################################
返回的数据信息
https://curl.haxx.se/libcurl/c/curl_easy_getinfo.html
name                type       comments
==========================================================================================================
url                 string      请求URL
effect_url          string      最后一次请求的URL
                                Last used URL
status_code         string      Last received response code
                                来自 HTTP_CODE 或 RESPONSE_CODE
redirect_count      int         重定向次数
redirect_time       float       Time taken for all redirect steps before the final transfer
                                整个过程重定向的耗时，如果整个过程没有重定向，这个时间为0
remote_ip           string      最后一次连接的IP地址
                                IP address of the last connection
                                remote_ip = primary_ip
remote_port         int         最后一次连接的端口号
                                Port of the last connection.
                                remote_port = primary_port
local_ip            string      Local-end IP address of last connection
                                最后一次连接的本地IP地址
local_port          int         Local-end port of last connection
                                最后一次连接的本地端口号
totoal_time         float       Total time of previous transfer
period_nslookup     float       域名解析耗时
                                period_nslookup = nslookup_time
period_tcp_connect  float       TCP连接耗时
                                period_tcp_connect = connect_time - nslookup_time
period_ssl_connect  float       SSL连接耗时
                                if appconnect_time > connect time:
                                    period_ssl_connect = appconnect_time - connect_time
                                else：
                                    period_ssl_connect = 0
period_request      float       Request请求耗时
                                if appconnect_time > connect_time:
                                    period_request = pre_transfer_time - appconnect_time
                                else:
                                    period_request = pre_transfer_time - connect_time
period_response     float       Response处理耗时, 服务器处理耗时
                                period_response = start_transfer_time - pre_transfer_time
period_transfer     float       Response传输耗时
                                period_transfer = total_time - start_transfer_time 
                                
totoal_time = period_nslookup + period_tcp_connect + period_ssl_connect 
              + period_request + period_response + period_transfer
                                
size_upload         float       Number of bytes uploaded
size_download       float       Number of bytes downloaded
speed_upload        float       Average upload speed
                                单位 bytes/second
speed_download      float       Average download speed
                                单位 bytes/second
header_size         float       Number of bytes of all headers received
               
"""


logger = logging.getLogger(__name__)


def add_logger_handler(logger):
    fn = LOGGING_PATH + 'natrixclient_http.log'
    fh = logging.handlers.RotatingFileHandler(filename=fn, maxBytes=FILE_MAX_BYTES, backupCount=FILE_BACKUP_COUNTS)
    fh.setLevel(logging.DEBUG)
    fh_fmt = logging.Formatter(fmt=THREAD_LOGGING_FORMAT, datefmt=FILE_LOGGING_DATE_FORMAT)
    fh.setFormatter(fh_fmt)
    logger.addHandler(fh)


def execute(operation, destination, request_parameters, response_parameters):
    if request_parameters.get("logger"):
        global logger
        logger = logging.getLogger(request_parameters.get("logger"))
        add_logger_handler(logger)
    
    logger.info("==================HTTP EXECUTE========================")
    # TODO, need to check interface exist and connection
    # execute http
    HttpThread(operation, destination, request_parameters, response_parameters).start()


class HttpThread(threading.Thread):
    def __init__(self, operation, destination, request_parameters, response_parameters):
        threading.Thread.__init__(self)
        self.operation = operation
        self.destination = destination
        self.request_parameters = request_parameters
        self.response_parameters = response_parameters

    def run(self):
        action_msg = "http {} {}".format(self.operation, self.destination)
        http_obj = HttpTest(self.operation, self.destination, self.request_parameters)
        logger.debug("starting {} ......".format(action_msg))
        http_dict = http_obj.execute()
        logger.debug("processing {} response: command ......".format(action_msg))
        if self.response_parameters.get("command_uuid"):
            command = dict()
            command["uuid"] = self.response_parameters.get("command_uuid")
            command["terminal"] = self.response_parameters.get("command_terminal")
            http_dict["command"] = command

        logger.debug("saving {} result ......".format(action_msg))
        storage(result=http_dict, parameters=self.response_parameters)


class HttpTest(object):
    def __init__(self, operation, destination, parameters):
        self.operation = operation
        self.destination = destination
        # parameters
        self.parameters = parameters
        # logger
        if parameters.get("logger"):
            global logger
            logger = logging.getLogger(parameters.get("logger"))
            add_logger_handler(logger)
        # 设置 HTTP VERSION
        # self.http_version = parameters.get("http_version", None)
        self.interface = parameters.get("interface", None)
        self.allow_redirects = parameters.get("allow_redirects", HTTP_ALLOW_REDIRECTS)
        self.max_redirects = parameters.get("max_redirects", HTTP_MAX_REDIRECTS)
        self.auth_type = parameters.get("auth_type", HTTP_AUTH_TYPE)
        self.auth_user = parameters.get("auth_user", None)
        self.timeout = parameters.get("timeout", HTTP_TIMEOUT)
        self.connect_timeout = parameters.get("connect_timeout", HTTP_CONNECT_TIMEOUT)
        # self.request_timeout = parameters.get("request_timeout", const.HTTP_REQUEST_TIMEOUT)
        self.dns_cache_timeout = parameters.get("dns_cache_timeout", HTTP_DNS_CACHE_TIMEOUT)
        self.fresh_connect = parameters.get("fresh_connect", HTTP_FRESH_CONNECT)
        # self.user_agent = parameters.get("user_agent", const.HTTP_USER_AGENT)
        self.http_header = parameters.get("http_header", None)
        self.http_body = parameters.get("http_body", None)
        self.save_response_header = parameters.get("save_response_header", HTTP_SAVE_RESPONSE_HEADER)
        self.response_header_buffer = None
        self.response_header = None
        self.response_headers = None
        self.save_response_body = parameters.get("save_response_body", HTTP_SAVE_RESPONSE_BODY)
        self.response_body_buffer = None
        self.response_body = None
        self.pcurl = pycurl.Curl()
        # 指定请求的URL
        # http://pycurl.io/docs/latest/unicode.html
        self.pcurl.setopt(pycurl.URL, self.destination)
        # 时间戳
        self.server_request_generate_time = parameters.get("server_request_generate_time")
        self.terminal_request_receive_time = parameters.get("terminal_request_receive_time")
        self.terminal_request_send_time = None
        self.terminal_response_receive_time = None
        # 结果
        self.http_result = None

    def execute(self):
        if self.operation == HttpOperation.GET:
            return self.get()
        elif self.operation == HttpOperation.POST:
            return self.post()
        elif self.operation == HttpOperation.PUT:
            return self.put()
        elif self.operation == HttpOperation.DELETE:
            return self.delete()
        else:
            logger.error("ERROR: Do not support {}, just support GET/POST/PUT/DELETE".format(self.operation))

    def get(self):
        # 计算结果
        get_result = self.calc_result()
        return get_result

    def post(self):
        # https://curl.haxx.se/libcurl/c/CURLOPT_POST.html
        # 设置POST
        # request an HTTP POST
        # DEFAULT 0, disabled
        # A parameter set to 1 tells libcurl to do a regular HTTP post.
        # This will also make the library use a
        # "Content-Type: application/x-www-form-urlencoded" header.
        # (This is by far the most commonly used POST method).
        self.pcurl.setopt(pycurl.POST, True)

        # 设置body
        if self.http_body:
            # TODO, 检查body格式
            # postfields = urlencode(self.http_body)
            self.pcurl.setopt(pycurl.POSTFIELDS, self.http_body)

        # TODO, 实现文件上传
        # Upload data, DEFAULT 0, default is download
        # c.setopt(pycurl.UPLOAD, True)

        # 计算结果
        post_result = self.calc_result()
        return post_result

    def put(self):
        # 设置PUT
        # c.setopt(pycurl.PUT, True)
        self.pcurl.setopt(pycurl.CUSTOMREQUEST, "PUT")

        # 设置body
        if self.http_body:
            # TODO, 检查body格式
            self.pcurl.setopt(pycurl.POSTFIELDS, self.http_body)

        # TODO, 实现文件上传
        # Upload data, DEFAULT 0, default is download
        # c.setopt(pycurl.UPLOAD, True)

        # 计算结果
        get_result = self.calc_result()
        return get_result

    def delete(self):
        # 设置 DELETE
        self.pcurl.setopt(pycurl.CUSTOMREQUEST, "DELETE")

        # 设置body
        if self.http_body:
            # TODO, 检查body格式
            # postfields = urlencode(self.http_body)
            self.pcurl.setopt(pycurl.POSTFIELDS, self.http_body)

        # TODO, 实现文件上传
        # Upload data, DEFAULT 0, default is download
        # c.setopt(pycurl.UPLOAD, True)

        # 计算结果
        delete_result = self.calc_result()
        return delete_result

    def calc_result(self):
        # if self.http_version:
        #     if "1.0" == self.http_version:
        #         self.pcurl.setopt(pycurl.HTTP_VERSION, pycurl.CURL_HTTP_VERSION_1_0)
        #     elif "1.1" == self.http_version:
        #         self.pcurl.setopt(pycurl.HTTP_VERSION, pycurl.CURL_HTTP_VERSION_1_1)
        #     elif "2.0" == self.http_version:
        #         self.pcurl.setopt(pycurl.HTTP_VERSION, pycurl.CURL_HTTP_VERSION_2_0)
        #     else:
        #         self.pcurl.setopt(pycurl.HTTP_VERSION, pycurl.CURL_HTTP_VERSION_NONE)

        # 设置网卡
        # Bind connection locally to this
        # source interface for outgoing traffic
        if self.interface:
            self.pcurl.setopt(pycurl.INTERFACE, self.interface)

        # 重定向 redirect
        # 允许跳转, 这样对于301, 302这种跳转就直接忽略
        # 指定HTTP重定向的最大数, 只有允许重定向的时候才有意义
        if self.allow_redirects:
            self.pcurl.setopt(pycurl.FOLLOWLOCATION, True)
            self.pcurl.setopt(pycurl.MAXREDIRS, self.max_redirects)
        else:
            self.pcurl.setopt(pycurl.FOLLOWLOCATION, False)

        # 整个请求超时时间
        self.pcurl.setopt(pycurl.TIMEOUT, self.timeout)

        # 请求连接的等待时间
        # 设置为0则不超时
        # natrix设置默认连接超时 1 分钟
        self.pcurl.setopt(pycurl.CONNECTTIMEOUT, self.connect_timeout)

        # 设置保存DNS信息的时间，默认为60秒
        self.pcurl.setopt(pycurl.DNS_CACHE_TIMEOUT, self.dns_cache_timeout)

        # 强制获取新的连接，即替代缓存中的连接
        # 缺省是0, 代表可以使用老的连接
        # natrix默认每次强制获取新连接
        self.pcurl.setopt(pycurl.FRESH_CONNECT, self.fresh_connect)

        # 验证
        if self.auth_user:
            if self.auth_type == AuthType.BASIC.value:
                self.pcurl.setopt(pycurl.HTTPAUTH, pycurl.HTTPAUTH_BASIC)
                self.pcurl.setopt(pycurl.USERPWD, self.auth_user)

        # 配置请求HTTP头的User-Agent
        # self.pcurl.setopt(pycurl.USERAGENT, self.user_agent)

        # 设置头部信息
        if self.http_header:
            self.pcurl.setopt(pycurl.HTTPHEADER, [self.http_header])

        # 是否屏蔽下载进度条，非0则屏蔽
        # switch off the progress meter
        # DEFAULT 1, meaning it normally runs without a progress meter.
        self.pcurl.setopt(pycurl.NOPROGRESS, 1)
        # 完成交互后强制断开连接，不重用
        self.pcurl.setopt(pycurl.FORBID_REUSE, 1)
        # Display verbose information
        # set verbose mode on/off
        # Set the onoff parameter to 1 to make the library display a lot of verbose information
        # about its operations on this handle.
        # Very useful for libcurl and/or protocol debugging and understanding.
        # DEFAULT, 0, meaning disabled.
        self.pcurl.setopt(pycurl.VERBOSE, 0)

        # 将返回的HTTP HEADER定向到回调函数getheader
        if self.save_response_header:
            # TODO, 前期通过header字段返回, 后期直接保存成文件返回
            self.response_header_buffer = BytesIO()
            self.pcurl.setopt(pycurl.WRITEHEADER, self.response_header_buffer)

        # 如果不对WRITEDATA进行重定向,默认就会打印到console
        # if self.save_response_body:
        # TODO, 前期通过body字段返回, 后期直接保存成html文件返回
        self.response_body_buffer = BytesIO()
        # PycURL does not provide storage for the network response - that is the application’s job
        self.pcurl.setopt(pycurl.WRITEDATA, self.response_body_buffer)

        try:
            self.terminal_request_send_time = time.time()
            self.pcurl.perform()
            self.terminal_response_receive_time = time.time()
            logger.debug("begin to parse url = %s" % self.destination)
            self.parse_response_info()
            # 得到返回的header快照
            if self.save_response_header:
                self.parse_response_header()
            # 得到返回的body快照
            if self.save_response_body:
                self.parse_response_body()
        except pycurl.error as e:
            # http://pycurl.io/docs/latest/callbacks.html#error-reporting
            error_info = {"errorcode": e.args[0], "errorinfo": e.args[1]}
            self.http_result = {
                "status": 1,
                "data": error_info,
                "stamp": {
                    "server_request_generate_time": self.server_request_generate_time,
                    "terminal_request_receive_time": self.terminal_request_receive_time,
                    "terminal_request_send_time": self.terminal_request_send_time,
                    "terminal_response_receive_time": self.terminal_response_receive_time,
                }
            }
        except Exception as e:
            logger.exception("this is a http exception message!")
            # TODO, 需要将HTTP Exception ERROR 仔细做好分类
            error_info = {"errorcode": 122, "errorinfo": e.message}
            self.http_result = {
                "status": 1,
                "data": error_info,
                "stamp": {
                    "server_request_generate_time": self.server_request_generate_time,
                    "terminal_request_receive_time": self.terminal_request_receive_time,
                    "terminal_request_send_time": self.terminal_request_send_time,
                    "terminal_response_receive_time": self.terminal_response_receive_time,
                }
            }
        finally:
            self.pcurl.close()
        return self.http_result

    def parse_response_info(self):
        # 最后一次请求的URL
        last_url = self.pcurl.getinfo(pycurl.EFFECTIVE_URL)
        # 响应代码  get_status
        http_code = self.pcurl.getinfo(pycurl.HTTP_CODE)
        # 重定向
        # 重定向次数
        redirect_count = self.pcurl.getinfo(pycurl.REDIRECT_COUNT)
        # 如果存在转向的话，花费的时间
        # 重定向所消耗的时间
        redirect_time = self.pcurl.getinfo(pycurl.REDIRECT_TIME) * 1000
        # TODO, 重定向历史信息
        # 最后一次连接的远程IP地址
        ipt = IpLocation(self.parameters)
        remote_ip = self.pcurl.getinfo(pycurl.PRIMARY_IP)
        remote_location = ipt.get_location(remote_ip)
        # TODO, 通过IP信息得到地址和地域信息
        # 最后一次连接的远程端口号
        remote_port = self.pcurl.getinfo(pycurl.PRIMARY_PORT)
        # 最后一次连接的本地IP地址
        local_ip = self.pcurl.getinfo(pycurl.LOCAL_IP)
        local_location = ipt.get_location(local_ip)
        # 最后一次连接的本地端口号
        local_port = self.pcurl.getinfo(pycurl.LOCAL_PORT)

        # 时间信息
        # 请求总的时间 get_total_time
        # 传输结束时所消耗的总时间
        total_time = self.pcurl.getinfo(pycurl.TOTAL_TIME) * 1000
        # DNS解析-->TCP连接-->跳转【如有】-->SSL握手【如有】-->客户端准备-->服务器响应-->数据传输
        # 域名解析时间 ms
        # DNS解析所消耗的时间
        namelookup_time = self.pcurl.getinfo(pycurl.NAMELOOKUP_TIME) * 1000
        # 建立连接时间 ms
        # 建立连接所消耗的时间
        connect_time = self.pcurl.getinfo(pycurl.CONNECT_TIME) * 1000
        # 从发起请求到SSL建立握手时间
        appconnect_time = self.pcurl.getinfo(pycurl.APPCONNECT_TIME) * 1000
        # 连接上后到开始传输时的时间
        # 从建立连接到准备传输所消耗的时间
        pretransfer_time = self.pcurl.getinfo(pycurl.PRETRANSFER_TIME) * 1000
        # 接收到第一个字节的时间
        # 从建立连接到数据开始传输所消耗的时间
        starttransfer_time = self.pcurl.getinfo(pycurl.STARTTRANSFER_TIME) * 1000

        # 需要对时间做一些处理
        # 从而让
        # DNS解析-->TCP连接-->SSL握手(如有)-->客户端准备-->服务器响应-->数据传输
        # totoal_time = period_nslookup + period_tcp_connect + period_ssl_connect
        # + period_request + period_response + period_transfer
        # TCP连接耗时
        period_tcp_connect = connect_time - namelookup_time
        # SSL连接耗时
        if appconnect_time > connect_time:
            period_ssl_connect = appconnect_time - connect_time
        else:
            period_ssl_connect = 0
        # Request请求耗时
        if appconnect_time > connect_time:
            period_request = pretransfer_time - appconnect_time
        else:
            period_request = pretransfer_time - connect_time
        # Response处理耗时
        period_response = starttransfer_time - pretransfer_time
        # Response传输耗时
        period_transfer = float(total_time) - float(starttransfer_time)

        # 数据信息
        # 上传数据包大小
        size_upload = self.pcurl.getinfo(pycurl.SIZE_UPLOAD)
        # 下载数据包大小
        size_download = self.pcurl.getinfo(pycurl.SIZE_DOWNLOAD)
        # 上传速度
        speed_upload = self.pcurl.getinfo(pycurl.SPEED_UPLOAD)
        # 下载速度
        speed_download = self.pcurl.getinfo(pycurl.SPEED_DOWNLOAD)
        # 头部大小
        header_size = self.pcurl.getinfo(pycurl.HEADER_SIZE)

        self.http_result = {
            "status": 0,
            "data": {
                "url": self.destination,
                "last_url": last_url,
                "status_code": http_code,
                "redirect_count": redirect_count,
                "redirect_time": redirect_time,
                "remote_ip": remote_ip,
                "remote_location": remote_location,
                "remote_port": remote_port,
                "local_ip": local_ip,
                "local_location": local_location,
                "local_port": local_port,
                "total_time": total_time,
                "period_nslookup": namelookup_time,
                "period_tcp_connect": period_tcp_connect,
                "period_ssl_connect": period_ssl_connect,
                "period_request": period_request,
                "period_response": period_response,
                "period_transfer": period_transfer,
                "header_size": header_size,
                "size_upload": size_upload,
                "size_download": size_download,
                "speed_upload": speed_upload,
                "speed_download": speed_download,
            },
            "stamp": {
                "server_request_generate_time": self.server_request_generate_time,
                "terminal_request_receive_time": self.terminal_request_receive_time,
                "terminal_request_send_time": self.terminal_request_send_time,
                "terminal_response_receive_time": self.terminal_response_receive_time,
            }
        }
        return self.http_result

    def parse_response_header(self):
        encoding = 'iso-8859-1'
        # HTTP standard specifies that headers are encoded in iso-8859-1.
        # On Python 2, decoding step can be skipped.
        # On Python 3, decoding step is required.
        self.response_header = self.response_header_buffer.getvalue().decode(encoding)
        self.http_result["data"]["response_header"] = self.response_header

        self.response_headers = {}
        # 返回例子
        # HTTP/1.1 200 OK
        # server: Cowboy
        # date: Mon, 21 Jan 2019 07:35:36 GMT
        # content-length: 61
        # content-type: application/json\
        # vary: accept, accept-encoding, origin
        # Cache-Control: no-cache
        # Header lines include the first status line (HTTP/1.x ...).
        # We are going to ignore all lines that don't have a colon in them.
        # This will botch headers that are split on multiple lines...
        for header_line in self.response_header.split("\n"):
            if ':' not in header_line:
                return
            # Break the header line into header name and value.
            name, value = header_line.split(':', 1)
            # Remove whitespace that may be present.
            # Header lines include the trailing newline, and there may be whitespace
            # around the colon.
            name = name.strip()
            value = value.strip()
            # Header names are case insensitive.
            # Lowercase name here.
            name = name.lower()
            # Now we can actually record the header name and value.
            # Note: this only works when headers are not duplicated, see below.
            self.response_headers[name] = value
        return self.response_header

    def parse_response_body(self):
        body = self.response_body_buffer.getvalue()
        # 使用header自己的编码信息
        encoding = 'iso-8859-1'
        if self.response_headers and 'content-type' in self.response_headers:
            content_type = self.response_headers['content-type'].lower()
            match = re.search('charset=(\S+)', content_type)
            if match:
                encoding = match.group(1)
                logger.debug('Decoding using %s' % encoding)
        self.response_body = body.decode(encoding)
        self.http_result["data"]["response_body"] = self.response_body
        return self.response_body
