# 应对CC攻击的自动防御系统——原理与实现

0x00 系统效果
=========

* * *

此DDOS应用层防御系统已经部署在了[http://www.yfdc.org](http://www.yfdc.org/ "http://www.yfdc.org")网站上(如果访问失败,请直接访问位于国内的服务器[http://121.42.45.55](http://121.42.45.55/ "http://121.42.45.55")进行在线测试)。

此防御系统位于应用层，可以有效防止非法用户对服务器资源的滥用:

```
只要是发送高频率地、应用层请求以实现大量消耗系统资源的攻击方式，皆可有效防御。

```

其实现的基本思想是:

```
定期分析所有访问用户在过去各个时间段内的请求频率，将频率高于指定阈值的用户判定为资源滥用者，将其封杀一段时间，时效过后，防御系统自动将其解封。

```

**在线效果测试:**

进入[http://www.yfdc.org](http://www.yfdc.org/ "http://www.yfdc.org")-> 点击右上侧**在线查询**，此时将会进入`/shell/yf`域内，`/shell/yf`是一个用`bash scripts`写的动态`web-cgi`程序，用户每一次提交信息，此程序将会执行一些服务器端的查询操作，然后将数据处理后返回到客户端。

为了防止非法用户高频率地访问这个程序，而影响到其他正常用户的访问，故需要进行一些保护措施。

最终效果:

![enter image description here](http://drops.javaweb.org/uploads/images/0d559aea7a0b6b3f6f2f87c91556f1d544656856.jpg)

`被封信息页面`

```
在/shell/yf域内，按住F5不放，一直刷新，几秒后松开，就能看到被封信息和解封时间。
只要某个用户对/shell/yf的访问超过了正常的频率，服务将会对这个用户关闭一段时间，期满后自动解封。

```

0x01 系统原理
=========

* * *

`操作系统: CentOS 6.5 x86_64``开发语言: Bash Shell Scripts``Web服务器: Apache Httpd`

![enter image description here](http://drops.javaweb.org/uploads/images/0b586875fb32a0d2c6bba4722ee67b79a6ffbd60.jpg)

`(此图为系统结构的鸟瞰图 可存至本地后放大查看)`

2.1 自定义日志:/etc/httpd/logs/yfddos_log
------------------------------------

* * *

![enter image description here](http://drops.javaweb.org/uploads/images/41f2a11838d62d74a49d10ac8e92ab79d3794ac9.jpg)

`(自定义日志文件的格式)`

在httpd.conf的日志参数中，加入如下两行：

```
LogFormat "%a \"%U\" %{local}p %D %{%s}t " yfddos
CustomLog logs/yfddos_log yfddos

```

我们接下来重点分析日志文件/etc/httpd/logs/yfddos_log.

`LogFormat "%a \"%U\" %{local}p %D %{%s}t " yfddos`

解释:

```
%a -> 用户的IP
%U -> 请求的URL地址，但并不包含query string（The URL path requested, not including any query string.）
%{local}p -> 用户请求的服务器端口（一般为80）
%D -> 这个请求共消耗了服务器多少微秒（The time taken to serve the request, in microseconds.）
%{%s}t -> 服务器收到这个请求时，时间戳的值（seconds since 1970-01-01 00:00:00 UTC）

```

例子:

```
192.168.31.1 "/shell/yf" 80 118231 1417164313

```

译为:`IP为192.168.31.1的主机,在时间戳为1417164313的时候，访问了/shell/yf，并由服务器的80端口向其提供服务，共耗时118231微秒`

或为:`IP为192.168.31.1的主机,在2014-11-28 16:45:13的时候，访问了/shell/yf，并由服务器的80端口向其提供服务，共耗时0.118231秒`

至于为什么不使用httpd.conf中官方定义的日志，原因如下:

```
- 用户访问日志的一条记录可大约控制在60Bytes以内，数据量小，便于后期分析，官方定义的日志太过臃肿，影响分析速度
- 使用时间戳标志时间，便于后期分析，官方定义的日志时间参数为常规的表达方式，不便于直接进行处理
- httpd的日志系统本身就是从旧到新进行排序记录的，所以/etc/httpd/logs/yfddos_log日志条目的时间戳，亦为从小到大进行排序的，数据记录更加鲜明

```

2.2 yfddosd黑名单文件格式
------------------

* * *

![enter image description here](http://drops.javaweb.org/uploads/images/80b5741891c44a97eeae46606c8fd9c68f813e98.jpg)

`黑名单文件格式`

yfddosd黑名单文件/etc/yfddos/web-yf-search.b格式如下:

```
# ip    add-stamp  rmv-stamp
1.2.3.4 1416046335 1416046395
1.2.3.5 1416046336 1416046396
1.2.3.6 1416046339 1416046399

```

每一行为一个黑名单条目，上面第一个条目的意义为：

```
IP地址  :1.2.3.4
开始时间:时间戳1416046335，即 2014-11-15 18:12:15
终止时间:时间戳1416046395，即 2014-11-15 18:13:15

```

直观意义为:

`IP地址:1.2.3.4，从2014-11-15 18:12:15开始，被封杀1分钟，在2014-11-15 18:13:15时自动解封。`

这个文件将由驻留在系统中的daemon守护进程yfddosd进行维护更新。

2.3 守护进程yfddosd:防御系统的逻辑核心
-------------------------

* * *

![enter image description here](http://drops.javaweb.org/uploads/images/8afab64c28e8ca8286ef4135fb5e5617c80e947c.jpg)

`守护进程的原理图`

守护进程yfddosd是整个CC防御系统的核心，而`function analyze_and_insert_black()`则是yfddosd的核心。

yfddosd的配置参数:

```
yfddos_blackfilePath='/etc/yfddos/web-yf-search.b'
yfddos_accesslogPath='/etc/httpd/logs/yfddos_log'

function analyze_and_insert_black() { 
  # analyze_and_insert_black() :
  #   $1:max frequency(seems as abuse if above that) $2:blackip-ttl,time to live,unit is seconds (s) 
  #   $3:the access log ${3} seconds before will be analyzed to generate the abuse ip lists that we will block
  # example : analyze_and_insert_black "limit" "ttl" "time"
  # example : analyze_and_insert_black "4" "10" "5"
  # 分析在过去5s内的用户访问日志 如果有人在这5s内访问量>=4 系统将视其为资源滥用者 将其加入服务黑名单
  # 一条黑名单的作用时间为10s 即在10s之后 系统自动删除此黑名单条目 服务则继续向其开放
  # global vars:
  # stamp logtmpfile yfddos_blackfilePath
  # ......
}

```

函数`analyze_and_insert_black`有三个输入参数：

例子:`analyze_and_insert_black "4" "10" "5"`

```
解释: 分析日志文件/etc/httpd/logs/yfddos_log中,在过去5s内的用户访问日志,如果有IP在这5s内访问量>=4,守护进程yfddosd将视其为资源滥用者，
    然后将这个IP加入到黑名单文件/etc/yfddos/web-yf-search.b中，此条黑名单的作用时间为10s，在10s之后，守护进程yfddosd将删除此黑名单条目。

```

例子:`analyze_and_insert_black "150" "2700" "905"`

```
解释: 分析日志文件/etc/httpd/logs/yfddos_log中,在过去905s内的用户访问日志,如果有IP在这905s内访问量>=150,守护进程yfddosd将视其为资源滥用者，
    然后将这个IP加入到黑名单文件/etc/yfddos/web-yf-search.b中，此条黑名单的作用时间为2700s，在2700s之后，守护进程yfddosd将删除此黑名单条目。

```

简记为:`analyze_and_insert_black "limit" "ttl" "time"`

```
解释: 分析日志文件/etc/httpd/logs/yfddos_log中,在过去(time)s内的用户访问日志,如果有IP在这(time)s内访问量>=limit,守护进程yfddosd将视其为资源滥用者，
    然后此IP将会被加入到黑名单文件/etc/yfddos/web-yf-search.b中，作用时间为(ttl)s，在(ttl)s之后，守护进程yfddosd将自动删除此条目。

```

从上述中可看出，守护进程yfddosd至少需要完成如下三个任务:

*   分析日志文件/etc/httpd/logs/yfddos_log中指定时间内的用户访问记录
*   将资源滥用者的IP加入文件/etc/yfddos/web-yf-search.b，并设置封杀TTL参数值
*   将/etc/yfddos/web-yf-search.b中已经过期的条目全部及时删除

守护进程`yfddosd`是如何实现上面三个逻辑的:

*   分析日志文件/etc/httpd/logs/yfddos_log中指定时间内的用户访问记录:
    
    ```
    (1) 取出/etc/httpd/logs/yfddos_log中过去time秒的访问日志数据，使用二分法将这一操作的时间复杂度压缩到K*log2(N)以内，
        其中N为/etc/httpd/logs/yfddos_log中日志总行数，K为一次测试的耗时量，一般为1ms以内，即如有1048576条访问记录，这一操作将仅需要20*1ms
    (2) 使用正则RE对这些数据进行二次处理，过滤出所有访问指定URL的用户IP(这个URL为想要防御的http服务url，例如在http://www.yfdc.org系统中，
        所防御的就是/shell/yf,这个服务向访问者提供信息的search与get服务)，再次使用sort与uniq对这些IP进行处理，以统计出每个IP的访问次数并进行高低排序
    
    ```
*   将资源滥用者的IP加入文件/etc/yfddos/web-yf-search.b，并设置封杀TTL参数值
    
    ```
    将所有访问次数超过阈值limit的IP更新到黑名单文件/etc/yfddos/web-yf-search.b中,每个黑名单条目的封杀时间为ttl秒
    
    ```
*   将/etc/yfddos/web-yf-search.b中已经过期的条目全部及时删除
    
    ```
    遍历/etc/yfddos/web-yf-search.b中所有黑名单条目，结合当前时间戳，将所有已经过期的条目一一删去    
    
    ```

下面是守护进程yfddosd状态机的伪代码:(略去了一些处理细节)

```
#init and FSM start work...
counter=0
while true
do
  sleep 5
  counter=counter+1
  delete obsolete items #将/etc/yfddos/web-yf-search.b中已经过期的条目全部删除
  if # every 5 seconds : 5s
  then
    analyze_and_insert_black "6" "10" "5"
    # 分析在过去5s内访问的用户 如果有人其访问量大于等于6 系统将视其为资源滥用者 
    # 遂将其加入服务黑名单 其作用时间为10s 在10s之后 daemon进程自动删除这个ip黑名单条目
  fi
  if #every 5*3 seconds : 15s 
  then
    analyze_and_insert_black "14" "45" "15"
  fi
  if #every 5*3*4+5 seconds : 65s
  then
    analyze_and_insert_black "40" "840" "65"
  fi
  if #every 5*3*4*3*5+5 seconds : 905s : 15min
  then
    analyze_and_insert_black "150" "2700" "905"
  fi
  if #every 5*3*4*3*5*4+5 seconds : 3605s : 1h
  then
    analyze_and_insert_black "300" "7200" "3605"
  fi
  if #every 5*3*4*3*5*4*3+5 seconds : 10805s : 3h
  then
    analyze_and_insert_black "400" "21600" "10805"
    if #在每天的00:01-04:59时间区间 一天仅执行一次
    then
        #备份日志 
    fi
  fi
done

```

防御者应斟酌调整每个检测时间点的参数值(封杀时间ttl与判定阈值limit)，以调节系统应对CC攻击到来时的反应时间。

0x02 源代码
========

* * *

```
##################################### vim /usr/local/bin/yfddosd.sh :
##################################### nohup bash /usr/local/bin/yfddosd.sh &>"/etc/yfddos/""yfddosd-log-`date +%Y-%m-%d`" & 
##################################### yfddos daemon
mkdir /etc/yfddos
yfddos_blackfilePath='/etc/yfddos/web-yf-search.b'
yfddos_accesslogPath='/etc/httpd/logs/yfddos_log'

### refresh tll
logtmpfile=`mktemp`
stamp=`date +%s`
touch "$yfddos_blackfilePath"
if grep -Po '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' "$yfddos_blackfilePath" &>/dev/null
then
  cat "$yfddos_blackfilePath" | while read i
  do
    deadstamp=`echo "$i" | grep -Po '[0-9]+$'` 
    if [ "$stamp" -le "$deadstamp" ]
    then
      echo "$i" >>"$logtmpfile"
    fi
  done
fi
chmod o+r "$logtmpfile"
mv -f "$logtmpfile" "$yfddos_blackfilePath"
if ! grep -Po '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' "$yfddos_blackfilePath" &>/dev/null
then
  echo '255.255.255.255 0 0' >> "$yfddos_blackfilePath"
fi

function analyze_and_insert_black() { 
  # analyze_and_insert_black() :
  #   $1:max frequency(seems as abuse if above that) $2:blackip-ttl,time to live,unit is seconds (s) 
  #   $3:the access log ${3} seconds before will be analyzed to generate the abuse ip lists that we will block
  # example : analyze_and_insert_black "limit" "ttl" "time"
  # example : analyze_and_insert_black "4" "10" "5"
  # 分析在过去5s内的用户访问日志 如果有人在这5s内访问量>=4 系统将视其为资源滥用者 将其加入服务黑名单
  # 一条黑名单的作用时间为10s 即在10s之后 系统自动删除此黑名单条目 服务则继续向其开放
  # global vars:
  # stamp logtmpfile yfddos_blackfilePath
  local threshold="$1"
  local ttl="$2"
  local stamp_pre="$3"
  local i=0
  local num=""
  local fre=0
  local ip=0
  local localbuf=0
  local linenum=0
  local deadstamp=0
  stamp_pre="$((stamp-stamp_pre))"

  #二分查找初始化
  local temp=0
  local yf_x='1'
  local yf_y=`cat "$logtmpfile" | wc -l`
  if [ "$yf_y" -le "1" ]
  then 
    yf_y=1
  fi
  local yf_I=$(((yf_x+yf_y)/2))

  temp=`cat "$logtmpfile" | wc -l`
  if [ "$temp" -gt "0" ]
  then
    temp=`sed -n '$p' "$logtmpfile" | grep -Po '[0-9]+ $'`
    if [ "$temp" -lt "$stamp_pre" ]
    then
      num=""
    else  
      while true #使用二分查找的方法 快速地分析访问日志
      do
        temp=`sed -n "${yf_x}p" "$logtmpfile" | grep -Po '[0-9]+ $'`
        if [ "$temp" -ge "$stamp_pre" ]
        then
          break
        fi
        if [ "$((yf_y-yf_x))" -le "1" ]
        then
          yf_x="$yf_y"
          break
        fi
        temp=`sed -n "${yf_I}p" "$logtmpfile" | grep -Po '[0-9]+ $'`
        if [ "$temp" -lt "$stamp_pre" ]
        then
          yf_x="$yf_I"
          yf_y="$yf_y"
          yf_I="$(((yf_x+yf_y)/2))"
          continue
        fi
        yf_x="$yf_x"
        yf_y="$yf_I"
        yf_I="$(((yf_x+yf_y)/2))"  
        continue
      done
      temp=`sed -n "${yf_x}p" "$logtmpfile" | grep -Po '[0-9]+ $'`
      if [ "$temp" -ge "$stamp_pre" ]
      then
        num="$yf_x"
      else
        num=""
      fi
    fi  

    if [ -n "$num" ]
    then
      sed -n "${num},\$p" "$logtmpfile" | grep -Po '^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' | sort -n | uniq -c | sort -rn | while read i
      do
        fre=`echo "$i" | grep -Po '[0-9]+' | head -1`
        ip=`echo "$i" | grep -Po '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' `
        if [ "$fre" -ge "$threshold" ]
        then #insert illegal ips : cat "$yfddos_blackfilePath"
          # ip    add-stamp  rmv-stamp
          #1.2.3.4 1416046335 1416046395
          temp=`grep -Pn "${ip//./\\.} " "$yfddos_blackfilePath"`
          if [ -n "$temp" ]
          then
            linenum=`echo "$temp" | grep -Po '^[0-9]+' | head -1`
            deadstamp=`echo "$temp" | grep -Po '[0-9]+$' | sort -rn | head -1 `  
            if [ "$((stamp+ttl))" -gt "$deadstamp" ]
            then
              sed -i "${linenum}s/.*/${ip} ${stamp} $((stamp+ttl))/g" "$yfddos_blackfilePath"
            fi
          else
            sed -i "\$a ${ip} ${stamp} $((stamp+ttl))" "$yfddos_blackfilePath"
          fi 
        else
          break
        fi
      done
    fi

  fi
}

#init and yfddosd's FSM start work...
counter=0

while true
do
  sleep 5
  counter=$((counter+1))
  echo -n `date +%Y-%m-%d\ %H:%M:%S`" ""counter ${counter}:"`cat /proc/uptime | grep -Po '[0-9\.]+' | head -1`"  "
  echo -n "refresh tll:"`cat /proc/uptime | grep -Po '[0-9\.]+' | head -1`"  "
  ### refresh tll
    #refresh ttl: analyze file: "$yfddos_blackfilePath" if some items'ttl has been reach the date , we will remove it and open service to the ip had been banned before.
      #insert illegal ips : cat "$yfddos_blackfilePath"
      # ip    add-stamp  rmv-stamp
      #1.2.3.4 1416046335 1416046395
    #sed -i "/^.* $((stamp-5))$/d;/^.* $((stamp-4))$/d;/^.* $((stamp-3))$/d;/^.* $((stamp-2))$/d;/^.* $((stamp-1))$/d;/^.* $((stamp))$/d;/^$/d" "$yfddos_blackfilePath"  
  logtmpfile=`mktemp`
  stamp=`date +%s`
  touch "$yfddos_blackfilePath"
  if grep -Po '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' "$yfddos_blackfilePath" &>/dev/null
  then
    cat "$yfddos_blackfilePath" | while read i
    do
      deadstamp=`echo "$i" | grep -Po '[0-9]+$'` 
      if [ "$stamp" -le "$deadstamp" ]
      then
        echo "$i" >>"$logtmpfile"
      fi
    done
  fi
  chmod o+r "$logtmpfile"
  mv -f "$logtmpfile" "$yfddos_blackfilePath"
  if ! grep -Po '[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+' "$yfddos_blackfilePath" &>/dev/null
  then
    echo '255.255.255.255 0 0' >> "$yfddos_blackfilePath"
  fi

  logtmpfile=`mktemp`
  stamp=`date +%s`
  cat "$yfddos_accesslogPath" | grep -P ' "/shell/yf" ' >"$logtmpfile"
  if true # every 5 seconds : 5s
  then
    echo -n "analyze_and_insert_black 6 10 5:"`cat /proc/uptime | grep -Po '[0-9\.]+' | head -1`"  "
    #analyze yfddos log : analyze_and_insert_black() $1:max frequency(seems as abuse if above that) $2:blackip-ttl $3:the access log ${3} seconds before will be analyzed to generate the abuse ips that we will block
    analyze_and_insert_black "6" "10" "5"
    # 分析在过去5s内访问的用户 如果有人其访问量大于等于6 系统将视其为资源滥用者 遂将其加入服务黑名单 其作用时间为10s 在10s之后 daemon进程自动删除这个ip黑名单条目
  fi
  if [ "$((counter%(3)))" -eq "0" ] #every 5*3 seconds : 15s 
  then
    echo -n "analyze_and_insert_black 14 45 15:"`cat /proc/uptime | grep -Po '[0-9\.]+' | head -1`"  "    
  # example : analyze_and_insert_black "limit" "ttl" "time"
    analyze_and_insert_black "10" "45" "15"
  fi
  if [ "$((counter%(3*4+1)))" -eq "0" ] #every 5*3*4+5 seconds : 65s
  then
    echo -n "analyze_and_insert_black 40 840 65:"`cat /proc/uptime | grep -Po '[0-9\.]+' | head -1`"  "
  # example : analyze_and_insert_black "limit" "ttl" "time"
    analyze_and_insert_black "25" "840" "65"
  fi
  if [ "$((counter%(3*4*3*5+1)))" -eq "0" ] #every 5*3*4*3*5+5 seconds : 905s : 15min
  then
    echo -n "analyze_and_insert_black 150 2700 905:"`cat /proc/uptime | grep -Po '[0-9\.]+' | head -1`"  "
  # example : analyze_and_insert_black "limit" "ttl" "time"
    analyze_and_insert_black "150" "2700" "905"
  fi
  if [ "$((counter%(3*4*3*5*4+1)))" -eq "0" ] #every 5*3*4*3*5*4+5 seconds : 3605s : 1h
  then
    echo -n "analyze_and_insert_black 300 7200 3605:"`cat /proc/uptime | grep -Po '[0-9\.]+' | head -1`"  "
  # example : analyze_and_insert_black "limit" "ttl" "time"
    analyze_and_insert_black "300" "7200" "3605"
  fi
  if [ "$((counter%(3*4*3*5*4*3+1)))" -eq "0" ] #every 5*3*4*3*5*4*3+5 seconds : 10805s : 3h
  then
    echo -n "analyze_and_insert_black 400 21600 10805:"`cat /proc/uptime | grep -Po '[0-9\.]+' | head -1`"  "
  # example : analyze_and_insert_black "limit" "ttl" "time"
    analyze_and_insert_black "400" "21600" "10805"
    #### "${yfddos_accesslogPath}" backup : 在每天的00:01-04:59时间区间内 备份日志一次
    if [ "`date +%H`" -le "5" ] && ! [ -f "${yfddos_accesslogPath}-`date +%Y-%m-%d`" ]
    then
      service httpd stop
      mv "${yfddos_accesslogPath}" "${yfddos_accesslogPath}-`date +%Y-%m-%d`"
      service httpd start
    fi
  fi
  rm -fr "$logtmpfile"
  echo "sleep:"`cat /proc/uptime | grep -Po '[0-9\.]+' | head -1`"  "
done

```