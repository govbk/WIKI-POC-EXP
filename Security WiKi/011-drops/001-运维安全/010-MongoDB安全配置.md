# MongoDB安全配置

0x00 MongoDB权限介绍
----------------

* * *

1.MongoDB安装时不添加任何参数,默认是没有权限验证的,登录的用户可以对数据库任意操作而且可以远程访问数据库，需以--auth参数启动。

2.在刚安装完毕的时候MongoDB都默认有一个admin数据库,此时admin数据库是空的,没有记录权限相关的信息。当admin.system.users一个用户都没有时，即使mongod启动时添加了--auth参数,如果没有在admin数据库中添加用户,此时不进行任何认证还是可以做任何操作(不管是否是以--auth 参数启动),直到在admin.system.users中添加了一个用户。

3.MongoDB的访问分为连接和权限验证，即使以--auth参数启动还是可以不使用用户名连接数据库，但是不会有任何的权限进行任何操作

4.admin数据库中的用户名可以管理所有数据库，其他数据库中的用户只能管理其所在的数据库。

5.在2.4之前版本中，用户的权限分为只读和拥有所有权限；2.4版本的权限管理主要分为：数据库的操作权限、数据库用户的管理权限、集群的管理权限，建议由超级用户在admin数据库中管理这些用户。不过依然兼容2.4版本之前的用户管理方法。

0x01 MongoDB中用户的角色说明
--------------------

* * *

### 1. read角色

数据库的只读权限，包括：

```
aggregate,checkShardingIndex,cloneCollectionAsCapped,collStats,count,dataSize,dbHash,dbStats,distinct,filemd5，mapReduce (inline output only.),text (beta feature.)geoNear,geoSearch,geoWalk,group 

```

### 2. readWrite角色

数据库的读写权限，包括：

read角色的所有权限

```
cloneCollection (as the target database.),convertToCapped，create (and to create collections implicitly.)，renameCollection (within the same database.)findAndModify,mapReduce (output to a collection.) 
drop(),dropIndexes,emptycapped,ensureIndex() 

```

### 3. dbAdmin角色

数据库的管理权限，包括：

```
clean,collMod,collStats,compact,convertToCappe 
create,db.createCollection(),dbStats,drop(),dropIndexes 
ensureIndex()，indexStats,profile,reIndex 
renameCollection (within a single database.),validate 

```

### 4. userAdmin角色

数据库的用户管理权限

### 5. clusterAdmin角色

集群管理权限(副本集、分片、主从等相关管理)，包括：

```
addShard,closeAllDatabases,connPoolStats,connPoolSync,_cpuProfilerStart_cpuProfilerStop,cursorInfo,diagLogging,dropDatabase 
shardingState,shutdown,splitChunk,splitVector,split,top,touchresync 
serverStatus,setParameter,setShardVersion,shardCollection 
replSetMaintenance,replSetReconfig,replSetStepDown,replSetSyncFrom 
repairDatabase,replSetFreeze,replSetGetStatus,replSetInitiate 
logRotate,moveChunk,movePrimary,netstat,removeShard,unsetSharding 
hostInfo,db.currentOp(),db.killOp(),listDatabases,listShardsgetCmdLineOpts,getLog,getParameter,getShardMap,getShardVersion 
enableSharding,flushRouterConfig,fsync,db.fsyncUnlock() 

```

### 6. readAnyDatabase角色

任何数据库的只读权限(和read相似)

### 7. readWriteAnyDatabase角色

任何数据库的读写权限(和readWrite相似)

### 8. userAdminAnyDatabase角色

任何数据库用户的管理权限(和userAdmin相似)

### 9. dbAdminAnyDatabase角色

任何数据库的管理权限(dbAdmin相似)

0x02 MongoDB安装注意事项
------------------

* * *

### 1. 安装的时候需要加--auth

加了--auth之后MongoDB才需要验证

### 2. 需要加--nohttpinterface

不加会有一个28017的端口监听，可以通过网页管理mongodb，不需要请去掉

### 3. 可以加--bind_ip

加之后可以限制访问的ip

### 4. 可以加--port

加了之后可以重新制定端口，默认为27017

### 5. 安装完之后需立即在admin数据库中添加一个用户

只有在admin数据库中添加一个用户后才能使认证生效

注：安装的过程其实就是添加1个服务，指定启动时候的参数。

0x03 用户授权
---------

* * *

### 1. 2.4之前版本的用户管理方式

#### 1.1、进入admin创建一个管理账号

```
use admin 
db.addUser("test","test") 

```

#### 1.2、进入需要使用的数据库中创建一个程序使用用户

```
use test 
db.addUser("test","test")默认拥有读写权限 
db.addUser("test","test",True)拥有读取权限 

```

### 2. 2.4版本的用户管理，也可使用之前版本的方式

#### 2.1、进入admin创建一个管理账号

```
use admin 
db.addUser("test","test") 

```

2.2、进入admin给使用的数据库test创建一个对数据库及日志拥有读写权限的账户

```
use admin 
db.addUser({
    "user": "test", 
    "pwd": "test", 
    "roles": [ ], 
    "otherDBRoles": {
        "test": [
            "readWrite"
        ], 
        "test_log": [
            "readWrite"
        ]
    }
}) 

```

0x04 安全配置方案
-----------

* * *

### 1. 安装的时候加--auth，并立即在admin数据库创建一个用户

默认情况下MongoDB是无需验证的，所以这是至关重要的一步

### 2. 可以考虑安装的时候修改端口和指定访问ip

具体根据实际情况来设定，也可以直接在服务器防火墙上做

### 3. 安装的时候建议加上--nohttpinterface取消默认的一个网页管理方式

默认的web管理一般不会用，且很多人不知道，最好关闭

### 4. 管理用户处理

因需要在admin中建立一个管理账户用于管理，最好是设置强密码，但是不要给其他程序使用

### 5. MongoDB服务运行账户

windows下可以使用network service 或者新建一个用户，使用默认的USERS组，然后添加给予数据库文件及日志存储目录的写权限，并建议取消对cmd等程序的执行权限。

linux下新建一个账户，给予程序的执行权限和数据库文件及日志目录的读写权限，并建议取消对sh等程序的执行权限。

### 6. 控制好网站或者其他程序使用的连接用户权限

网站或者其他程序使用的用户只给予对应库的权限，不要使用admin数据库中的管理账户。

0x05 常用命令
---------

* * *

### 1. 安装

```
mongod --dbpath d:\mongodb\data --logpath d:\mongodb\log\mongodb.log ----nohttpinterface --auth --install

```

### 2. 添加用户

```
use admin 
db.addUser("test","test") 

```

### 3. 显示所有数据库

```
show dbs 

```

### 4. 使用某个数据库

```
use test 

```

### 5. 连接数据库

```
mongo test -uroot -p123456 

```

### 6. 添加用户认证

```
db.auth("username","password") 

```

### 7. 查看用户

```
db.system.users.find() 

```

就写几个基本的，其他的网上很多，或者用工具连上去之后操作。

0x06 管理工具
---------

* * *

### 1. MongoVUE

客户端形式的管理工具

### 2. rockmongo

基于php的web管理

不足之处求大牛指正！
