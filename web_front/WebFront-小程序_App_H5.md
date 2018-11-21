## 小程序的实现原理

![01](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/web_front_app/01.png)

根据微信官方的说明，微信小程序的运行环境有 3 个平台，iOS 的 WebKit（苹果开源的浏览器内核），Android 的 X5 (QQ 浏览器内核)，开发时用的 nw.js（C++ 实现的 web 转桌面应用）。

| 平台     | 渲染                          | js 运行环境    |
| -------- | ----------------------------- | -------------- |
| iOS      | WKWebView                     | JavaScriptCore |
| Android  | X5 基于 Mobile Chrome 37 内核 | X5 JSCore      |
| 开发工具 | Chrome WebView                | nw.js          |

小程序运行时会创建两个线程：View Thread 和 AppService Thread，相互隔离，通过桥接协议 WeixinJsBridage 进行通信（包括 setData 调用、canvas 指令和各种 DOM 事件）。

下述表格展示了两个线程的区别：

| 线程名称   | 所属模块 | 运行代码  | 原理                | 说明                                                         |
| ---------- | -------- | --------- | ------------------- | ------------------------------------------------------------ |
| View       | 视图层   | WXML/WXSS | WebView 渲染        | wxml 编译器把 wxml 文件转为 js 并构建 virtual dom；wxss 编译器把 wxss 文件转化为 js。 |
| AppService | 逻辑层   | JS        | JavascriptCore 运行 | 无法访问 window / document 对象                              |

两个线程是通过系统层的 JSBridage 来通信的，逻辑层把数据变化通知到视图层，触发视图层页面更新，视图层把触发的事件通知到逻辑层进行业务处理。

## 小程序与 App 的区别

![02](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/web_front_app/02.png)

- 运行环境

  原生 App 直接运行在操作系统的单独进程中（在 Android 中还可以开启多进程），而小程序只能运行在微信的进程中。

- 开发成本

  原生 App 的开发涉及到 Android/iOS 多个平台、开发工具、开发语言、不同设备的适配等问题；而小程序只需要开发一个就可以在 Android/iOS 等不同平台不同设备上运行。

  原生 App 需要在商店上架（Android 需要上架各种商店）；小程序只能在微信平台发布。

- 系统权限

  原生 App 调用的是系统资源，也就是说系统提供给开发的的 API 都可以使用；而小程序是基于微信的，小程序所有的功能都受限于微信，也就是说微信给开发者提供 API 才可以使用，不能绕过微信直接使用系统提供的 API。

  原生 App 可以给用户推送消息；小程序不允许主动给用户发送消息，只能回复模版消息 。

  原生 App 有独立的数据库，可以做离线存储；小程序只能存储到 LocalStorage，无法做离线存储。

  原生 App 需要下载，安装包比较大；小程序无需下载，可以通过小程序码等方式通过微信直接打开。

- 运行流畅度

  原生 App 运行在操作系统中，所有的原生组件可以直接调用 GPU 进行渲染；而小程序运行在微信的进程中，只能通过 WebView 进行渲染。

## 小程序与 H5 的区别

![03](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/web_front_app/03.png)

- 运行环境

简单来说，小程序是一种应用，运行的环境是微信（App）；H5 是一种技术，依附的外壳是是浏览器。

H5 的运行环境是浏览器，包括 WebView，而微信小程序的运行环境并非完整的浏览器，因为小程序的开发过程中只用到一部分H5 技术。

小程序的运行环境是微信开发团队基于浏览器内核完全重构的一个内置解析器，针对性做了优化，配合自己定义的开发语言标准，提升了小程序的性能。

小程序中无法使用浏览器中常用的 window 对象和 document 对象，H5 可以随意使用。

- 开发成本

H5 的开发，涉及开发工具（vscode、Atom等）、前端框架（Angular、react等）、模块管理工具（Webpack 、Browserify 等）、任务管理工具（Grunt、Gulp等），还有 UI 库选择、接口调用工具（ajax、Fetch Api等）、浏览器兼容性等等。

尽管这些工具可定制化非常高，大部分开发者也有自己的配置模板，但对于项目中各种外部库的版本迭代、版本升级，这些成本加在一起那就是个不小数目了。

而开发一个微信小程序，由于微信团队提供了开发者工具，并且规范了开发标准，则简单得多。前端常见的 HTML、CSS 变成了微信自定义的 WXML、WXSS，官方文档中都有明确的使用介绍，开发者按照说明专注写程序就可以了。

需要调用后端接口时，调用发起请求API；需要上传下载时，调用上传下载API；需要数据缓存时，调用本地存储API；引入地图、使用罗盘、调用支付、调用扫码等等功能都可以直接使用；UI 库方面，框架带有自家 weui 库加成。

并且在使用这些 API 时，不用考虑浏览器兼容性，不用担心出现 BUG，显而易见微信小程序的开发成本相对低很多。

- 系统权限

微信小程序相对于 H5 能获得更多的系统权限，比如：网络通信状态、数据缓存能力等，这些系统级权限都可以和微信小程序无缝衔接。

而这一点恰巧是 H5 被诟病的地方，这也是 H5 的大多应用场景被定位在业务逻辑简单、功能单一的原因。

- 运行流畅度

这条无论对于用户还是开发者来说，都是最直观的感受。长久以来，当HTML5应用面对复杂的业务逻辑或者丰富的页面交互时，它的体验总是不尽人意，需要不断的对项目优化来提升用户体验。但是由于微信小程序运行环境独立，尽管同样用 `HTML` +`CSS` + `JS` 去开发，但配合微信的解析器最终渲染出来的是原生组件的效果，自然体验上将会更进一步。

## 小程序多平台互转原理

![04](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/web_front_app/04.png)

微信小程序与支付宝小程序有很多相似之处，可以封装两个小程序之间的差异进行转换，从而实现一套逻辑代码运行在两个平台。

项目目录结构：

```json
|-ProjectName
    |-arch//基础框架
        |-arch.js//框架入口，只需要导入这一个 js 即可
        |-cache.js//缓存相关，封装了 LocalStorage
        |-net.js//网络相关，封装了 网路请求
        |-page.js//页面跳转相关，封装了导航操作
        |-phone.js//设备相关，封装了系统信息，打电话，扫码，剪切板，定位，支付
        |-ui.js//平台 UI 相关，封装了 Toast，Alert，Loading，ActionSheet，NavigationBar
    |-config//项目配置
        |-api.js//项目 API 相关，接口参数配置等
        |-config.js//项目配置，如：平台判断，LocalStorage 的 key
    |-pages//页面
        |-home 
            |-home.acss/wxss
            |-home.axml/wxml
            |-home.js
            |-home.json
    |-utils//工具类
        |-crypto-js.min.js//加密工具库（按需添加）
        |-date.js//常用 Date 操作
        |-money.js//常用 money 操作
        |-net-api.js//自定义通用 API 请求方式，如：封装统一头部和响应体
        |-param.js//参数加密（按需添加）
```

- API 差异

```javascript
//微信小程序
wx.setStorageSync("key", "value")

//支付宝小程序
my.setStorageSync({
  key:"key",
  data:"value"
})
```

封装后的 API：

```javascript
function set(key, value) {
    if (config.isAlipay) {
        my.setStorageSync({
            key: key,
            data: value,
        });
    } else {
        wx.setStorageSync(key, value);
    }
}
```

- 布局差异

```html
<!-- 微信小程序 -->
<view bindtap="onClick"
touchstart="onTouchStart"
touchmove="onTouchMove"
touchcancel="onTouchCancel"
touchend="onTouchEnd"
tap="onTap"></view>

<!-- 支付宝小程序 -->
<view onTap="onClick"
touchStart="onTouchStart"
touchMove="onTouchMove"
touchCancel="onTouchCancel"
touchEnd="onTouchEnd"
tap="onTap"></view>
```

可以通过程序进行转换。

## 小程序平台

- [微信](https://mp.weixin.qq.com/cgi-bin/wx)
- [支付宝](https://open.alipay.com/channel/miniIndex.htm)
- [百度](https://smartprogram.baidu.com/mappconsole/main/login)
- 今日头条
- 淘宝
- 抖音
- QQ