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

<img src="https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/web_front/web_front_app/app_arch.png" alt=""/>

## 小程序与 Android & iOS 对比

- 生命周期

<img src="https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/web_front/web_front_app/app_android_ios.png" alt=""/>

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
2. 需要独立开发，不能在非微信/支付宝环境运行。
3. 开发者不可以扩展新组件。
4. 服务端接口返回的头无法执行，比如：Set-Cookie。
5. 依赖浏览器环境的 js 库不能使用，因为是 JSCore 执行的，没有 window、document 对象。
6. WXSS/ASS 中无法使用本地（图片、字体等），ASS 可以使用本地图片。
7. WXSS/ASS 转化成 js 而不是 css，为了兼容 rpx。
8. WXSS/ASS 不支持级联选择器。
9. 小程序无法打开页面，无法拉起 APP。

## 我的公众号

欢迎你「扫一扫」下面的二维码，关注我的公众号，可以接受最新的文章推送，有丰厚的抽奖活动和福利等着你哦！😍

<img src="https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/about_me/qrcode_android_besos_black_512.png" width=250 height=250 />

如果你有什么疑问或者问题，可以 [点击这里](https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/issues) 提交 issue，也可以发邮件给我 [jeanboy@foxmail.com](mailto:jeanboy@foxmail.com)。

同时欢迎你 [![Android技术进阶：386463747](https://camo.githubusercontent.com/615c9901677f501582b6057efc9396b3ed27dc29/687474703a2f2f7075622e69647171696d672e636f6d2f7770612f696d616765732f67726f75702e706e67)](http://shang.qq.com/wpa/qunwpa?idkey=0b505511df9ead28ec678df4eeb7a1a8f994ea8b75f2c10412b57e667d81b50d) 来一起交流学习，群里有很多大牛和学习资料，相信一定能帮助到你！