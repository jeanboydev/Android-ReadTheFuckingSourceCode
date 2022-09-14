# Redis 使用手册

## 简介

Redis（Remote Dictionary Server）是一个由 Salvatore Sanfilippo 写的 key-value 存储系统，是跨平台的非关系型数据库。

Redis 是一个开源的使用 ANSI C 语言编写、遵守 BSD 协议、支持网络、可基于内存、分布式、可选持久性的键值对（Key-Value）存储数据库，并提供多种语言的 API。

Redis 通常被称为数据结构服务器，因为（value）可以是字符串（String）、哈希（Hash）、列表（List）、集合（sets）和有序集合（sorted sets）等类型。

## 安装

下载地址：https://github.com/tporadowski/redis/releases

Windows 下安装：Redis 支持 32 位和 64 位。这个需要根据你系统平台的实际情况选择，这里我们下载 Redis-x64-xxx.zip 压缩包并解压（例如解压后目录为：D:\Develop\Redis-x64-5.0.14.1）。

打开一个 cmd 窗口 使用 cd 命令切换目录到解压目录：

> $ cd D:\Develop\Redis-x64-5.0.14.1

运行命令：

> $ ./redis-server.exe redis.windows.conf

后面的那个 redis.windows.conf 可以省略，如果省略，会启用默认的，显示如下：

```text
PS D:\Develop\Redis-x64-5.0.14.1> ./redis-server.exe redis.windows.conf
[25528] 12 Sep 18:49:49.119 # oO0OoO0OoO0Oo Redis is starting oO0OoO0OoO0Oo
[25528] 12 Sep 18:49:49.119 # Redis version=5.0.14.1, bits=64, commit=ec77f72d, modified=0, pid=25528, just started
[25528] 12 Sep 18:49:49.119 # Configuration loaded
                _._
           _.-``__ ''-._
      _.-``    `.  `_.  ''-._           Redis 5.0.14.1 (ec77f72d/0) 64 bit
  .-`` .-```.  ```\/    _.,_ ''-._
 (    '      ,       .-`  | `,    )     Running in standalone mode
 |`-._`-...-` __...-.``-._|'` _.-'|     Port: 6379
 |    `-._   `._    /     _.-'    |     PID: 25528
  `-._    `-._  `-./  _.-'    _.-'
 |`-._`-._    `-.__.-'    _.-'_.-'|
 |    `-._`-._        _.-'_.-'    |           http://redis.io
  `-._    `-._`-.__.-'_.-'    _.-'
 |`-._`-._    `-.__.-'    _.-'_.-'|
 |    `-._`-._        _.-'_.-'    |
  `-._    `-._`-.__.-'_.-'    _.-'
      `-._    `-.__.-'    _.-'
          `-._        _.-'
              `-.__.-'

[25528] 12 Sep 18:49:49.135 # Server initialized
[25528] 12 Sep 18:49:49.135 * Ready to accept connections
```

这时候另启一个 cmd 窗口，原来的不要关闭，不然就无法访问服务端了。

切换到 redis 目录下运行:

> $ ./redis-cli.exe -h 127.0.0.1 -p 6379

设置键值对：

> $ set myKey abc

取出键值对：

> $ get myKey

输出如下：

```text
127.0.0.1:6379> set myKey abc
OK
127.0.0.1:6379> get myKey
"abc"
127.0.0.1:6379>
```

## 数据类型

Redis 支持五种数据类型：string（字符串），hash（哈希），list（列表），set（集合）及zset（sorted set：有序集合）。

### String（字符串）

string 类型是 Redis 最基本的数据类型，string 类型的值最大能存储 512MB。

string 类型是二进制安全的。意思是 redis 的 string 可以包含任何数据。比如 jpg 图片或者序列化的对象。

示例：

> // 设置一个字符串
> 
> $ set test "这是一个字符串，哈哈哈哈哈哈"
> 
> // 读取字符串
> 
> $ get test

输出如下：

```text
127.0.0.1:6379> set test "这是一个字符串，哈哈哈哈哈哈"
OK
127.0.0.1:6379> get test
"这是一个字符串，哈哈哈哈哈哈"
```

### Hash（哈希）

Redis hash 是一个 string 类型的 field 和 value 的映射表，hash 特别适合用于存储对象。

每个 hash 可以存储 232 -1 键值对（40多亿）。

示例：

> // 设置一个 Hash
> 
> $ hmset person name "dnm" age 18
> 
> // 读取 person 的 name
> 
> $ hget person name
> 
> // 读取 person 的 age
> 
> $ hget person age
> 
> // 删除 person
> 
> $ del person

输出如下：

```text
127.0.0.1:6379> hmset person name "dnm" age 18
OK
127.0.0.1:6379> hget person name
"dnm"
127.0.0.1:6379> hget person age
"18"
127.0.0.1:6379> del person
(integer) 1
```

### List（列表）

Redis 列表是简单的字符串列表，按照插入顺序排序。你可以添加一个元素到列表的头部（左边）或者尾部（右边）。

列表最多可存储 232 - 1 元素 (4294967295, 每个列表可存储40多亿)。

示例：

> // 向列表 list 中插入一条数据 apple
> 
> $ lpush list apple
> $ lpush list banana
> $ lpush list orange
> 
> // 读取 list 中的前 10 条数据
> 
> $ lrange list 0 10

输出如下：

```text
127.0.0.1:6379> lpush list apple
(integer) 1
127.0.0.1:6379> lpush list banana
(integer) 2
127.0.0.1:6379> lpush list orange
(integer) 3
127.0.0.1:6379> lrange list 0 10
1) "orange"
2) "banana"
3) "apple"
```

### Set（集合）

Redis 的 Set 是 string 类型的无序集合。

集合是通过哈希表实现的，所以添加，删除，查找的复杂度都是 O(1)。

#### sadd 命令

添加一个 string 元素到 key 对应的 set 集合中，成功返回 1，如果元素已经在集合中返回 0。

示例：

> // 向集合 set 中插入一条数据 apple
> 
> $ sadd set apple
> $ sadd set banana
> $ sadd set orange
> 
> // 读取 set 中的数据
> 
> $ smembers set

输出如下：

```text
127.0.0.1:6379> sadd set apple
(integer) 1
127.0.0.1:6379> sadd set banana
(integer) 1
127.0.0.1:6379> sadd set orange
(integer) 1
127.0.0.1:6379> smembers set
1) "orange"
2) "apple"
3) "banana"
```

#### zset（sorted set：有序集合）

Redis zset 和 set 一样也是 string 类型元素的集合，且不允许重复的成员。

不同的是每个元素都会关联一个 double 类型的分数。redis 正是通过分数来为集合中的成员进行从小到大的排序。

zset 的成员是唯一的，但分数（score）却可以重复。

#### zadd 命令

添加元素到集合，元素在集合中存在则更新对应 score。

示例：

> // 向集合 set 中插入一条数据 apple
> 
> $ zadd set_order 0 apple
> $ zadd set_order 0 banana
> $ zadd set_order 0 orange
> 
> // 读取 set 中的数据
> 
> $ zrangebyscore set_order 0 10

输出如下：

```text
127.0.0.1:6379> zadd set_order 0 apple
(integer) 1
127.0.0.1:6379> zadd set_order 0 banana
(integer) 1
127.0.0.1:6379> zadd set_order 0 orange
(integer) 1
127.0.0.1:6379> zrangebyscore set_order 0 10
1) "apple"
2) "banana"
3) "orange"
```

## 常用操作

### 查看 key 类型

> $ type <key_name>

## 参考资料

Redis 官网：https://redis.io

源码地址：https://github.com/redis/redis

Redis 在线测试：http://try.redis.io/

Redis 教程：https://www.runoob.com/redis/redis-tutorial.html
