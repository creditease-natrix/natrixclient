#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json


class Browser(object):
    def __init__(self, headless=True):
        self.browser = None
        self.headless = headless

    """
    parames format
    {
        "implicitly_wait": 3,
        "page_load_timeout": 4,
        "script_timeout": 5,
        "use_cookies": False,
        "proxy": {
            "type": "static/pac/auto"
            "proxy": {
                # see proxy below
            }
        }
    }
    .implicitly_wait(2)
        time unit is second
        Sets a sticky timeout to implicitly wait for an element to be found, or a command to complete. 
        This method only needs to be called one time per session. 
        To set the timeout for calls to execute_async_script, see set_script_timeout.
    .set_script_timeout(3)
        Set the amount of time that the script should wait during an execute_async_script call before throwing an error.
    .set_page_load_timeout(300)
        Set the amount of time to wait for a page load to complete before throwing an error.
    .add_cookie(cookie)
        add cookie, ignore
    .delete_all_cookies()   
        delete cookie
    proxy use
        https://github.com/SeleniumHQ/selenium/blob/master/py/test/selenium/webdriver/common/proxy_tests.py
        MANUAL_PROXY = {
            'httpProxy': 'some.url:1234',
            'ftpProxy': 'ftp.proxy',
            'noProxy': 'localhost, foo.localhost',
            'sslProxy': 'ssl.proxy:1234',
            'socksProxy': 'socks.proxy:65555',
            'socksUsername': 'test',
            'socksPassword': 'test',
        }

        PAC_PROXY = {
            'proxyAutoconfigUrl': 'http://pac.url:1234',
        }

        AUTODETECT_PROXY = {
            'autodetect': True,
        }
    screenshot
        .get_screenshot_as_file(self, filename)
        .save_screenshot(self, filename)
        .get_screenshot_as_png(self)
        .get_screenshot_as_base64(self)

    desired_capabilities
        {
            u 'takesScreenshot': True, 
            u 'acceptSslCerts': True, 
            u 'networkConnectionEnabled': False, 
            u 'mobileEmulationEnabled': False, 
            u 'unexpectedAlertBehaviour': u '', 
            u 'applicationCacheEnabled': False, 
            u 'locationContextEnabled': True, 
            u 'rotatable': False, 
            u 'chrome': {
                u 'chromedriverVersion': u '2.33.506092 (733a02544d189eeb751fe0d7ddca79a0ee28cce4)',
                u 'userDataDir': u '/tmp/.org.chromium.Chromium.3movVU'
            }, 
            u 'hasTouchScreen': False, 
            u 'platform': u 'Linux', 
            u 'version': u '69.0.3497.100', 
            u 'nativeEvents': True, 
            u 'handlesAlerts': True, 
            u 'takesHeapSnapshot': True, 
            u 'javascriptEnabled': True, 
            u 'databaseEnabled': False, 
            u 'browserName': u 'chrome', 
            u 'webStorageEnabled': True, 
            u 'browserConnectionEnabled': False, 
            u 'cssSelectorsEnabled': True, 
            u 'setWindowRect': True, 
            u 'pageLoadStrategy': u 'normal'
        }

    https://www.w3.org/TR/navigation-timing/
    https://www.w3.org/TR/navigation-timing-2/
    https://developer.mozilla.org/en-US/docs/Web/API/Performance
    https://www.ibm.com/developerworks/cn/data/library/bd-r-javascript-w3c/
    Performance Timing Events flow
        navigationStart -> redirectStart -> redirectEnd -> fetchStart -> domainLookupStart -> domainLookupEnd
        -> connectStart -> connectEnd -> requestStart -> responseStart -> responseEnd
        -> domLoading -> domInteractive -> domContentLoaded -> domComplete -> loadEventStart -> loadEventEnd
    window.performance.timing返回值
    navigationStart 准备加载新页面的起始时间
    redirectStart	如果发生了HTTP重定向，并且从导航开始，中间的每次重定向，都和当前文档同域的话，就返回开始重定向的timing.fetchStart的值。其他情况，则返回0
    redirectEnd	    如果发生了HTTP重定向，并且从导航开始，中间的每次重定向，都和当前文档同域的话，就返回最后一次重定向，接收到最后一个字节数据后的那个时间.其他情况则返回0
    fetchStart	    如果一个新的资源获取被发起，则 fetchStart必须返回用户代理开始检查其相关缓存的那个时间，其他情况则返回开始获取该资源的时间
    domainLookupStart	返回用户代理对当前文档所属域进行DNS查询开始的时间。如果此请求没有DNS查询过程，如长连接，资源cache,甚至是本地资源等。 那么就返回 fetchStart的值
    domainLookupEnd	    返回用户代理对结束对当前文档所属域进行DNS查询的时间。如果此请求没有DNS查询过程，如长连接，资源cache，甚至是本地资源等。那么就返回 fetchStart的值
    connectStart	    返回用户代理向服务器服务器请求文档，开始建立连接的那个时间，如果此连接是一个长连接，又或者直接从缓存中获取资源（即没有与服务器建立连接）。则返回domainLookupEnd的值
    (secureConnectionStart) 可选特性。用户代理如果没有对应的东东，就要把这个设置为undefined。如果有这个东东，并且是HTTPS协议，那么就要返回开始SSL握手的那个时间。 如果不是HTTPS， 那么就返回0
    connectEnd	    返回用户代理向服务器服务器请求文档，建立连接成功后的那个时间，如果此连接是一个长连接，又或者直接从缓存中获取资源（即没有与服务器建立连接）。则返回domainLookupEnd的值
    requestStart	返回从服务器、缓存、本地资源等，开始请求文档的时间
    responseStart	返回用户代理从服务器、缓存、本地资源中，接收到第一个字节数据的时间
    responseEnd	    返回用户代理接收到最后一个字符的时间，和当前连接被关闭的时间中，更早的那个。同样，文档可能来自服务器、缓存、或本地资源
    domLoading
        开始渲染dom的时间   
        返回用户代理把其文档的 "current document readiness" 设置为 "loading"的时候
    domInteractive   
        返回用户代理把其文档的 "current document readiness" 设置为 "interactive"的时候.
    domContentLoadedEventStart	
        开始触发DomContentLoadedEvent事件的时间
        返回文档发生 DOMContentLoaded 事件的时间
    domContentLoadedEventEnd	
        DomContentLoadedEvent事件结束的时间
        返回文档 DOMContentLoaded 事件的结束时间
    domComplete	    
        返回用户代理把其文档的 "current document readiness" 设置为 "complete"的时候
    loadEventStart	
        文档触发load事件的时间。如果load事件没有触发，那么该接口就返回0
    loadEventEnd	
        文档触发load事件结束后的时间。如果load事件没有触发，那么该接口就返回0
    navigation返回值计算
    总时间       loadEventEnd - navigationStart
    重定向耗时	redirectEnd - redirectStart
    DNS缓存时间   domainLookupStart - fetchStart;
    DNS查询耗时	domainLookupEnd - domainLookupStart
    TCP连接耗时	connectEnd - connectStart
    SSL连接耗时  connectEnd - secureConnectionStart
    Request请求耗时	responseStart - requestStart
    Response返回耗时	responseEnd - responseStart
    解析DOM耗时	    domContentLoadedEventEnd - domLoading
    加载Load事件耗时  loadEventEnd - loadEventStart
    TTFB
        读取页面第一个字节的时间
        TTFB 即 Time To First Byte 的意思
        https://en.wikipedia.org/wiki/Time_To_First_Byte
        responseStart - navigationStart;
    白屏时间
    	responseStart - navigationStart
    domready时间
    	domContentLoadedEventEnd - navigationStart
    onload时间 
        执行 onload 回调函数的时间	
        loadEventEnd - navigationStart

    https://www.w3.org/TR/resource-timing-1/
    https://www.w3.org/TR/resource-timing-2/
    https://developer.mozilla.org/en-US/docs/Web/API/PerformanceResourceTiming
    所有网络请求都被视为资源。通过网络对它们进行检索时，资源具有不同生命周期
    Resource Timing API 为网络事件（如重定向的开始和结束事件, DNS查找的开始和结束事件, 请求开始, 响应开始和结束时间等）生成有高分辨率时间戳( high-resolution timestamps )的资源加载时间线, 并提供了资源大小和资源类型
    通过Resource Timing API可以获取和分析应用资源加载的详细网络计时数据, 应用程序可以使用时间度量标准来确定加载特定资源所需要的时间，比如 XMLHttpRequest、<SVG>、图片、或者脚本
    resource timing 返回值
    name
        Returns the resources URL
        资源URL
        请求资源的绝对地址, 即便请求重定向到一个新的地址此属性也不会改变
    entryType
        Returns "resource"
        统一返回resource
        PerformanceResourceTiming 对象的 entryType 属性永远返回字符串 "resource"
    initiatorType
        代表了资源类型
        简单来说 initiatorType 属性返回的内容代表资源是从哪里发生的请求行为.
        initiatorType 属性会返回下面列表中列出的字符串中的其中一个:
            css	如果请求是从 CSS 中的 url() 指令发出的
            xmlhttprequest	通过 XMLHttpRequest 对象发出的请求
            fetch	通过 Fetch 方法发出的请求
            beacon	通过 beacon 方法发出的请求
            link	通过 link 标签发出的请求
            script	通过 script 标签发出的请求
            iframe	通过 iframe 标签发出的请求
            other	没有匹配上面条件的请求
    startTime
        Returns the timestamp for the time a resource fetch started. This value is equivalent to PerformanceEntry.fetchStart
        获取资源的开始时间
        用户代理开始排队获取资源的时间. 如果 HTTP 重定则该属性与 redirectStart 属性相同, 其他情况该属性将与 fetchStart 相同
    fetchStart
        A DOMHighResTimeStamp immediately before the browser starts to fetch the resource.
        与startTime相同
    redirectStart 
        A DOMHighResTimeStamp that represents the start time of the fetch which initiates the redirect.
        重定向开始时间
    redirectEnd	
        A DOMHighResTimeStamp immediately after receiving the last byte of the response of the last redirect.
        重定向结束时间
    duration
        Returns a timestamp that is the difference between the responseEnd and the startTime properties.
        startTime与responseEnd的差值
    domainLookupStart
        A DOMHighResTimeStamp immediately before the browser starts the domain name lookup for the resource.
        域名解析开始时间
    domainLookupEnd
        A DOMHighResTimeStamp representing the time immediately after the browser finishes the domain name lookup for the resource
        域名解析结束时间
    connectStart
        浏览器开始和服务器建立连接的时间
    secureConnectionStart
        浏览器在当前连接下，开始与服务器建立安全握手的时间
    connectEnd
        浏览器与服务器建立连接结束时间
    requestStart
        A DOMHighResTimeStamp immediately before the browser starts requesting the resource from the server.
    responseStart
        A DOMHighResTimeStamp immediately after the browser receives the first byte of the response from the server.
    responseEnd
        A DOMHighResTimeStamp immediately after the browser receives the last byte of the resource or immediately before the transport connection is closed, whichever comes first.
    transferSize
        A number representing the size (in octets) of the fetched resource. The size includes the response header fields plus the response payload body
        获取资源的大小(采用八进制, 请注意转换), 大小包含了response头部和实体
    encodedBodySize
        A number representing the size (in octets) received from the fetch (HTTP or cache), of the payload body, before removing any applied content-codings.
        表示从 HTTP 网络或缓存中接收到的有效内容主体 (Payload Body) 的大小(在删除所有应用内容编码之前)
    decodedBodySize
        A number that is the size (in octets) received from the fetch (HTTP or cache) of the message body, after removing any applied content-codings.
        表示从 HTTP 网络或缓存中接收到的消息主体 (Message Body) 的大小(在删除所有应用内容编码之后)
    resourcce timing 计算公式
    https://www.cnblogs.com/zhuyang/p/4789020.html
    总时间   
        duration    
        loadEventEnd - startTime
    重定向耗时	redirectEnd - redirectStart
    DNS缓存时间   domainLookupStart - fetchStart;
    DNS查询耗时	domainLookupEnd - domainLookupStart
    TCP连接耗时	connectEnd - connectStart
    SSL连接耗时  connectEnd - secureConnectionStart
    Request请求耗时	responseStart - requestStart
    Response返回耗时	responseEnd - responseStart

    https://stackoverflow.com/questions/6509628/how-to-get-http-response-code-using-selenium-webdriver
    https://github.com/wkeeling/selenium-wire
    """

    def get_performance(self, url, default_timeout=60, page_timeout=60, script_timeout=60, delete_cookies=False):
        self.browser.implicitly_wait(default_timeout)
        self.browser.set_page_load_timeout(page_timeout)
        self.browser.set_script_timeout(script_timeout)
        if delete_cookies:
            self.browser.delete_all_cookies()

        performance = {}
        self.browser.get(url)
        timing = self.browser.execute_script("return window.performance.timing")

        performance["timing"] = timing
        # resources = self.browser.execute_script("window.performance.getEntriesByType(\"resource\")")
        resources = self.browser.execute_script("return window.performance.getEntries()")
        performance["resources"] = resources

        # close, Closes the current window.
        # quit, Quits the driver and closes every associated window.
        # 所有检测使用同一个browser实例可能导致数据混乱，前期每个URL开一个browser
        # 但这样会带来较大的性能问题
        # TODO
        # 后期需要做成进程池，加锁
        self.browser.quit()

        return performance

    """
    navigation timing
    https://www.w3.org/TR/navigation-timing/
    """

    def get_performance_timing(self, url):
        self.browser.get(url)
        # the result is dict
        perf = self.browser.execute_script("return window.performance.timing")
        self.browser.close()
        return json.dumps(perf)

    def get_performance_resource(self, url):
        self.browser.get(url)
        # the result is list
        perf = self.browser.execute_script("return window.performance.getEntries()")
        self.browser.close()
        return json.dumps(perf)


if __name__ == '__main__':
    from natrixclient.command.performance.webdriver import Firefox
    browser = Firefox()
    # print browser.get_performance("http://www.baidu.com")
    # browser.get_performance_memory("http://www.baidu.com")
    # print browser.get_performance_timing("http://www.baidu.com")
    # print browser.get_performance_resource("http://www.baidu.com")
