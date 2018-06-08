## CSS布局

## 盒模型

![img](https://gss3.bdstatic.com/7Po3dSag_xI4khGkpoWK1HF6hhy/baike/c0%3Dbaike80%2C5%2C5%2C80%2C26/sign=f1a5cfd90633874488c8272e3066b29c/a9d3fd1f4134970a37cf81a69fcad1c8a6865dfe.jpg)

```css
div{
    width: 200px;
    height: 200px;
    margin-left: 10px;
    margin-right: 20px;
    margin-top: 40px;
    margin-bottom: 50px;
    margin: 40px 20px 50px 10px;/*上 右 下 左*/
    margin: 40px 20px 10px;/*上 (右左) 下*/
    margin: 40px 20px;/*(上下) (右左) */
    pading-left: 10px;
    border-left: 1px solid #000000;
}
```

```xml
<!-- Android -->
<View
    android:id="@+id/tv_username"
    android:layout_width="wrap_content"
    android:layout_height="match_parent"
    android:layout_marginLeft="10dp"
    android:layout_marginRight="20dp"
    android:layout_marginTop="30dp"
    android:layout_marginBottom="40dp"
    android:layout_margin="10dp"
    android:paddingLeft="10dp"
    android:background="@drawable/border" />
```

```swift
/* swift */
view.snp.makeConstraints { (make) in
    make.width.equalTo(200)
    make.height.equalTo(200)
    make.left.equalTo(10)
    make.right.equalTo(20)
    make.top.equalTo(30)
    make.bottom.equalTo(40)
}
```



- 传统模型

  当你设置了元素的宽度，实际展现的元素却超出你的设置：这是因为元素的边框和内边距会撑开元素。

  ```css
  .simple {
    width: 500px;
    margin: 20px auto;
  }
  
  .fancy {
    width: 500px;
    margin: 20px auto;
    padding: 50px;
    border-width: 10px;
  }
  ```

  ![image-20180601101512748](/var/folders/t1/6fv89nkj5n18p798wmgj3cqc0000gn/T/abnerworks.Typora/image-20180601101512748.png)

- box-sizing

  人们慢慢的意识到传统的盒子模型不直接，所以他们新增了一个叫做 `box-sizing` 的CSS属性。当你设置一个元素为 `box-sizing: border-box;` 时，此元素的内边距和边框不再会增加它的宽度。

  ```css
  .simple {
    width: 500px;
    margin: 20px auto;
    -webkit-box-sizing: border-box;
       -moz-box-sizing: border-box;
            box-sizing: border-box;
  }
  
  .fancy {
    width: 500px;
    margin: 20px auto;
    padding: 50px;
    border: solid blue 10px;
    -webkit-box-sizing: border-box;
       -moz-box-sizing: border-box;
            box-sizing: border-box;
  }
  ```

  既然没有比这更好的方法，一些CSS开发者想要页面上所有的元素都有如此表现。所以开发者们把以下CSS代码放在他们页面上：

  ```css
  * {
    -webkit-box-sizing: border-box;
       -moz-box-sizing: border-box;
            box-sizing: border-box;
  }
  ```

  ![image-20180601101526804](/var/folders/t1/6fv89nkj5n18p798wmgj3cqc0000gn/T/abnerworks.Typora/image-20180601101526804.png)

## display

`display` 是CSS中最重要的用于控制布局的属性。每个元素都有一个默认的 display 值，这与元素的类型有关。对于大多数元素它们的默认值通常是 `block` 或 `inline` 。一个 block 元素通常被叫做块级元素。一个 inline 元素通常被叫做行内元素。

- none

  `display:none` 通常被 JavaScript 用来在不删除元素的情况下隐藏或显示元素。

  它和 `visibility` 属性不一样。把 `display` 设置成 `none` 元素不会占据它本来应该显示的空间，但是设置成 `visibility: hidden;` 还会占据空间。

- block

  `div` 是一个标准的块级元素。一个块级元素会新开始一行并且尽可能撑满容器。其他常用的块级元素包括 `p` 、 `form` 和HTML5中的新元素： `header` 、 `footer` 、 `section` 等等。

- inline

  `span` 是一个标准的行内元素。一个行内元素可以在段落中 <span> 像这样 </span>包裹一些文字而不会打乱段落的布局。 `a` 元素是最常用的行内元素，它可以被用作链接。

- inline-block

  - `vertical-align` 属性会影响到 `inline-block` 元素，你可能会把它的值设置为 `top` 。
  - 你需要设置每一列的宽度
  - 如果HTML源代码中元素之间有空格，那么列与列之间会产生空隙

- flex

  Flex 是 Flexible Box 的缩写，意为"弹性布局"，用来为盒状模型提供最大的灵活性。

  ```css
  .box{
    display: flex;
    flex-direction: row | row-reverse | column | column-reverse;
    flex-wrap: nowrap | wrap | wrap-reverse;
    justify-content: flex-start | flex-end | center | space-between | space-around;
    align-items: flex-start | flex-end | center | baseline | stretch;
    align-content: flex-start | flex-end | center | space-between | space-around | stretch;
  }
  ```

  ![img](http://www.ruanyifeng.com/blogimg/asset/2015/bg2015071004.png)

  

## 行内元素与块级元素

- 行内元素

  行内元素会在一条直线上排列，都是同一行的，水平方向排列。

  <a>、<b>、<img>、<span>、<label>

- 块级元素

  块级元素各占据一行，垂直方向排列。块级元素从新行开始结束接着一个断行。

  <div>、<form>、<h1>、<p>、<pre>、<li>

## 居中

- 水平居中

  ```css
  #main {
    width: 600px;
    margin: 0 auto; 
  }
  ```

  设置块级元素的 `width` 可以防止它从左到右撑满整个容器。然后你就可以设置左右外边距为 `auto` 来使其水平居中。元素会占据你所指定的宽度，然后剩余的宽度会一分为二成为左右外边距。

  唯一的问题是，当浏览器窗口比元素的宽度还要窄时，浏览器会显示一个水平滚动条来容纳页面。

  ```Css
  #main {
    max-width: 600px;
    margin: 0 auto; 
  }
  ```

  在这种情况下使用 `max-width` 替代 `width` 可以使浏览器更好地处理小窗口的情况。这点在移动设备上显得尤为重要，调整下浏览器窗口大小检查下吧！

- 垂直居中

  ```css
  /*文字垂直居中*/
  div {
      height: 100px;
      line-height: 100px;
  }
  ```

  ```css
  div {
      position: absolute;
      top: 50%;
      height: 240px;
      margin-top: -120px;
  }
  ```

  ```css
  div {
      position: absolute;
      top: 50%;
      height: 240px;
      transform: translateX(-50%);
  }
  ```

  

- 水平垂直居中

  ```css
  div{
      width: 200px;
      height: 200px;
      left: 50%;
      top: 50%;
      transform: translate(-50%, -50%);
  }
  ```

  ```css
  parent{
      display: flex;
      justify-content: center;
      align-items: center;
  }
  div{
    /*居中*/  
  }
  ```


## position

- static

  ```Css
  .static {
    position: static;
  }
  ```

  `static` 是默认值。任意 `position: static;` 的元素不会被特殊的定位。一个 static 元素表示它*不会被“positioned”*，一个 position 属性被设置为其他值的元素表示它*会被“positioned”*。

- relative

  ```css
  .relative1 {
    position: relative;
  }
  .relative2 {
    position: relative;
    top: -20px;
    left: 20px;
    background-color: white;
    width: 500px;
  }
  ```

  `relative` 表现的和 `static` 一样，除非你添加了一些额外的属性。

  在一个相对定位（position属性的值为relative）的元素上设置 `top`、 `right` 、 `bottom` 和 `left` 属性会使其偏离其正常位置。其他的元素的位置则不会受该元素的影响发生位置改变来弥补它偏离后剩下的空隙。

- fixed

  一个固定定位（position属性的值为fixed）元素会相对于视窗来定位，这意味着即便页面滚动，它还是会停留在相同的位置。和 `relative` 一样， `top` 、 `right` 、 `bottom`和 `left` 属性都可用。

  ```css
  .fixed {
    position: fixed;
    bottom: 0;
    right: 0;
    width: 200px;
    background-color: white;
  }
  ```

  一个固定定位元素不会保留它原本在页面应有的空隙（脱离文档流）。

- absolute

  `absolute` 是最棘手的position值。 `absolute` 与 `fixed` 的表现类似，但是它不是相对于视窗而是相对于*最近的“positioned”祖先元素*。如果绝对定位（position属性的值为absolute）的元素没有“positioned”祖先元素，那么它是相对于文档的 body 元素，并且它会随着页面滚动而移动。记住一个“positioned”元素是指 position 值不是 `static`的元素。

  ```css
  .relative {
    position: relative;
    width: 600px;
    height: 400px;
  }
  .absolute {
    position: absolute;
    top: 120px;
    right: 0;
    width: 300px;
    height: 200px;
  }
  ```

## float

```
img {
  float: right;
  overflow: auto;
}
```

## 百分比宽度

```css
nav {
  float: left;
  width: 25%;
}
section {
  margin-left: 25%;
}
```

## 媒体查询

```css
@media screen and (min-width:600px) {
  nav {
    float: left;
    width: 25%;
  }
  section {
    margin-left: 25%;
  }
}
@media screen and (max-width:599px) {
  nav li {
    display: inline;
  }
}
```



## background

```css
div{
    background-color: #ffffff;
    background-image: url(/images/xxx.png);
    background-position: x y;
    background-size: w h;
    background-repeat: no-repeat;
}
```

