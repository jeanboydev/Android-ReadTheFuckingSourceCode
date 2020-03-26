# 代理模式

代理模式是一种设计模式，提供了对目标对象额外的访问方式，即通过代理对象访问目标对象，这样可以在不修改原目标对象的前提下，提供额外的功能操作，扩展目标对象的功能。

简言之，代理模式就是设置一个中间代理来控制访问原目标对象，以达到增强原对象的功能和简化访问方式。

- 代理模式 UML 类图

![代理模式UML类图](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/plugin/01.png)

## 静态代理

由程序员创建或工具生成代理类的源码，再编译代理类。所谓静态也就是在程序运行前就已经存在代理类的字节码文件，代理类和委托类的关系在运行前就确定了。

- UserService

```java
public interface UserService {
  void select();
  void update();
}
```

- UserServiceImpl

```java
public class UserServiceImpl implements UserService {
  @Override
  public void select() {
    System.out.println("查询");
  }

  @Override
  public void update() {
    System.out.println("更新");
  }
}
```

- UserServiceProxy

```java
public class UserServiceProxy implements UserService {

  private final UserService target; // 被代理对象

  public UserServiceProxy(UserService target) {
    this.target = target;
  }

  @Override
  public void select() {
    before();
    target.select();
    after();
  }

  @Override
  public void update() {
    before();
    target.update();
    after();
  }

  private void before(){
    System.out.println("静态代理-----方法执行前");
  }

  private void after(){
    System.out.println("静态代理-----方法执行后");
  }
}
```

- 测试

```java
UserService userService = new UserServiceImpl();
UserServiceProxy userServiceProxy = new UserServiceProxy(userService);
userServiceProxy.select();
```

## 动态代理

动态代理的源码是在程序运行期间由 JVM 根据反射等机制动态的生成，所以在运行前并不存在代理类的字节码文件。

- ProxyHandler

```java
public class ProxyHandler implements InvocationHandler {

  private final Object target; // 被代理对象

  public ProxyHandler(Object target) {
    this.target = target;
  }

  @Override
  public Object invoke(Object proxy, Method method, Object[] args) 
    throws Throwable {
    before();
    // 调用 target 的 method 方法
    Object result = method.invoke(target, args);
    after();
    return result;
  }

  private void before() {
    System.out.println("动态代理-----方法执行前");
  }

  private void after() {
    System.out.println("动态代理-----方法执行后");
  }
}
```

- 测试

```java
UserService userService = new UserServiceImpl();
ClassLoader classLoader = userService.getClass().getClassLoader();
Class<?>[] interfaces = userService.getClass().getInterfaces();
ProxyHandler proxyHandler = new ProxyHandler(userService);
UserService proxy = (UserService) Proxy.newProxyInstance(classLoader, interfaces, proxyHandler);
proxy.select();
```

### InvocationHandler

可以看到 Proxy.newProxyInstance() 是动态代理的核心方法。

```java
public static Object newProxyInstance(ClassLoader loader,
                                      Class<?>[] interfaces,
                                      InvocationHandler h)
  throws IllegalArgumentException
{
  // 要求 h 非空，否则抛出空指针异常
  Objects.requireNonNull(h);
	// 克隆一份代理目标类所实现的所有接口的 class 对象数组
  final Class<?>[] intfs = interfaces.clone();
  // 拿到代理类的 class 对象
  Class<?> cl = getProxyClass0(loader, intfs);
  
  try {
    // 拿到代理类的构造方法
    final Constructor<?> cons = cl.getConstructor(constructorParams);
    final InvocationHandler ih = h;
    // 访问修饰符
    if (!Modifier.isPublic(cl.getModifiers())) {
      cons.setAccessible(true);
    }
    // 返回构造的代理对象
    return cons.newInstance(new Object[]{h});
  } catch (IllegalAccessException|InstantiationException e) {
    // ...
  }
}
```

先看看这三个参数：

- loader

ClassLoader 是一个抽象类，作用是将字节码文件加载进虚拟机并生成相应的 class（注意是小写的），这里得到的 loader 是其子类 AppClassLoader（负责加载应用层字节码）的一个实例。

- interfaces

interfaces 就是被实现的那些业务接口。

- h

h 是 InvocationHandler 接口的实例，具体代理操作就被放在这个 InvocationHandler 的 invoke 函数中。

接下来看看生成业务代理类的 getProxyClass0() 的实现：

```java
private static Class<?> getProxyClass0(ClassLoader loader,
                                       Class<?>... interfaces) {
  if (interfaces.length > 65535) {
    throw new IllegalArgumentException("interface limit exceeded");
  }
  // 如果缓存中有代理类了直接返回，否则将由代理类工厂 ProxyClassFactory 创建代理类
  return proxyClassCache.get(loader, interfaces);
}
```

点击 get() 方法来看下怎么生成的代理类：

```java
public V get(K key, P parameter) {
  // 要求 parameter 非空，否则抛出空指针异常
  Objects.requireNonNull(parameter);
  // 清除已经被GC回收的弱引用
  expungeStaleEntries();
  // 将 ClassLoader 包装成 CacheKey，作为一级缓存的 key
  Object cacheKey = CacheKey.valueOf(key, refQueue);
  // 获取得到二级缓存
  ConcurrentMap<Object, Supplier<V>> valuesMap = map.get(cacheKey);
  if (valuesMap == null) {
    ConcurrentMap<Object, Supplier<V>> oldValuesMap
      = map.putIfAbsent(cacheKey,
                        valuesMap = new ConcurrentHashMap<>());
    if (oldValuesMap != null) {
      valuesMap = oldValuesMap;
    }
  }
	// 根据代理类实现的接口数组来生成二级缓存 key
  Object subKey = Objects.requireNonNull(subKeyFactory.apply(key, parameter));
  // 通过 subKey 获取二级缓存值
  Supplier<V> supplier = valuesMap.get(subKey);
  Factory factory = null;

  while (true) {
    if (supplier != null) {
      // 在这里 supplier 可能是一个 Factory 也可能会是一个 CacheValue
			// 在这里不作判断，而是 在Supplier 实现类的 get 方法里面进行验证
      V value = supplier.get();
      if (value != null) {
        return value;
      }
    }
    if (factory == null) {
      // 新建一个 Factory 实例作为 subKey 对应的值
      factory = new Factory(key, parameter, subKey, valuesMap);
    }

    if (supplier == null) {
      supplier = valuesMap.putIfAbsent(subKey, factory);
      if (supplier == null) {
        // 到这里表明成功将 factory 放入缓存
        supplier = factory;
      }
    } else {
      if (valuesMap.replace(subKey, supplier, factory)) {
        // 成功将 factory 替换成新的值
        supplier = factory;
      } else {
        // 替换失败, 继续使用原先的值
        supplier = valuesMap.get(subKey);
      }
    }
  }
}
```

可以看到 subKeyFactory.apply(key, parameter)，具体实现在 ProxyClassFactory 中。

```java
private static final class ProxyClassFactory implements BiFunction<ClassLoader, Class<?>[], Class<?>> {
  // 统一代理类的前缀名都以 $Proxy
  private static final String proxyClassNamePrefix = "$Proxy";
  // 使用唯一的编号给作为代理类名的一部分，如 $Proxy0，$Proxy1 等
  private static final AtomicLong nextUniqueNumber = new AtomicLong();

  private ProxyClassFactory() { }

  public Class<?> apply(ClassLoader var1, Class<?>[] var2) {
    IdentityHashMap var3 = new IdentityHashMap(var2.length);
    Class[] var4 = var2;
    int var5 = var2.length;

    for(int var6 = 0; var6 < var5; ++var6) {
      Class var7 = var4[var6];
      Class var8 = null;

      try {
        var8 = Class.forName(var7.getName(), false, var1);
      } catch (ClassNotFoundException var15) {
      }

      if (var8 != var7) {
        throw new IllegalArgumentException(var7 + " is not visible from class loader");
      }

      if (!var8.isInterface()) {
        throw new IllegalArgumentException(var8.getName() + " is not an interface");
      }

      if (var3.put(var8, Boolean.TRUE) != null) {
        throw new IllegalArgumentException("repeated interface: " + var8.getName());
      }
    }

    String var16 = null;
    byte var17 = 17;
    Class[] var18 = var2;
    int var20 = var2.length;

    for(int var21 = 0; var21 < var20; ++var21) {
      Class var9 = var18[var21];
      int var10 = var9.getModifiers();
      if (!Modifier.isPublic(var10)) {
        var17 = 16;
        String var11 = var9.getName();
        int var12 = var11.lastIndexOf(46);
        String var13 = var12 == -1 ? "" : var11.substring(0, var12 + 1);
        if (var16 == null) {
          var16 = var13;
        } else if (!var13.equals(var16)) {
          throw new IllegalArgumentException("non-public interfaces from different packages");
        }
      }
    }

    if (var16 == null) {
      var16 = "com.sun.proxy.";
    }

    long var19 = nextUniqueNumber.getAndIncrement();
    String var23 = var16 + "$Proxy" + var19;
    // 生成类字节码的方法
    byte[] var22 = ProxyGenerator.generateProxyClass(var23, var2, var17);

    try {
      return Proxy.defineClass0(var1, var23, var22, 0, var22.length);
    } catch (ClassFormatError var14) {
      throw new IllegalArgumentException(var14.toString());
    }
  }
}
```

可以看到，代理类创建真正在 ProxyGenerator.generateProxyClass() 方法中。

```java
public static byte[] generateProxyClass(final String var0, Class<?>[] var1, int var2) {
  ProxyGenerator var3 = new ProxyGenerator(var0, var1, var2);
  // 生成 class 文件
  final byte[] var4 = var3.generateClassFile();
  if (saveGeneratedFiles) {
    AccessController.doPrivileged(new PrivilegedAction<Void>() {
      public Void run() {
        try {
          int var1 = var0.lastIndexOf(46);
          Path var2;
          if (var1 > 0) {
            Path var3 = Paths.get(var0.substring(0, var1).replace('.', File.separatorChar));
            Files.createDirectories(var3);
            var2 = var3.resolve(var0.substring(var1 + 1, var0.length()) + ".class");
          } else {
            var2 = Paths.get(var0 + ".class");
          }

          Files.write(var2, var4, new OpenOption[0]);
          return null;
        } catch (IOException var4x) {
          throw new InternalError("I/O exception saving generated file: " + var4x);
        }
      }
    });
  }

  return var4;
}
```

代理类生成的最终方法是 ProxyGenerator.generateClassFile()。

```java
private byte[] generateClassFile() {
  // 添加代理方法
  this.addProxyMethod(hashCodeMethod, Object.class);
  this.addProxyMethod(equalsMethod, Object.class);
  this.addProxyMethod(toStringMethod, Object.class);
  Class[] var1 = this.interfaces;
  int var2 = var1.length;

  int var3;
  Class var4;
  for(var3 = 0; var3 < var2; ++var3) {
    var4 = var1[var3];
    Method[] var5 = var4.getMethods();
    int var6 = var5.length;

    for(int var7 = 0; var7 < var6; ++var7) {
      Method var8 = var5[var7];
      this.addProxyMethod(var8, var4);
    }
  }

  Iterator var11 = this.proxyMethods.values().iterator();

  List var12;
  while(var11.hasNext()) {
    var12 = (List)var11.next();
    checkReturnTypes(var12);
  }

  Iterator var15;
  try {
    this.methods.add(this.generateConstructor());
    var11 = this.proxyMethods.values().iterator();

    while(var11.hasNext()) {
      var12 = (List)var11.next();
      var15 = var12.iterator();

      while(var15.hasNext()) {
        ProxyGenerator.ProxyMethod var16 = (ProxyGenerator.ProxyMethod)var15.next();
        this.fields.add(new ProxyGenerator.FieldInfo(var16.methodFieldName, "Ljava/lang/reflect/Method;", 10));
        this.methods.add(var16.generateMethod());
      }
    }

    this.methods.add(this.generateStaticInitializer());
  } catch (IOException var10) {
    throw new InternalError("unexpected I/O Exception", var10);
  }

  if (this.methods.size() > 65535) {
    throw new IllegalArgumentException("method limit exceeded");
  } else if (this.fields.size() > 65535) {
    throw new IllegalArgumentException("field limit exceeded");
  } else {
    this.cp.getClass(dotToSlash(this.className));
    this.cp.getClass("java/lang/reflect/Proxy");
    var1 = this.interfaces;
    var2 = var1.length;

    for(var3 = 0; var3 < var2; ++var3) {
      var4 = var1[var3];
      this.cp.getClass(dotToSlash(var4.getName()));
    }

    this.cp.setReadOnly();
    ByteArrayOutputStream var13 = new ByteArrayOutputStream();
    DataOutputStream var14 = new DataOutputStream(var13);

    try {
      var14.writeInt(-889275714);
      var14.writeShort(0);
      var14.writeShort(49);
      this.cp.write(var14);
      var14.writeShort(this.accessFlags);
      var14.writeShort(this.cp.getClass(dotToSlash(this.className)));
      var14.writeShort(this.cp.getClass("java/lang/reflect/Proxy"));
      var14.writeShort(this.interfaces.length);
      Class[] var17 = this.interfaces;
      int var18 = var17.length;

      for(int var19 = 0; var19 < var18; ++var19) {
        Class var22 = var17[var19];
        var14.writeShort(this.cp.getClass(dotToSlash(var22.getName())));
      }

      var14.writeShort(this.fields.size());
      var15 = this.fields.iterator();

      while(var15.hasNext()) {
        ProxyGenerator.FieldInfo var20 = (ProxyGenerator.FieldInfo)var15.next();
        var20.write(var14);
      }

      var14.writeShort(this.methods.size());
      var15 = this.methods.iterator();

      while(var15.hasNext()) {
        ProxyGenerator.MethodInfo var21 = (ProxyGenerator.MethodInfo)var15.next();
        var21.write(var14);
      }

      var14.writeShort(0);
      return var13.toByteArray();
    } catch (IOException var9) {
      throw new InternalError("unexpected I/O Exception", var9);
    }
  }
}
```

通过 addProxyMethod() 添加 hashcode、equals、toString 方法。

```java
private void addProxyMethod(Method var1, Class<?> var2) {
  String var3 = var1.getName();
  Class[] var4 = var1.getParameterTypes();
  Class var5 = var1.getReturnType();
  Class[] var6 = var1.getExceptionTypes();
  String var7 = var3 + getParameterDescriptors(var4);
  Object var8 = (List)this.proxyMethods.get(var7);
  if (var8 != null) {
    Iterator var9 = ((List)var8).iterator();

    while(var9.hasNext()) {
      ProxyGenerator.ProxyMethod var10 = (ProxyGenerator.ProxyMethod)var9.next();
      if (var5 == var10.returnType) {
        ArrayList var11 = new ArrayList();
        collectCompatibleTypes(var6, var10.exceptionTypes, var11);
        collectCompatibleTypes(var10.exceptionTypes, var6, var11);
        var10.exceptionTypes = new Class[var11.size()];
        var10.exceptionTypes = (Class[])var11.toArray(var10.exceptionTypes);
        return;
      }
    }
  } else {
    var8 = new ArrayList(3);
    this.proxyMethods.put(var7, var8);
  }

  ((List)var8).add(new ProxyGenerator.ProxyMethod(var3, var4, var5, var6, var2));
}
```

### $Proxy0

最终生成的代理类 $Proxy0 反编译如下：

```java
public final class $Proxy0 extends Proxy implements UserService {
  private static Method m1;
  private static Method m2;
  private static Method m3;
  private static Method m4;
  private static Method m0;

  public $Proxy0(InvocationHandler var1) throws  {
    super(var1);
  }

  public final boolean equals(Object var1) throws  {
    try {
      return ((Boolean)super.h.invoke(this, m1, new Object[]{var1})).booleanValue();
    } catch (RuntimeException | Error var3) {
      throw var3;
    } catch (Throwable var4) {
      throw new UndeclaredThrowableException(var4);
    }
  }

  public final String toString() throws  {
    try {
      return (String)super.h.invoke(this, m2, (Object[])null);
    } catch (RuntimeException | Error var2) {
      throw var2;
    } catch (Throwable var3) {
      throw new UndeclaredThrowableException(var3);
    }
  }

  public final void update() throws  {
    try {
      super.h.invoke(this, m3, (Object[])null);
    } catch (RuntimeException | Error var2) {
      throw var2;
    } catch (Throwable var3) {
      throw new UndeclaredThrowableException(var3);
    }
  }

  public final void select() throws  {
    try {
      super.h.invoke(this, m4, (Object[])null);
    } catch (RuntimeException | Error var2) {
      throw var2;
    } catch (Throwable var3) {
      throw new UndeclaredThrowableException(var3);
    }
  }

  public final int hashCode() throws  {
    try {
      return ((Integer)super.h.invoke(this, m0, (Object[])null)).intValue();
    } catch (RuntimeException | Error var2) {
      throw var2;
    } catch (Throwable var3) {
      throw new UndeclaredThrowableException(var3);
    }
  }

  static {
    try {
      m1 = Class.forName("java.lang.Object").getMethod("equals", new Class[]{Class.forName("java.lang.Object")});
      m2 = Class.forName("java.lang.Object").getMethod("toString", new Class[0]);
      m3 = Class.forName("com.jeanboy.proxy.UserService").getMethod("update", new Class[0]);
      m4 = Class.forName("com.jeanboy.proxy.UserService").getMethod("select", new Class[0]);
      m0 = Class.forName("java.lang.Object").getMethod("hashCode", new Class[0]);
    } catch (NoSuchMethodException var2) {
      throw new NoSuchMethodError(var2.getMessage());
    } catch (ClassNotFoundException var3) {
      throw new NoClassDefFoundError(var3.getMessage());
    }
  }
}
```

当我们将业务接口 UserService 和业务代理操作类 ProxyHandler 传入 Proxy 中后，Proxy 会为我们生成一个实现了 UserService 接口并继承了 Proxy 的业务代理类 $Proxy0。

在我们具体调用方法 proxy.select() 时它其实是调用了 \$Proxy0 中的 select() 方法，然后再调用 Proxy 类的 invoke 方法，所以 ProxyHandler 中的 invoke 方法才是最终执行的方法，这个方法给了我们扩展的可能并且最终我们实现了代理对象访问原对象的目的，也就是 $Proxy0 代理了 UserServiceImpl。

## 参考资料

- [Java动态代理实现及原理分析](https://www.jianshu.com/p/23d3f1a2b3c7)
- [JDK动态代理实现原理(jdk8)](https://blog.csdn.net/yhl_jxy/article/details/80586785)