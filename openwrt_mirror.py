# -*- coding: utf-8 -*-
#  
# Openwrt Package Grabber  
#  
# Copyright (C) 2014 http://shuyz.com
# modified by xiuxiu10201@2021.02

packages_url = "https://downloads.openwrt.org/snapshots/targets/ramips/mt7621/packages/"
save_path = "/var/www/packages"

import requests
import re
import os
from concurrent.futures import ThreadPoolExecutor
threadPool = ThreadPoolExecutor(max_workers=24, thread_name_prefix="download_")


def download(location,url,item,rc=0):
    isOk="success"
    color = 32
    try:
        rfile = requests.get(url).content
        with open(location, "wb") as code:
            code.write(rfile)
    except:
        if rc<5:
            download(location,url,item,rc+1)
            return
        isOk="fail"
        color = 31
    # 150
    point = "."*(100-len(item))
    print(f"{item}{point}\033[1;{color};40m{isOk}\033[0m")

def save_packages(url, location):
    location = os.path.abspath(location) + os.path.sep
    if not os.path.exists(location):
        os.makedirs(location)
    print(f'fetching package list from {url}')
    content = requests.get(url).text.replace("\n","")
    
    tablePattern = r"(?<=\<table\>).*?(?=\<\/table\>)"
    content = "".join(re.findall(tablePattern,content))

    print('packages list ok, analysing...')
    pattern = r'<a href="(.*?)">'
    items = re.findall(pattern, content)

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
    threadPool.shutdown(wait=True)
    print("done.")

if __name__ == '__main__':
    save_packages(packages_url, save_path)
