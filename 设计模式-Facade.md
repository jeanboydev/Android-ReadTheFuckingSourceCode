# Facade（外观模式） #
## 概述 ##
外观模式（Facade Pattern）隐藏系统的复杂性，并向客户端提供了一个客户端可以访问系统的接口。 这种类型的设计模式属于结构型模式，它向现有的系统添加一个接口，来隐藏系统的复杂性。

这种模式涉及到一个单一的类，该类提供了客户端请求的简化方法和对现有系统类方法的委托调用。

## 使用 ##
### 示例 ###
模拟电脑开机关机过程。

### 实现 ###
1. 创建CPU
```Java
public class CPU {

    public void startup(){
        System.out.println("cpu startup!");
    }

    public void shutdown(){
        System.out.println("cpu shutdown!");
    }
}
```
2. 创建内存
```Java
public class Memory {

    public void startup(){
        System.out.println("memory startup!");
    }

    public void shutdown(){
        System.out.println("memory shutdown!");
    }
}
```
3. 创建硬盘
```Java
public class Disk {

    public void startup(){
        System.out.println("disk startup!");
    }

    public void shutdown(){
        System.out.println("disk shutdown!");
    }
}
```
5. 创建电脑
```Java
public class Computer {

    private CPU cpu;
    private Memory memory;
    private Disk disk;

    public Computer() {
        cpu = new CPU();
        memory = new Memory();
        disk = new Disk();
    }

    public void startup() {
        System.out.println("start the computer!");
        cpu.startup();
        memory.startup();
        disk.startup();
        System.out.println("start computer finished!");
    }

    public void shutdown() {
        System.out.println("begin to close the computer!");
        cpu.shutdown();
        memory.shutdown();
        disk.shutdown();
        System.out.println("computer closed!");
    }
}
```
4. 测试
```Java
public class FacadeTest {

    @Test
    public void testFacade() {

        Computer computer = new Computer();
        computer.startup();
        computer.shutdown();
    }
}
```

> 可以看出，通过外观模式，用户只需要知道开机关机操作即可，至于CPU，内存，硬盘是怎么工作的并不需要知道。

## 使用场景 ##
1. 为复杂的模块或子系统提供外界访问的模块。
2. 子系统相对独立。
3. 预防低水平人员带来的风险。

## 优点 ##
1. 减少系统相互依赖。
2. 提高灵活性。
3. 提高了安全性。

## 缺点 ##
不符合开闭原则，如果要改东西很麻烦，继承重写都不合适。

## 注意事项 ##
在层次化结构中，可以使用外观模式定义系统中每一层的入口。