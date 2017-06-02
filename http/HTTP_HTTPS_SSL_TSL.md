# HTTP，HTTPS，SSL/TSL #
## 概述

## HTTP

超文本传输协议（HTTP，HyperText Transfer Protocol)是互联网上应用最为广泛的一种网络协议。所有的WWW文件都必须遵守这个标准。设计HTTP最初的目的是为了提供一种发布和接收HTML页面的方法。
Web 使用一种名为 HTTP 的协议作为规范，完成从客户端到服务器端等一系列运作流程。而协议是指规则的约定。

简单来说，HTTP 是一个网络协议，专门用来帮你传输 Web 内容的。

流程图：开始->浏览网页->http://www.baidu.com->HTTP协议生成请求报文->TCP协议将HTTP请求报文分割成报文段（数据包）->IP协议搜索对方的地址---->TCP协议接收报文段（数据包）重组->HTTP协议处理请求

## URI 和 URL

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

IANA - Uniform Resource Identifier (URI) SCHEMES（统一资源标识符方案）
http://www.iana.org/assignments/uri-schemes

具体详见：http://baike.baidu.com/item/URI

- URL（Uniform Resource Locator，统一资源定位符）

通常而言，我们所熟悉的 URL 的常见定义格式为：

```XML
scheme://host[:port#]/path/.../[;url-params][?query-string][#anchor]
```
> scheme //有我们很熟悉的http、https、ftp以及著名的ed2k，迅雷的thunder等。
> host   //HTTP服务器的IP地址或者域名
> port#  //HTTP服务器的默认端口是80，这种情况下端口号可以省略。如果使用了别的端口，必须指明，例如tomcat的默认端口是8080 http://localhost:8080/
> path   //访问资源的路径
> url-params  //所带参数 
> query-string    //发送给http服务器的数据
> anchor //锚点定位

具体详见：http://baike.baidu.com/item/URL


## HTTP 通讯

1. 建立 TCP 连接（3次握手）
2. Http 请求1
3. Http 响应1
4. Http 请求2
5. Http 响应2
6. ...
7. 断开 TCP 连接（4次握手）

## HTTP 缺点
1. 通信使用明文（不加密），内容可能会被窃听
2. 不验证通信方的身份，因此有可能遭遇伪装
3. 无法证明报文的完整性，所以有可能已遭篡改

## HTTPS

SSL 是“Secure Sockets Layer”的缩写，中文叫做“安全套接层”。它是在上世纪90年代中期，由网景（NetScape）公司设计的。（顺便插一句，网景公司不光发明了 SSL，还发明了很多 Web 的基础设施——比如“CSS 样式表”和“JS 脚本”）。

为什么要发明 SSL 这个协议？因为原先互联网上使用的 HTTP 协议是明文的，存在很多缺点——比如传输内容会被偷窥（嗅探）和篡改。发明 SSL 协议，就是为了解决这些问题。
到了1999年，SSL 因为应用广泛，已经成为互联网上的事实标准。IETF 就在那年把 SSL 标准化。标准化之后的名称改为 TLS（是“Transport Layer Security”的缩写），中文叫做“传输层安全协议”。
很多相关的文章都把这两者并列称呼（SSL/TLS），因为这两者可以视作同一个东西的不同阶段。

互联网加密协议历史：
1994年，NetScape 公司设计了 SSL 协议（Secure Sockets Layer）的1.0版，但是未发布。
1995年，NetScape 公司发布 SSL 2.0版，很快发现有严重漏洞。
1996年，SSL 3.0 版问世，得到大规模应用。
1999年，互联网标准化组织 ISOC 接替 NetScape 公司，发布了 SSL 的升级版 TLS 1.0 版。
2006年和2008年，TLS 进行了两次升级，分别为 TLS 1.1 版和 TLS 1.2 版。最新的变动是2011年 TLS 1.2 的修订版。

目前，应用最广泛的是TLS 1.0，接下来是SSL 3.0。但是，主流浏览器都已经实现了TLS 1.2的支持。
TLS 1.0通常被标示为SSL 3.1，TLS 1.1为SSL 3.2，TLS 1.2为SSL 3.3。

“HTTP over SSL”或“HTTP over TLS”

HTTPS = HTTP + SSL/TSL

http://www.techug.com/post/https-ssl-tls.html

https://sanwen8.cn/p/3edfj7S.html