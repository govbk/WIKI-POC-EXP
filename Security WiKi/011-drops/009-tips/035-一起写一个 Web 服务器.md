# 一起写一个 Web 服务器

翻译于[一起写一个 Web 服务器](http://ruslanspivak.com/lsbaws-part2/)

还记的么，在第一部分[Part 1](http://ruslanspivak.com/lsbaws-part1/)我问过一个问题，“怎样在你的刚完成的WEB服务器下运行 Django 应用、Flask 应用和 Pyramid 应用？在不单独修改服务器来适应这些不同的 WEB 框架的情况下。”

继续读，下面将会给出答案。在过去，你选择一个python web 框架将会限制web服务器的使用，反之亦然。 如果web框架和服务器被设计的一起工作，那么他们将没问题：

![lsbaws_part2_before_wsgi.png](http://drops.javaweb.org/uploads/images/ed2bd3e0d9b966022e9ebe49fd9c6768944d83b4.jpg)

但是，当你试图组合不是被设计的一起工作的一个web框架和一个web服务器时你可能已经遇到下面的问题:

![lsbaws_part2_after_wsgi.png](http://drops.javaweb.org/uploads/images/4f7a09acb36e156c0db9ff5d77c921f58b0705a1.jpg)

基本上，你必须使用一起工作的而不是你想要用的组合。

所以，你怎么能确定你能跑你的web服务器兼容多个web框架的同时而又不用写代码来改变web服务器或者web框架？答案就是**Python Web Server Gateway Interface **(或者[WSGI] (https://www.python.org/dev/peps/pep-0333/) 作为简写, 发音 _“wizgy”_).

![lsbaws_part2_wsgi_idea.png](http://drops.javaweb.org/uploads/images/d1e0062e062720f573d29464b753802176a36a5a.jpg)

[WSGI](https://www.python.org/dev/peps/pep-0333/) 允许开发者分别选择web框架和web服务器。现在你们混合使用匹配的web框架和服务器来满足你的需求。你能跑  [Django](https://www.djangoproject.com/), [Flask](http://flask.pocoo.org/), 或者 [Pyramid](http://trypyramid.com/), 例如, 使用 [Gunicorn](http://gunicorn.org/) 或者 [Nginx/uWSGI](http://uwsgi-docs.readthedocs.org/) 又或者 [Waitress](http://waitress.readthedocs.org/). 真的混合且匹配这要归功于 WSGI 既支持服务器有支持框架: 

![lsbaws_part2_wsgi_interop.png](http://drops.javaweb.org/uploads/images/5946d3489988115bfd03975213200c12fb34f937.jpg)

所以, [WSGI](https://www.python.org/dev/peps/pep-0333/)  是第一部分我问的问题的答案  [Part 1](http://ruslanspivak.com/lsbaws-part1/) 也在文章最开始提到。你的web服务器必须实现WSGI的服务端接口，现在所有的python web 框架已经实现了WSGI的框架端接口 , 这允许你使用它们而不需修改代码来适配一个特殊的web框架。 现在你知道了WSGI 支持 Web servers 和 Web frameworks 允许你选择一个匹配的组合,这也得利于服务端和框架开发者因为它们能集中于它们想关注的方面.其他语言有类似的接口 : 例如Java, 有 [Servlet API](http://en.wikipedia.org/wiki/Java_servlet) 同时Ruby 有 [Rack](http://en.wikipedia.org/wiki/Rack_%28web_server_interface%29). 这都没问题，你可能会说: “给我展示你的代码!”好的,看一下这个完美的最小 WSGI 服务器实现:

```
# Tested with Python 2.7.9, Linux & Mac OS X
import socket
import StringIO
import sys


class WSGIServer(object):

    address_family = socket.AF_INET
    socket_type = socket.SOCK_STREAM
    request_queue_size = 1

    def __init__(self, server_address):
        # Create a listening socket
        self.listen_socket = listen_socket = socket.socket(
            self.address_family,
            self.socket_type
        )
        # Allow to reuse the same address
        listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # Bind
        listen_socket.bind(server_address)
        # Activate
        listen_socket.listen(self.request_queue_size)
        # Get server host name and port
        host, port = self.listen_socket.getsockname()[:2]
        self.server_name = socket.getfqdn(host)
        self.server_port = port
        # Return headers set by Web framework/Web application
        self.headers_set = []

    def set_app(self, application):
        self.application = application

    def serve_forever(self):
        listen_socket = self.listen_socket
        while True:
            # New client connection
            self.client_connection, client_address = listen_socket.accept()
            # Handle one request and close the client connection. Then
            # loop over to wait for another client connection
            self.handle_one_request()

    def handle_one_request(self):
        self.request_data = request_data = self.client_connection.recv(1024)
        # Print formatted request data a la 'curl -v'
        print(''.join(
            '< {line}\n'.format(line=line)
            for line in request_data.splitlines()
        ))

        self.parse_request(request_data)

        # Construct environment dictionary using request data
        env = self.get_environ()

        # It's time to call our application callable and get
        # back a result that will become HTTP response body
        result = self.application(env, self.start_response)

        # Construct a response and send it back to the client
        self.finish_response(result)

    def parse_request(self, text):
        request_line = text.splitlines()[0]
        request_line = request_line.rstrip('\r\n')
        # Break down the request line into components
        (self.request_method,  # GET
         self.path,            # /hello
         self.request_version  # HTTP/1.1
         ) = request_line.split()

    def get_environ(self):
        env = {}
        # The following code snippet does not follow PEP8 conventions
        # but it's formatted the way it is for demonstration purposes
        # to emphasize the required variables and their values
        #
        # Required WSGI variables
        env['wsgi.version']      = (1, 0)
        env['wsgi.url_scheme']   = 'http'
        env['wsgi.input']        = StringIO.StringIO(self.request_data)
        env['wsgi.errors']       = sys.stderr
        env['wsgi.multithread']  = False
        env['wsgi.multiprocess'] = False
        env['wsgi.run_once']     = False
        # Required CGI variables
        env['REQUEST_METHOD']    = self.request_method    # GET
        env['PATH_INFO']         = self.path              # /hello
        env['SERVER_NAME']       = self.server_name       # localhost
        env['SERVER_PORT']       = str(self.server_port)  # 8888
        return env

    def start_response(self, status, response_headers, exc_info=None):
        # Add necessary server headers
        server_headers = [
            ('Date', 'Tue, 31 Mar 2015 12:54:48 GMT'),
            ('Server', 'WSGIServer 0.2'),
        ]
        self.headers_set = [status, response_headers + server_headers]
        # To adhere to WSGI specification the start_response must return
        # a 'write' callable. We simplicity's sake we'll ignore that detail
        # for now.
        # return self.finish_response

    def finish_response(self, result):
        try:
            status, response_headers = self.headers_set
            response = 'HTTP/1.1 {status}\r\n'.format(status=status)
            for header in response_headers:
                response += '{0}: {1}\r\n'.format(*header)
            response += '\r\n'
            for data in result:
                response += data
            # Print formatted response data a la 'curl -v'
            print(''.join(
                '> {line}\n'.format(line=line)
                for line in response.splitlines()
            ))
            self.client_connection.sendall(response)
        finally:
            self.client_connection.close()


SERVER_ADDRESS = (HOST, PORT) = '', 8888


def make_server(server_address, application):
    server = WSGIServer(server_address)
    server.set_app(application)
    return server


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit('Provide a WSGI application object as module:callable')
    app_path = sys.argv[1]
    module, application = app_path.split(':')
    module = __import__(module)
    application = getattr(module, application)
    httpd = make_server(SERVER_ADDRESS, application)
    print('WSGIServer: Serving HTTP on port {port} ...\n'.format(port=PORT))
    httpd.serve_forever()

```

这比第一部分 [Part 1](http://ruslanspivak.com/lsbaws-part1/)打多了, 但是 他也足够小（仅仅150行） 让你们能理解而又不用陷入细节中 .

上面的代码实现了更多--他能跑基本的web框架 ,不论他是 Pyramid, Flask, Django,或者其他 PythonWSGI 框架. 不信？自己试试保存上面的代码  _webserver2.py_或者直接从[GitHub](https://github.com/rspivak/lsbaws/blob/master/part2/webserver2.py)下载.如果你跑它而不用参数，他将报错然后退出 .

```
$ python webserver2.pyProvide a WSGI application object as module:callable

```

它真的想服务你的web应用 , 这也是它有趣的开始。你只需要安装python就可以运行起来。 但是为了运行使用 Pyramid, Flask,和 Django 框架的应用，你需要先安装这些框架。接下来我们安装这三个框架，我更喜欢使用  [virtualenv](https://virtualenv.pypa.io/).只需要按下面的步骤来创建和激活一个虚拟环境和安装这三个web框架

```
$ [sudo] pip install virtualenv
$ mkdir ~/envs
$ virtualenv ~/envs/lsbaws/
$ cd ~/envs/lsbaws/
$ ls
bin  include  lib
$ source bin/activate
(lsbaws) $ pip install pyramid
(lsbaws) $ pip install flask
(lsbaws) $ pip install django

```

这里你需要创建一个web 应用，我们先从  [Pyramid](http://trypyramid.com/) 开始. 保存下面的代码_pyramidapp.py_ 到你保存_webserver2.py_的目录或者下载它从[GitHub](https://github.com/rspivak/lsbaws/blob/master/part2/pyramidapp.py):

```
from pyramid.config import Configurator
from pyramid.response import Response


def hello_world(request):
    return Response(
        'Hello world from Pyramid!\n',
        content_type='text/plain',
    )

config = Configurator()
config.add_route('hello', '/hello')
config.add_view(hello_world, route_name='hello')
app = config.make_wsgi_app()

```

现在你已经准备好在你的服务器上运行你的 Pyramid 应用了 :

```
(lsbaws) $ python webserver2.py pyramidapp:app
WSGIServer: Serving HTTP on port 8888 ...

```

你只需要告诉你的服务器加载那个应用_‘app’_ ，他可以从python模块调用。你的服务器现在已经可以接受请求了，他会转给你的 Pyramid 应用 这个应用只处理一个路由 ：那个_/hello_ 路由. 在浏览器里输入 [http://localhost:8888/hello](http://localhost:8888/hello)  可以看到下面的变化:![Pyramid](http://drops.javaweb.org/uploads/images/9a706655f34db00d9b89023079641b71ff8c3f37.jpg)你也可以在命令行使用curl 调用服务器

```
$ curl -v http://localhost:8888/hello...

```

检查服务器和curl 的标准打印，现在看[Flask](http://flask.pocoo.org/). 按下面的步骤.

```
from flask import Flask
from flask import Response
flask_app = Flask('flaskapp')


@flask_app.route('/hello')
def hello_world():
    return Response(
        'Hello world from Flask!\n',
        mimetype='text/plain'
    )

app = flask_app.wsgi_app

```

保存上面的代码  _flaskapp.py_ 或者从 [GitHub](https://github.com/rspivak/lsbaws/blob/master/part2/flaskapp.py)下载，在服务器上运行:

```
(lsbaws) $ python webserver2.py flaskapp:app
WSGIServer: Serving HTTP on port 8888 ...

```

在浏览器输入 [http://localhost:8888/hello](http://localhost:8888/hello):![Flask](http://drops.javaweb.org/uploads/images/99719169d8f8d25eb08b1b6dda3d1105271466bb.jpg)再次使用 _‘curl’_ 来看服务器返回信息 :

```
$ curl -v http://localhost:8888/hello...

```

服务器也能处理一个  [Django](https://www.djangoproject.com/) 应用。试一试t! 这需要多一点的处理，所以我建议克隆整个repo并使用 [djangoapp.py](https://github.com/rspivak/lsbaws/blob/master/part2/djangoapp.py), 这是 [GitHub repository](https://github.com/rspivak/lsbaws/)的部分内容. 下面是源码，他基本的添加了 Django _‘helloworld’_ 工程 到当前的python 目录并导入 WSGI 应用.

```
import sys
sys.path.insert(0, './helloworld')
from helloworld import wsgi


app = wsgi.application

```

保存上面的代码  _djangoapp.py_ ，运行 Django 应用 :

```
(lsbaws) $ python webserver2.py djangoapp:app
WSGIServer: Serving HTTP on port 8888 ...

```

在浏览器输入 :

![Django](http://drops.javaweb.org/uploads/images/9e8afe0c9b948eea83fb80dea5a6f0e8a2addd64.jpg)确认是 Django 应用处理 的请求

```
$ curl -v http://localhost:8888/hello...

```

你试了吗？你确定这个服务器在这三个框架下能工作吗？如果没有，试试吧 .阅读很重要，但是这个系列是关于重建的，这意味着你需要去尝试 。大胆的试试吧，我将等你，不用担心 。你需要尝试确保他可以按预先想的那样运行。 好的，你已经体验了  WSGI的威力:他运行你混合选择web服务器和web框架 . WSGI 提供了最小的服务器和框架间的接口 .这很重要且容易实现两边 .下面的代码展示了服务器和框架的接口 :

```
def run_application(application):
    """Server code."""
    # This is where an application/framework stores
    # an HTTP status and HTTP response headers for the server
    # to transmit to the client
    headers_set = []
    # Environment dictionary with WSGI/CGI variables
    environ = {}

    def start_response(status, response_headers, exc_info=None):
        headers_set[:] = [status, response_headers]

    # Server invokes the ‘application' callable and gets back the
    # response body
    result = application(environ, start_response)
    # Server builds an HTTP response and transmits it to the client
    …

def app(environ, start_response):
    """A barebones WSGI app."""
    start_response('200 OK', [('Content-Type', 'text/plain')])
    return ['Hello world!']

run_application(app)

```

他是这样工作的：

1.  框架提供可调用的应用 ( WSGI 没有描述需要如何实现)
    
2.  服务器调用可调用的应用给他接收到的每一个http请求 . 他传递一个 字典_‘environ’_ 包含 WSGI/CGI变量和一个 _‘start_response’_ 可调用接口
    
3.  框架/应用产生  HTTP 状态和 HTTP 响应头传递给 _‘start_response’_ 服务器. 框架/应用也产生响应体
    
4.  服务器组装状态，响应头和响应体为一个  HTTP 响应并传输到客户端
    

下面是一个接口的简单图示：

![WSGI Interface](http://drops.javaweb.org/uploads/images/d1501c644ff9eadcd88c0a4243099920e602142d.jpg)

目前，你已经看来 Pyramid, Flask, and Django Web 应用你也看来服务端的代码实现  WSGI  . 你已经知道了  WSGI 的最难的部分而且他并没有使用任何框架.

但你使用框架写一个web应用时，你在一个更高的水平工作，并没有直接使用  WSGI  , 但是你好奇框架端的  WSGI 接口, 因为你在读这篇文章.

所以，我们创建一个最小的 WSGI Web 应用/Web 框架不使用 Pyramid, Flask, 或者 Django 并在服务器上运行:

```
def app(environ, start_response):
    """A barebones WSGI application.

    This is a starting point for your own Web framework :)
    """
    status = '200 OK'
    response_headers = [('Content-Type', 'text/plain')]
    start_response(status, response_headers)
    return ['Hello world from a simple WSGI application!\n']

```

再次保存 _wsgiapp.py_ 或者从 [GitHub](https://github.com/rspivak/lsbaws/blob/master/part2/wsgiapp.py) 下载并部署在服务器下

```
(lsbaws) $ python webserver2.py wsgiapp:app
WSGIServer: Serving HTTP on port 8888 ...

```

在浏览器输入:

![Simple WSGI Application](http://drops.javaweb.org/uploads/images/52479ca04fc83624e2ce4a5858479e7e9d3b73ba.jpg)

你刚才在学习写服务器的同时已经写了一个自己的最小  WSGI Web 框架 !  .现在我们看服务器给客户端传输了什么？这是当你调用Pyramid应用时服务器产生的 HTTP 响应 :

![HTTP Response Part 1](http://drops.javaweb.org/uploads/images/7517db322651ec0dc2155d9c9e3ba0067cdead04.jpg)

响应有一些相似于第一部分  [Part 1](http://ruslanspivak.com/lsbaws-part1/) 但是他也有一些新东西 .例如他包含四个[HTTP headers](http://en.wikipedia.org/wiki/List_of_HTTP_header_fields)  :_Content-Type_, _Content-Length_, _Date_, and _Server_. 这些头部是一个web服务器应该生产的 .尽管没有一个是严格必须的。

这些头部的目的是为了添加额外的信息给htpp 请求/应答的.

现在你知道了  WSGI 接口, 下面是同样的  HTTP 需要和更多的生成信息 :

![HTTP Response Part 2](http://drops.javaweb.org/uploads/images/589f99851fbf795009b3f2eb37c9e7e7abd1f7d5.jpg)

我还没有说任何关于e **‘environ’** 字典的信息 , 但是基本上他是一个 Python 字典，他必须包含  WSGI 和 CGI 变量 . 服务器从字典中取http请求值 .这是字典内容像这样的 :

![Environ Python Dictionary](http://drops.javaweb.org/uploads/images/10195cc281cee772c9012d42b6590fe44cc7f5d2.jpg)

一个web框架使用字典中的信息决定使用哪一个view 和路由,请求方法等. 哪里读取请求主体和哪里写错误信息，如果有 .到现在你已经创建了你自己的  WSGI Web 服务器和你的web应用. .这是见鬼了的过程 .我们来回顾  WSGI Web server 需要做些什来吸纳关于一个 WSGI 应用:

*   首先，服务器开始并加载应用
*   然后, 服务器读取请求
*   然后, 服务器解析他
*   然后, 服务器使用请求数据创建 _‘environ’_ 字典
*   然后,服务器使用 ‘environ’_ 字典调用应用并添加一个 *‘start_response’_ 获取一个阻塞的 响应体.
*   然后, 服务器创建http响应
*   最后，服务器传输http 响应给客户端

![Server Summary](http://drops.javaweb.org/uploads/images/d2fbcd03f12615ee957b622b8cd4a14b165914e0.jpg)

这就是所有的，你已经有一个可以工作的  WSGI 服务器,服务基本的web应用基于  WSGI 实现，兼容 Web 框架 如 [Django](https://www.djangoproject.com/), [Flask](http://flask.pocoo.org/),[Pyramid](http://trypyramid.com/), 或者你自己的WSGI 框架. 最好的是服务器可以运行多种框架而不必修改服务端代码 .

在你继续之前，考虑下面的问题 , _“怎么才能使你的服务器同时处理多个请求 ?”_继续关注在第三部分我将继续解答  Cheers!