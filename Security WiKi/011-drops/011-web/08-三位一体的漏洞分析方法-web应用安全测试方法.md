# 三位一体的漏洞分析方法-web应用安全测试方法

0x00 前言
=======

* * *

节选自： http://www.owasp.org.cn/OWASP_Conference/owasp-20140924/02OWASPWeb20140915.pdf

*   4.1  主动式（全自动 ）：Web2.0、交互式漏洞扫描 
*   4.2  半自动式漏洞分析：业务重放、url镜像，实现高覆盖度 
*   4.3  被动式漏洞分析：应对0Day和孤岛页面

0x01 主动式（全自动 ）Web扫描 
====================

* * *

• 使用常见的漏洞扫描器  • 自动fuzz，填充各种攻击性数据  • 业务逻辑混淆，导致服务出错 

![enter image description here](http://drops.javaweb.org/uploads/images/96574a26503733067a44b296449d8dad28eef327.jpg)

• 局限：  • 难以处理高交互式应用  • 只能发现暴露给用户（搜索引擎）的链接，难以覆盖100%的业务链接  • 解决方法：引入半被动式漏洞分析方法  • 在人工未参与的情况下，50%以上的Web应用系统存在高危漏洞 

0x02 半自动式漏洞分析：业务重放+url镜像，实现高覆盖度 
================================

* * *

1. 方法一：业务重放 
------------

* * *

*   测试过程使用 burpsuite、fiddler：  

1.  HTTP（S）业务流量录制与重放扫描 
2.  手工修改业务数据流 
3.  对手机APP也适用 

  检测逻辑漏洞：  •水平权限绕过  •订单修改  •隐藏域修改 

![enter image description here](http://drops.javaweb.org/uploads/images/0e619fab10161747ee60661058cb972f8158d769.jpg)

2. 方法二： 手工记录
------------

* * *

• 从日志中获取url记录 

```
1. Fiddler的Url日志 
2. 获取Apache、Nginx、Tomcat的access日志 
3. 从旁路镜像中提取url日志 （安全人员不用再被动等待应用 的上线通知） 

```

1.  从Fiddler2、 burpsuite 导出Url日志 再导入到漏洞扫描器扫描

![enter image description here](http://drops.javaweb.org/uploads/images/8c76f1bbc1ead45feed55a6e73bf236ae00d0410.jpg)

![enter image description here](http://drops.javaweb.org/uploads/images/d1e7c5eade34795fd2a08af2af75e88fc68e9397.jpg)

2.获取Apache、Nginx、Tomcat的access日志 

*   360-日志宝 
*   Splunk 
*   各种日志审计系统 

1.  从旁路镜像中提取url日志 （安全人员不用再被动等待应用 的上线通知）  如：jnstniffer、 360鹰眼、各大IT公司等

![enter image description here](http://drops.javaweb.org/uploads/images/730ad0ab8c15bed662d6f8e02ffc94c8135a2ed7.jpg)

• 从旁路镜像中获取url列表，能高效地检出大量的漏洞，不需要运维人员通知，便可以获知业务系统的上线情况并执行漏洞扫描任务。

0x03 半自动式漏洞分析：业务重放、url镜像，高覆盖度
=============================

* * *

  - 局限  ① 时间滞后/token: 流量重发时，不一定能100%重现当时的业务流程及出现的bug。  ② 依然难以覆盖100%的业务链接，存在孤岛页面。（正常数据流不触发）  ③ 漏洞检测（防御）技术滞后于攻击技术，无法解决0day漏洞  - 解决方法：引入全被动式漏洞分析 

0x04 全被动式漏洞分析： 
===============

* * *

  国外产品：Nessus PVS被动扫描 

![enter image description here](http://drops.javaweb.org/uploads/images/db08cfb7a7d17d0cf3377dd9617249b1ca5a2e93.jpg)

全被动式漏洞分析（不发送任何数据包) 
-------------------

* * *

*   全被动式扫描VS主动式漏洞扫描器  相同点：都是根据双向数据包的内容，判断漏洞是否存在  不同点：  检测方式：被动式扫描不需要联网，不会主动发出url请求，也不发出任何数据包 PVS和IDS的区别：  • 更关注漏洞感知，而不是入侵，如页面出现sql错误信息，可触发pvs报警，但不会触发ids报警。  • 报警结果不一样：pvs按照漏洞的风险等级，ids按照黑客的攻击手段报警  • 双向分析数据报文  • 更关注于web应用，OWASP TOP10的攻击手段  • 按攻击影响报警（分析双向报文），而不是按攻击手段去报警（分析单向报文） Nessus的PVS只是一个思路，它专注及网络及主机漏洞，对Web应用的检测能力有限，需要重新设计一个针对web的PVS出来:WebPVS，同步接受用户提交的所有业务请求，通过扫描引擎识别请求，一旦发现恶意请求或者该请求返回数据，触发报警处理

![enter image description here](http://drops.javaweb.org/uploads/images/5a6a14ebe7fcf17a0834c6ea02775b04d4de547a.jpg)

• WebPVS的优点：    • 虽然依然难以覆盖100%的业务链接，但是能覆盖100%已经发生的业务链接。  • 能与黑客同步发现各种漏洞 • 由于HTTP协议是固定，因此能够根据回包情况发现0day攻击。