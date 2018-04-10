# 小程序

## 基础知识

- [HTML5 教程](http://www.w3school.com.cn/html5/index.asp)
- [CSS3 教程](http://www.w3school.com.cn/css3/index.asp)
- [ECMAScript 6 入门](http://es6.ruanyifeng.com/)

- [微信小程序官网](https://mp.weixin.qq.com/cgi-bin/wx) 
- [微信小程序 API](https://developers.weixin.qq.com/miniprogram/dev/api/) 
- [支付宝小程序官网](https://mini.open.alipay.com/channel/miniIndex.htm) 
- [支付宝小程序 API](https://docs.alipay.com/mini/developer/getting-started) 

## 小程序实现原理

- 微信

iOS 运行在 webkit（苹果开源的浏览器内核），Android 运行在 X5(QQ浏览器内核)。

- 支付宝

- 小程序调用系统的 API

Android 可以参考 [JsBridge](https://github.com/lzyzsd/JsBridge)，iOS 可以参考 [WebViewJavascriptBridge](https://github.com/marcuswestin/WebViewJavascriptBridge)


- 小程序的架构

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/web_front_app/app_arch.png" alt=""/>

## 小程序与 Android & iOS 对比

- 生命周期

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/web_front_app/app_android_ios.png" alt=""/>

- 数据存储

Android：SQLite、Realm、SharedPreferences、File

iOS：SQLite、Realm、plist、归档、NSUserDefaults、File

微信小程序：localStorage、File

支付宝小程序：localStorage

- 网络

Android：OkHttp、Volley

iOS：Alamofire

微信小程序：wx.request()

支付宝小程序：my.httpRequest()

## 项目结构

```
|-ProjectName
    |-component//template，组件
        |-common-button
    |-config
    |-images
    |-pages//页面
        |-home 
            |-home.acss/wxss
            |-home.axml/wxml
            |-home.js
            |-home.json
    |-utils
    |-app.acss/wxss
    |-app.js
    |-app.json
```

- App

微信小程序

```JS
App({
  onLaunch: function(options) {
    // Do something initial when launch.
  },
  onShow: function(options) {
      // Do something when show.
  },
  onHide: function() {
      // Do something when hide.
  },
  onError: function(msg) {
    console.log(msg)
  },
  globalData: 'I am global data'
})
```

支付宝小程序

```JS
App({
  onLaunch(options) {
    // 小程序初始化
  },
  onShow(options) {
    // 小程序显示
  },
  onHide() {
    // 小程序隐藏
  },
  onError(msg) {
    console.log(msg)
  },
  globalData: {
    foo: true,
  }
})
```

- Page

微信小程序

```JS
Page({
  data: {
    text: "This is page data."
  },
  onLoad: function(options) {
    // Do some initialize when page load.
  },
  onReady: function() {
    // Do something when page ready.
  },
  onShow: function() {
    // Do something when page show.
  },
  onHide: function() {
    // Do something when page hide.
  },
  onUnload: function() {
    // Do something when page close.
  },
  // Event handler.
  viewTap: function() {
    this.setData({
      text: 'Set some data for updating view.'
    }, function() {
      // this is setData callback
    })
  },
  customData: {
    hi: 'MINA'
  }
})
```

支付宝小程序

```JS
Page({
  data: {
    title: "Alipay"
  },
  onLoad(query) {
    // 页面加载
  },
  onReady() {
    // 页面加载完成
  },
  onShow() {
    // 页面显示
  },
  onHide() {
    // 页面隐藏
  },
  onUnload() {
    // 页面被关闭
  },
  viewTap() {
    // 事件处理
    this.setData({
      text: 'Set data for updat.'
    })
  },
  go() {
    // 带参数的跳转，从 page/index 的 onLoad 函数的 query 中读取 xx
    my.navigateTo('/page/index?xx=1')
  },
  customData: {
    hi: 'alipay'
  }
})
```

- localStorage


微信小程序

```JS
//同步保存数据
wx.setStorageSync({
  key:"key",
  data:"value"
})

wx.getStorageSync({key: 'key'})//同步读取数据
wx.removeStorageSync('key')//同步删除数据
```

支付宝小程序：my.httpRequest()

```JS
//同步保存数据
my.setStorageSync({
  key:"key",
  data:"value"
})

my.getStorageSync({key: 'key'})//同步读取数据
my.removeStorageSync('key')//同步删除数据
```


- 网络请求

微信小程序：wx.request()

```JS
wx.request({
  url: 'http://xxx.xx',
  data: {
     x: '' ,
     y: ''
  },
  header: {
      'content-type': 'application/json'
  },
  success: function(res) {
    console.log(res.data)
  },
  fail: function(res) {
    console.log(res.data)
  },
  complete: function(res) {
    console.log(res.data)
  }
})
```

支付宝小程序：my.httpRequest()

```JS
my.httpRequest({
  url: 'http://xxx.xx',
  method: 'POST',
  data: {
    x: '' ,
    y: ''
  },
  dataType: 'json',
  success: function(res) {
    my.alert({content: 'success'});
  },
  fail: function(res) {
    my.alert({content: 'fail'});
  },
  complete: function(res) {
    my.alert({content: 'complete'});
  }
});
```



## 小程序的特点


1. 提前新建 WebView，准备新页面渲染。
2. View 层和逻辑层分离，通过数据驱动，不直接操作 DOM。
3. 使用 Virtual DOM，进行局部更新。
4. 全部使用 https，确保传输中安全。
5. 前端组件化开发。
6. 加入 rpx 单位，隔离设备尺寸，方便开发。


## 小程序的不足

1. 小程序仍然使用 WebView 渲染，并非原生渲染
2. 需要独立开发，不能在非微信环境运行。
3. 开发者不可以扩展新组件。
4. 服务端接口返回的头无法执行，比如：Set-Cookie。
5. 依赖浏览器环境的 js 库不能使用，因为是 JSCore 执行的，没有 window、document 对象。
6. WXSS 中无法使用本地（图片、字体等）。
7. WXSS 转化成 js 而不是 css，为了兼容 rpx。
8. WXSS 不支持级联选择器。
9. 小程序无法打开页面，无法拉起 APP。



-------








# 分享



发展史

- 1990 HTML
- 1994.7 HTML 2.0 规范发布
- 1994 万维网联盟（World Wide Web Consortium）成立，简称 W3C
- 1995 网景推出 JavaScript
- 1996 微软发布 VBScript 和 JScript，并内置于 Internet Explorer 3 中
- 1996.12 W3C 推出了 CSS 1.0 规范
- 1997.1 HTML3.2 作为 W3C 推荐标准发布
- 1997.6 ECMA 以 JavaScript 语言为基础制定了 ECMAScript 1.0 标准规范
- 1997.12 HTML 4.0 规范发布
- 1998 W3C 推出了 CSS 2.0 规范
- 1998.6 ECMAScript 2.0 规范发布
- 1999.12 ECMAScript 3.0 规范发布，在此后的十年间，ECMAScript 规范基本没有发生变动。
- 1999 W3C发布 HTML 4.01 标准，同年微软推出用于异步数据传输的ActiveX，随即各大浏览器厂商模仿实现了XMLHttpRequest（AJAX 雏形）。
- 2000: W3C采用了一个大胆的计划，把XML引入HTML，XHTML1.0 作为W3C推荐标准发布
- 2001.5 W3C 推出了CSS 3.0 规范草案
- 2002-2006 XHTML2.0 最终放弃
- 2004 Google 发布 Gmail 和 Google Map，使用了大量的 AJAX
- 2006 XMLHttpRequest 被W3C正式纳入标准。
- 2007.10 Mozilla 主张的 ECMAScript 4.0 版草案发布，该草案遭到了以 Yahoo、Microsoft、Google 为首的大公司的强烈反对。最后由于各方分歧太大，ECMA 开会决定废弃中止ECMAScript 4.0 草案。
- 2008.1.12 HTML 5 草案
- 2008.12 Chrome 发布，JavaScript 引擎 V8
- 2009 W3C 宣布 XHTML2.0 不再继续，宣告死亡
- 2009.12 ECMAScript 5.0 规范发布
- 2011.6 ECMAScript 5.1 规范发布
- 2014.10.28 W3C 正式发布 HTML 5.0 推荐标准
- 2015.6 ECMAScript 6.0 规范发布，TC39委员会计划以后每年都发布一个新版本的ECMAScript，所以ECMAScript 6.0改名为ECMAScript 2015。
- 2016.6 在ECMAScript 2015的基础上进行了部分增强，发布了ECMAScript 2016。

- HTML5 新特性
- CSS3 新特性
- ES6 新特性

## JavaScript V8 引擎

## 浏览器渲染机制


## 布局

- flex
- grid
- @media

