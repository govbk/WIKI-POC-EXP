## SRUM (System Resource Usage Monitor)

> Technology that monitors desktop application programs,services, windows apps and network connections

适用于`win8`及以上系统，数据加密，实时记录

可以使用python解析：https://github.com/ianxtianxt/srum-dump

用法实例：

```bash
srum_dump2.exe --SRUM_INFILE c:\Windows\system32\sru\SRUDB.dat

python srum_dump2.py --SRUM_INFILE c:\Windows\system32\sru\SRUDB.dat

```

