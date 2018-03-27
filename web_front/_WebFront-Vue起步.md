# Vue 起步

## 简介

Vue (读音 /vjuː/，类似于 view) 是一套用于构建用户界面的渐进式框架。

- [Vue 官网](https://cn.vuejs.org/v2/guide/)

## 准备

Windows 系统手动安装下面环境：

- [Git 官网](https://git-scm.com/)

安装 Node 环境：

- [Node.js 官网](https://nodejs.org/en/)

开始配置环境：

- NPM

打包工具，运行命令安装：
> $ npm install vue

对于中国大陆用户，建议将 NPM 源设置为[国内的镜像](https://npm.taobao.org/)，可以大幅提升安装速度。

使用定制的 cnpm (gzip 压缩支持) 命令行工具代替默认的 npm:
> $ npm install -g cnpm --registry=https://registry.npm.taobao.org
> $ cnpm install vue

- 命令行工具 (CLI)

Vue 提供一个官方命令行工具，可用于快速搭建大型单页应用。
> // 全局安装 vue-cli
> $ npm install --global vue-cli
> 
> // 创建一个基于 webpack 模板的新项目
> $ vue init webpack my-project
> 
> // 进入项目目录
> $ cd my-project
> 
> // 安装依赖
> $ npm install
> 
> // 启动项目
> $ npm run dev

- 常用命令

> $ npm init//初始化为 npm 项目，生成 package.json
> $ npm install [webpack vue ...]//安装组件依赖
> $ npm update -g//更新

## 开发工具

- Visual Studio Code
- WebStorm

## 项目结构

```JSON
|-ProjectName
    |-build//临时文件
    |-dist//打包后的文件
    |-config
    |-node_modules//依赖库
    |-src
        |-assets//资源文件
        |-components//组件
        |-css
        |   |-common
        |-script
        |-app.vue
    |-package.json
    |-package-lock.json
    |-webpack.config.js
```


## Vue 基础




## 小标题

<img src="https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/resources/images/xxx/xxx.png" alt=""/>

## 参考资料

- [webpack 4 入门](https://www.cnblogs.com/samwu/p/8545161.html)


