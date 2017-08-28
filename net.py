#!/usr/bin/python
#coding=utf-8
import os
import gzip
import random
import StringIO
import traceback
import requests

#some common net operation

def de_gzip(data):
    """decomporess data from gzip
    """
    cmps = StringIO.StringIO(data)
    gzipper = gzip.GzipFile(fileobj=cmps)
    return gzipper.read()


def get(url, header=None, cookie=None, redirect=False, timeout=20, data_only=True):
    """ Http Get.
    """
    try:
        rep = requests.get(url, headers=header, cookies=cookie, allow_redirects=redirect,
                           timeout=timeout)
        rheaders = rep.headers
        rheaders["charset"] = rep.encoding
        rheaders["code"] = rep.status_code
        ret_data = rep.content
        if not data_only:
            ret_data = rep
        return (dict(rheaders), ret_data, rep.cookies) if cookie else (dict(rheaders), ret_data)
    except Exception, msg:
        error_msg = str(traceback.format_exc(str(msg)))
        return ({"code": -1}, error_msg, None) if cookie else ({"code": -1}, error_msg)


def post(url, data, header=None, cookie=None, redirect=False, timeout=20, files=None, data_only=True):
    """http post
    """
    try:
        rep = requests.post(url, data=data, headers=header, cookies=cookie,
                            files=files, timeout=timeout, allow_redirects=redirect)
        rheaders = rep.headers
        rheaders["charset"] = rep.encoding
        rheaders["code"] = rep.status_code
        ret_data = rep.content
        if not data_only:
            ret_data = rep
        return (dict(rheaders), ret_data, rep.cookies) if cookie else (dict(rheaders), ret_data)
    except Exception, msg:
        error_msg = str(traceback.format_exc(str(msg)))
        return ({"code": -1}, error_msg, None) if cookie else ({"code": -1}, error_msg)


def download(url, local, header=None, cookie=None, redirect=False, timeout=60):
    """Download file"""
    try:
        rep = requests.get(url, headers=header, cookies=cookie,
                           allow_redirects=redirect, timeout=timeout)
        rheaders = rep.headers
        rheaders["charset"] = rep.encoding
        rheaders["code"] = rep.status_code
        with open(local, "wb") as code:
            code.write(rep.content)
            code.close()
        return (dict(rheaders), True, rep.cookies) if cookie else (dict(rheaders), True)
    except Exception, msg:
        error_msg = {"code": -1, "error": str(traceback.format_exc(str(msg)))}
        return (error_msg, False, None) if cookie else (error_msg, False)

def download_file(url, local, header=None, cookie=None, redirect=False, timeout=60):
    return download(url, local, header, cookie, redirect, timeout)

#================================ 使用代理

G_PROXY_LIST = {}
def proxy_init(proxy_file):
    """
        Load proxy config file to initialize G_PROXY_LIST,
        proxy config format is => ip_addr:port\tdescription
        proxy_get and proxy_post will use the proxies in
        G_PROXY_LIST randomly.
    """
    if not os.path.exists(proxy_file):
        return False

    lines = open(proxy_file, "r+").read()
    lines = lines.replace("\t", " ")
    for length in range(0, 9):
        length = 10 - length
        lines = lines.replace(" "*length, " ")

    count = 0
    for line in lines.split("\n"):
        if line == "" or line[0] == "#":
            continue
        row = line.split(" ")
        addr = row[0].split(":")
        ip = addr[0]
        port = addr[1]
        if not ip in G_PROXY_LIST:
            proxy = {row[1]: [ip, port], "count": count, "desc": row[2]}
            G_PROXY_LIST[ip] = proxy
            count = count + 1
        else:
            G_PROXY_LIST[ip][row[1]] = [ip, port]
    return proxy_reset()

def proxy_reset():
    """Set current proxy."""
    if not G_PROXY_LIST:
        return False
    rint = random.randint(0, len(G_PROXY_LIST.keys()) - 1)
    proxy = G_PROXY_LIST[G_PROXY_LIST.keys()[rint]]
    proxies = {}
    if 'http' in proxy:
        proxies['http'] = "http://" + proxy['http'][0] + ":" + proxy['http'][1]
    if 'https' in proxy:
        proxies['https'] = "http://" + proxy['https'][0] + ":" + proxy['https'][1]
    proxy['proxies'] = proxies
    G_PROXY_LIST["current"] = proxy
    return True


def proxy_get(url, header=None, cookie=None, redirect=False, timeout=20, data_only=True):
    """
        Http get use proxy. Must had call proxy_init() before.
        datatype: define the return data
            True: will return string
            False: return the http object response
    """
    try:
        if not G_PROXY_LIST:
            error_msg = "Proxy not inited!!"
            return {"code": -2}, error_msg, None if cookie else {"code": -2}, error_msg
        rep = requests.get(url, headers=header, cookies=cookie, allow_redirects=redirect,
                           timeout=timeout, proxies=G_PROXY_LIST['current']['proxies'])
        rheaders = rep.headers
        rheaders["charset"] = rep.encoding
        rheaders["code"] = rep.status_code
        return (dict(rheaders), rep.content, rep.cookies) if cookie else (dict(rheaders), rep.content)
    except Exception, msg:
        error_msg = str(traceback.format_exc(str(msg)))
        return ({"code": -1}, error_msg, None) if cookie else ({"code": -1}, error_msg)


def proxy_post(url, data, header=None, cookie=None, redirect=False, timeout=20, files=None, data_only=True):
    """
        Http post use proxy. Must had call proxy_init() before.
        datatype: define the return data
            True: will return string
            False: return the http object response
    """
    try:
        if not G_PROXY_LIST:
            error_msg = "Proxy not inited!!"
            return {"code": -2}, error_msg, None if cookie else {"code": -2}, error_msg

        rep = requests.post(url, data=data, headers=header, cookies=cookie, files=files, timeout=timeout,
                            allow_redirects=redirect, proxies=G_PROXY_LIST['current']['proxies'])
        rheaders = rep.headers
        rheaders["charset"] = rep.encoding
        rheaders["code"] = rep.status_code
        ret_data = rep.content
        if not data_only:
            ret_data = rep
        return (dict(rheaders), ret_data, rep.cookies) if cookie else (dict(rheaders), ret_data)
    except Exception, msg:
        error_msg = str(traceback.format_exc(str(msg)))
        return ({"code": -1}, error_msg, None) if cookie else ({"code": -1}, error_msg)
