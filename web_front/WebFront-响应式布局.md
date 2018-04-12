# 响应式布局

## 基础知识

- [HTML5 教程](http://www.w3school.com.cn/html5/index.asp)
- [CSS3 教程](http://www.w3school.com.cn/css3/index.asp)

## rem

> rem - “font size of the root element (根元素的字体大小)” 

1. header 中加入 meta 属性

```HTML
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=0，minimum-scale=1.0">
```

2. 设置根元素字体大小

子元素字体大小 = 设计稿 px / 根元素字体大小。

```CSS
html{
    font-size: 16px;//1rem = 16px
}

body {
    width: 10rem;
    margin: auto;
}

div{
    font-size: 2rem;//32px/16px
}
```

3. 根据屏幕宽度，动态设置根元素字体大小

```JS
/* rem.js文件内容 */
(function () {
    var html = document.documentElement;

    function onWindowResize() {
        html.style.fontSize = html.getBoundingClientRect().width / 10 + 'px';
    }

    window.addEventListener('resize', onWindowResize);
    onWindowResize();
})();
```

- 屏幕宽度：DomWidth(W) = document.documentElement.getBoundingClientRect().width//例如：1920px
- 缩放比例：Scale(S) = 10
- 设计稿屏幕宽度：DesignWidth(DW) = 350px
- 设计稿字体大小：DesignFontSize(DFS) = 22px
- 设计稿元素宽度：DesignElementWidth(DEW) = 10px
- 设计稿元素高度：DesignElementHeight(DEH) = 20px
- 字体 rem 大小：remWidth = DFS / DW * S
- 元素 rem 宽度：remWidth = DEW / DW * S
- 元素 rem 高度：remHeight = DEH / DEW * remWidth

终极解决方案：使用 [auto_rem.html]() 来自动计算。

## flex

- [Flex 布局教程：语法篇](http://www.ruanyifeng.com/blog/2015/07/flex-grammar.html)
- [Flex 布局教程：实例篇](http://www.ruanyifeng.com/blog/2015/07/flex-examples.html)

Flex 是 Flexible Box 的缩写，意为"弹性布局"，用来为盒状模型提供最大的灵活性。

任何一个容器都可以指定为 Flex 布局。

```CSS
.box{
  display: flex;
}
```

行内元素也可以使用 Flex 布局。

```CSS
.box{
  display: inline-flex;
}
```

> 注意，设为 Flex 布局以后，子元素的 float、clear 和 vertical-align 属性将失效。

```CSS
.box {
  /* 子元素排列方向 */
  flex-direction: row | row-reverse | column | column-reverse;
  /* 子元素排列方式 */
  flex-wrap: nowrap | wrap | wrap-reverse;
  /* 水平方向对齐方式 */
  justify-content: flex-start | flex-end | center | space-between | space-around;
  /* 垂直方向对齐方式 */
  align-items: flex-start | flex-end | center | baseline | stretch;
  /* 子元素多轴线排列方式 */
  align-content: flex-start | flex-end | center | space-between | space-around | stretch;
}

.item {
  order: <integer>;/* 数值越小，排列越靠前，默认为0 */
  flex-grow: <number>;/* 放大比例，默认为0 */
  flex-shrink: <number>;/* 缩小比例，默认为0 */
  flex-basis: <length> | auto;/* 缩小比例，默认为0 */
  /* flex属性是flex-grow, flex-shrink 和 flex-basis的简写，默认值为0 1 auto。后两个属性可选。 */
  flex: none | [ <'flex-grow'> <'flex-shrink'>? || <'flex-basis'> ]
  /* 允许单个项目有与其他项目不一样的对齐方式，可覆盖 align-items 属性。默认值为auto，表示继承父元素的 align-items 属性。 */
  align-self: auto | flex-start | flex-end | center | baseline | stretch;
}
```

- 兼容性处理

```CSS
.box{
    display: -webkit-box;/* OLD - iOS 6-, Safari 3.1-6 */
    display: -moz-box;/* OLD - Firefox 19- (buggy but mostly works) */
    display: -ms-flexbox;/* TWEENER - IE 10 */
    display: -webkit-flex;/* NEW - Chrome */
    display: flex;/* NEW, Spec - Opera 12.1, Firefox 20+ */
    
    -webkit-flex-direction: row;
    -moz-flex-direction: row;
    -ms-flex-direction: row;
    -o-flex-direction: row;
    flex-direction: row;
    
    -webkit-flex-wrap: nowrap;
    -moz-flex-wrap: nowrap;
    -ms-flex-wrap: nowrap;
    -o-flex-wrap: nowrap;
    flex-wrap: nowrap; 
    
    -webkit-justify-content: flex-start;
    -moz-justify-content: flex-start;
    -ms-justify-content: flex-start;
    -o-justify-content: flex-start;
    justify-content: flex-start;
    
    -webkit-align-items: flex-start;
    -moz-align-items: flex-start;
    -ms-align-items: flex-start;
    -o-align-items: flex-start;
    align-items: flex-start;
    
    -webkit-align-content: flex-start;
    -moz-align-content: flex-start;
    -ms-align-content: flex-start;
    -o-align-content: flex-start;
    align-content: flex-start;
}
```

## grid

- [CSS Grid 系列(上)-Grid布局完整指南](https://segmentfault.com/a/1190000012889793)

## @media

- [利用@media screen实现网页布局的自适应](https://blog.csdn.net/inuyasha1121/article/details/50777116)

1. 设置 meta 标签

```HTML
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
```

- width = device-width：宽度等于当前设备的宽度
- height = device-height：高度等于当前设备的高度
- initial-scale：初始的缩放比例（默认设置为1.0）  
- minimum-scale：允许用户缩放到的最小比例（默认设置为1.0）    
- maximum-scale：允许用户缩放到的最大比例（默认设置为1.0）   
- user-scalable：用户是否可以手动缩放（默认设置为no，因为我们不希望用户放大缩小页面） 

2. CSS3 Media 写法

```CSS
/* 当页面小于 960px 的时候执行它下面的 CSS */
@media screen and (max-width: 960px){
    body{
        background: #000;
    }
}
/* 省略 screen */
@media (max-width: 960px){
    body{
        background: #000;
    }
}

/* 当页面宽度大于 960px 小于 1200px 的时候执行下面的 CSS */
@media (min-width:960px) and (max-width:1200px){
    body{
        background: yellow;
    }
}

/* 竖屏 */  
@media screen and (orientation: portrait) and (max-width: 720px) { 对应样式 }  
  
/* 横屏 */  
@media screen and (orientation: landscape) { 对应样式 }  
```

> 发现上面这段代码里面有个 screen，它的意思是在告知设备在打印页面时使用衬线字体，在屏幕上显示时用无衬线字体。

Media 所有参数汇总：

- width：浏览器可视宽度。
- height：浏览器可视高度。
- device-width：设备屏幕的宽度。
- device-height：设备屏幕的高度。
- orientation：检测设备目前处于横向还是纵向状态。
- aspect-ratio：检测浏览器可视宽度和高度的比例。(例如：aspect-ratio：16/9)
- device-aspect-ratio：检测设备的宽度和高度的比例。
- color：检测颜色的位数。（例如：min-color：32就会检测设备是否拥有32位颜色）
- color-index：检查设备颜色索引表中的颜色，他的值不能是负数。
- monochrome：检测单色楨缓冲区域中的每个像素的位数。（这个太高级，估计咱很少会用的到）
- resolution：检测屏幕或打印机的分辨率。(例如：min-resolution：300dpi 或 min-resolution：118dpcm)。
- grid：检测输出的设备是网格的还是位图设备。

```CSS
/* >=1920 大屏 */
@media (min-width: 1920px){ 对应样式 }
/* >=1366 中屏 */
@media (min-width: 1366px){ 对应样式 }
/* <1366 小屏 */
@media (max-width: 1365px){ 对应样式 }
```

## 判断浏览器类型

```JS
/* device.js文件内容 */
function getBrowserName(ua) {
    if (ua.indexOf("Opera") > -1 || ua.indexOf("OPR") > -1) {
        return 'Opera';
    } else if (ua.indexOf("compatible") > -1 && ua.indexOf("MSIE") > -1) {
        return 'IE';
    } else if (ua.indexOf("Edge") > -1) {
        return 'Edge';
    } else if (ua.indexOf("Firefox") > -1) {
        return 'Firefox';
    } else if (ua.indexOf("Safari") > -1 && ua.indexOf("Chrome") == -1) {
        return 'Safari';
    } else if (ua.indexOf("Chrome") > -1 && ua.indexOf("Safari") > -1) {
        return 'Chrome';
    } else if (!!window.ActiveXObject || "ActiveXObject" in window) {
        return 'IE>=11';
    } else {
        return 'Unkonwn';
    }
}
var browser = {
    device: function () {
        var ua = navigator.userAgent,
            app = navigator.appVersion;
        return {
            trident: ua.indexOf('Trident') > -1, //IE 内核
            presto: ua.indexOf('Presto') > -1, //opera 内核
            webKit: ua.indexOf('AppleWebKit') > -1, //苹果、谷歌内核
            gecko: ua.indexOf('Gecko') > -1 && ua.indexOf('KHTML') == -1, //火狐内核
            isMobile: !!ua.match(/AppleWebKit.*Mobile.*/), //是否为移动终端
            isIOS: !!ua.match(/\(i[^;]+;( U;)? CPU.+Mac OS X/), //iOS 终端
            isAndroid: ua.indexOf('Android') > -1 || ua.indexOf('Linux') > -1, //Android 终端或 uc 浏览器
            isIPhone: ua.indexOf('iPhone') > -1, //是否为 iPhone 或者 QQHD 浏览器
            isIPad: ua.indexOf('iPad') > -1, //是否 iPad
            isWebApp: ua.indexOf('Safari') == -1, //是否 web 应该程序，没有头部与底部
            name: getBrowserName(ua) //获取浏览器名称
        };
    }(),
    language: (navigator.browserLanguage || navigator.language).toLowerCase()
}
console.log(browser.language); //系统语言
console.log(browser.device); //设备信息判断
console.log(navigator.userAgent);
console.log("设备类型：" + (browser.device.isMobile ? "移动端" : "电脑端"));
console.log("浏览器名称：" + browser.device.name);
console.log("Android：" + browser.device.isAndroid);
console.log("iOS：" + browser.device.isIOS);
console.log("iPhone：" + browser.device.isIPhone);
console.log("iPad：" + browser.device.isIPad);
```

