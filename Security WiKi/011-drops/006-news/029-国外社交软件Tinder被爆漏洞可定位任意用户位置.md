# 国外社交软件Tinder被爆漏洞可定位任意用户位置

Tinder是国外的一款手机交友APP，这款应用在推出的两个月内，推荐匹配了超过 100 万对的爱慕者（双方第一眼互有好感），并获取了 3500 万个用户的账号打分。而它最初的着力点，正是在校园。它的功能实际很简单：基于你的地理位置，应用每天为你“推荐”一定距离内的四个对象，根据你们在 Facebook 上面的共同好友数量、共同兴趣和关系网给出评分，得分最高的推荐对象优先展示。

![enter image description here](http://drops.javaweb.org/uploads/images/34296b0fe1f1b4a97e78b70c00f5f7808834e4f5.jpg)

在2013年七月的时候，Tinder就被爆有API接口暴露iOS客户端的经纬度，可以定位任意用户位置。

下面介绍的这个API是新发现的，而不是之前被暴露的。

通过代理抓取iPhone的请求，抓取Tinder的通信情况，抓到一个API通过用户的ID返回信息如下：

```
{
   "status":200,
   "results":{
      "bio":"",
      "name":"Anthony",
      "birth_date":"1981-03-16T00:00:00.000Z",
      "gender":0,
      "ping_time":"2013-10-18T18:31:05.695Z",
      "photos":[
      //cut to save space
      ],
      "id":"52617e698525596018001418",
      "common_friends":[

      ],
      "common_likes":[

      ],
      "common_like_count":0,
      "common_friend_count":0,
      "distance_mi":4.760408451724539
   }
}

```

不再返回准确的GPS信息，但是`distance_mi`字段为距离信息，是一个64位双精度字段，精确度非常的高了。

利用此信息，我们就可以获取改ID对应用户的比较准确的GPS信息。看看下图你就明白了：

![enter image description here](http://drops.javaweb.org/uploads/images/818803047821836c05118583e88797f166e50b60.jpg)

利用三个位置的距离信息就可以定位到该用户的准确位置，其原理与GPS定位是一样的。

通过伪造GPS信息，通过API​​来告诉Tinder，我在任意的位置，并查询API查找到用户的距离。

创建Tinder的3个测试账号。然后告诉了Tinder的API，我所在的三个位置，以及到该用户的距离。

然后，根据[公式](https://en.wikipedia.org/wiki/Trilateration#Derivation)就可以算出该用户的GPS信息了。

这种问题似乎微信与陌陌之前也有，不知道现在还有没有呢？:)