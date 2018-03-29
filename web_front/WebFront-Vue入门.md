# Vue 起步

## 简介

Vue (读音 /vjuː/，类似于 view) 是一套用于构建用户界面的渐进式框架。

- [Vue 官网](https://cn.vuejs.org/v2/guide/)

## 准备

安装下面环境：

- [Git 官网](https://git-scm.com/)
- [Node.js 官网](https://nodejs.org/en/)

推荐阅读：

- [ECMAScript 6 入门](http://es6.ruanyifeng.com/)
- [NPM 入门文档](https://segmentfault.com/a/1190000005799797)

开始配置环境：

- NPM

NPM 是随同 NodeJS 一起安装的包管理工具。

> // 使用 NPM 安装 vue
> $ npm install vue

对于中国大陆用户，建议将 NPM 源设置为[国内的镜像](https://npm.taobao.org/)，可以大幅提升安装速度。

使用定制的 cnpm (gzip 压缩支持) 命令行工具代替默认的 npm:
> $ npm install -g cnpm --registry=https://registry.npm.taobao.org<br/>
> 
> // 使用 cnpm 代替 npm<br/>
> $ cnpm install vue

- webpack

[Webpack 入门](https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/web_front/WebFront-Webpack入门.md)

- 命令行工具 (CLI)

Vue 提供一个官方命令行工具，可用于快速搭建大型单页应用。
> // 全局安装 vue-cli<br/>
> $ npm install --global vue-cli

## 开发工具

- Visual Studio Code
- WebStorm

## 创建项目

确保前面的准备工作中 Node.js，webpack，vue-cli 已经成功安装，接下来开始创建 vue 项目：

> // 创建一个基于 webpack 模板的新项目<br/>
> $ vue init webpack <项目文件夹>
> 
> // 进入项目目录<br/>
> $ cd <项目文件夹>
> 
> // 安装依赖<br/>
> $ npm install
> 
> // 启动项目<br/>
> $ npm run dev


## 项目结构

```JSON
|-ProjectName
    |-build//构建配置
    |-dist//打包后的文件
    |-config//项目配置
    |-node_modules//依赖库
    |-src
        |-assets//资源文件
        |-components//组件
        |-css
        |   |-common
        |-script
        |-app.vue
        |-main.js
    |-static
    |-.babelrc//babel 配置
    |-package.json//npm init 生成的文件
```


## Vue 基础





