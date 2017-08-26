#!/usr/bin/python

####################################################################### example
#xpath example: http://www.23us.com/html/51/51053/
config = {\
    "bookname":{"key":"""/html/body//h1/text()"""},     #no use ex_func
    "bookname2":{\
        "key":"""/html/body//h1/text()""",
        #use split, and get index 0
        "remake":[{"method":"split", "argv":[" ", "0"]}]\
    },
    "author":{\
        "key":"""/html/body//h3/text()""",
        #use replace
        "remake":[\
            {"method":"split", "argv":[":", "1"]},\
            {"method":"replace", "argv":["zangsun", ""]},\
        ]\
    },
    #the pick result is a dict
    "info":{\
        "type":"dict",
        "data":{\
            "title":{"key":"""/html//title/text()"""},
            "css":{\
                "key":"""/html//link/@href""",
                #regular expression to replace
                "remake":[\
                    {"method":"re.sub", "argv":[r"\w*.css", "test.css"]}\
                ]\
            },
            "js":{\
                "key":"""/html/head/script/@src""",
                "not_abs_url":1,     #not convert url to entire path.
                #regular expression get value.
                "remake":[{"method":"re", "argv":[r"\w*.js"]}]\
            }\
        }\
    },\
    #pick result is list.
    "chapter":{\
        "type":"list",
        "block":"""/html/body//table[@id="at"]//td""",
        "data":{\
            "name":{"key":"""./a/text()"""},
            "url":{"key":"""./a/@href"""},\
        }\
    },\
}

#json example: http://apps.wandoujia.com/api/v1/apps/com.tencent.mtt
config = {\
    "name":{"key":"""/title"""},
    "info":{\
        "type":"dict",
        "data":{\
            "packageName":{"key":"""/apks/0/packageName"""},
            "md5":{"key":"""/apks/0/md5"""},
            "version":{\
                "key":"""/apks/0/versionName""",
                "remake":[{"method":"replace", "argv":[".", "_"]}]\
            },\
        }\
    },
    "chapter":{\
        "type":"list",
        "block":"""/apks/0/securityDetail""",
        "data":{\
            "provider":{"key":"""/provider"""},
            "status":{"key":"""/status"""},
            "failedInfo":{"key":"""/failedInfo"""},\
        }\
    },\
}

