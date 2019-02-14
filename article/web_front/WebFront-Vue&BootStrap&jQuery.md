# Vue & BootStrap & jQuery

## 准备

- [Bootstrap](https://getbootstrap.com/)
- [jQuery](http://jquery.com/)


> // 安装 bootstrap 和 jquery<br/>
> $ npm install bootstrap jquery --save
> 
> // bootstrap 的 dropdown 插件依赖 popper.js<br/>
> $ npm install popper.js --save

在 `main.js` 里依次载入 jQuery 和 Bootstrap，添加类似如下代码：

```JS
import $ from 'jquery'
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap/dist/js/bootstrap.min.js'
```

此处使用未压缩的版本也是可以的，另外上面的 CSS 和 JS 都可以酌情使用，Bootstrap 的 JS 引入之前必须先引入 jQuery。

接着，打开 `build\webpack.base.conf.js` 打包配置，在头部加入

```JS
var webpack = require('webpack')
```

接下来添加的配置中因为使用了 webpack 模块，如果不写这个会报错 webpack 未定义。

然后在 `build\webpack.base.conf.js` 的 plugins 配置块中，加入 jQuery 配置，整个 webpack.base.conf.js 文件看起来类似这样（部分无关代码已省略）：

```JS
...
var webpack = require('webpack');
...

module.exports = {
    entry: { ... },
    output: { ... },
    resolve: { ... },
    module: { ... },
    ...
    plugins: [ // 配置全局使用 jquery
    new webpack.ProvidePlugin({
      $: "jquery",
      jQuery: "jquery",
      jquery: "jquery",
      "window.jQuery": "jquery",
      Popper: ['popper.js', 'default']
    })
  ],
    ...
};
```

这样就可以在 Vue 项目中直接使用 $() 了。

## 参考资料

- [vue2.0+webpack 如何使用bootstrap？](https://segmentfault.com/q/1010000007233864)
- [vue引入bootstrap——webpack](https://blog.csdn.net/wild46cat/article/details/77662555)

## 我的公众号

欢迎你「扫一扫」下面的二维码，关注我的公众号，可以接受最新的文章推送，有丰厚的抽奖活动和福利等着你哦！😍

<img src="https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/about_me/qrcode_android_besos_black_512.png" width=250 height=250 />

如果你有什么疑问或者问题，可以 [点击这里](https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/issues) 提交 issue，也可以发邮件给我 [jeanboy@foxmail.com](mailto:jeanboy@foxmail.com)。

同时欢迎你 [![Android技术进阶：386463747](https://camo.githubusercontent.com/615c9901677f501582b6057efc9396b3ed27dc29/687474703a2f2f7075622e69647171696d672e636f6d2f7770612f696d616765732f67726f75702e706e67)](http://shang.qq.com/wpa/qunwpa?idkey=0b505511df9ead28ec678df4eeb7a1a8f994ea8b75f2c10412b57e667d81b50d) 来一起交流学习，群里有很多大牛和学习资料，相信一定能帮助到你！