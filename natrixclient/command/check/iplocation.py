#!/usr/bin/env python
# -*- coding: utf-8 -*-


import logging
import json
import os
import requests
from natrixclient.command.check.ipregion import IpRegion


logger = logging.getLogger(__name__)


class IpLocation(object):
    def __init__(self, parameters=None):
        if parameters and parameters.get("logger"):
            global logger
            logger = logging.getLogger(parameters.get("logger"))

    @staticmethod
    def get_location(ip):
        return IpLocation.get_location_by_ip2region(ip)

    @staticmethod
    def get_location_by_ip2region(ip):
        logger.debug("get location information by ip2region")
        location = {
            "country": None,
            "region": None,
            "province": None,
            "city": None,
            "isp": None
        }

        dirpath = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
        dbFile = dirpath + "/data/ip2region.db"
        algorithm = "binary"
        if (not os.path.isfile(dbFile)) or (not os.path.exists(dbFile)):
            logger.error("ip2region db file {} is not exists.".format(dbFile))
        searcher = IpRegion(dbFile)
        if not searcher.isip(ip):
            logger.error("invalid IP {}.".format(ip))
        try:
            if algorithm == "binary":
                data = searcher.binarySearch(ip)
            elif algorithm == "memory":
                data = searcher.memorySearch(ip)
            else:
                # b-tree
                # TODO, btreeSearch存在bug
                data = searcher.btreeSearch(ip)
            # 中国|0|北京|北京市|电信
            region = data["region"].decode('utf-8')
            if region:
                rsplits = region.split("|")
                location["country"] = IpLocation.parse_country(rsplits[0])
                location["region"] = IpLocation.parse_region(rsplits[1])
                location["province"] = IpLocation.parse_province(rsplits[2])
                location["city"] = IpLocation.parse_city(rsplits[3])
                location["isp"] = IpLocation.parse_isp(rsplits[4])
        except Exception as e:
            logger.exception("fail to get location info for ip {}".format(ip))
        searcher.close()
        return location

    # 获取公网ip所在地址信息,如果公网ip是空，不处理
    # there are some problems when using raspberry to invoke this url
    @staticmethod
    def get_location_by_taobao(publicip):
        apiurl = "http://ip.taobao.com/service/getIpInfo.php?ip=%s" % publicip
        logger.debug("request url = %s" % apiurl)
        try:
            response = requests.get(apiurl)
            if response.status_code == 200:
                content = response.text
                logger.debug("content = " + content)
                try:
                    code = json.loads(content)['code']
                    data = json.loads(content)['data']
                except ValueError as ve:
                    logger.error("loads code or data error: %s" % ve)
                    code = 1
                if code == 0:
                    # 创建字典
                    location = {
                        'country': data['country'],
                        'area': data['area'],
                        'region': data['region'],
                        'city': data['city'],
                        'county': data['county'],
                        'isp': data['isp']
                    }
                    return location
            else:
                return None
        except:
            return None

    @staticmethod
    def get_location_by_baidu(publicip):
        apiurl = "https://api.map.baidu.com/location/ip?ip=%s&ak=2E143C563ced2b7dc8602d448eb3db37&coor=bd09ll" % publicip
        logger.debug("request url = %s" % apiurl)
        try:
            response = requests.get(apiurl)
            if response.status_code == 200:
                content = response.text
                logger.debug("content = " + content)
                try:
                    code = json.loads(content)['status']
                    data = json.loads(content)['address']
                except ValueError as ve:
                    logger.exception("loads code or data error: %s" % ve)
                    code = 1
                if code == 0:
                    # 创建字典
                    datalist = data.split('|')
                    location = {
                        'country': datalist[0],
                        'area': None,
                        'region': datalist[1],
                        'city': datalist[2],
                        'county': datalist[3],
                        'isp': datalist[4]
                    }
                    return location
            else:
                return None
        except:
            return None

    @staticmethod
    def parse_country(country):
        return country

    @staticmethod
    def parse_region(region):
        return region

    @staticmethod
    def parse_province(region):
        return region

    @staticmethod
    def parse_city(city):
        return city

    @staticmethod
    def parse_isp(isp):
        return isp

