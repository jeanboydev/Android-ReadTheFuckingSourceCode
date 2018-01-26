# CentOS 7 常用命令
## vi 常用命令

* 新插入一行并进入编辑模式：o
* 从目前光标所在处插入：i
* 跳转到文件第一行：gg
* 跳转到文件末尾：G
* 向下查找：/<word>
* 向上查找：?<word>
* 删除后一个字符：x	相当于[Delete]
* 删除前一个字符：X	相当于[Backspace]
* 删除所在的一行：dd
* 复制所在的一行：yy
* 粘贴已复制的数据在光标下一行：p
* 粘贴已复制的数据在光标上一行：P
* 撤销上一个操作：u
* 撤销多个操作：Ctrl + r
* 重复上一个操作：.
* 保存文件：Esc + :w
* 强制保存只读文件：Esc + :w!
* 离开不保存文件：Esc + :q
* 强制离开不保存文件：Esc + :q!
* 保存后离开文件：Esc + :wq
* 强制保存后离开文件：Esc + :wq!

## 文件/文件夹常用命令

* 查看文件权限：ls –l
* 切换目录：cd <路径>
* 创建文件夹：mkdir <路径> 
* 删除空文件夹：rmdir <路径>
* 创建空文件：touch <文件名>
* 创建带内容的文件：echo <文件名>
* 查看文件内容：cat <文件路径>
* 复制文件：cp <源文件路径> <目标文件路径>
* 移动或重命名文件：mv <源文件路径> <目标文件路径>
* 删除文件：rm <源文件路径>
* 递归删除，可删除子目录及文件：rm –r <源文件路径>
* 强制删除：rm –f <源文件路径>
* 搜索文件：find
* 搜索：whereis <java>
* 解压压缩包：tar –zxv –f <源文件路径> <目标文件路径>
* 删除压缩包：rm -rf <源文件路径>



## 系统软件源常用命令

* 更新软件源：yum –y update
* 搜索软件：yum [–y:该参数默认yes] search <软件名>
* 安装软件：yum [–y:该参数默认yes] install <软件名>  //软件名例如：vim*
* 删除软件：yum [–y:该参数默认yes] remove <软件名>
* 列出可安装的软件：yum list
* 列出可更新的软件：yum list updates
* 列出已安装的软件：yum list installed
* 列出已安装但不在 yum 库中的软件：yum extras
* 列出所有软件包信息：yum info

## 系统用户常用命令

* 创建用户：adduser <用户名>
* 修改用户密码：passwd <用户名>
* 通过变价sudoers文件给创建的用户赋权：
    > visudo

    在sudoers文件最后一行加入
    > <用户名>	ALL=(ALL)	ALL
    
## 系统安全加固

通过配置 ssh 服务，修改默认端口号，禁止 root 用户登录，加强云主机安全性。使用创建的用户登录执行命令：
> vi /etc/ssh/sshd_config

在ssh配置文件末尾添加，port端口号可自定义：

> Port 10022
> Protocol 2
> PermitRootLogin no

保存后退出，然后reload ssh服务，使配置生效：

> service sshd reload

使用命令行登录云主机：

> ssh -p <port> <用户名>@<公网IP地址>


## 系统防火墙

> firewall-cmd --list-ports	//查看防火墙已经开放的端口
> systemctl status firewalld	//查看防火墙状态
> systemctl start firewalld	//开启防火墙

开启防火墙 8080 端口：

> firewall-cmd --permanent --zone=public --add-port=8080/tcp
> firewall-cmd --reload

端口操作：

> netstat -tunlp|grep <port>	//查看端口占用情况

-t：仅显示tcp相关选项
-u：仅显示udp相关选项
-n：拒绝显示别名
-l：仅列出有在Listen的服务状态
-p：显示简历相关链接的程序名

## 系统其它常用命令

systemctl 操作：（systemctl主要负责控制systemd系统和服务管理器，取代service方式）

> systemctl start <软件名> //启动
> systemctl restart <软件名>   //重启
> systemctl stop <软件名>  //停止
> systemctl reload <软件名>    //重载服务
> systemctl status <软件名>    //查看服务状态
> systemctl enable <软件名>    //设置开机启动
> systemctl disable <软件名>   //禁止开机启动
> systemctl kill <软件名>  //杀死服务

进程操作：

> ps –ef | grep <软件名>   //查看进程是否存在，例如：nginx，tomcat
> kill -9 <进程号> //强制停止
> kill -quit <进程号>  //停止进程






