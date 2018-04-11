# HTML 5 & CSS 3

## 基础知识

- [HTML5 教程](http://www.w3school.com.cn/html5/index.asp)
- [CSS3 教程](http://www.w3school.com.cn/css3/index.asp)

## HTML 5

## CSS 3

## CSS 3 布局

- flex
- grid
- @media

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/xxx/xxx.png" alt=""/>

## 参考资料

- [资料标题](http://www.baidu.com)








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

如果设计稿的宽度为 750px，那么 1rem = 750/10px = 75px。


