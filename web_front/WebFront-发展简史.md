# 前端发展简史

## 起源

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/web_front_trend/time_line.png" alt=""/>

- 1990 HTML

1990 年，Tim 以超文本语言 HTML 为基础在 NeXT 电脑上发明了最原始的 Web 浏览器。

1991 年，Tim 作为布道者在 Internet 上广泛推广 Web 的理念，与此同时，美国国家超算应用中心（National Center for Supercomputer Applications）对此表现出了浓厚的兴趣，并开发了名为 Mosaic 的浏览器，于 1993 年 4 月进行了发布。

1994 年 5 月，第一届万维网大会在日内瓦召开。

- 1994.7 HTML 2.0 规范发布

1994 年 9 月，因特网工程任务组（Internet Engineering Task Force）设立了 HTML 工作组。

1994 年 11 月，Mosaic 浏览器的开发人员创建了网景公司（Netscape Communications Corp.），并发布了 Mosaic Netscape 1.0 beta 浏览器，后改名为 Navigator。

- 1994 万维网联盟（World Wide Web Consortium）成立，简称 W3C

1994 年底，由 Tim 牵头的万维网联盟（World Wide Web Consortium）成立，这标志着万维网的正式诞生。

此时的网页以 HTML 为主，是纯静态的网页，网页是“只读”的，信息流只能通过服务器到客户端单向流通，由此世界进入了 Web 1.0 时代。

- 1995 网景推出 JavaScript

1995 年，网景工程师 Brendan Eich 花了10天时间设计了 JavaScript 语言。起初这种脚本语言叫做 Mocha，后改名 LiveScript，后来为了借助 Java 语言创造良好的营销效果最终改名为 JavaScript。网景公司把这种脚本语言嵌入到了 Navigator 2.0 之中，使其能在浏览器中运行。

与此相对的是，1996 年，微软发布了 VBScript 和 JScript。JScript 是对 JavaScript 进行逆向工程的实现，并内置于 Internet Explorer 3 中。但是 JavaScript 与 JScript 两种语言的实现存在差别，这导致了程序员开发的网页不能同时兼容 Navigator 和 Internet Explorer 浏览器。 Internet Explorer 开始抢夺 Netscape 的市场份额，这导致了第一次浏览器战争。

## 第一次浏览器战争

1996 年 11 月，为了确保 JavaScript 的市场领导地位，网景将 JavaScript 提交到欧洲计算机制造商协会（European Computer Manufacturers Association）以便将其进行国际标准化。

- 1996.12 W3C 推出了 CSS 1.0 规范

- 1997.1 HTML3.2 作为 W3C 推荐标准发布

- 1997.6 ECMA 以 JavaScript 语言为基础制定了 ECMAScript 1.0 标准规范

1997 年 6 月，ECMA 以 JavaScript 语言为基础制定了 ECMAScript 标准规范 ECMA-262。JavaScript 是 ECMAScript 规范最著名的实现之一，除此之外，ActionScript 和 JScript 也都是 ECMAScript 规范的实现语言。自此，浏览器厂商都开始逐步实现 ECMAScript 规范。

- 1997.12 HTML 4.0 规范发布

- 1998 W3C 推出了 CSS 2.0 规范

- 1998.6 ECMAScript 2 规范发布

1998 年 6 月，ECMAScript 2 规范发布，并通过 ISO 生成了正式的国际标准 ISO/IEC 16262 。

- 1999.12 ECMAScript 3 规范发布

1999 年 12 月，ECMAScript 3 规范发布，在此后的十年间，ECMAScript 规范基本没有发生变动。ECMAScript 3 成为当今主流浏览器最广泛使用和实现的语言规范基础。

第一次浏览器战争以 IE 浏览器完胜 Netscape 而结束，IE 开始统领浏览器市场，份额的最高峰达到 2002 年的 96%。随着第一轮大战的结束，浏览器的创新也随之减少。

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/web_front_trend/netspace.png" alt=""/>

## XHTML

- 1999 W3C 发布 HTML 4.01 标准，同年微软推出用于异步数据传输的 ActiveX，随即各大浏览器厂商模仿实现了 XMLHttpRequest（AJAX 雏形）。
- 2000: W3C 采用了一个大胆的计划，把 XML 引入 HTML，XHTML1.0 作为 W3C 推荐标准发布
- 2001.5 W3C 推出了 CSS 3.0 规范草案
- 2002-2006 XHTML 2.0 最终放弃
- 2009 W3C 宣布 XHTML2.0 不再继续，宣告死亡

## 动态页面的崛起

JavaScript 诞生之后，可以用来更改前端 DOM 的样式，实现一些类似于时钟之类的小功能。那时候的JavaScript 仅限于此，大部分的前端界面还很简单，显示的都是纯静态的文本和图片。这种静态页面不能读取后台数据库中的数据，为了使得 Web 更加充满活力，以 PHP、JSP、ASP.NET 为代表的动态页面技术相继诞生。

PHP（PHP：Hypertext Preprocessor）最初是由 Rasmus Lerdorf 在 1995 年开始开发的，现在PHP 的标准由 PHP Group 维护。PHP 是一种开源的通用计算机脚本语言，尤其适用于网络开发并可嵌入 HTML 中使用。PHP 的语法借鉴吸收 C 语言、Java 和 Perl 等流行计算机语言的特点，易于一般程序员学习。PHP 的主要目标是允许网络开发人员快速编写动态页面。

JSP（JavaServer Pages）是由 Sun 公司倡导和许多公司参与共同创建的一种使软件开发者可以响应客户端请求，从而动态生成 HTML、XML 或其他格式文档的 Web 网页的技术标准。JSP 技术是以 Java 语言为基础的。1999 年，JSP 1.2 规范随着 J2EE 1.2 发布。

ASP（Active Server Pages）1.0 在 1996 年随着 IIS 3.0 而发布。2002 年，ASP.NET 发布，用于替代 ASP。

随着这些动态服务器页面技术的出现，页面不再是静止的，页面可以获取服务器数据信息并不断更新。以 Google 为代表的搜索引擎以及各种论坛相继出现，使得 Web 充满了活力。

随着动态页面技术的不断发展，后台代码变得庞大臃肿，后端逻辑也越来越复杂，逐渐难以维护。此时，后端的各种 MVC 框架逐渐发展起来，以 JSP 为例，Struct、Spring 等框架层出不穷。

从 Web 诞生至 2005 年，一直处于后端重、前端轻的状态。

- AJAX 的流行

在 Web 最初发展的阶段，前端页面要想获取后台信息需要刷新整个页面，这是很糟糕的用户体验。

Google 分别在 2004 年和 2005 年先后发布了两款重量级的 Web 产品：Gmail 和 Google Map。这两款 Web 产品都大量使用了 AJAX 技术，不需要刷新页面就可以使得前端与服务器进行网络通信，这虽然在当今看来是理所应当的，但是在十几年前AJAX却是一项革命性的技术，颠覆了用户体验。

随着 AJAX 的流行，越来越多的网站使用 AJAX 动态获取数据，这使得动态网页内容变成可能，像 Facebook 这样的社交网络开始变得繁荣起来，前端一时间呈现出了欣欣向荣的局面。

AJAX 使得浏览器客户端可以更方便地向服务器发送数据信息，这促进了 Web 2.0 的发展。

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/web_front_trend/ajax.png" alt=""/>

Google Trend: AJAX 从 2005 年开始得到开发人员的广泛关注。

- 2006 XMLHttpRequest 被 W3C 正式纳入标准。

## 第二次浏览器大战

- 前端兼容性框架的出现

IE 在第一次浏览器大战中击败 Netscape 赢得胜利，垄断了浏览器市场。作为独裁者，IE 并不遵循 W3C 的标准，IE 成了事实标准。

Netscape 于 1998 年被 AOL 收购前创建了 Mozilla 社区，Firefox 于 2004 年 11 月首次发布，并且 9 个月内下载量超过 6000 万，获取了巨大的成功，IE 的主导地位首次受到了挑战， Firefox 被认为是 Netscape 的精神续作。

之后 Firefox 浏览器一路奋起直追，逐渐蚕食 IE 市场份额，这引发了第二次浏览器战争。在 2008 年底时，Firefox 的市场份额达到了 25% 以上，IE 则跌至 65% 以下。

第二次浏览器战争中，随着以 Firefox 和 Opera 为首的 W3C 阵营与 IE 对抗程度的加剧，浏览器碎片化问题越来越严重，不同的浏览器执行不同的标准，对于开发人员来说这是一个恶梦。

为了解决浏览器兼容性问题，Dojo、jQuery、YUI、ExtJS、MooTools 等前端 Framework 相继诞生。前端开发人员用这些 Framework 频繁发送 AJAX 请求到后台，在得到数据后，再用这些 Framework 更新 DOM 树。

其中，jQuery 独领风骚，几乎成了所有网站的标配。Dojo、YUI、ExtJS 等提供了很多组件，这使得开发复杂的企业级 Web 应用成为可能。

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/web_front_trend/jquery.png" alt=""/>

Google Trend: 蓝色 jQuery，红色 Dojo，绿色 YUI，紫色 ExtJS，黄色 MooTools

## HTML 5

1999年，W3C发布了 HTML 4.01 版本，在之后的几年，没有再发布更新的 Web 标准。随着Web的迅猛发展，旧的Web标准已不能满足 Web 应用的快速增长。

2004 年 6 月，Mozilla 基金会和 Opera 软件公司在万维网联盟（W3C）所主办的研讨会上提出了一份联合建议书，其中包括 Web Forms 2.0 的初步规范草案。建议举行一次投票，以表决 W3C 是否应该扩展 HTML 和 DOM，从而满足 Web 应用中的新需求。研讨会最后以 8 票赞成，14 票反对否决此建议，这引起一些人的不满，不久后，部分浏览器厂商宣布成立网页超文本技术工作小组（WHATWG），以继续推动该规范的开发工作，该组织再度提出 Web Applications 1.0 规范草案，后来这两种规范合并形成 HTML5。2007 年，获得 W3C 接纳，并成立了新的 HTML 工作团队。2008 年 1 月 22 日，第一份正式草案发布。

- 2008.12 Chrome 发布，JavaScript 引擎 V8

HTML5 草案发布不久，Google 在 2008 年 12 月发布了 Chrome 浏览器，加入了第二次浏览器大战当中。Chrome 使用了 Safari 开源的 WebKit 作为布局引擎，并且研发了高效的 JavaScript 引擎 V8。

尽管 HTML5 在网络开发人员中非常出名了，但是它成为主流媒体的一个话题是在 2010 年的 4 月，当时苹果公司的 CEO 乔布斯发表一篇题为“对 Flash 的思考”的文章，指出随着 HTML5 的发展，观看视频或其它内容时，Adobe Flash 将不再是必须的。这引发了开发人员间的争论，包括 HTML5 虽然提供了加强的功能，但开发人员必须考虑到不同浏览器对标准不同部分的支持程度的不同，以及 HTML5 和 Flash 间的功能差异。

在第二次浏览器大战中，各个浏览器厂商都以提升 JavaScript 运行效率和支持 HTML5 各种新特性为主要目标，促进了浏览器的良性竞争。在这一场战争中，Chrome 攻城略地，抢夺 IE 市场份额。2013 年，Chrome 超过 IE，成为市场份额最高的浏览器。2016 年，Chrome 占据了浏览器市场的半壁江山。

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/web_front_trend/browser_trend.png" alt=""/>

全球浏览器市场份额（2009-2017）

自 2008 年以来，浏览器中不断支持的 HTML5 新特性让开发者激动不已：WebWorker 可以让 JavaScript 运行在多线程中，WebSocket 可以实现前端与后台的双工通信，WebGL 可以创建 Web3D 网页游戏......

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/web_front_trend/html5_support.png" alt=""/>

桌面浏览器对 HTML5 支持程度（2009-2017）

- 2009.12 ECMAScript 5.0 规范发布

- 2011.6 ECMAScript 5.1 规范发布

- 2012.10 微软发布 TypeScript 公开版

TypeScript 是一种由微软开发的自由和开源的编程语言。它是 JavaScript 的一个超集，而且本质上向这个语言添加了可选的静态类型和基于类的面向对象编程。

TypeScript 扩展了 JavaScript 的语法，所以任何现有的 JavaScript 程序可以不加改变的在 TypeScript 下工作。TypeScript 是为大型应用之开发而设计，而编译时它产生 JavaScript 以确保兼容性。

- 2013.6.19 TypeScript 0.9 正式版

- 2014.10.28 W3C 正式发布 HTML 5.0 推荐标准

2014 年 10 月 28 日，W3C 正式发布 HTML 5.0 推荐标准。

## Node.js 的爆发

早在 1994 年，Netspace 就公布了其 Netspace Enterprise Server 中的一种服务器脚本实现，叫做 LiveWire，是最早的服务器端 JavaScript，甚至早于浏览器中的 JavaScript。对于这门图灵完备的语言，Netspace 很早就开始尝试将它用在后端。

微软在 1996 年发布的 IE 3.0 中内嵌了自己的 JScript语言，其兼容 JavaScript 语法。1997 年年初，微软在它的服务器 IIS 3.0 中也包含了 JScript，这就是我们在 ASP 中能使用的脚本语言。

1997 年，Netspace 为了用 Java 实现 JavaScript 而创建了 Rhino 项目，最终 Rhino 演变成一个基于 Java 实现的 JavaScript 引擎，由 Mozilla 维护并开源。Rhino 可以为 Java 应用程序提供脚本能力。2006 年 12 月，J2SE 6 将 Rhino 作为 Java 默认的脚本引擎。

SpiderMonkey 是 Mozilla 用 C/C++ 语言实现的一个 JavaScript 引擎，从 Firefox 3.5 开始作为 JavaScript 编译引擎，并被 CouchDB 等项目作为服务端脚本语言使用。

可以看到，JavaScript 最开始就能同时运行在前后端，但时在前后端的待遇却不尽相同。随着 Java、PHP、.Net 等服务器端技术的风靡，与前端浏览器中的 JavaScript 越来越流行相比，服务端 JavaScript 逐渐式微。

2008 年 Chrome 发布，其 JavaScript 引擎 V8 的高效执行引起了 Ryan Dahl 的注意。2009 年，Ryan 利用 Chrome 的 V8 引擎打造了基于事件循环的异步 I/O 框架 —— Node.js 诞生。

Node.js 具有以下特点：

- 基于事件循环的异步 I/O 框架，能够提高 I/O 吞吐量
- 单线程运行，能够避免了多线程变量同步的问题
- 使得 JavaScript 可以编写后台代码，前后端编程语言统一。

Node.js 的出现吸引了很多前端开发人员开始用 JavaScript 开发服务器代码，其异步编程风格也深受开发人员的喜爱。Node.js 的伟大不仅在于拓展了 JavaScript 在服务器端的无限可能，更重要的是它构建了一个庞大的生态系统。

2010 年 1 月，NPM 作为 Node.js 的包管理系统首次发布。开发人员可以按照 CommonJS 的规范编写 Node.js 模块，然后将其发布到 NPM 上面供其他开发人员使用。目前 NPM 具有 40 万左右的模块，是世界上最大的包模块管理系统。

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/web_front_trend/npm.png" alt=""/>

2016 年常见包管理系统模块数量，NPM 高居榜首

Node.js 也催生了 node-webkit 等项目，用 JavaScript 开发跨平台的桌面软件也成为可能。Node.js 给开发人员带来了无穷的想象，JavaScript 大有一统天下的趋势。



## 前端 MV* 架构

随着 HTML5 的流行，前端不再是人们眼中的小玩意，以前在 C/S 中实现的桌面软件的功能逐步迁移到了前端，前端的代码逻辑逐渐变得复杂起来。

以前只用于后台的 MV* 等架构在前端逐渐使用起来，以下列举了部分常用的 MV* 框架。

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/web_front_trend/mv_.png" alt=""/>


随着这些 MV* 框架的出现，网页逐渐由 Web Site 演变成了 Web App，最终导致了复杂的单页应用（ Single Page Application）的出现。


## 移动 Web 和 Hybrid App


随着 iOS 和 Android 等智能手机的广泛使用，移动浏览器也逐步加强了对 HTML5 特性的支持力度。

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/web_front_trend/mobile_html5_support.png" alt=""/>

移动浏览器对 HTML5 支持程度（2009-2017）

移动浏览器的发展，导致了流量入口逐渐从 PC 分流到移动平台，这是 Web 发展的新机遇。移动 Web 面临着更大的碎片化和兼容性问题，jQuery Mobile、Sencha Touch、Framework7、Ionic 等移动 Web 框架也随之出现。

相比于 Native App，移动 Web 开发成本低、跨平台、发布周期短的优势愈发明显，但是 Native App的性能和 UI 体验要远胜于移动 Web。移动 Web 与 Native App 孰优孰劣的争论愈演愈烈，在无数开发者的实践中，人们发现两者不是替代关系，而是应该将两者结合起来，取长补短，Hybrid 技术逐渐得到认同。

Hybrid 技术指的是利用 Web 开发技术，调用 Native 相关 API，实现移动与 Web 二者的有机结合，既能体现 Web 开发周期短的优势，又能为用户提供 Native 体验。

根据实现原理，Hybrid 技术可以分为两大类：

1. 将 HTML 5 的代码放到 Native App 的 WebView 控件中运行，WebView 为 Web 提供宿主环境，JavaScript 代码通过 WebView 调用 Native API。典型代表有 PhoneGap(Cordova) 以及国内的 AppCan 等。

2. 将 HTML 5 代码针对不同平台编译成不同的原生应用，实现了 Web 开发，Native 部署。这一类的典型代表有 Titanium 和 NativeScript。

Hybrid 一系列技术中很难找出一种方案适应所有应用场景，我们需要根据自身需求对不同技术进行筛选与整合。


## ECMAScript 6

JavaScript 语言是 ECMAScript 标准的一种实现，截止 2017 年 2 月，ECMAScript 一共发布了 7 个版本。

1997 年 6 月， ECMAScript 1.0 标准发布。

1998 年 6 月，ECMAScript 2.0 发布。

1999 年 12 月，ECMAScript 3.0 发布。

2007 年 10 月，Mozilla 主张的 ECMAScript 4.0 版草案发布，对 3.0 版做了大幅升级，该草案遭到了以 Yahoo、Microsoft、Google 为首的大公司的强烈反对，JavaScript 语言的创造者 Brendan Eich 和 IE 架构师 Chris Wilson 甚至在博客上就ES4向后兼容性问题打起了口水仗，最后由于各方分歧太大，ECMA 开会决定废弃中止 ECMAScript 4.0 草案。经各方妥协，在保证向下兼容的情况下，将部分增强的功能放到 ECMAScript 3.1 标准中，将原有 ECMAScript 4.0 草案中激进的功能放到以后的标准中。不久，ECMAScript 3.1 就改名为 ECMAScript 5。

2009 年 12 月，本着'Don’t break the web'原则，ECMAScript 5 发布。新增了 strict 模式、属性 getter 和 setter 等。

2011 年 6 月，ECMAScript 5.1 发布。

2015 年 6 月，ECMAScript 6.0 发布。该版本增加了许多新的语法，包括支持 let、const、Arrow function、Class、Module、Promise、Iterator、Generator、Set、Map、async、Symbol、Proxy、Reflect、Decorator 等。TC39 委员会计划以后每年都发布一个新版本的 ECMAScript，所以 ECMAScript 6.0 改名为 ECMAScript 2015。

2016 年 6 月，在 ECMAScript 2015 的基础上进行了部分增强，发布了 ECMAScript 2016。

在 ECMAScript 的各个版本中，ECMAScript 6.0 无疑最受人瞩目的，它增加了许多新特性，极大拓展了 JavaScript 语法和能力，以至于许多浏览器都只能支持部分 ES6 中的新特性。随之，Babel 和 TypeScript 逐渐流行起来，编写 ES6 代码，然后用 Babel 或 TypeScript 将其编译为 ES5 等浏览器支持的 JavaScript。

ECMAScript 以后每年将会发布一个新版本，这无疑将持续促使浏览器厂商不断为 JavaScript 注入新的功能与特性，JavaScript走上了快速发展的正轨。


## 参考资料

- [前端发展简史](http://www.360doc.com/content/17/0601/20/35378950_659102709.shtml)
- [前端发展史](https://www.jianshu.com/p/8dc5c6aa01fc)


