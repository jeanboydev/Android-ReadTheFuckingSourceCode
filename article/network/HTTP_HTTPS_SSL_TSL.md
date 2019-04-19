# HTTP，HTTPS，SSL/TSL
## 概述

## 什么是 HTTP ？

超文本传输协议（HTTP，HyperText Transfer Protocol)是互联网上应用最为广泛的一种网络协议。所有的 WWW 文件都必须遵守这个标准。【摘自百度百科】

伴随着计算机网络和浏览器的诞生，HTTP1.0 也随之而来，处于计算机网络中的应用层，HTTP 是建立在 TCP 协议之上，所以 HTTP 协议的瓶颈及其优化技巧都是基于 TCP 协议本身的特性。

![http 版本][1]

早在 HTTP 建立之初，主要就是为了将超文本标记语言(HTML)文档从 Web 服务器传送到客户端的浏览器。也是说对于前端来说，我们所写的 HTML 页面将要放在我们的 web 服务器上，用户端通过浏览器访问 url 地址来获取网页的显示内容，但是到了 WEB2.0 以来，我们的页面变得复杂，不仅仅单纯的是一些简单的文字和图片，同时我们的 HTML 页面有了 CSS，Javascript，来丰富我们的页面展示，当 ajax 的出现，我们又多了一种向服务器端获取数据的方法，这些其实都是基于 HTTP 协议的。同样到了移动互联网时代，我们页面可以跑在手机端浏览器里面，但是和 PC 相比，手机端的网络情况更加复杂，这使得我们开始了不得不对 HTTP 进行深入理解并不断优化过程中。 

设计 HTTP 最初的目的是为了提供一种发布和接收 HTML 页面的方法。简单来说，HTTP 是一个网络协议，专门用来帮你传输 Web 内容的。

## HTTP 和 TCP 之间的关系

![http TCP][2]

简单地说，TCP 协议是 HTTP 协议的基石——HTTP 协议需要依靠 TCP 协议来传输数据。在网络分层模型中，TCP 被称为“传输层协议”，而 HTTP 被称为“应用层协议”。

![http connect][3]

HTTP 对 TCP 连接的使用，分为两种方式：俗称“短连接”和“长连接”（“长连接(Keep-Alive)”又称“持久连接(Persistent Connection)”）。

![http simple][4]

假设有一个网页，里面包含好多图片，还包含好多【外部的】 CSS 文件和 JS 文件。在“短连接”的模式下，浏览器会先发起一个 TCP 连接，拿到该网页的 HTML 源代码（拿到 HTML 之后，这个 TCP 连接就关闭了）。然后，浏览器开始分析这个网页的源码，知道这个页面包含很多外部资源（图片、CSS、JS）。然后针对【每一个】外部资源，再分别发起一个个 TCP 连接，把这些文件获取到本地（同样的，每抓取一个外部资源后，相应的 TCP 就断开）

![http keep][5]

相反，如果是“长连接”的方式，浏览器也会先发起一个 TCP 连接去抓取页面。但是抓取页面之后，该 TCP 连接并不会立即关闭，而是暂时先保持着（所谓的“Keep-Alive”）。然后浏览器分析 HTML 源码之后，发现有很多外部资源，就用刚才那个 TCP 连接去抓取此页面的外部资源。

在 HTTP 1.0 版本，【默认】使用的是“短连接”（那时候是 Web 诞生初期，网页相对简单，“短连接”的问题不大）；
到了1995年底开始制定 HTTP 1.1 草案的时候，网页已经开始变得复杂（网页内的图片、脚本越来越多了）。这时候再用短连接的方式，效率太低下了（因为建立 TCP 连接是有“时间成本”和“CPU 成本”的）。所以，在 HTTP 1.1 中，【默认】采用的是“Keep-Alive”的方式。

## URI 和 URL 之间的关系

- URI （Uniform Resource Identifier，统一资源标识符）。 

URI 属于 URL 更高层次的抽象，一种字符串文本标准。就是说，URI 属于父类，而 URL 属于 URI 的子类。URL 是 URI 的一个子集。
二者的区别在于，URI 表示请求服务器的路径，定义这么一个资源。而 URL 同时说明要如何访问这个资源（http://）。

```XML
ftp://ftp.is.co.za/rfc/rfc1808.txt (URL)
http://www.ietf.org/rfc/rfc2396.txt (URL)
ldap://[2001:db8::7]/c=GB?objectClass?one (URL)
mailto:John.Doe@example.com (URL)
news:comp.infosystems.www.servers.unix (URL)
tel:+1-816-555-1212
telnet://192.0.2.16:80/ (URL)
urn:oasis:names:specification:docbook:dtd:xml:4.1.2
```

[IANA - Uniform Resource Identifier (URI) SCHEMES（统一资源标识符方案）](http://www.iana.org/assignments/uri-schemes)

具体详见：http://baike.baidu.com/item/URI

- URL（Uniform Resource Locator，统一资源定位符）

通常而言，我们所熟悉的 URL 的常见定义格式为：

```XML
scheme://host[:port#]/path/.../[;url-params][?query-string][#anchor]
```
> scheme //有我们很熟悉的http、https、ftp以及著名的ed2k，迅雷的thunder等。
> 
> host   //HTTP服务器的IP地址或者域名
> 
> port#  //HTTP服务器的默认端口是80，这种情况下端口号可以省略。如果使用了别的端口，必须指明，例如tomcat的默认端口是8080 http://localhost:8080/
> 
> path   //访问资源的路径
> 
> url-params  //所带参数 
> 
> query-string    //发送给http服务器的数据
> 
> anchor //锚点定位

具体详见：http://baike.baidu.com/item/URL

## HTTP 的缺点

1. 通信使用明文（不加密），内容可能会被窃听
2. 不验证通信方的身份，因此有可能遭遇伪装
3. 无法证明报文的完整性，所以有可能已遭篡改

## HTTPS 的诞生

为了解决 HTTP 协议的以上缺点，在上世纪90年代中期，由网景（NetScape）公司设计了 SSL 协议。SSL 是“Secure Sockets Layer”的缩写，中文叫做“安全套接层”。（顺便插一句，网景公司不光发明了 SSL，还发明了很多 Web 的基础设施——比如“CSS 样式表”和“JS 脚本”）。

到了1999年，SSL 因为应用广泛，已经成为互联网上的事实标准。IETF 就在那年把 SSL 标准化。标准化之后的名称改为 TLS（是“Transport Layer Security”的缩写），中文叫做“传输层安全协议”。

很多相关的文章都把这两者并列称呼（SSL/TLS），因为这两者可以视作同一个东西的不同阶段。

互联网加密协议历史：
- 1994年，NetScape 公司设计了 SSL 协议的1.0版，但是未发布。
- 1995年，NetScape 公司发布 SSL 2.0版，很快发现有严重漏洞。
- 1996年，SSL 3.0 版问世，得到大规模应用。
- 1999年，互联网标准化组织 ISOC 接替 NetScape 公司，发布了 SSL 的升级版 TLS 1.0 版。
- 2006年和2008年，TLS 进行了两次升级，分别为 TLS 1.1 版和 TLS 1.2 版。最新的变动是2011年 TLS 1.2 的修订版。

目前，应用最广泛的是TLS 1.0，接下来是SSL 3.0。但是，主流浏览器都已经实现了TLS 1.2的支持。
TLS 1.0通常被标示为SSL 3.1，TLS 1.1为SSL 3.2，TLS 1.2为SSL 3.3。

所谓的 HTTPS 其实是“HTTP over SSL”或“HTTP over TLS”，它是 HTTP 与 SSL/TSL 的结合使用而已。

![http https][6]

## “对称加密”与“非对称加密”

- 明文传输消息

![pass_none][7]

- “加密”和“解密”

通俗而言，你可以把“加密”和“解密”理解为某种【互逆的】数学运算。就好比“加法和减法”互为逆运算、“乘法和除法”互为逆运算。
“加密”的过程，就是把“明文”变成“密文”的过程；反之，“解密”的过程，就是把“密文”变为“明文”。在这两个过程中，都需要一个关键的东西——叫做“密钥”——来参与数学运算。

- “对称加密”

![pass_key][8]

所谓的“对称加密技术”，意思就是说：“加密”和“解密”使用【相同的】密钥。这个比较好理解。就好比你用 7zip 或 WinRAR 创建一个带密码（口令）的加密压缩包。当你下次要把这个压缩文件解开的时候，你需要输入【同样的】密码。在这个例子中，密码/口令就如同刚才说的“密钥”。

存在疑问：密钥怎么传输？
如果密钥可以安全的传输，那么消息也应该可以安全的传输，就像蛋生鸡，鸡生蛋一样。

- “非对称加密”

![pass_pub_pre_key][9]

所谓的“非对称加密技术”，意思就是说：“加密”和“解密”使用【不同的】密钥。当年“非对称加密”的发明，还被誉为“密码学”历史上的一次革命。

被劫持情况：

![pass_pub_hacker][10]

窃听者可以伪造服务器的公钥与客户端通讯，客户端以为是跟服务器通讯，其实是与窃听者在通讯，后果可想而知。


## CA 证书

CA 是 PKI 系统中通信双方信任的实体，被称为可信第三方（Trusted Third Party，简称TTP）。　CA 证书，顾名思义，就是 CA 颁发的证书。

CA 的初始是为了解决上面非对称加密被劫持的情况，服务器申请 CA 证书时将服务器的“公钥”提供给 CA，CA 使用自己的“私钥”将“服务器的公钥”加密后（即：CA证书）返回给服务器，服务器再将“CA 证书”提供给客户端。一般系统或者浏览器会内置 CA 的根证书（公钥），

HTTPS 中 CA 证书的获取
![https_ca][12]

注：上图步骤 2 之后，客户端获取到“CA 证书”会进行本地验证，即使用本地系统或者浏览器中的公钥进行解密，每个“CA 证书”都会有一个证书编号可用于解密后进行比对（具体验证算法请查阅相关资料）。

步骤 5 之前使用的是非对称加密，之后将使用对称加密来提高通讯效率。

## SPDY

2012年google如一声惊雷提出了SPDY的方案，大家才开始从正面看待和解决老版本HTTP协议本身的问题，SPDY可以说是综合了HTTPS和HTTP两者有点于一体的传输协议，缩短 Web 页面的加载时间（50%）。

[SPDY- The Chromium Projects](http://www.chromium.org/spdy/)

![http_spdy][11]

SPDY位于HTTP之下，TCP和SSL之上，这样可以轻松兼容老版本的HTTP协议(将HTTP1.x的内容封装成一种新的frame格式)，同时可以使用已有的SSL功能。

具体详见：http://baike.baidu.com/item/SPDY

## HTTP2.0

顾名思义有了HTTP1.x，那么HTTP2.0也就顺理成章的出现了。HTTP2.0可以说是SPDY的升级版（其实原本也是基于SPDY设计的），但是，HTTP2.0 跟 SPDY 仍有不同的地方，主要是以下两点：
HTTP2.0 支持明文 HTTP 传输，而 SPDY 强制使用 HTTPS。
HTTP2.0 消息头的压缩算法采用 HPACK，而非 SPDY 采用的 DEFLATE。

具体详见：http://baike.baidu.com/item/HTTP%202.0

## 参考资料

《图解HTTP》、《图解TCP/IP》、百度百科

[1]:https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/network/http_version.jpg
[2]:https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/network/http_tcp.jpg
[3]:https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/network/http_connect.jpg
[4]:https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/network/http_connect_simple.jpg
[5]:https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/network/http_connect_keep.jpg
[6]:https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/network/http_https.jpg
[7]:https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/network/pass_none.jpg
[8]:https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/network/pass_key.jpg
[9]:https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/network/pass_pub_pre_key.jpg
[10]:https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/network/pass_pub_hacker.jpg
[11]:https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/network/http_spdy.jpg
[12]:https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/network/https_ca.jpg

## 我的公众号

欢迎你「扫一扫」下面的二维码，关注我的公众号，可以接受最新的文章推送，有丰厚的抽奖活动和福利等着你哦！😍

<img src="https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/about_me/qrcode_android_besos_black_512.png" width=250 height=250 />

如果你有什么疑问或者问题，可以 [点击这里](https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/issues) 提交 issue，也可以发邮件给我 [jeanboy@foxmail.com](mailto:jeanboy@foxmail.com)。

同时欢迎你 [![Android技术进阶：386463747](https://camo.githubusercontent.com/615c9901677f501582b6057efc9396b3ed27dc29/687474703a2f2f7075622e69647171696d672e636f6d2f7770612f696d616765732f67726f75702e706e67)](http://shang.qq.com/wpa/qunwpa?idkey=0b505511df9ead28ec678df4eeb7a1a8f994ea8b75f2c10412b57e667d81b50d) 来一起交流学习，群里有很多大牛和学习资料，相信一定能帮助到你！

