# -*- coding: utf-8 -*-

packages_url = ["https://downloads.openwrt.org/snapshots/packages/mipsel_24kc/",
                "https://downloads.openwrt.org/snapshots/targets/ramips/mt7621/packages/",
                "https://downloads.openwrt.org/snapshots/targets/ramips/mt7621/kmods/5.4.101-1-d6599289bf075640da0d2b759f6c1d71"
            ]
save_path = "/var/www/openwrt"

proxies = {"http": "http://127.0.0.1:10808","https": "http://127.0.0.1:10808"}

import requests
import re
import os
from concurrent.futures import ThreadPoolExecutor,ProcessPoolExecutor
import threading
import ssl
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.poolmanager import PoolManager
class SSLAdapter(HTTPAdapter):
    '''An HTTPS Transport Adapter that uses an arbitrary SSL version.'''
    def __init__(self, ssl_version=None, **kwargs):
        self.ssl_version = ssl_version

        super(SSLAdapter, self).__init__(**kwargs)

    def init_poolmanager(self, connections, maxsize, block=False):
        self.poolmanager = PoolManager(num_pools=connections,
                                       maxsize=maxsize,
                                       block=block,
                                       ssl_version=self.ssl_version)


chunk_size=512*4
requests.adapters.DEFAULT_RETRIES = 5
request = requests.Session()
#request.mount('https://', SSLAdapter(ssl.PROTOCOL_TLSv1))
#request.proxies = proxies
request.headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.190 Safari/537.36"}
request.keep_alive = False
#threadPool = ThreadPoolExecutor(max_workers=12, thread_name_prefix="download_")
processPool = ProcessPoolExecutor()
lock=threading.Lock()
count = 0
fail_list = []

def download(location,url,name,rc=0):
    global fail_list
    isOk="success"
    color = 32
    point = "."*(100-len(name))
    try:
        with request.get(url,stream=True) as rfile:
            with open(location, "wb") as code:
                for chunk in rfile.iter_content(chunk_size=chunk_size):
                    if chunk:
                        code.write(chunk)
    except:
        if os.path.exists(location):
            os.remove(location)
        if rc<5:
            download(location,url,name,rc+1)
            return
        isOk="fail"
        color = 31
        lock.acquire()
        fail_list.append(name)
        lock.release()
    print(f"{name}{point}\033[1;{color};40m{isOk}\033[0m")

def save_packages(url, location):
    global count
    location = os.path.abspath(location) + os.path.sep
    if not os.path.exists(location):
        os.makedirs(location)
    if url[-1]!="/":
        url += "/"
    content = request.get(url).text.replace("\n","")
    
    tablePattern = r"(?<=\<table\>).*?(?=\<\/table\>)"
    content = "".join(re.findall(tablePattern,content))
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
            if not os.path.isfile(location + item):
                #threadPool.submit(download, location + item,url + item,item)
                processPool.submit(download, location + item,url + item,item)
                count +=1

if __name__ == '__main__':
    for url in packages_url:
        save_packages(url, save_path+url.replace("https://downloads.openwrt.org",""))
    #threadPool.shutdown(wait=True)
    processPool.shutdown(wait=True)
    failStr = "\n".join(fail_list)
    print(f"Total {count}\ndone.\n\033[1;31;40m{failStr}\033[0m")
