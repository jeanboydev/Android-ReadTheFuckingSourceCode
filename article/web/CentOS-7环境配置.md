# CentOS 7 环境配置
## 安装 Nginx

1. 安装

> yum install nginx

2. 查看安装是否正确

> rpm -qa | grep nginx
> 
> rpm -ql nginx	//查看生成的文件

3. 配置

默认的配置文件在 `/etc/nginx/nginx.conf`，打开配置文件：
> vi /etc/nginx/nginx.conf

在 `server` 模块中添加：
> include /home/<用户名>/nginx/config/*.conf;

在上面目录下创建 `*.conf` 文件，内容如下：


```Java
upstream tomcat_server{ #负载均衡的服务器列表
    ip_hash;   #ip进行hash值分发，同一个ip客户端只分发到一个tomcat里
    server 127.0.0.1:8080 weight=1 max_fails=2 fail_timeout=30s;
    #server 127.0.0.1:8081 weight=1 max_fails=2 fail_timeout=30s;
}

server {
    listen 80; #监听80端口
    server_name <配置域名>; #监听的域名
    root   /home/<用户名>/webapp/<配置网站目录>;  #站点根目录位置
    location / {   #转发或处理
        proxy_pass http://tomcat_server;   #请求转向定义的服务器列表（反向代理）
        proxy_redirect off;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header REMOTE-HOST $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_next_upstream http_502 http_504 error timeout invalid_header;

        client_max_body_size 50m;
        client_body_buffer_size 256k;
    }  
   
   #错误页
   error_page 500 502 503 504 /50x.html;  
   location = /50x.html {
        root   /home/<用户名>/webapp/error;
   }
   
   #所有js,css相关的静态资源文件的请求由Nginx处理
   location ~.*\.(js|css)$ {
      root    /home/<用户名>/webapp/static-resources; #指定文件路径
      expires     12h;   #过期时间为12小时
   }
   
   #所有图片等多媒体相关静态资源文件的请求由Nginx处理
   location ~.*\.(html|jpg|jpeg|png|bmp|gif|ico|mp3|mid|wma|mp4|swf|flv|rar|zip|txt|doc|ppt|xls|pdf)$ {
      root    /home/<用户名>/webapp/static-resources; #指定文件路径
      expires     7d;    #过期时间为7天
   }
}
```

4. 常用操作

> systemctl start nginx //启动
> 
> systemctl stop nginx  //关闭
> 
> systemctl reload nginx    //重载配置文件

## 安装 Java

1. 查看已安装的 Java

> java -version //查看已安装的 java 版本

2. 安装 Java

> yum install –y openjdk    //-y 默认全部 yes

3. 配置环境变量

打开配置文件：

> vi /etc/profile

添加以下内容：

```Java
JAVA_HOME=/usr/lib/jvm/java-1.8.0-openjdk-1.8.0.161-0.b14.el7_4.x86_64
JRE_HOME=$JAVA_HOME/jre
CLASS_PATH=.:$JAVA_HOME/lib/dt.jar:$JAVA_HOME/lib/tools.jar:$JRE_HOME/lib
PATH=$PATH:$JAVA_HOME/bin:$JRE_HOME/bin
export JAVA_HOME JRE_HOME CLASS_PATH PATH
```

更新环境变量：

> source /etc/profile

## 安装 Tomcat

1. 下载 tar.gz 安装包

https://tomcat.apache.org/download-80.cgi

2. 上传至服务器并解压

解压到：`/home/<用户名>/tomcat`
> tar –zxv –f apache-tomcat-xxx.tar.gz	//解压压缩包
> 
> rm -rf apache-tomcat-7.0.29.tar.gz	//删除压缩包

3. 配置外部应用目录

在 `/home/<用户名>/tomcat/conf/server.xml` 下配置，指定外部应用路径

在 `<Host>...</Host>` 的标签之间添加

```Xml
<!-- path 的值为：127.0.0.1/<path>-->
<Context path="" docBase="外部路径"/>

```

4. 去掉项目名

在 `<Host>...</Host>` 的标签之间添加

```Xml
<Context path="" docBase="项目路径"/>
```

5. 修改默认端口号

```Xml
<Connector port="8080" protocol="HTTP/1.1" connectionTimeout="20000"
 redirectPort="8443" />
```

只需要将8080修改为80

6. 启动与停止

> /home/<用户名>/tomcat/bin/startup.sh	//启动
> 
> /home/<用户名>/tomcat/bin/shutdown.sh	//停止

启动或停止出错时，使用进程命令操作：

> ps -ef | grep tomcat
> 
> kill -9 <进程号>

7. 应用 war 部署

Idea 打 war 包
> Build -> Build Artifacts -> Gradle:xxx.war -> Build

war 包保存位置
> Project Structure -> Artifacts -> Output directory

将 war 包复制到 tomcat -> webapps 目录下，tomcat 自动解压

## 安装 MySQL

1. 配置yum源

在 MySQL 官网中下载 yum 源 rpm 安装包：
http://dev.mysql.com/downloads/repo/yum/
> sudo wget https://repo.mysql.com//mysql57-community-release-el7-11.noarch.rpm
> 
> sudo yum localinstall mysql57-community-release-el7-11.noarch.rpm

2. 检查 MySQL 源是否安装成功：

> yum repolist enabled | grep "mysql.*-community.*"

3. 安装

> yum install mysql-community-server

4. 启动

> systemctl start mysqld

设置开机启动：
> systemctl enable mysqld
> systemctl daemon-reload

5. 修改root本地登录密码

MySQL 安装完成之后，在 `/var/log/mysqld.log` 文件中给 root 生成了一个默认密码。通过下面的方式找到 root 默认密码，然后登录 MySQL 进行修改：
> grep 'temporary password' /var/log/mysqld.log
> 
> mysql -uroot –p	//登录mysql
> 
> ALTER USER 'root'@'localhost' IDENTIFIED BY '新密码';

添加远程登录用户：
> GRANT ALL PRIVILEGES ON *.* TO '用户名'@'%' IDENTIFIED BY '密码' WITH GRANT OPTION;

6. 配置默认编码为utf-8:

> sudo vi /etc/my.cnf

添加内容：

```Xml
[mysqld]
character_set_server=utf8
init_connect='SET NAMES utf8'
```

7. 默认配置文件路径：

配置文件：/etc/my.cnf 

日志文件：/var/log//var/log/mysqld.log 

服务启动脚本：/usr/lib/systemd/system/mysqld.service 

socket文件：/var/run/mysqld/mysqld.pid

