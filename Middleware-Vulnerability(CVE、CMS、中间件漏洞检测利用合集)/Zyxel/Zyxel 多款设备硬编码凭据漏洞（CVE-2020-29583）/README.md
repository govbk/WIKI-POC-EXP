# Zyxel 多款设备硬编码凭据漏洞（CVE-2020-29583）

影响范围：
- 防火墙
ATP系列正在运行固件ZLD V4.60
USG系列运行固件ZLD V4.60
USG FLEX系列运行固件ZLD V4.60
运行固件ZLD V4.60的VPN系列
- 控制器
运行固件V6.00至V6.10的NXC2500
运行固件V6.00至V6.10的NXC5500

POC:
```
Example:  python3 scan_CVE-2020-29583.py 192.168.1.1/24            # vuln scan for cve-2020-0609 on UDP 3391
Example2  python3 scan_CVE-2020-29583.py 192.168.1.1/24 --webcheck # check webpage for RD gateway
Example3: python3 scan_CVE-2020-29583.py 192.168.1.1 
Example4: python3 scan_CVE-2020-29583.py fakewebsiteaddress.com 
Example5: python3 scan_CVE-2020-29583.py as15169 
Example6: python3 scan_CVE-2020-29583.py file:hostfile.txt

usage: scan_CVE-2020-29583.py [-h] [--port PORT] 
                                    [--verbose]
                                    target
```

[@2d4d](https://github.com/2d4d/scan_CVE-2020-29583)