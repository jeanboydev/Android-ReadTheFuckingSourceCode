# Dagger 2

## 准备

- 控制反转

IoC（Inversion of Control），它把传统上由程序代码直接操控的对象的调用权交给容器，通过容器来实现对象组件的装配和管理。所谓的“控制反转”概念就是对组件对象控制权的转移，从程序代码本身转移到了外部容器。

- 依赖注入

DI（Dependency Injection），依赖注入和控制反转是同一个概念。把直接操控的对象的调用权交给容器，通过容器来实现对象组件的装配和管理，称为控制反转；通过容器创建对象，然后注入调用者，因此也称为依赖注入。

## @Inject

- 注解构造函数

通过注解标记构造函数，告诉 Dagger 2 在需要使用这个类时可以通过构造函数来创建。

- 注解依赖变量

通过标记变量，告诉 Dagger 2 在哪里需要使用被注解标记构造函数的对象，也就是需要注入的位置。

```Java
public class UserBean {
    private String name;
    
    @Inject
    public UserBean() {//注解构造函数，提供依赖对象
        this.name = "张三";
    }
}

public class MainActivity extends Activity {
    @Inject
    UserBean userBean;//注入依赖对象
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
    }
}
```

这样我们就可以让目标类中所依赖的其他类与其他类的构造函数之间有了一种无形的联系。但是要想使它们之间产生直接的关系，还得需要一个桥梁来把它们之间连接起来。那这个桥梁就是 Component。

## @Component

```Java
//modules 表示 Component 从哪些 Module 中查找依赖
@Component(modules = ActivityModule.class)
public interface ActivityComponent {
    
    void inject(MainActivity activity);
}
```

编译时，被 @Component 注解的接口在编译时会产生相应的实例，名称一般以 Dagger 为前缀。比如，接口名称为 ActivityComponent，那么编译时生成的实例名称为 DaggerActivityComponent。

```Java
public class MainActivity extends Activity {
    
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        DaggerActivityComponent.builder()
            .activityModule(new ActivityModule(this))//创建 Module
            .build().inject(this);//将 Module 中提供的对象注入
    }
}
```
Component 注入规则是：

- 步骤 1：查找 Module 中是否存在创建该类的方法
- 步骤 2：若存在创建类方法，查看该方法是否存在参数

1. 步骤 2.1：若存在参数，则按从步骤 1 开始依次初始化每个参数
2. 步骤 2.2：若不存在参数，则直接初始化该类实例，一次依赖注入到此结束

- 步骤 3：若不存在创建类方法，则查找 Inject 注解的构造函数，看构造函数是否存在参数

1. 步骤 3.1：若存在参数，则从步骤 1 开始依次初始化每个参数
2. 步骤 3.2：若不存在参数，则直接初始化该类实例，一次依赖注入到此结束

## @Module

之前已经提到了，@Inject 可以提供依赖关系，但是其不是万能的。如果我们所需要的提供的构造函数没有使用 @Inject 注解，比如，第三方库里的类，我们并没有权限修改源码。这时，Module 类可以在不修改源码构造函数的情况下，提供依赖关系。即使是可以用 @Inject 注解的，依然可以通过 Module 提供依赖关系。

```Java
@Module
public class ModuleClass{
    //A 是第三方类库中的一个类
    A provideA(){
       return new A();
    }
}
```

## @Provides

@Provides 可以认为是对 @Inject 的补充。对于 @Inject 不能满足的情况，可以使用 @Provides 注解方法来满足依赖性，该方法的定义返回类型满足了其依赖关系。不管是接口还是第三方库的类，甚至是相关的配置对象，都可以通过 @Provides 方法来提供了，以弥补 @Inject 的盲区。

值得注意的是，@Provides 方法本身是不能独立存在的，它必须依附于一个 Module。

```Java
@Module
public class ActivityModule {

    private final Activity activity;
    // 有参构造函数，表示该 Module 必须初始化
    public ActivityModule(Activity activity) {
        this.activity = activity;
    }

    @Provides
    Activity provideActivity() {
        return this.activity;
    }
}
```

## @Qualifier

当一个类有多个构造方法被 @Inject 注解时，通过 Qualifier 限定符可以来标识不同的构造方法。

- 自定义 @Qualifier

```Java
@Qualifier //限定符
@Documented
@Retention(RetentionPolicy.RUNTIME)
public @interface Type {
    String value() default "";
}
```

- 使用

```Java
public class AppleBean {
    private String name;
    private double price;
    private String color;

    public AppleBean() {
    }

    public AppleBean(String color) {
        this.color = color;
    }

    public AppleBean(String name, double price) {
        this.name = name;
        this.price = price;
    }

    @Override
    public String toString() {
        return "AppleBean{" +
                "name='" + name + '\'' +
                ", price=" + price +
                '}';
    }
}
```

```Java
@Module()
public class FruitModule {

    //使用限定符来区别使用哪个构造函数返回对象
    @Type("color")
    @Provides
    public AppleBean provideColorApple() {
        return new AppleBean("red");
    }

    @Type("name")
    @Provides
    public AppleBean provideNameApple() {
        return new AppleBean("红富士", 6.88);
    }
}
```

## @Scope

@Scope 是 javax.inject 包下的一个注解，其是用来标识范围的注解，该注解适用于注解包含可注入的构造函数的类，并控制该如何重复使用类的实例。

在默认情况下，也就是说仅仅使用 @Inject 注解构造函数，而没有使用 @Scope 注解类时，每次依赖注入都会创建一个实例（通过注入类型的构造函数创建实例）。如果使用了 @Scope 注解了该类，注入器会缓存第一次创建的实例，然后每次重复注入缓存的实例，而不会再创建新的实例。

```Java
@Scope
public class A {
    @Inject
    public A() {
        Log.d("test", "A()");
    }
}

public class B {
    @Inject
    public B() {
        Log.d("test", "B()");
    }
}
```

```Java
@Module
public class TestModule {

    @Provides
    public A providerA() {
        return new A();
    }
    
    @Provides
    public B providerB() {
        return new B();
    }
}

@Scope
@Component(modules = {TestModule})
public interface ActivityComponent {

    void inject(TestActivity activity);
}
```

```Java
public class TestActivity extends AppCompatActivity {

    @Inject
    A a1;
    @Inject
    A a2;

    @Inject
    B b1;
    @Inject
    B b2;

    protected void onCreate(Bundle savedInstanceState) {
        ...

        //  a1:com.jeanboy.bean.A@3d061bc8
        Log.d("test", "a1:" + a1.toString());
        //  a2:com.jeanboy.bean.A@3d061bc8
        Log.d("test", "a2:" + a2.toString());

        //  b1:com.jeanboy.bean.B@19345792
        Log.d("test", "b1:" + b1.toString());
        //  b2:com.jeanboy.bean.B@275e96a1
        Log.d("test", "b2:" + b2.toString());
    }
}
```

我们可以清晰的看出：

1. A 的构造函数被调用了一次，而 B 的构造函数被调用了两次。
2. A 的两个实例的内存地址是一致的，而 B 的两个实例地址是不一致的。

值得注意的是，如果有类注入实例的类被 @Scope 注解，那么其 Component 必须被相同的 Scope 注解。比如，A 被 @Scope 注解，那么 ActivityComponent 也必须被 @Scope 注解。如果ActivityComponent 没有 @Scope 注解，编译时会报错。

## @Singleton

@Singleton 是 @Scope 的一个特例，或者是说是 @Scope 的一种实现方式。

用 @Singleton 注解一个类表明该类的创建采用的是单例模式，其会被多个线程共同使用：

```Java
@Singleton
class A {
  ...
}
```

对于 @Singleton 而言，其并不是严格意义上的单例模式，而是在当前 Component 中，调用构造函数新建实例，然后每次注入实例时，都会读取缓存中的实例。对于其他 Component 而言，是无效的。

## Subcomponent

对于继承，大家应该都不陌生，其实就是子类继承父类，子类自动获取了的父类的属性和行为。我觉得我们也可以这么认为子组件。子组件是继承和扩展父组件的对象的组件。我们可以将应用程序的各个功能分割为模块，以将应用程序的不同部分彼此封装或在组件中使用多个范围。

- 声明子组件

与 @Component 注解不同的是，使用 @Subcomponent 注解子组件，必须声明其 xxComponent.Builder，否则编译时，会报错。

```Java
@Subcomponent(modules = AppleModule.class)
public interface AppleSubcomponent {

    AppleBean supplyApple();

    @Subcomponent.Builder
    interface Builder{
        Builder appleModule(AppleModule module);
        AppleSubcomponent build();
    }
}
```

- 通过 @Component 的 dependencies 属性依赖父组件

```Java
@Module
public class FruitModule {

    @Provides
    public Fruits provideFruit() {
        return new Fruits("这是一个水果");
    }
}

@Component(modules = {FruitModule.class})
public interface FruitComponent {
    // 将 FruitModule 中的 Fruits 暴露出来，以便于其他依赖于 FruitComponent 的 Component 调用
    // 若不将 Fruits 暴露出来，依赖于 FruitComponent 的 Component 无法获取该实例，此时编译会报错，提示为该实例提供 @Inject 注解或者 @Provides 方法
    Fruits supplyFruits();
}
```

```Java
@Module
public class OrangeModule {

    @Provides
    public OrangeBean provideOrange() {
        return new OrangeBean("这是一个橘子");
    }
}

@Component(modules = OrangeModule.class, dependencies = FruitComponent.class)
public interface OrangeComponent {
    void inject(OrangeFragment fragment);
}
```

```Java
public class OrangeFragment extends Fragment {

    @Inject
    OrangeBean mOrangeBean;
    @Inject
    Fruits mFruits;
    
    public OrangeFragment() {}
    
    @Override
    public void onCreate(@Nullable Bundle savedInstanceState) {
        FruitComponent fruitComponent = DaggerFruitComponent.create();
        OrangeComponent orangeComponent = DaggerOrangeComponent.builder()
                .fruitComponent(fruitComponent)
                .build();
        orangeComponent.inject(this);
        super.onCreate(savedInstanceState);
    }
}
```

## Dagger - Android



## 参考资料

- [User's Guide](https://google.github.io/dagger/users-guide)
- [Android：dagger2让你爱不释手-基础依赖注入框架篇](https://www.jianshu.com/p/cd2c1c9f68d4)
- [Android：dagger2让你爱不释手-重点概念讲解、融合篇](https://www.jianshu.com/p/1d42d2e6f4a5)
- [Android：dagger2让你爱不释手-终结篇](https://www.jianshu.com/p/65737ac39c44)
- [New Android Injector with Dagger 2 — part 1](https://medium.com/@iammert/new-android-injector-with-dagger-2-part-1-8baa60152abe)

## 我的公众号

欢迎你「扫一扫」下面的二维码，关注我的公众号，可以接受最新的文章推送，有丰厚的抽奖活动和福利等着你哦！😍

<img src="https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/about_me/qrcode_android_besos_black_512.png" width=250 height=250 />

如果你有什么疑问或者问题，可以 [点击这里](https://github.com/jeanboydev/Android-ReadTheFuckingSourceCode/issues) 提交 issue，也可以发邮件给我 [jeanboy@foxmail.com](mailto:jeanboy@foxmail.com)。

同时欢迎你 [![Android技术进阶：386463747](https://camo.githubusercontent.com/615c9901677f501582b6057efc9396b3ed27dc29/687474703a2f2f7075622e69647171696d672e636f6d2f7770612f696d616765732f67726f75702e706e67)](http://shang.qq.com/wpa/qunwpa?idkey=0b505511df9ead28ec678df4eeb7a1a8f994ea8b75f2c10412b57e667d81b50d) 来一起交流学习，群里有很多大牛和学习资料，相信一定能帮助到你！



