# Vue 起步

## 简介

Vue (读音 /vjuː/，类似于 view) 是一套用于构建用户界面的渐进式框架。

- [Vue 官网](https://cn.vuejs.org/v2/guide/)

## 基础知识

- [HTML5 教程](http://www.w3school.com.cn/html5/index.asp)
- [CSS3 教程](http://www.w3school.com.cn/css3/index.asp)
- [ECMAScript 6 入门](http://es6.ruanyifeng.com/)

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

- [Webpack 入门](https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/blob/master/web_front/WebFront-Webpack入门.md)

- 命令行工具 (CLI)

Vue 提供一个官方命令行工具，可用于快速搭建大型单页应用。
> // 全局安装 vue-cli<br/>
> $ npm install --global vue-cli

## 开发工具

- [Visual Studio Code](https://code.visualstudio.com/)
- [WebStorm](https://www.jetbrains.com/webstorm/)

## 创建项目

确保前面的准备工作中 Node.js，webpack，vue-cli 已经成功安装，接下来开始创建 vue 项目：

> // 创建一个基于 webpack 模板的新项目<br/>
> $ vue init webpack <项目文件夹>
> 
> // 进入项目目录<br/>
> $ cd <项目文件夹>
> 
> // 安装依赖，不要从国内镜像 cnpm 安装(会导致后面缺了很多依赖库)<br/>
> $ npm install
> 
> // 安装 vue 路由模块 vue-router 和网络请求模块 vue-resource<br/>
> $ npm install vue-router vue-resource --save
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

Data：

```HTML
<div id="app">
  {{ message }}
</div>
```
```JS
var app = new Vue({
  el: '#app',
  data: {
    message: 'Hello Vue!'//当 Message 内容被修改时，页面中 Message 也会更新
  }
})
```

指令：

- v-bind

```HTML
<div id="app-2">
  <span v-bind:title="message"><!--这里动态绑定了 title 的内容-->
    鼠标悬停几秒钟查看此处动态绑定的提示信息！
  </span>
</div>
```
```JS
var app2 = new Vue({
  el: '#app-2',
  data: {
    message: '页面加载于 ' + new Date().toLocaleString()
  }
})
```

- v-if

```HTML
<div id="app-3">
  <p v-if="seen">现在你看到我了</p><!--这里 seen 为 true 时，元素才会添加到页面中-->
</div>
```
```JS
var app3 = new Vue({
  el: '#app-3',
  data: {
    seen: true
  }
})
```

- v-show

```HTML
<h1 v-show="ok">Hello!</h1>
```

不同的是带有 v-show 的元素始终会被渲染并保留在 DOM 中。v-show 只是简单地切换元素的 CSS 属性 display。

- v-for

```HTML
<div id="app-4">
  <ol>
    <!--相当于 java 中：
        for(int i = 0; i < todos.lenght; i++){
            Todo todo = todos.get(i);
        }
    -->
    <!--相当于 swift 中：
        for todo in todos {
            //do something...
        }
    -->
    <li v-for="todo in todos">
      {{ todo.text }}
    </li>
  </ol>
</div>
```
```JS
var app4 = new Vue({
  el: '#app-4',
  data: {
    todos: [
      { text: '学习 JavaScript' },
      { text: '学习 Vue' },
      { text: '整个牛项目' }
    ]
  }
})
```

- v-on

```HTML
<div id="app-5">
  <p>{{ message }}</p>
  <!--添加一个 click 事件监听器-->
  <button v-on:click="reverseMessage">逆转消息</button>
</div>
```
```JS
var app5 = new Vue({
  el: '#app-5',
  data: {
    message: 'Hello Vue.js!'
  },
  methods: {//响应事件需要在 methods 添加方法
    reverseMessage: function () {
      this.message = this.message.split('').reverse().join('')
    }
  }
})
```

- v-model

```HTML
<div id="app-6">
  <p>{{ message }}</p>
  <input v-model="message"><!--实现双向绑定，input 中值修改时，页面中值也会更新-->
</div>
```
```JS
var app6 = new Vue({
  el: '#app-6',
  data: {
    message: 'Hello Vue!'
  }
})
```

- v-html

```HTML
<div id="app-3">
  <span v-html="rawHtml"></span><!--将 html 标签直接输出，不会被解析-->
</div>
```
```JS
var app3 = new Vue({
  el: '#app-3',
  data: {
    rawHtml: '<span style=\'color: red\'>Red</span>'
  }
})
```

缩写：

 对于一些频繁用到的指令来说，Vue 提供了特定简写。
 
 - v-bind
 
 ```HTML
 <!-- 完整语法 -->
 <a v-bind:href="url">...</a>

 <!-- 缩写 -->
 <a :href="url">...</a>
 ```
 
 - v-on

 ```HTML
 <!-- 完整语法 -->
 <a v-on:click="doSomething">...</a>

 <!-- 缩写 -->
 <a @click="doSomething">...</a>
 ```
 
生命周期：

<img src="https://cn.vuejs.org/images/lifecycle.png" alt="Vue 生命周期"/>

```JS
new Vue({
  data: {
    a: 1
  },
  created: function () {
    // `this` 指向 vm 实例
    console.log('a is: ' + this.a)
  }
})
```

- created
- mounted
- updated
- destroyed


侦听器：

```HTML
<div id="watch-example">
  <p>
    Ask a yes/no question:
    <input v-model="question">
  </p>
  <p>{{ answer }}</p>
</div>
```

```HTML
<!-- 因为 AJAX 库和通用工具的生态已经相当丰富，Vue 核心代码没有重复 -->
<!-- 提供这些功能以保持精简。这也可以让你自由选择自己更熟悉的工具。 -->
<script src="https://cdn.jsdelivr.net/npm/axios@0.12.0/dist/axios.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/lodash@4.13.1/lodash.min.js"></script>
<script>
var watchExampleVM = new Vue({
  el: '#watch-example',
  data: {
    question: '',
    answer: 'I cannot give you an answer until you ask a question!'
  },
  watch: {
    // 如果 `question` 发生改变，这个函数就会运行
    question: function (newQuestion, oldQuestion) {
      this.answer = 'Waiting for you to stop typing...'
      this.getAnswer()
    }
  },
  methods: {
    // `_.debounce` 是一个通过 Lodash 限制操作频率的函数。
    // 在这个例子中，我们希望限制访问 yesno.wtf/api 的频率
    // AJAX 请求直到用户输入完毕才会发出。想要了解更多关于
    // `_.debounce` 函数 (及其近亲 `_.throttle`) 的知识，
    // 请参考：https://lodash.com/docs#debounce
    getAnswer: _.debounce(
      function () {
        if (this.question.indexOf('?') === -1) {
          this.answer = 'Questions usually contain a question mark. ;-)'
          return
        }
        this.answer = 'Thinking...'
        var vm = this
        axios.get('https://yesno.wtf/api')
          .then(function (response) {
            vm.answer = _.capitalize(response.data.answer)
          })
          .catch(function (error) {
            vm.answer = 'Error! Could not reach the API. ' + error
          })
      },
      // 这是我们为判定用户停止输入等待的毫秒数
      500
    )
  }
})
</script>
```

事件修饰符：

- .stop
- .prevent
- .capture
- .self
- .once

```HTML
<!-- 阻止单击事件继续传播 -->
<a v-on:click.stop="doThis"></a>

<!-- 提交事件不再重载页面 -->
<form v-on:submit.prevent="onSubmit"></form>

<!-- 修饰符可以串联 -->
<a v-on:click.stop.prevent="doThat"></a>

<!-- 只有修饰符 -->
<form v-on:submit.prevent></form>

<!-- 添加事件监听器时使用事件捕获模式 -->
<!-- 即元素自身触发的事件先在此处处理，然后才交由内部元素进行处理 -->
<div v-on:click.capture="doThis">...</div>

<!-- 只当在 event.target 是当前元素自身时触发处理函数 -->
<!-- 即事件不是从内部元素触发的 -->
<div v-on:click.self="doThat">...</div>

<!-- 2.1.4 新增：点击事件将只会触发一次 -->
<a v-on:click.once="doThis"></a>
```

按键修饰符：

在监听键盘事件时，我们经常需要检查常见的键值。Vue 允许为 v-on 在监听键盘事件时添加按键修饰符：

```HTML
<!-- 只有在 `keyCode` 是 13 时调用 `vm.submit()` -->
<input v-on:keyup.13="submit">
```

记住所有的 keyCode 比较困难，所以 Vue 为最常用的按键提供了别名：

```HTML
<!-- 同上 -->
<input v-on:keyup.enter="submit">

<!-- 缩写语法 -->
<input @keyup.enter="submit">
```

- .enter
- .tab
- .delete (捕获“删除”和“退格”键)
- .esc
- .space
- .up
- .down
- .left
- .right

## Vue 组件

- 全局注册

创建一个 Vue 实例：

```JS
new Vue({
  el: '#some-element',
  // 选项
})
```

要注册一个全局组件，可以使用 Vue.component(tagName, options)。例如：

```JS
Vue.component('my-component', {
  // 选项
})
```

组件在注册之后，便可以作为自定义元素 <my-component></my-component> 在一个实例的模板中使用。注意确保在初始化根实例之前注册组件：

```HTML
<div id="example">
  <my-component></my-component>
</div>
```

```JS
// 注册
Vue.component('my-component', {
  template: '<div>A custom component!</div>'
})

// 创建根实例
new Vue({
  el: '#example'
})
```

渲染为

```HTML
<div id="example">
  <div>A custom component!</div>
</div>
```

- 局部注册

你不必把每个组件都注册到全局。你可以通过某个 Vue 实例/组件的实例选项 components 注册仅在其作用域中可用的组件：

```JS
var Child = {
  template: '<div>A custom component!</div>'
}

new Vue({
  // ...
  components: {
    // <my-component> 将只在父组件模板中可用
    'my-component': Child
  }
})
```

Prop：

- 使用 Prop 传递数据

组件实例的作用域是孤立的。这意味着不能 (也不应该) 在子组件的模板内直接引用父组件的数据。父组件的数据需要通过 prop 才能下发到子组件中。

子组件要显式地用 props 选项声明它预期的数据：

```JS
Vue.component('child', {
  // 声明 props
  props: ['message'],
  // 就像 data 一样，prop 也可以在模板中使用
  // 同样也可以在 vm 实例中通过 this.message 来使用
  template: '<span>{{ message }}</span>'
})
```

然后我们可以这样向它传入一个普通字符串：

```HTML
<child message="hello!"></child>
```

Prop 是单向绑定的：当父组件的属性变化时，将传导给子组件，但是反过来不会。这是为了防止子组件无意间修改了父组件的状态，来避免应用的数据流变得难以理解。

另外，每次父组件更新时，子组件的所有 prop 都会更新为最新值。这意味着你不应该在子组件内部改变 prop。如果你这么做了，Vue 会在控制台给出警告。


- [组件使用 Demo](https://github.com/jeanboydev/Vue-demo)

## Vue 路由

## Vuex

## 项目上线

> // 开发环境打包<br/>
> $ npm run dev
> 
> // 生产环境打包<br/>
> $ npm run build

将 dist 目录下所有文件丢到服务器就可以了。




