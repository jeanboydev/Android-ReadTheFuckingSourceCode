# Chain of Responsibility（责任链模式） #
## 概述 ##
顾名思义，责任链模式（Chain of Responsibility Pattern）为请求创建了一个接收者对象的链。这种模式给予请求的类型，对请求的发送者和接收者进行解耦。这种类型的设计模式属于行为型模式。

在这种模式中，通常每个接收者都包含对另一个接收者的引用。如果一个对象不能处理该请求，那么它会把相同的请求传给下一个接收者，依此类推。

## 使用 ##
### 示例 ###
继续回到我们的辣条工厂，随着辣条生意越做越大，来的客户也越来越多。 
有一天张三来到我们工厂找到业务员说，我要进5w的货。 业务员一想，在我的批准范围之内，准了。
第二天李四来到我们工厂找到业务员说，我要进10w的货。 业务员一想，超出我的批准范围了，我得请示下上级。 上级一想，在我的批准范围之内，准了。
...

### 实现 ###
1. 创建一个订单类，用来存储客户订单信息
```Java
public class Order {
    private double amount;
    private String purpose;

    public Order(double amount, String purpose) {
        this.amount = amount;
        this.purpose = purpose;
    }

    public double getAmount() {
        return amount;
    }

    public void setAmount(double amount) {
        this.amount = amount;
    }

    public String getPurpose() {
        return purpose;
    }

    public void setPurpose(String purpose) {
        this.purpose = purpose;
    }

    @Override
    public String toString() {
        return "Order{" +
                "amount=" + amount +
                ", purpose='" + purpose + '\'' +
                '}';
    }
}
```
2. 创建一个人物类，分别实现各级员工
```Java
public abstract class Person {

    private Order order;

    private Person superior;

    public Order getOrder() {
        return order;
    }

    public void setOrder(Order order) {
        this.order = order;
    }

    public Person getSuperior() {
        return superior;
    }

    public void setSuperior(Person superior) {
        this.superior = superior;
    }

    public abstract void handle();
}
```
```Java
public class CEO extends Person {

    private final static double MAX_AMOUNT = 100;

    @Override
    public void handle() {
        if (getOrder().getAmount() > MAX_AMOUNT) {
            System.out.println("CEO 不批准！订单：" + getOrder().toString());
        } else {
            System.out.println("CEO 批准！订单：" + getOrder().toString());
        }
    }
}
```
```Java
public class Manager extends Person {

    private final static double MAX_AMOUNT = 50;

    @Override
    public void handle() {
        if (getOrder().getAmount() > MAX_AMOUNT) {
            getSuperior().setOrder(getOrder());
            getSuperior().handle();
        } else {
            System.out.println("Manager 批准！金额：" + getOrder().toString());
        }
    }
}
```

```Java
public class Leader extends Person {

    private final static double MAX_AMOUNT = 10;

    @Override
    public void handle() {
        if (getOrder().getAmount() > MAX_AMOUNT) {
            getSuperior().setOrder(getOrder());
            getSuperior().handle();
        } else {
            System.out.println("Leader 批准！订单：" + getOrder().toString());
        }
    }
}
```

```Java
public class Employee extends Person {

    private final static double MAX_AMOUNT = 5;

    @Override
    public void handle() {
        if (getOrder().getAmount() > MAX_AMOUNT) {
            getSuperior().setOrder(getOrder());
            getSuperior().handle();
        } else {
            System.out.println("Employee 批准！金额：" + getOrder().toString());
        }
    }
}
```

3. 测试
```Java
public class ChainTest {

    @Test
    public void testChain() {

        CEO ceo = new CEO();//老板
        Manager manager = new Manager();//经理
        Leader leader = new Leader();//小组长
        Employee employee = new Employee();//员工

        //设置上级
        employee.setSuperior(leader);
        leader.setSuperior(manager);
        manager.setSuperior(ceo);

        Order order1 = new Order(5, "进货");
        Order order2 = new Order(10, "进货");
        Order order3 = new Order(100, "控股");
        Order order4 = new Order(200, "收购");
        Order order5 = new Order(50, "开一条生产线");
        employee.setOrder(order1);
        employee.handle();
        employee.setOrder(order2);
        employee.handle();
        employee.setOrder(order3);
        employee.handle();
        employee.setOrder(order4);
        employee.handle();
        employee.setOrder(order5);
        employee.handle();
    }
}
```

4. 输出
```Java
03-22 20:22:29.791 9645-9675/? I/System.out: Employee 批准！金额：Order{amount=5.0, purpose='进货'}
03-22 20:22:29.791 9645-9675/? I/System.out: Leader 批准！订单：Order{amount=10.0, purpose='进货'}
03-22 20:22:29.791 9645-9675/? I/System.out: CEO 批准！订单：Order{amount=100.0, purpose='控股'}
03-22 20:22:29.791 9645-9675/? I/System.out: CEO 不批准！订单：Order{amount=200.0, purpose='收购'}
03-22 20:22:29.791 9645-9675/? I/System.out: Manager 批准！金额：Order{amount=50.0, purpose='开一条生产线'}
```

> 从输出信息可以看出，超出批准范围时会交给上级处理。

## 使用场景 ##
1. 有多个对象可以处理同一个请求，具体哪个对象处理该请求由运行时刻自动确定。
2. 在不明确指定接收者的情况下，向多个对象中的一个提交一个请求。 
3. 可动态指定一组对象处理请求。

## 主要解决 ##
职责链上的处理者负责处理请求，客户只需要将请求发送到职责链上即可，无须关心请求的处理细节和请求的传递，所以职责链将请求的发送者和请求的处理者解耦了。

## 优点 ##
1. 降低耦合度。它将请求的发送者和接收者解耦。 
2. 简化了对象。使得对象不需要知道链的结构。 
3. 增强给对象指派职责的灵活性。通过改变链内的成员或者调动它们的次序，允许动态地新增或者删除责任。 
4. 增加新的请求处理类很方便。

## 缺点 ##
1. 不能保证请求一定被接收。 
2. 系统性能将受到一定影响，而且在进行代码调试时不太方便，可能会造成循环调用。 
3. 可能不容易观察运行时的特征，有碍于除错。

## 注意事项 ##
在 JAVA WEB 中遇到很多应用。