# Elasticsearch集群的备份与恢复

0x00 NFS准备
==========

* * *

在ES集群上做一个NFS，并挂载：

```
[root@localhost ~]# yum install nfs-utils*
[root@localhost ~]# vi /etc/exports

```

输入集群的IP地址，例如：

```
192.168.1.2(rw)
192.168.1.3(rw)
192.168.1.4(rw)

```

保存退出,并启动NFS服务

```
[root@localhost ~]# service nfs start
[root@localhost ~]# service rpcgissd start
[root@localhost ~]# service rpcbind start

```

挂载NFS

```
[root@localhost ~]# mount elasticsearch.master:/data/es/es_backup /data/es/es_backup

```

0x01 配置
=======

* * *

在elasticsearch.master端执行:

```
curl -XPUT 'http://elasticsearch.master:9200/_snapshot/backup' -d '{
"type": "fs",
"settings": {
    "location": "/data/es/es_backup",
    "compress": true
  }
}'

```

备份操作，名字根据自己的情况修改

```
curl -XPUT http://elasticsearch.master:9200/_snapshot/backup/logstash-2016.01.01 -d '     
{"indices":"logstash-sec-2016.01.01",
"ignore_unavailable": "true",
"include_global_state": false }'

```

0x02 备份常用命令
===========

* * *

查看备份状态:

```
curl –XGET  http://elasticsearch.master:9200/_snapshot/backup/logstash-security-2016.01.01

```

删除备份

```
curl -XDELETE  http://elasticsearch.master:9200/_snapshot/backup/logstash-security-2016.01.01

```

恢复备份

```
curl -XPOST http://elasticsearch.master:9200/_snapshot/backup/logstash-security-2016.01.01/_restore -d ' { "indices" : "logstash-security-2016.01.01"}'

```

0x03 最后附备份脚本
============

* * *

```
# -*- coding:UTF-8 -*- #
"""
自动备份ElaticSearch
"""

import sys,requests
import simplejson
import time,os
import zipfile

URL="http://elasticsearch.master:9200/_snapshot/backup"
BAK_DIR="/var/wd/elasticsearch_backup/data" 
ZIP_DIR="/var/wd/elasticsearch_backup/zip"

if __name__=='__main__':
    date=time.strftime('%Y.%m.%d',time.localtime(time.time()-86400))

    data1={"type": "fs","settings": {"location":BAK_DIR ,"compress": True}}
    r1=requests.post(URL,simplejson.dumps(data1))
    print r1.text

    index='logstash-sec-'+date
    url=URL+'/'+index

    #开始备份指定INDEX
    data2={"indices":index,"ignore_unavailable": True,"include_global_state": False }
    r2=requests.post(url,simplejson.dumps(data2))
    print r2.text

    #查询备份状态
    r3=requests.get(url)
    dic=simplejson.loads(r3.text)
    while  (dic['snapshots'][0]['state']=='IN_PROGRESS'):
        print "%s Backup is IN_PROGRESS..." % index
        time.sleep(10)
        r3=requests.get(url)
        dic=simplejson.loads(r3.text)

    if dic['snapshots'][0]['state']=='SUCCESS':
        print '%s 备份成功' % index
        try:
            #压缩文件
            zfile=ZIP_DIR+'/'+index+'.zip'
            z = zipfile.ZipFile(zfile,'w',zipfile.ZIP_DEFLATED,allowZip64=True) 
            print "开始压缩文件..."
            for dirpath, dirnames, filenames in os.walk(BAK_DIR):  
                for filename in filenames:  
                    z.write(os.path.join(dirpath,filename))  
            z.close()

            os.system('rm -rf '+BAK_DIR) #删除原文件目录

            print "备份结束"


        except Exception,e:
            print e
        print "开始删除index: %s" % index
        os.system('curl -XDELETE "http://elasticsearch.master:9200/%s"' % index)

    else:
        print '%s 备份失败' % index
```