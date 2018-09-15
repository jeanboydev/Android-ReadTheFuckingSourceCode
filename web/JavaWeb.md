# 

## 

```json
|-WebApp
	|-META-INF//自动生成，存放项目信息
	|-WEB-INF//JavaWeb 应用的安全目录，客户端无法访问，只有服务器端可以访问
		|-lib//存放项目所需要的各种 jar 文件
		|-classes//存放项目中运行文件
			|-com.xxx.xxx//存放项目中所有的 class 文件
			|-config
				|-database.properties//数据库配置文件
		|-web.xml//项目配置文件，描述了 servlet 和其他的应用组件配置及命名规则
	|-index.html
```

## 

```json
|-ProjectName
	|-build//自动构建时输出路径
	|-gradle//gradle 环境配置
	|-out//打包输出路径
	|-src//项目源码
		|-main//打包到 webapp 的 classes 路径下
			|-java
			|-resources
				|-config
		|-webapp//打包到 webapp 中
			|-WEB-INF
				|-web.xml
			|-index.html
	|-build.gradle//当前 module 配置文件
	|-settings.gradle//module 全局配置
```

## 

- 创建项目

![01](/Users/next/Work/Mine/Android-ReadTheFuckingSourceCode/resources/images/web_project/01.png)

![02](/Users/next/Work/Mine/Android-ReadTheFuckingSourceCode/resources/images/web_project/02.png)

![03](/Users/next/Work/Mine/Android-ReadTheFuckingSourceCode/resources/images/web_project/03.png)

![04](/Users/next/Work/Mine/Android-ReadTheFuckingSourceCode/resources/images/web_project/04.png)

![05](/Users/next/Work/Mine/Android-ReadTheFuckingSourceCode/resources/images/web_project/05.png)

- 生成 web.xml

![06](/Users/next/Work/Mine/Android-ReadTheFuckingSourceCode/resources/images/web_project/06.png)

![07](/Users/next/Work/Mine/Android-ReadTheFuckingSourceCode/resources/images/web_project/07.png)

![08](/Users/next/Work/Mine/Android-ReadTheFuckingSourceCode/resources/images/web_project/08.png)

![09](/Users/next/Work/Mine/Android-ReadTheFuckingSourceCode/resources/images/web_project/09.png)

- 配置 Tomcat

首先下载 zip 安装包
https://tomcat.apache.org/download-80.cgi

![10](/Users/next/Work/Mine/Android-ReadTheFuckingSourceCode/resources/images/web_project/10.png)

![11](/Users/next/Work/Mine/Android-ReadTheFuckingSourceCode/resources/images/web_project/11.png)

![12](/Users/next/Work/Mine/Android-ReadTheFuckingSourceCode/resources/images/web_project/12.png)

![13](/Users/next/Work/Mine/Android-ReadTheFuckingSourceCode/resources/images/web_project/13.png)

![14](/Users/next/Work/Mine/Android-ReadTheFuckingSourceCode/resources/images/web_project/14.png)

![15](/Users/next/Work/Mine/Android-ReadTheFuckingSourceCode/resources/images/web_project/15.png)

![16](/Users/next/Work/Mine/Android-ReadTheFuckingSourceCode/resources/images/web_project/16.png)