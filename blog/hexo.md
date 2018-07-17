## GitHub

1. 创建 `github.io` 仓库

   仓库名：<username>.github.io

   > 例如：jeanboydev.github.io
   >
   > 创建好之后就可以访问 https://jeanboydev.github.io
   >
   > 显示一个 GitHub 的 404 页面

2. 创建博客项目仓库

   仓库名：blog.io

3. 将两个项目都 `clone` 到本地

## 环境配置

1. 安装 `Node.js`

2. 安装 `Git`

3. 安装 `Hexo`

   > $ npm install hexo-cli -g

## Hexo

1. 创建一个 `hexo` 文件夹，并进入文件夹

   > $ cd ~/hexo

2. 初始化 hexo 项目

   > $ hexo init

   配置 npm：

   > $ npm install

   加载 hexo 基础 html、css、js 等文件：

   > $ hexo g

   开启了一个本地的服务器：

   > $ hexo s

   在浏览器中访问 `http://localhost:4000/` 即可看到创建好的 hexo 项目

3. 将 `hexo` 文件夹下的所有文件拷贝到，`blog.io` 项目的文件夹下，然后键入 `blog.io` 目录下

4. 安装主题

   例如安装这个主题：https://github.com/klugjo/hexo-theme-anodyne

   > $ git clone https://github.com/klugjo/hexo-theme-anodyne themes/anodyne

5. 修改根目录下的 `_config.yml`  文件

   ```js
   # Extensions
   ## Plugins: https://hexo.io/plugins/
   ## Themes: https://hexo.io/themes/
   theme: landscape
   ## 修改为
   theme: anodyne
   ```

   执行命令预览：

   > $ hexo s

6. 配置与 `github.io` 关联

   继续修改根目录下的 `_config.yml`  文件：

   ```js
   # Deployment
   ## Docs: https://hexo.io/docs/deployment.html
   deploy:
     type: git
     repo: https://github.com/jeanboydev/jeanboydev.github.io.git
     branch: master
   ```

   执行命令保存配置：

   > $ npm install hexo-deployer-git -save

   发布 hexo 到 github page：

   > //等于一次性执行了，清空、刷新、部署三个命令
   >
   > $ hexo clean && hexo g && hexo d

   此时访问：https://jeanboydev.github.io 

   即可看到我们发布的 hexo 项目。

7. 配置 `github.io`

   在 `settings` -> `GitHub Pages` 中设置 `Custom domain` 为自己的域名。

   > 如：blog.jeanboy.cn

8. 需要配置 DNS 解析

   获取 ip 地址：

   > $ ping jeanboydev.github.io

   得到 ip 地址，在 DNS 服务器中配置即可。

## 管理

- 新建页面

  > $ hexo new page "about"

  在主题的 `_configy.yml`  设置：

  ```js
  menu:
    home: /
    about: /about
  ```

- 新建文章

  > $ hexo new "<文章文件名>"

  命令新建一个文件 `source/_posts/<文章文件名>.md` ，然后打开这个文件编辑：

  ```markdown
  ---
  title: 文章标题
  date: 2018-07-04 11:53:46 #创建时间
  updated: 2018-07-04 11:53:46 #修改时间
  comments: true #是否开启评论
  categories: #分类
  - 默认
  tags: #标签
  - 测试
  - 文章
  ---
  #以下是文章内容，请使用 Markdown 书写
  
  这是摘要这是摘要这是摘要这是摘要这是摘要这是摘要这是摘要这是摘要
  
  <!-- more -->
  
  这是正文这是正文这是正文这是正文这是正文这是正文这是正文这是正文这是正文这是正文这是正文这是正文这是正文这是正文这是正文这是正文这是正文这是正文这是正文这是正文这是正文这是正文这是正文这是正文这是正文这是正文这是正文
  ```

- 新建标签页

  > $ hexo new page tags

  找到创建的文件打开编辑：

  ```markdown
  ---
  title: 所有标签
  date: 2018-07-04 12:17:30
  type: "tags"
  comments: false
  ---
  ```

- 新建分类页

  > $ hexo new page categories

  找到创建的文件打开编辑：

  ```markdown
  ---
  title: 所有分类
  date: 2018-07-04 12:17:30
  type: "categories"
  comments: false
  ---
  ```

- 发布 hexo 到 github page：

  > //等于一次性执行了，清空、刷新、部署三个命令
  >
  > $ hexo clean && hexo g && hexo d

## 插件

- 通过 git 发布

  > $ npm install hexo-deployer-git --save

- 本地服务

  > $ npm install hexo-server --save

- 索引生成器

  > $ npm install hexo-generator-index --save

- 归档生成器

  > $ npm install hexo-generator-archive --save

- 分类生成器

  > $ npm install hexo-generator-category --save

- 标签生成器

  > $ npm install hexo-generator-tag --save

- 本地搜索功能

  > $ npm install hexo-generator-search --save
  >
  > $ npm install hexo-generator-searchdb --save

  在博客目录的 `_config.yml` 中添加如下代码：

  ```js
  # 本地搜索
  search:
    path: search.xml
    field: post
    format: html
    limit: 10000
  ```

  编译你的博客：

  > $ hexo g

- 生成搜索引擎网站地图

  > $ npm install hexo-generator-sitemap --save
  >
  > $ npm install hexo-generator-baidu-sitemap --save

  在博客目录的 `_config.yml` 中添加如下代码：

  ```js
  # 自动生成 sitemap
  sitemap:
  	path: sitemap.xml
  baidusitemap:
  	path: baidusitemap.xml
  ```

  编译你的博客：

  > $ hexo g

- 可视化编辑博客

  > $ npm install --save hexo-admin
  >
  > $ hexo server -d

- RSS

  > $ npm install hexo-generator-feed --save