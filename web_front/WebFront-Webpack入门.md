# Webpack 入门

## 简介

Webpack 是一个现代 JavaScript 应用程序的静态模块打包器(module bundler)。当 webpack 处理应用程序时，它会递归地构建一个依赖关系图(dependency graph)，其中包含应用程序需要的每个模块，然后将所有这些模块打包成一个或多个 bundle。

- [英文官网](https://webpack.js.org/)
- [中文版](https://www.webpackjs.com/)
- [Webpack GitHub](https://github.com/webpack/webpack)
- [Babel 官网](http://babeljs.io)
- [NPM 官网](https://www.npmjs.com/)

## 准备

安装下面环境：

- [Git 官网](https://git-scm.com/)
- [Node.js 官网](https://nodejs.org/en/)

推荐阅读：

- [ECMAScript 6 入门](http://es6.ruanyifeng.com/)
- [NPM 入门文档](https://segmentfault.com/a/1190000005799797)

## 安装 Webpack

你可以在全局环境安装 Webpack，也可以在项目根目录安装 Webpack。在模块化盛行的当下，我推荐后者。因为 Webpack 是开发环境必需的依赖，安装在全局，对它的依赖就不能写入 package.json，换个开发环境运行项目，就会出现依赖缺失的问题。

全局安装 webpack：

> // 全局安装<br/>
> $ npm install -g webpack
> 
> // 安装命令行工具<br/>
> $ npm install -g webpack-cli
> 
> // 查看是否安装成功<br/>
> $ webpack -v

局部安装（推荐）：

> // 进入项目将要保存的目录<br/>
> $ cd <项目保存目录>
> 
> // 创建项目文件夹<br/>
> $ mkdir webpack-demo
> 
> // 进入文件夹<br/>
> $ cd webpack-demo
> 
> // 快速初始化为 npm 项目，生成 package.json<br/>
> npm init -y

这时，webpack-demo 下会生成一个 package.json 文件，内容如下：

```JSON
{
  "name": "webpack-demo",
  "version": "1.0.0",
  "description": "",
  "main": "index.js",
  "scripts": {
    "test": "echo \"Error: no test specified\" && exit 1"
  },
  "keywords": [],
  "author": "",
  "license": "ISC"
}
```

接着，在 webpack-demo 项目中安装 webpack：

> $ npm install -D webpack
> 
> // 查看 webpack 版本<br/>
> $ npx webpack --version
> 
> // 如果没有返回版本号，继续安装 webpack-cli<br/>
> $ npm install -D webpack-cli
> 
> // 执行 webpack<br/>
> $ npx webpack

```
Hash: 61a2268bf5b55510bbf6
Version: webpack 4.2.0
Time: 88ms
Built at: 2018-3-27 15:27:16

WARNING in configuration
The 'mode' option has not been set. Set 'mode' option to 'development' or 'production' to enable defaults for this environment.

ERROR in Entry module not found: Error: Can't resolve './src' in '/Users/next/Work/Web/webpack-demo'
```

两个错误：

1. 未设定 mode，这是 webpack 4 引入的，有俩种模式，development 与 production，默认为 production - 其实还有一个隐藏的 none 模式，
2. 入口模块不存在 - webpack 4 默认从项目根目录下的 ./src/index.js 中加载入口模块，所以我们或者新建一个 src/index.js 文件，或者指定一个入口文件。

让我们新建一下 `src/index.js` 文件，不过暂时不写内容。

> $ mkdir src<br/>
> $ touch src/index.js
> 
> // 执行 webpack<br/>
> $ npx webpack

目录下多出了 `dist/main.js` 文件。

```JSON
|-webpack-demo
    |-dist//打包后的文件
        |-main.js//*新增
    |-node_modules//依赖库
    |-src
        |-index.js
    |-package.json
    |-package-lock.json
```

## webpack-dev-server

至于自动刷新浏览器的问题，webpack 提供 [webpack-dev-server](https://github.com/webpack/webpack-dev-server) 来解决，它是一个基于 expressjs 的开发服务器，提供实时刷新浏览器页面的功能。不过目前 webpack-dev-server 已经进入维护模式，因此，除非你想在旧浏览器上测试页面，否则请使用 [webpack-serve](https://github.com/webpack-contrib/webpack-serve) - 全新的 webpack 开发服务器，webpack-dev-server 的继任者。

安装 webpack-dev-server：

> $ npm install -D webpack-dev-server

注意，我们应该安装支持 webpack 4 的 webpack-dev-server 3 版本，否则可能出现如下错误：

```
Cannot find module 'webpack/bin/config-yargs'
```

接着在命令行下执行 webpack-dev-server：

> $ npx webpack-dev-server --mode development

```
ℹ ｢wds｣: Project is running at http://localhost:8080/
ℹ ｢wds｣: webpack output is served from /
ℹ ｢wdm｣: Hash: ac35ce1d1935e2bb8d2e
Version: webpack 4.2.0
Time: 383ms
Built at: 2018-3-27 15:45:27
  Asset     Size  Chunks             Chunk Names
main.js  337 KiB    main  [emitted]  main
Entrypoint main = main.js
[./node_modules/ansi-html/index.js] 4.16 KiB {main} [built]
[./node_modules/events/events.js] 8.13 KiB {main} [built]
[./node_modules/loglevel/lib/loglevel.js] 7.68 KiB {main} [built]
[./node_modules/node-libs-browser/node_modules/punycode/punycode.js] 14.3 KiB {main} [built]
[./node_modules/querystring-es3/index.js] 127 bytes {main} [built]
[./node_modules/sockjs-client/dist/sockjs.js] 176 KiB {main} [built]
[./node_modules/url/url.js] 22.8 KiB {main} [built]
   [0] multi (webpack)-dev-server/client?http://localhost:8080 ./src 40 bytes {main} [built]
[./node_modules/webpack-dev-server/client/index.js?http://localhost:8080] (webpack)-dev-server/client?http://localhost:8080 7.75 KiB {main} [built]
[./node_modules/webpack-dev-server/client/overlay.js] (webpack)-dev-server/client/overlay.js 3.58 KiB {main} [built]
[./node_modules/webpack-dev-server/client/socket.js] (webpack)-dev-server/client/socket.js 1.05 KiB {main} [built]
[./node_modules/webpack-dev-server/node_modules/strip-ansi/index.js] (webpack)-dev-server/node_modules/strip-ansi/index.js 161 bytes {main} [built]
[./node_modules/webpack/hot sync ^\.\/log$] (webpack)/hot sync nonrecursive ^\.\/log$ 170 bytes {main} [built]
[./node_modules/webpack/hot/emitter.js] (webpack)/hot/emitter.js 77 bytes {main} [built]
[./src/index.js] 0 bytes {main} [built]
    + 11 hidden modules
ℹ ｢wdm｣: Compiled successfully.

```

我们现在可以在 http://localhost:8080/ 访问我们的项目。

我们需要创建一个 html 文件，添加以下内容：

```HTML
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Webpack 4 测试</title>
</head>
<body>
    <script src="dist/main.js"></script>
</body>
</html>
```

> 注意：我们的 script 引用的文件是 dist/main.js，而不是 index.js。这正是前端开发领域的一个趋势：开发的源文件（例子中的 index.js）与最终部署的文件（例子中的 dist/main.js）是区分开的，之所以这样，是因为开发环境与用户的使用环境并不一致。
> 
> 比如：我们可以在开发环境使用 ES2017 甚至 ES2018 的特性，而用户的浏览器不见得支持 - 这也是 webpack 等打包工具的一个意义，它们能够辅助我们构建出在目标用户浏览器上正常运行的代码。


在入口文件 `src/index.js` 里再添加一行代码验证下浏览器页面的实时刷新功能：

```JS
console.log('hello webpack!');
```

webpack 重新打包了 dist/main.js，但是浏览器并没有刷新。

webpack-dev-server 未刷新页面，这个问题不注意的话很容易发生，所以单独说一下。

我们看前面 npx webpack-dev-server --mode development 的输出里有这么一行：

```
webpack output is served from /
```

webpack-dev-server 构建的 main.js 其实是在 `http://localhost:8080/main.js` 的位置，而不是 `http://localhost:8080/dist/main.js`，而且，它存在于内存中，并不写入磁盘。而我们在 index.html 页面中引用的是 dist/main.js。

我们可以在运行 webpack-dev-server 时指定 output.publicPath：

> $ npx webpack-dev-server --mode development --output-public-path dist

```
webpack output is served from /dist
```

好了，解决问题。

现在再修改 src/index.js 文件，我们就可以在 chrome 浏览器的控制台看到如下内容：

```
hello webpack!
```

页面不仅自动刷新，连 index.js 都重新打包 - webpack-dev-server 一举解决我们前面提出的两个问题。

## webpack 与 Vue


我们在 `index.html` 中添加一个 `div`：

```HTML
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Webpack 4 测试</title>
</head>
<body>
    <!-- *新增 -->
    <div id='app'></div>
    <script src="./dist/main.js"></script>
</body>
</html>
```

然后清空之前添加到 `index.js` 中的内容，新增内容如下：

```JS
import Vue from 'vue';
import App from './App.vue';

new Vue({
    el: '#app',
    components: { App },
    template: '<App/>'
})
```

最后新建一个 `App.vue` 文件：

```HTML
<template>
    <div id="app">
        <div>Vue 测试</div>
    </div>
</template>

<script>
    export default {
        name: "app"
    }
</script>

<style scoped>
    #app {
        font-family: 'Avenir', Helvetica, Arial, sans-serif;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
        text-align: center;
        color: #2c3e50;
        margin-top: 60px;
        font-size: 48px;
    }
</style>
```

> // 安装 babel-loader<br/>
> $ npm install -D babel-loader<br/>
> $ npm install -D babel-core<br/>
> $ npm install -D babel-preset-env
> 
> // 安装 vue<br/>
> $ npm install -D vue<br/>
> $ npm install -D vue-loader<br/>
> $ npm install -D vue-template-compiler
> 
> // 安装创建 HTML 文件的插件<br/>
> $ npm install -D html-webpack-plugin

常见错误：

```
ERROR in ./xxx/xxx
Module not found: Error: Can't resolve 'xxx-loader' in '/Users/xxx/xxx'
```

表示缺少 `xxx-loader`，需要安装：

> $ npm install -D `xxx-loader`

最后创建 `webpack.config.js`，新增如下内容：

```JS
const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');

const config = {
    entry: path.resolve(__dirname, './src/index.js'),
    output: {
        path: path.resolve(__dirname, './dist'),
        filename: './[name].js'
    },
    module: {
        rules: [{
            test: /\.vue$/,
            loader: 'vue-loader'
        }, {
            test: /\.js$/,
            exclude: /(node_modules|bower_components)/,
            use: {
                loader: 'babel-loader',
                options: {
                    presets: ['env']
                }
            }
        }]
    },
    plugins: [
        new HtmlWebpackPlugin({
            template: './index.html',
            hash: true
        })
    ],
    resolve: {
        alias: {
            'vue$': 'vue/dist/vue.common.js'
        }
    }
}

module.exports = config;
```

新增文件目录如下：

```JSON
|-webpack-demo
    |-dist//打包后的文件
        |-main.js
    |-node_modules//依赖库
    |-src
        |-index.js
        |-App.vue//*新增
    |-index.html
    |-package.json
    |-package-lock.json
    |-webpack.config.js//webpack 配置文件，*新增
```

最后在控制台关闭 `webpack-dev-server`（Ctrl+C），继续执行下面命令：

> // webpack 打包<br/>
> $ webpack
> 
> // 重启 webpack-dev-server<br/>
> $ npx webpack-dev-server --mode development --output-public-path dist

## webpack 配置文件

- 插件

1. html-webpack-plugin：生成 HTML 文件

- Loader

1. babel-core：
2. babel-preset-env：
3. balbel-loader：将 `ES6` 转换成浏览器支持的 js
4. style-loader：注入 `<style>` 标签将 CSS 添加到 DOM 中
5. css-loader：解释 `@import` 和 `url()`
6. postcss-loader：自动给 CSS 属性添加兼容不同浏览器的前缀
7. html-loader：将 HTML 导出为字符串
8. file-loader：转换项目中的 URL，根据配置将文件拷贝到相应路径
9. url-loader：将文件加载为 base64 编码的 URL
10. image-webpack-loader：图片压缩
11. vue-loader：编译写入 .vue 文件
12. vue-html-loader：编译 vue 的 template 部分
13. vue-style-loader：编译 vue 的样式部分
14. vue-hot-reload-api：webpack 对 vue 实现热替换


最终配置：

```JS
const path = require('path');
const HtmlWebpackPlugin = require('html-webpack-plugin');

const config = {
    entry: path.resolve(__dirname, './src/index.js'),
    output: {
        path: path.resolve(__dirname, './dist'),
        filename: './[name].js',
        // publicPath: 'http://cdn.example.com/[hash]/'
    },
    module: {
        rules: [{
            test: /\.vue$/,
            loader: 'vue-loader'
        }, {
            test: /\.js$/,
            exclude: /(node_modules|bower_components)/,
            use: {
                loader: 'babel-loader',
                options: {
                    presets: ['env']
                }
            }
        }, {
            test: /\.css$/,
            use: [
                {loader: 'style-loader'},
                {loader: 'css-loader', options: { importLoaders: 1 }},
                {loader: 'postcss-loader', options: { parser: 'sugarss', exec: true }}
            ]
        },{
            test: /\.(png|jpg|jpeg|gif)$/,
            use: [
                {
                    loader: 'file-loader',
                    options: {}
                },{
                    loader: 'url-loader',
                    options: {
                        limit: 1024
                    }
                },{
                    loader: 'image-webpack-loader',
                    options: {
                        bypassOnDebug: true
                    },
                }
            ]
        },{
            test: /\.(html)$/,
            use: {
                loader: 'html-loader',
                options: {
                    attrs: [':data-src']
                }
            }
        }]
    },
    plugins: [
        new HtmlWebpackPlugin({
            template: './index.html',
            hash: true
        })
    ],
    resolve: {
        alias: {
            'vue$': 'vue/dist/vue.common.js'
        }
    }
}

module.exports = config;
```


- production 和 development 模式

修改 `package.json` 文件的 `scripts` 字段：

```JSON
"scripts": {
    "dev": "webpack --mode development --progress --display-modules --colors --display-reason",
    "build": "webpack --mode production"
}
```

> // 生产环境打包<br/>
> $ npm run build
> 
> // 开发环境打包<br/>
> $ npm run dev

你会看到 `./dist/main.js` 不同的变化：

1. production 模式下，默认对打包的进行 minification(文件压缩)，Tree Shaking(只导入有用代码)，scope hoisting（作用域提升）等等操作。总之是让打包文件更小。
2. development 模式下，对打包文件不压缩，同时打包速度更快。
3. 如果没指定任何模式，默认是 production 模式。



## 参考资料

- [webpack 4 教程](https://blog.zfanw.com/webpack-tutorial/)
- [WebPack2配置我的Vue开发环境](https://segmentfault.com/a/1190000008678236)


