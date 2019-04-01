#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import time
import logging


logger = logging.getLogger(__name__)


def get_net_speed(macaddr):
    try:
        r = os.popen("speedtest-cli")
        text = r.read()
        r.close()  # 运行speedtest，读取返回信息
        logger.info(text)
        down_pattern = re.compile("Download:.*(\d\.\d{2}).*Mbit/s")  # 提取下载速度信息
        download_speed = re.findall(down_pattern, text)[0]
        download_speed_kbps = float(download_speed) * 128
        up_pattern = re.compile("Upload:.*(\d\.\d{2}).*Mbit/s")  # 提取上传速度信息
        upload_speed = re.findall(up_pattern, text)[0]
        upload_speed_kbps = float(upload_speed) * 128
        net_speed_info = {
            "status": 0,
            "macaddress": macaddr,
            "response_time": int(time.time()),
            "data": {
                "download_speed": download_speed_kbps,
                "upload_speed": upload_speed_kbps
            }
        }
        return net_speed_info
    except Exception as e:
        net_speed_info = {
            "status": 1,
            "macaddress": macaddr,
            "response_time": int(time.time()),
            "data": {
                "errorcode": 100,
                "errorinfo": "Domain name resolution failure"
            }
        }
        return net_speed_info
