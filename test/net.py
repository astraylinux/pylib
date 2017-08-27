#!/usr/bin/python
#coding=utf-8
"""
    Unit test for net.py.
"""
import os
import sys
from pylib import net

DOC_URL = "http://res.astraylinux.com/doc/libbson/index.html"

def download_file():
    """
        download my picture for test download.
        function 'download_file' must check the file size.
    """
    print "Test DownloadFile()"
    down_url = "http://res.astraylinux.com/server/http_post_optimization.png"
    local = "./downloadtest.png"
    if not net.download_file(down_url, local, timeout=20):
        print "download failed!"
        return
    if not os.path.getsize(local) == 19764:
        print "file size error!"
    os.remove("./downloadtest.png")

def get():
    print "Test get()"
    (headers, html) = net.get(DOC_URL)
    if not headers["code"] == 200:
        print "download failed\n", headers
    if not len(html) == 8187:
        print "Length error:", len(html), 8187

def post():
    print "Test post()"
    post_data = {"query":"qq"}
    (headers, html) = net.post("http://fanyi.baidu.com/langdetect", post_data)
    if not headers["code"] == 200:
        print "download failed\n", headers
    if not "success" in html:
        print html

def proxy_get():
    print "Test proxy_get()"
    net.proxy_init("./proxy_list")
    (headers, html) = net.proxy_get("http://www.atool.org/regex.php")
    if not headers["code"] == 200:
        print "download failed\n", headers
        print html
    if not len(html) > 5000:
        print "Length error:", len(html)

def proxy_post():
    print "Test proxy_post()"
    net.proxy_init("./proxy_list")
    post_data = {"query":"qq"}
    (headers, html) = net.proxy_post("http://fanyi.baidu.com/langdetect", post_data)
    if not headers["code"] == 200:
        print "download failed\n", headers
    if not "success" in html:
        print html

if __name__ == "__main__":
    step = "all"
    if len(sys.argv) > 1:
        step = sys.argv[1]
    if step == "download_file" or step == "all":
        download_file()
    if step == "get" or step == "all":
        get()
    if step == "post" or step == "all":
        post()
    if step == "proxy_get" or step == "all":
        proxy_get()
    if step == "proxy_post" or step == "all":
        proxy_post()
