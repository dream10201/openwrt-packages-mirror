# -*- coding: utf-8 -*-
#  
# Openwrt Package Grabber  
#  
# Copyright (C) 2014 http://shuyz.com
# modified by xiuxiu10201@2021.02
# src/gz openwrt_core https://downloads.openwrt.org/snapshots/targets/ramips/mt7621/packages
# src/gz openwrt_base https://downloads.openwrt.org/snapshots/packages/mipsel_24kc/base
# src/gz openwrt_kmods https://downloads.openwrt.org/snapshots/targets/ramips/mt7621/kmods/5.4.98-1-6b0e6ccfc1a63ac8682d721effce8201
# src/gz openwrt_freifunk https://downloads.openwrt.org/snapshots/packages/mipsel_24kc/freifunk
# src/gz openwrt_luci https://downloads.openwrt.org/snapshots/packages/mipsel_24kc/luci
# src/gz openwrt_packages https://downloads.openwrt.org/snapshots/packages/mipsel_24kc/packages
# src/gz openwrt_routing https://downloads.openwrt.org/snapshots/packages/mipsel_24kc/routing
# src/gz openwrt_telephony https://downloads.openwrt.org/snapshots/packages/mipsel_24kc/telephony

packages_url = ["https://downloads.openwrt.org/snapshots/packages/mipsel_24kc/",
                "https://downloads.openwrt.org/snapshots/targets/ramips/mt7621/packages/",
                "https://downloads.openwrt.org/snapshots/targets/ramips/mt7621/kmods/5.4.98-1-6b0e6ccfc1a63ac8682d721effce8201/"
            ]
save_path = "/var/www/openwrt"
ignore_list = ["tesseract"]

import requests
import re
import os
from concurrent.futures import ThreadPoolExecutor
requests.adapters.DEFAULT_RETRIES = 5
request = requests.Session()
request.keep_alive = False
threadPool = ThreadPoolExecutor(max_workers=12, thread_name_prefix="download_")
count = 0

def download(location,url,name,rc=0):
    isOk="success"
    color = 32
    try:
        rfile = request.get(url).content
        with open(location, "wb") as code:
            code.write(rfile)
    except:
        if rc<5:
            download(location,url,name,rc+1)
            return
        isOk="fail"
        color = 31
    # 150
    point = "."*(70-len(name))
    print(f"{name}{point}\033[1;{color};40m{isOk}\033[0m")

def save_packages(url, location):
    global count
    location = os.path.abspath(location) + os.path.sep
    if not os.path.exists(location):
        os.makedirs(location)
    #print(f'fetching package list from {url}')
    content = request.get(url).text.replace("\n","")
    
    tablePattern = r"(?<=\<table\>).*?(?=\<\/table\>)"
    content = "".join(re.findall(tablePattern,content))

    #print('packages list ok, analysing...')
    pattern = r'<a href="(.*?)">'
    items = re.findall(pattern, content)
    items.reverse()
    for item in items:
        if item == '../':
            continue
        elif item[-1] == '/':
            save_packages(url + item, location + item)
        else:
            item = item.replace('%2b', '+')
            if os.path.isfile(location + item):
                #print('file exists, ignored.')
                pass
            else:
                flag = True
                for ignore in ignore_list:
                    if ignore in item:
                        flag = False
                        break
                if flag:
                    threadPool.submit(download, location + item,url + item,item)
                    count +=1

if __name__ == '__main__':
    for url in packages_url:
        if url[-1]!="/":
            url += "/"
        save_packages(url, save_path+url.replace("https://downloads.openwrt.org",""))
    threadPool.shutdown(wait=True)
    print(f"Total {count}\ndone.")
