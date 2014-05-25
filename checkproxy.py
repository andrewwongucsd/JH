#!/usr/bin/env python
from multiprocessing import Pool
import socket
import socks
import os
import urllib.request

scriptPath = os.path.dirname(os.path.realpath(__file__))
url = "http://what-is-my-ip.net/?text"

def isWorking(proxy):
    print("trying {0}...".format(proxy[0]))
    if proxy[2] == "5":
        socks.set_default_proxy(socks.SOCKS5, proxy[0], int(proxy[1]))
    elif proxy[2] == "4":
        socks.set_default_proxy(socks.SOCKS4, proxy[0], int(proxy[1]))
    elif proxy[2] == "3":
        socks.set_default_proxy(socks.HTTP, proxy[0], int(proxy[1]))
    socket.socket = socks.socksocket
    try:
        urlContent = urllib.request.urlopen(url, timeout = 5).read().decode()
        if urlContent == proxy[0]:
            print(proxy[0] + " works!")
            return proxy
    except:
        pass

with open(scriptPath + "/proxies.txt") as proxyFile:
    content = proxyFile.read()
    contentLines = content.split("\n")
    proxies = [contentLine.split(":") for contentLine in contentLines if contentLine != ""]
    
pool = Pool(processes = 24)    
results = pool.map(isWorking, proxies)

print("-------------------------")
with open(scriptPath + "/workingproxies2.txt", "w") as proxyFile:
    for proxy in results:
        if proxy != None:
            print("{0}:{1}:{2}".format(proxy[0], proxy[1], proxy[2]))
            proxyFile.write("{0}:{1}:{2}\n".format(proxy[0], proxy[1], proxy[2]))