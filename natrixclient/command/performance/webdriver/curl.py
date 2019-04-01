#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pycurl
import logging

from natrixclient.command.performance.webdriver import Browser


logger = logging.getLogger(__name__)
#
#
# '''
# http接口
#
# //处理成功
# {
#     status: 0,
#     taskid: 1,                          #后期添加
#     macaddress: 'ff:ff:ff:ff:ff:ff',    #后期添加
#     create_time: 1234567880,            #后期添加
#     data: {
#         "STARTTRANSFER_TIME": "22.85",
#         "connect_time": "20.17",
#         "HEADER_SIZE": 106,
#         "get_total_time": "22.89",
#         "REDIRECT_TIME": 0.0,
#         "get_status": 200,     #httpcode  404,502,503
#         "download_speed": 47317.0,
#         "download_size": 1083.0,
#         "desturl": "http://www.cnbeta.com",
#         "PRETRANSFER_TIME": "20.27",
#         "dns parse time": "13.75",
#         "REDIRECT_COUNT": 0,
#     }
# }
#
# // 处理失败
# {
#     status: 1,  这里只表示http请求失败,各种原因,网络原因?,pycurl的原因?
#     taskid: 1,                          #后期添加
#     macaddress: 'ff:ff:ff:ff:ff:ff',    #后期添加
#     create_time: 1234567880,            #后期添加
#     data: {
#         "errorcode": 100,
#         "errorinfo": "域名解析失败",
#     }
# }
#
# '''
#
#


class Curl(Browser):
    def __init__(self):
        super(Browser, self).__init__()
        logger.info("output from curl")
        self.browser = pycurl.Curl()

    def get_performance(self, url, default_timeout=60, page_timeout=60, script_timeout=60, delete_cookies=False):
        logger.debug("input http test url = " + url)
        # if not url.startswith("http"):
        #     url = "http://" + url
        # url = url.encode('utf-8')
        logger.debug("transfer http test url = " + url)
        logger.debug("start performan http request = %s" % url)

        # Follow redirect.
        # 允许跳转, 这样对于301, 302这种跳转就直接忽略
        # 如果没有这个参数, 访问 网站 的时候就会出现返回 302
        self.browser.setopt(pycurl.FOLLOWLOCATION, True)
        # 指定HTTP重定向的最大数
        # http_curl.setopt(http_curl.MAXREDIRS, 0)

        # 连接的等待时间，设置为0则不等待
        self.browser.setopt(pycurl.CONNECTTIMEOUT, 10)
        # 请求超时时间
        self.browser.setopt(pycurl.TIMEOUT, 10)
        # 是否屏蔽下载进度条，非0则屏蔽
        self.browser.setopt(pycurl.NOPROGRESS, 1)
        # 指定HTTP重定向的最大次数
        self.browser.setopt(pycurl.MAXREDIRS, 5)
        # 完成交互后强制断开连接，不重用
        self.browser.setopt(pycurl.FORBID_REUSE, 1)
        # 强制获取新的连接，即替代缓存中的连接
        self.browser.setopt(pycurl.FRESH_CONNECT, 1)
        # 设置保存DNS信息的时间，默认为120秒
        self.browser.setopt(pycurl.DNS_CACHE_TIMEOUT, 60)
        # 指定请求的URL
        # http://pycurl.io/docs/latest/unicode.html
        self.browser.setopt(pycurl.URL, url)
        # 配置请求HTTP头的User-Agent
        self.browser.setopt(pycurl.USERAGENT,
                 "Mozilla/5.2 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50324)")

        # 将返回的HTTP HEADER定向到回调函数getheader
        # self.browser.setopt(pycurl.HEADERFUNCTION, getheader)
        # 将返回的内容定向到回调函数getbody
        # self.browser.setopt(pycurl.WRITEFUNCTION, self.string.write)
        self.browser.setopt(pycurl.WRITEFUNCTION, lambda x: None)
        # 将返回的HTTP HEADER定向到fileobj文件对象
        # http_curl.setopt(pycurl.WRITEHEADER, fileobj)
        # 将返回的HTML内容定向到fileobj文件对象
        # http_curl.setopt(pycurl.WRITEDATA, fileobj)

        try:
            self.browser.perform()
            logger.debug("begin to parse url = %s" % url)
            result = self.parse(self.browser, url)
            # logger.debug("http url = %s, result = %s" % (url, json.dumps(result)))
            return result
        except Exception as e:
            error_info = {"errorcode": 122, "errorinfo": e}
            result = {
                "status": 1,
                "data": error_info
            }
            # logger.error("HTTP failed, url = " + url + ", error information = \
            # " + json.dumps(error_info, sort_keys=False))
            return result
        finally:
            self.browser.close()

    # get_status = models.IntegerField(u"GET状态", null=True)
    # get_total_time = models.FloatField(u"GET总时间", null=True)
    # get_parse_time = models.FloatField(u"GET解析时间", null=True)
    # get_connect_time = models.FloatField(u"GET连接时间", null=True)
    # get_first_time = models.FloatField(u"GET首字节时间", null=True)
    # get_download_time = models.FloatField(u"GET下载时间", null=True)
    # get_download_size = models.FloatField(u"GET下载大小", null=True)
    # get_file_size = models.FloatField(u"GET文件大小", null=True)
    # get_download_speed = models.FloatField(u"GET下载速度", null=True)
    def parse(self, http_curl, url):
        # 响应代码  get_status
        http_code = http_curl.getinfo(http_curl.HTTP_CODE)
        # 重定向的次数
        redirect_count = http_curl.getinfo(http_curl.REDIRECT_COUNT)

        # 请求总的时间 get_total_time
        # 传输结束时所消耗的总时间
        total_time = http_curl.getinfo(http_curl.TOTAL_TIME) * 1000
        # DNS解析-->TCP连接-->跳转【如有】-->SSL握手【如有】-->客户端准备-->服务器响应-->数据传输
        # 域名解析时间 ms
        # DNS解析所消耗的时间
        namelookup_time = http_curl.getinfo(http_curl.NAMELOOKUP_TIME) * 1000
        # 建立连接时间 ms
        # 建立连接所消耗的时间
        connect_time = http_curl.getinfo(http_curl.CONNECT_TIME) * 1000
        # 如果存在转向的话，花费的时间
        # 重定向所消耗的时间
        redirect_time = http_curl.getinfo(http_curl.REDIRECT_TIME) * 1000
        # 从发起请求到SSL建立握手时间
        ssl_time = http_curl.getinfo(http_curl.APPCONNECT_TIME) * 1000
        # 连接上后到开始传输时的时间
        # 从建立连接到准备传输所消耗的时间
        pretransfer_time = http_curl.getinfo(http_curl.PRETRANSFER_TIME) * 1000
        # 接收到第一个字节的时间
        # 从建立连接到数据开始传输所消耗的时间
        starttransfer_time = http_curl.getinfo(http_curl.STARTTRANSFER_TIME) * 1000

        # 需要对时间做一些处理
        # 从而让
        # DNS解析-->TCP连接-->跳转【如有】-->SSL握手【如有】-->客户端准备-->服务器响应-->数据传输
        # total_time = namelookup_time + connect_time + redirect_time + ssl_time + client_prepare_time + server_response_time + transfer_time
        # 传输时间
        transfer_time = float(total_time) - float(starttransfer_time)
        # 服务器响应时间，包括网络传输时间
        server_response_time = float(starttransfer_time) - float(pretransfer_time)
        if float(ssl_time) == 0:
            if float(redirect_time) == 0:
                # 客户端准备发送数据时间
                # 客户端发送请求准备时间
                client_prepare_time = float(pretransfer_time) - float(connect_time)
            else:
                client_prepare_time = float(pretransfer_time) - float(redirect_time)
                redirect_time = float(redirect_time) - float(connect_time)
        else:
            client_prepare_time = float(pretransfer_time) - float(ssl_time)

            if float(redirect_time) == 0:
                ssl_time = float(ssl_time) - float(connect_time)
                redirect_time = 0
            else:
                ssl_time = float(ssl_time) - float(redirect_time)
                redirect_time = float(redirect_time) - float(connect_time)

        # 上传数据包大小
        size_upload = http_curl.getinfo(http_curl.SIZE_UPLOAD)
        # 下载的数据大小
        size_download_byte = http_curl.getinfo(http_curl.SIZE_DOWNLOAD)
        # 下载速度
        speed_download_byte = http_curl.getinfo(http_curl.SPEED_DOWNLOAD)
        # 头部大小
        header_size_byte = http_curl.getinfo(http_curl.HEADER_SIZE)

        httpresult = {
            # "status": 0,
            "data": {
                "desturl": url,
                "get_status": http_code,
                "get_total_time": total_time,
                "dns_parse_time": namelookup_time,
                "connect_time": connect_time,
                "redirect_time": redirect_time,
                "ssl_time": ssl_time,
                "client_prepare_time": client_prepare_time,
                "server_response_time": server_response_time,
                "transfer_time": transfer_time,
                "pretransfer_time": pretransfer_time,
                "starttransfer_time": starttransfer_time,
                "header_size": header_size_byte,
                "redirect_count": redirect_count,
                "upload_size": size_upload,
                "download_size": size_download_byte,
                "download_speed": speed_download_byte,
            }
        }
        return httpresult


if __name__ == '__main__':
    test = Curl()
    print(test.get_performance("http://www.souhu.com"))
