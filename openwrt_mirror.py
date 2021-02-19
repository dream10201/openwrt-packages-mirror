# -*- coding: utf-8 -*-
#  
# Openwrt Package Grabber  
#  
# Copyright (C) 2014 http://shuyz.com
# modified by xiuxiu10201@2021.02

packages_url = ["https://downloads.openwrt.org/snapshots/packages/mipsel_24kc/",
                "https://downloads.openwrt.org/snapshots/targets/ramips/mt7621/packages/",
                "https://downloads.openwrt.org/snapshots/targets/ramips/mt7621/kmods/5.4.98-1-6b0e6ccfc1a63ac8682d721effce8201/"
            ]
save_path = "/var/www/openwrt"

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
    point = "."*(100-len(name))
    try:
        rfile = request.get(url).content
        with open(location, "wb") as code:
            code.write(rfile)
    except:
        if rc<5:
            print(f"{name}{point}\033[1;33;40mredownload\033[0m")
            download(location,url,name,rc+1)
            return
        isOk="fail"
        color = 31
    print(f"{name}{point}\033[1;{color};40m{isOk}\033[0m")

def save_packages(url, location):
    global count
    location = os.path.abspath(location) + os.path.sep
    if not os.path.exists(location):
        os.makedirs(location)
    if url[-1]!="/":
        url += "/"
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
                threadPool.submit(download, location + item,url + item,item)
                count +=1

if __name__ == '__main__':
    for url in packages_url:
        save_packages(url, save_path+url.replace("https://downloads.openwrt.org",""))
    threadPool.shutdown(wait=True)
    print(f"Total {count}\ndone.")
