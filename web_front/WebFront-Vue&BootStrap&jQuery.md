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

