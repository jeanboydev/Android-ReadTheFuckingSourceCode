# Singleton（单例模式） #
## 概述 ##
Singleton（单例模式）是一种常用的设计模式。在Java应用中，单例对象能保证在一个JVM中，该对象只有一个实例存在。 

优点：
1. 由于只有一个实例，故可以减少内存开销。
2. 可以避免对资源的多重占用，避免对同一资源进行多种操作。
3. 设置了全局的资源访问，可以优化和共享全局资源访问。

缺点：
1. 由于单例模式中没有抽象层，因此单例类的扩展有很大的困难。
2. 单例类的职责过重，在一定程度上违背了“单一职责原则”。
3. 如果单例对象长时间不被利用，系统会认为是垃圾，会自动销毁并回收资源，下次利用时又将重新实例化，这将导致共享的单例对象状态的丢失。

## 常用方式 ##
#### 一、懒汉式 ####
```Java
public class Singleton {  
    private static Singleton instance = null;  
    private Singleton() {  

    }    

    public static Singleton getInstance() {  
        if (instance == null) {  
            instance = new Singleton();  
          }  
        return instance;  
    }  
}
```
> 优点：在需要的时候才去加载
> 
> 缺点：在多线程的环境下，会出现线性不安全的情况

#### 二、加锁方式 ####
```Java
public static synchronized Singleton getInstance() {  
     if (instance == null) {  
         instance = new Singleton();  
     }  
     return instance;  
}
```
> 优点：解决了线性同步问题
> 
> 缺点：每次调用都要判断同步锁，导致效率低

#### 三、加双重锁 ####
```Java
public static synchronized Singleton getInstance(){
    if(instance == null){
        synchronized(Object){
            if(instance == null){
                instance = new Singleton();
            }
        }
    }
}
```
> 在JVM编译的过程中会出现指令重排的优化过程，这就会导致当 instance 实际上还没初始化，就可能被分配了内存空间，也就是说会出现 instance !=null 但是又没初始化的情况，这样就会导致返回的 instance报错。在 JDK1.5 之后，官方已经注意到这种问题，因此调整了 JMM、 具体化了 volatile 关键字，因此如果是 JDK1.5 或之后的版本，只需要将instance的定义改成 “private volatile static SingletonKerriganD instance = null;” 就可以保证每次都去 instance 都从主内存读取，就可以使用DCL的写法来完成单例模式。当然 volatile 或多或少也会影响到性能。
> 
> 优点：在并发量不高、安全性不高的情况下可以很好的运行
> 
> 缺点：在不同的编译环境下可能出现不同的问题

#### 四、内部类 ####
```Java
public class SingletonInner {  

    /** 
     * 私有的构造器
     */  
    private SingletonInner() {  

    } 

    /** 
     * 内部类实现单例模式 
     * 延迟加载，减少内存开销 
     *  
     */  
    private static class SingletonHolder {  
        private static SingletonInner instance = new SingletonInner();  
    }  

    public static SingletonInner getInstance() {  
        return SingletonHolder.instance;  
    }  

    protected void method() {  
        System.out.println("ibinbin");  
    }  
}
```
> 优点：延迟加载、线性安全、减少内存消耗


