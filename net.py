#!/usr/bin/python
#coding=utf-8
import urllib
import urllib2
import requests
import gzip
import time
import random
import StringIO
import os
import traceback

#some common net operation

def de_gzip(data):
    """decomporess data from gzip
    """
    cmps = StringIO.StringIO(data)
    gzipper = gzip.GzipFile(fileobj=cmps)
    return gzipper.read()


def get(url, header=None, cookie=None, redirect=False, timeout=20):
    """ Http Get.
    """
    try:
        respo = requests.get(url, headers=header, cookies=cookie, allow_redirects=redirect,
                             timeout=timeout)
        rheaders = respo.headers
        rheaders["charset"] = respo.encoding
        rheaders["code"] = respo.status_code
        if cookie:
            return dict(rheaders), respo.content, respo.cookies
        else:
            return dict(rheaders), respo.content
    except Exception, msg:
        error_msg = traceback.format_exc(str(msg))
        if cookie:
            return {"code": -1}, error_msg, None
        else:
            return {"code": -1}, error_msg


def post(url, data, header=None, cookie=None, redirect=False, timeout=20, files=None):
    """http post
    """
    try:
        respo = requests.post(url, data=data, headers=header, cookies=cookie,
                              files=files, timeout=timeout, allow_redirects=redirect)
        rheaders = respo.headers
        rheaders["charset"] = respo.encoding
        rheaders["code"] = respo.status_code
        if cookie:
            return dict(rheaders), respo.content, respo.cookies
        else:
            return dict(rheaders), respo.content
    except Exception, msg:
        error_msg = traceback.format_exc(str(msg))
        if cookie:
            return {"code": -1}, error_msg, None
        else:
            return {"code": -1}, error_msg


def download(url, local, header=None, cookie=None, redirect=False, timeout=60):
    """Download file"""
    try:
        respo = requests.get(url, headers=header, cookies=cookie,
                             allow_redirects=redirect, timeout=timeout)
        rheaders = respo.headers
        rheaders["charset"] = respo.encoding
        rheaders["code"] = respo.status_code
        with open(local, "wb") as code:
            code.write(respo.content)
            code.close()
        if cookie:
            return dict(rheaders), True, respo.cookies
        else:
            return dict(rheaders), True
    except Exception, msg:
        error_msg = traceback.format_exc(str(msg))
        if cookie:
            return {"code": -1, "error": error_msg}, False, None
        else:
            return {"code": -1, "error": error_msg}, False

def download_file(url, local, header=None, cookie=None, redirect=False, timeout=60):
    return download(url, local, header, cookie, redirect, timeout)

#================================ 使用代理

G_PROXY_LIST = []
def init_proxy(proxy_file):
    """
        Load proxy config file to initialize G_PROXY_LIST,
        proxy config format is => ip_addr:port\tdescription
        proxy_get and proxy_post will use the proxies in
        G_PROXY_LIST randomly.
    """
    if not os.path.exists(proxy_file):
        return
    f_proxy = open(proxy_file, "r+")
    lines = f_proxy.readlines()
    f_proxy.close()
    count = 0
    for line in lines:
        if line[0] == "#":
            continue
        line = line.replace("\t", " ")
        line = line.replace("\n", "")
        ip_addr = line.split(" ")[0]
        desc = line.split(" ")[-1]
        proxy = {"http":ip_addr, "count":count, "desc":desc}
        count = count + 1
        G_PROXY_LIST.append(proxy)

def proxy_post(url, data, heads=None, datatype=True):
    """
        Http get use proxy. Must had call init_proxy() before.
        datatype: define the return data
            True: will return string
            False: return the http object response
    """
    retry = 3
    rep_header = {}
    rhead = {}
    proxy = G_PROXY_LIST[random.randint(0, len(G_PROXY_LIST)-1)]
    proxy_handler = urllib2.ProxyHandler(proxy)
    opener = urllib2.build_opener(proxy_handler)
    request = urllib2.Request(url)
    data = urllib.urlencode(data)
    code = 200
    if heads:
        for key in heads:
            request.add_header(key, heads[key])
    while retry:
        try:
            response = opener.open(request, data, timeout=10)
            code = response.getcode()
            rhead = response.info()
            if datatype:
                return ({"code":code}, response.read())
            else:
                return ({"code":code}, response)
        except EnvironmentError, msg:
            retry = retry - 1
            time.sleep(1)
            code = _get_error_code(str(msg))
            if code in NO_RETRY:
                rep_header["code"] = code
                return (rep_header, "")

    rep_header["code"] = code
    for key, val in    rhead.items():
        rep_header[key] = val
    return (rep_header, "")

def proxy_get(url, heads=None, datatype=True):
    """
        Http get use proxy. Must had call init_proxy() before.
        datatype: define the return data
            True: will return string
            False: return the http object response
    """
    retry = 3
    rep_header = {}
    rhead = {}
    proxy = G_PROXY_LIST[random.randint(0, len(G_PROXY_LIST)-1)]
    proxy_handler = urllib2.ProxyHandler(proxy)
    opener = urllib2.build_opener(proxy_handler)
    request = urllib2.Request(url)
    if heads:
        for key in heads:
            request.add_header(key, heads[key])
    while retry:
        try:
            response = opener.open(request, timeout=10)
            code = response.getcode()
            rhead = response.info()
            dict_head = {}
            for key, value in rhead.items():
                dict_head[key] = value
            rhead = dict_head
            rhead["code"] = int(code)

            if datatype:
                html = response.read()
                if "Content-Encoding" in rhead and 'gzip' in rhead["Content-Encoding"]:
                    html = de_gzip(html)
                return (rhead, html)
            else:
                return (rhead, response)
        except EnvironmentError, msg:
            retry = retry - 1
            if "304" in str(msg):
                rep_header["code"] = 304
                return (rep_header, "")
            time.sleep(1)
            if retry == 0:
                print proxy
                print traceback.format_exc(str(msg))
                if "404" in str(msg):
                    return ({"code":404}, "")
                else:
                    return ({"code":-1}, "")

    rep_header["code"] = code
    for key, val in rhead.items():
        rep_header[key] = val
    return (rep_header, "")
