# Command（命令模式） #
## 概述 ##
命令模式（Command Pattern）是一种数据驱动的设计模式，它属于行为型模式。 请求以命令的形式包裹在对象中，并传给调用对象。 调用对象寻找可以处理该命令的合适的对象，并把该命令传给相应的对象，该对象执行命令。

## 使用 ##
### 示例 ###
我们来模拟一下辣条厂中，小组长命令员工去工作的场景。

### 实现 ###
1. 创建一个命令处理接口
```Java
public interface Receiver {

    void action(String desc);
}
```
2. 员工实现接口处理命令
```Java
public class Employee implements Receiver {

    @Override
    public void action(String desc) {
        System.out.println("Employee 执行命令:" + desc);
    }
}
```
3. 创建命令接口
```Java
public interface Command {
    
    void execute(String desc);
}
```
```Java
public class WorkCommand implements Command {

    private Receiver receiver;

    public WorkCommand(Receiver receiver) {
        this.receiver = receiver;
    }

    @Override
    public void execute(String desc) {
        receiver.action(desc);
    }
}
```
4. 创建发送命令的小组长
```Java
public class Leader implements Receiver {

    private Command command;

    public Leader(Command command) {
        this.command = command;
    }

    @Override
    public void action(String desc) {
        command.execute(desc);
    }
}
```

5. 测试
```Java
public class CommandTest {

    @Test
    public void testCommand() {
        Receiver receiver = new Employee();//创建命令接受者
        Command command = new WorkCommand(receiver);//创建命令
        Leader leader = new Leader(command);//创建命令发送者
        leader.action("去工作");//发送命令
    }
}
```

4. 输出
```Java
03-23 11:53:42.221 31493-31521/? I/System.out: Employee 执行命令:去工作
```

> 从输出信息可以看出，最后员工执行了命令去工作了。

## 使用场景 ##
认为是命令的地方都可以使用命令模式，比如： 1. GUI 中每一个按钮都是一条命令。 2. 模拟 CMD。

## 主要解决 ##
在软件系统中，行为请求者与行为实现者通常是一种紧耦合的关系，但某些场合，比如需要对行为进行记录、撤销或重做、事务等处理时，这种无法抵御变化的紧耦合的设计就不太合适。

## 优点 ##
1. 降低了系统耦合度。
2. 新的命令可以很容易添加到系统中去。 

## 缺点 ##
使用命令模式可能会导致某些系统有过多的具体命令类。

## 注意事项 ##
系统需要支持命令的撤销(Undo)操作和恢复(Redo)操作，也可以考虑使用命令模式。