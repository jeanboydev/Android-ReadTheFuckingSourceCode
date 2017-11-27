# Log4j配置
## Log4j组件
- Loggers(记录器)
- Appenders(输出源)
- Layouts(布局)

## Loggers(记录器)
Loggers 组件在此系统中被分为五个级别：DEBUG < INFO < WARN < ERROR < FATAL

Log4j规则：只输出级别不低于设定级别的日志信息，假如 Loggers 级别设定为 INFO，则 INFO、WARN、ERROR 和 FATAL 级别的日志信息都会输出，而级别比 INFO 低的 DEBUG 则不会输出。

## Appenders（输出源）
禁用和使用日志请求是 Log4j 的基本功能，Log4j 日志系统提供许多强大的功能，比如允许把日志输出到不同的地方，如控制台(Console)、文件(Files）等，可以根据天数或者文件大小产生新的文件，可以以流的形式发送到其它地方等。

## Layouts（布局)
有时，用户希望根据自己的喜好格式化自己的日志输出，Log4j 可以在 Appenders 的后面附加 Layouts 来完成这个功能。Layouts 提供四种日志输出格式，如根据 HTML 样式、自由指定样式、包含日志级别与信息的样式、包含日志时间、线程、类别等信息的样式。

## Log4j 配置详解
在实际应用中，要使 Log4j 在系统运行中运行需事先设置配置文件。配置文件事实上也就是对 Logger、Appender 及 Layout 进行相应的设定。 
Log4j 支持两种配置文件格式，一种是 XML 格式的文件，一种是 properties 属性文件。下面以 properties 属性文件配置为例进行介绍 log4j.properties 的配置。

## 配置 Logger

> log4j.rootLogger = [ level ] , appenderName1, appenderName2, … 
> log4j.additivity.org.apache=false # 表示 Logger 不会在父 Logger 的 appender 里输出，默认为 true。

level ：设定日志记录的最低级别，可设的值有 OFF、FATAL、ERROR、WARN、INFO、DEBUG、ALL 或者自定义的级别，Log4j 建议只使用中间四个级别。通过在这里设定级别，您可以控制应用程序中相应级别的日志信息的开关，比如在这里设定了INFO级别，则应用程序中所有 DEBUG 级别的日志信息将不会被打印出来。 

appenderName：就是指定日志信息要输出到哪里。可以同时指定多个输出目的地，用逗号隔开。 
例如：log4j.rootLogger＝INFO,A1,B2,C3

## 配置 Appender

> log4j.appender.appenderName = className

appenderName: Appender 的名字，自定义，在 log4j.rootLogger 设置中使用； 
className：Appender 的类的全名（包含包名）

常用的 Appender 的 className 如下：

```Java
org.apache.log4j.ConsoleAppender #日志输出到控制台 
org.apache.log4j.FileAppender #日志保存为文件 
org.apache.log4j.DailyRollingFileAppender #每天产生一个日志文件 
org.apache.log4j.RollingFileAppender #文件大小到达指定大小的时候产生一个新的文件 
org.apache.log4j.WriterAppender #将日志信息以流格式发送到任意指定的地方 
org.apache.log4j.jdbc.JDBCAppender #数据库 
org.apache.log4j.net.JMSAppender # 
org.apache.log4j.net.SocketAppender #Socket 
org.apache.log4j.net.SMTPAppender #邮件
```

- ConsoleAppender 的选项

> Threshold=WARN：指定日志信息的最低输出级别，默认为DEBUG。
> ImmediateFlush=true：表示所有消息都会被立即输出，设为false则不输出，默认值是true。
> Target=System.err：默认值是System.out。

- FileAppender 的选项

> Threshold=WARN：指定日志信息的最低输出级别，默认为DEBUG。
> ImmediateFlush=true：表示所有消息都会被立即输出，设为false则不输出，默认值是true。
> Append=false：true表示消息增加到指定文件中，false则将消息覆盖指定的文件内容，默认值是true。
> File=D:/logs/logging.log4j：指定消息输出到logging.log4j文件中

- DailyRollingFileAppender 的选项

> Threshold=WARN：指定日志信息的最低输出级别，默认为DEBUG。
> ImmediateFlush=true：表示所有消息都会被立即输出，设为false则不输出，默认值是true。
> Append=false：true表示消息增加到指定文件中，false则将消息覆盖指定的文件内容，默认值是true。
> File=D:/logs/logging.log4j：指定当前消息输出到logging.log4j文件中。
> DatePattern=’.’yyyy-MM：每月滚动一次日志文件，即每月产生一个新的日志文件。当前月的日志文件名为 logging.log4j，前一个月的日志文件名为 logging.log4j.yyyy-MM。 
另外，也可以指定按周、天、时、分等来滚动日志文件，对应的格式如下： 
’.’yyyy-MM：每月
‘.’yyyy-ww：每周
‘.’yyyy-MM-dd：每天
‘.’yyyy-MM-dd-a：每天两次
‘.’yyyy-MM-dd-HH：每小时
‘.’yyyy-MM-dd-HH-mm：每分钟

- RollingFileAppender 的选项

> Threshold=WARN：指定日志信息的最低输出级别，默认为DEBUG。
> ImmediateFlush=true：表示所有消息都会被立即输出，设为false则不输出，默认值是true。
> Append=false：true表示消息增加到指定文件中，false则将消息覆盖指定的文件内容，默认值是true。
> File=D:/logs/logging.log4j：指定消息输出到logging.log4j文件中。
> MaxFileSize=100KB：后缀可以是 **KB, MB 或者 GB。在日志文件到达该大小时，将会自动滚动，即将原来的内容移到 logging.log4j.1 文件中。
> MaxBackupIndex=2：指定可以产生的滚动文件的最大数，例如，设为 2 则可以产生logging.log4j.1，logging.log4j.2两个滚动文件和一个logging.log4j文件。

## 配置 Layout

> log4j.appender.appenderName.layout=className

常用的 Layout 的 className 如下：

```Java
org.apache.log4j.HTMLLayout #以 HTML 表格表式布局 
org.apache.log4j.PatternLayout #可以灵活批定布局模式 
org.apache.log4j.SimpleLayout #包含日志信息的级别和信息字符串 
org.apache.log4j.TTCCLayout #包含日志产生的时间、线程、类别等信息
```

- HTMLLayout 选项

> LocationInfo=true：输出java文件名称和行号，默认值是false。
> Title=My Logging： 默认值是Log4J Log Messages。

- PatternLayout选项

> ConversionPattern=%m%n：设定以怎样的格式显示消息。

各种格式化说明如下：

> %p：输出日志信息的优先级，即DEBUG，INFO，WARN，ERROR，FATAL。
> %d：输出日志时间点的日期或时间，默认格式为ISO8601，也可以在其后指定格式，如：%d{yyyy/MM/dd HH:mm:ss,SSS}。
> %r：输出自应用程序启动到输出该log信息耗费的毫秒数。
> %t：输出产生该日志事件的线程名。
> %l：输出日志事件的发生位置，相当于%c.%M(%F:%L)的组合，包括类全名、方法、文件名以及在代码中的行数。例如：test.TestLog4j.main(TestLog4j.java:10)。
> %c：输出日志信息所属的类目，通常就是所在类的全名。
> %M：输出产生日志信息的方法名。
> %F：输出日志消息产生时所在的文件名称。
> %L:：输出代码中的行号。
> %m:：输出代码中指定的具体日志信息。
> %n：输出一个回车换行符，Windows平台为”\r\n”，Unix平台为”\n”。
> %x：输出和当前线程相关联的NDC(嵌套诊断环境)，尤其用到像java servlets这样的多客户多线程的应用中。
> %%：输出一个”%”字符。

另外，还可以在%与格式字符之间加上修饰符来控制其最小长度、最大长度、和文本的对齐方式。如：

> c：指定输出category的名称，最小的长度是20，如果category的名称长度小于20的话，默认的情况下右对齐。
> %-20c：”-“号表示左对齐。
> %.30c：指定输出category的名称，最大的长度是30，如果category的名称长度大于30的话，就会将左边多出的字符截掉，但小于30的话也不会补空格。

## Log4j常用配置

```Java
## 日志输出等级
log4j.rootLogger=DEBUG,console,logFile,rollingFile,dailyFile,errorFile
log4j.additivity.org.apache=true

## 控制台(console)
log4j.appender.console=org.apache.log4j.ConsoleAppender
log4j.appender.console.Threshold=DEBUG
log4j.appender.console.ImmediateFlush=true
log4j.appender.console.Target=System.err
log4j.appender.console.layout=org.apache.log4j.PatternLayout
log4j.appender.console.layout.ConversionPattern=%d{yyyy-MM-dd HH:mm:ss} [%p] %m%n

## 日志文件(logFile)
log4j.appender.logFile=org.apache.log4j.FileAppender
log4j.appender.logFile.Threshold=DEBUG
log4j.appender.logFile.ImmediateFlush=true
log4j.appender.logFile.Append=true
log4j.appender.logFile.File=${catalina.base}/logs/log_
log4j.appender.logFile.layout=org.apache.log4j.PatternLayout
log4j.appender.logFile.layout.ConversionPattern=%d{yyyy-MM-dd HH:mm:ss} [%p] %m%n

## 滚动文件(rollingFile)
log4j.appender.rollingFile=org.apache.log4j.RollingFileAppender
log4j.appender.rollingFile.Threshold=DEBUG
log4j.appender.rollingFile.ImmediateFlush=true
log4j.appender.rollingFile.Append=true
log4j.appender.rollingFile.File=logs/rolling-debug.log
log4j.appender.rollingFile.MaxFileSize=200KB
log4j.appender.rollingFile.MaxBackupIndex=50
log4j.appender.rollingFile.layout=org.apache.log4j.PatternLayout
log4j.appender.rollingFile.layout.ConversionPattern=%d{yyyy-MM-dd HH:mm:ss} [%p] %m%n

## 定期滚动日志文件(dailyFile)
log4j.appender.dailyFile=org.apache.log4j.DailyRollingFileAppender
log4j.appender.dailyFile.Threshold=DEBUG
log4j.appender.dailyFile.ImmediateFlush=true
log4j.appender.dailyFile.Append=true
log4j.appender.dailyFile.File=${catalina.base}/logs/log_
log4j.appender.dailyFile.DatePattern='.'yyyy-MM-dd'.log' 
log4j.appender.dailyFile.layout=org.apache.log4j.PatternLayout
log4j.appender.dailyFile.layout.ConversionPattern=%d{yyyy-MM-dd HH:mm:ss} [%p] %m%n

## Error 日志单独保存
log4j.appender.errorFile=org.apache.log4j.DailyRollingFileAppender
log4j.appender.errorFile.Threshold=ERROR
log4j.appender.errorFile.ImmediateFlush=true
log4j.appender.errorFile.Append=true
log4j.appender.errorFile.File=logs/error.log
log4j.appender.errorFile.DatePattern='.'yyyy-MM-dd
log4j.appender.errorFile.layout=org.apache.log4j.PatternLayout
log4j.appender.errorFile.layout.ConversionPattern=%d{yyyy-MM-dd HH:mm:ss} [%p] %m%n

```

## Log4j 局部配置
以上介绍的配置都是全局的，整个工程的代码使用同一套配置，意味着所有的日志都输出在了相同的地方，你无法直接了当的去看数据库访问日志、用户登录日志、操作日志，它们都混在一起，因此，需要为包甚至是类配置单独的日志输出，下面给出一个例子，为“com.demo.test”包指定日志输出器“test”，“com.demo.test”包下所有类的日志都将输出到 /log/test.log 文件

```Java
log4j.logger.com.demo.test=DEBUG,test
log4j.appender.test=org.apache.log4j.FileAppender
log4j.appender.test.File=/log/test.log
log4j.appender.test.layout=org.apache.log4j.PatternLayout
log4j.appender.test.layout.ConversionPattern=%d{yyyy-MM-dd HH:mm:ss} [%p] %m%n
```

也可以让同一个类输出不同的日志，为达到这个目的，需要在这个类中实例化两个 logger

```Java
private static Log logger1 = LogFactory.getLog("myTest1");
private static Log logger2 = LogFactory.getLog("myTest2");
```

然后分别配置

```Java
log4j.logger.myTest1= DEBUG,test1
log4j.additivity.myTest1=false
log4j.appender.test1=org.apache.log4j.FileAppender
log4j.appender.test1.File=/log/test1.log
log4j.appender.test1.layout=org.apache.log4j.PatternLayout
log4j.appender.test1.layout.ConversionPattern=%d{yyyy-MM-dd HH:mm:ss} [%p] %m%n
  
log4j.logger.myTest2=DEBUG,test2
log4j.appender.test2=org.apache.log4j.FileAppender
log4j.appender.test2.File=/log/test2.log
log4j.appender.test2.layout=org.apache.log4j.PatternLayout
log4j.appender.test2.layout.ConversionPattern=%d{yyyy-MM-dd HH:mm:ss} [%p] %m%n
```

## Logback 配置

依赖包

```Java
    //logback
//    compile 'org.slf4j:slf4j-api:1.7.25'
    compile 'org.slf4j:jcl-over-slf4j:1.7.25'
    compile 'ch.qos.logback:logback-core:1.2.3'
    compile 'ch.qos.logback:logback-classic:1.2.3'
    compile 'org.logback-extensions:logback-ext-spring:0.1.4'//logback与spring整合
```

web.xml 配置

```Xml
 <context-param>
        <param-name>logbackConfigLocation</param-name>
        <param-value>classpath:logback.xml</param-value>
    </context-param>
    <listener>
        <listener-class>ch.qos.logback.ext.spring.web.LogbackConfigListener</listener-class>
    </listener>
```


Xml 配置

```Xml
<?xml version="1.0" encoding="UTF-8"?>
<!--
-scan:当此属性设置为true时，配置文件如果发生改变，将会被重新加载，默认值为true
-scanPeriod:设置监测配置文件是否有修改的时间间隔，如果没有给出时间单位，默认单位是毫秒。
-           当scan为true时，此属性生效。默认的时间间隔为1分钟
-debug:当此属性设置为true时，将打印出logback内部日志信息，实时查看logback运行状态。默认值为false。
-
- configuration 子节点为 appender、logger、root
-->
<configuration scan="true" scanPeriod="60 second" debug="false">

    <!-- 配置信息 -->
    <property name="APP_NAME" value="test"/>
    <!-- 日志路径：推荐绝对路径 -->
    <property name="LOG_PATH"
              value="/Users/next/Library/Caches/IntelliJIdea2017.2/tomcat/Unnamed_test/logs/project-web"/>
    <!-- 格式化输出  -->
    <property name="LOG_PATTERN" value="[%d{yyyy-MM-dd HH:mm:ss.SSS}] [%5level] [%thread] %logger{50} : %msg%n" />
    <property name="CHARSET" value="UTF-8"/>

    <contextName>${APP_NAME}</contextName>

    <!-- 负责写日志,控制台日志 -->
    <appender name="STDOUT" class="ch.qos.logback.core.ConsoleAppender">

        <!-- 一是把日志信息转换成字节数组,二是把字节数组写入到输出流 -->
        <encoder>
            <Pattern>${LOG_PATTERN}</Pattern>
            <charset>${CHARSET}</charset>
        </encoder>
    </appender>

    <!-- 文件日志 -->
    <appender name="DEBUG" class="ch.qos.logback.core.FileAppender">
        <file>${LOG_PATH}/logs/debug.log</file>
        <!-- append: true,日志被追加到文件结尾; false,清空现存文件;默认是true -->
        <append>true</append>

        <filter class="ch.qos.logback.classic.filter.LevelFilter">
            <!-- LevelFilter: 级别过滤器，根据日志级别进行过滤 -->
            <level>DEBUG</level>
            <onMatch>ACCEPT</onMatch>
            <onMismatch>DENY</onMismatch>
        </filter>

        <encoder>
            <Pattern>${LOG_PATTERN}</Pattern>
            <charset>${CHARSET}</charset>
        </encoder>
    </appender>

    <!-- 滚动记录文件，先将日志记录到指定文件，当符合某个条件时，将日志记录到其他文件 -->
    <appender name="INFO" class="ch.qos.logback.core.rolling.RollingFileAppender">
        <file>${LOG_PATH}/logs/info.log</file>
        <append>true</append>
        <!-- ThresholdFilter:临界值过滤器，过滤掉 TRACE 和 DEBUG 级别的日志 -->
        <filter class="ch.qos.logback.classic.filter.ThresholdFilter">
            <level>INFO</level>
        </filter>

        <encoder>
            <Pattern>${LOG_PATTERN}</Pattern>
            <charset>${CHARSET}</charset>
        </encoder>

        <rollingPolicy class="ch.qos.logback.core.rolling.SizeAndTimeBasedRollingPolicy">
            <!-- 每天生成一个日志文件，保存30天的日志文件，单文件最大1MB，文件总大小1GB -->
            <fileNamePattern>${LOG_PATH}/logs/info.%d{yyyy-MM-dd_HH.mm.ss}_%i.log</fileNamePattern>
            <maxHistory>30</maxHistory>
            <maxFileSize>1MB</maxFileSize>
            <totalSizeCap>1GB</totalSizeCap>
        </rollingPolicy>
    </appender>

    <!-- 错误日志输出 -->
    <appender name="ERROR" class="ch.qos.logback.core.rolling.RollingFileAppender">
        <file>${LOG_PATH}/logs/error.log</file>

        <filter class="ch.qos.logback.classic.filter.ThresholdFilter">
            <level>ERROR</level>
        </filter>

        <encoder>
            <Pattern>${LOG_PATTERN}</Pattern>
            <charset>${CHARSET}</charset>
        </encoder>

        <rollingPolicy class="ch.qos.logback.core.rolling.SizeAndTimeBasedRollingPolicy">
            <!-- 每天生成一个日志文件，保存30天的日志文件，单文件最大1MB，文件总大小100M -->
            <fileNamePattern>${LOG_PATH}/logs/error.%d{yyyy-MM-dd_HH.mm.ss}_%i.log</fileNamePattern>
            <maxHistory>30</maxHistory>
            <maxFileSize>1MB</maxFileSize>
            <totalSizeCap>100MB</totalSizeCap>
        </rollingPolicy>
    </appender>

    <!-- 异步输出 -->
    <appender name="ASYNC" class="ch.qos.logback.classic.AsyncAppender">
        <!-- 不丢失日志.默认的,如果队列的80%已满,则会丢弃TRACT、DEBUG、INFO级别的日志 -->
        <discardingThreshold>0</discardingThreshold>
        <!-- 更改默认的队列的深度,该值会影响性能.默认值为256 -->
        <queueSize>512</queueSize>
        <!-- 添加附加的appender,最多只能添加一个 -->
        <appender-ref ref="ERROR"/>
    </appender>

    <!--
    - 1.name：包名或类名，用来指定受此logger约束的某一个包或者具体的某一个类
    - 2.未设置打印级别，所以继承他的上级<root>的日志级别“DEBUG”
    - 3.未设置additivity，默认为true，将此logger的打印信息向上级传递；
    - 4.未设置appender，此logger本身不打印任何信息，级别为“DEBUG”及大于“DEBUG”的日志信息传递给root，
    -  root接到下级传递的信息，交给已经配置好的名为“STDOUT”的appender处理，“STDOUT”appender将信息打印到控制台；
    -->
    <logger name="ch.qos.logback"/>

    <!--
    - 1.将级别为“INFO”及大于“INFO”的日志信息交给此logger指定的名为“STDOUT”的appender处理，在控制台中打出日志，
    -   不再向次logger的上级 <logger name="logback"/> 传递打印信息
    - 2.level：设置打印级别（TRACE, DEBUG, INFO, WARN, ERROR, ALL 和 OFF），还有一个特殊值INHERITED或者同义词NULL，代表强制执行上级的级别。
    -        如果未设置此属性，那么当前logger将会继承上级的级别。
    - 3.additivity：为false，表示此logger的打印信息不再向上级传递,如果设置为true，会打印两次
    - 4.appender-ref：指定了名字为"STDOUT"的appender。
    -->
    <logger name="com.jeanboy.web" level="INFO" additivity="false">
        <appender-ref ref="STDOUT"/>
        <appender-ref ref="DEBUG"/>
        <appender-ref ref="INFO"/>
        <appender-ref ref="ERROR"/>
        <appender-ref ref="ASYNC"/>
    </logger>

    <!--
    - 根logger
    - level:设置打印级别，大小写无关：TRACE, DEBUG, INFO, WARN, ERROR, ALL 和 OFF，不能设置为INHERITED或者同义词NULL。
    -       默认是DEBUG。
    -appender-ref:可以包含零个或多个<appender-ref>元素，标识这个appender将会添加到这个logger
    -->
    <root level="DEBUG">
        <appender-ref ref="STDOUT"/>
        <appender-ref ref="DEBUG"/>
        <appender-ref ref="INFO"/>
        <appender-ref ref="ERROR"/>
        <appender-ref ref="ASYNC"/>
    </root>
</configuration>
```


