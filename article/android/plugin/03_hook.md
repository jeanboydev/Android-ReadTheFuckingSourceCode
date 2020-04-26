# Hook 技术初探

最近在研究插件化技术，插件化的中经常会使用到 Hook 技术，查阅了很多资料这里总结下讲的比较好的，希望对大家有所帮助。

## Hook 技术

Hook 是钩子的意思，在 Android 操作系统中系统维护着自己的一套事件分发机制。应用程序，包括应用触发事件和后台逻辑处理，也是根据事件流程一步步地向下执行。

而钩子的意思，就是在事件传送到终点前截获监控事件的传输，像个钩子钩上事件一样，并且能够在钩上事件时，处理一些自己特定的事件。较为形象的流程如下图所示。

![Hook 技术原理](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/plugin/02.png)

Hook 的这个本领，使它能够将自身的代码「融入」被勾住（Hook）的程序的进程中，成为目标进程的一个部分。

在 Android 系统中使用了沙箱机制，普通用户程序的进程空间都是独立的，程序的运行彼此间都不受干扰。根据 Hook 对象与 Hook 后处理的事件方式不同， Hook 还分为不同的种类，如消息 Hook 、API Hook 等。

从 Android 的开发来说，Android 系统本身就提供给了我们两种开发模式，基于 Android SDK 的 Java 语言开发，基于 AndroidNDK 的 Native C/C++ 语言开发。所以，我们在讨论 Hook 的时候就必须在两个层面上来讨论。

## Java Hook

通过对 Android 平台的虚拟机注入与 Java 反射的方式，来改变 Android 虚拟机调用函数的方式（ClassLoader），从而达到 Java 函数重定向的目的，这里我们将此类操作称为 Java API Hook。

下面通过 Hook View 的 OnClickListener 来说明 Hook 的使用方法。

```java
btn_test.setOnClickListener(new View.OnClickListener() {
  @Override
  public void onClick(View v) {
    Toast.makeText(v.getContext(), "Button Click", 
                   Toast.LENGTH_SHORT).show();
  }
});
```

首先进入 View 的 setOnClickListener 方法，我们看到 OnClickListener 对象被保存在了一个叫做 ListenerInfo 的内部类里，其中 mListenerInfo 是 View 的成员变量。

```java
public void setOnClickListener(@Nullable OnClickListener l) {
  if (!isClickable()) {
    setClickable(true);
  }
  getListenerInfo().mOnClickListener = l;
}

ListenerInfo getListenerInfo() {
  if (mListenerInfo != null) {
    return mListenerInfo;
  }
  mListenerInfo = new ListenerInfo();
  return mListenerInfo;
}
```

ListeneInfo 里面保存了 View 的各种监听事件，比如 OnClickListener、OnLongClickListener、OnKeyListener 等等。

```java
static class ListenerInfo {
  //...
  public OnClickListener mOnClickListener;
  protected OnLongClickListener mOnLongClickListener;
  private OnKeyListener mOnKeyListener;
  private OnTouchListener mOnTouchListener;
  private OnHoverListener mOnHoverListener;
  private OnGenericMotionListener mOnGenericMotionListener;
  private OnDragListener mOnDragListener;
  //...
}
```

我们的目标是 Hook OnClickListener，所以就要在给 View 设置监听事件后，替换 OnClickListener 对象，注入自定义的操作。

```java
public class HookView {
  public static void hookOnClickListener(View view) {
    try {
      // 通过反射获取到 getListenerInfo() 方法
      @SuppressLint("DiscouragedPrivateApi")
      Method getListenerInfo = View.class.getDeclaredMethod("getListenerInfo");
      // 设置访问权限
      getListenerInfo.setAccessible(true);
      // 调用 view 的 getListenerInfo() 获取到 ListenerInfo
      Object listenerInfo = getListenerInfo.invoke(view);

      // 通过反射获取到 ListenerInfo 的 Class 对象
      @SuppressLint("PrivateApi")
      Class<?> listenerInfoClass = Class.forName("android.view.View$ListenerInfo");
      // 获取到 mOnClickListener 成员变量
      Field mOnClickListener = listenerInfoClass.getDeclaredField("mOnClickListener");
      // 设置访问权限
      mOnClickListener.setAccessible(true);
      // 获取 mOnClickListener 属性的值
      View.OnClickListener originOnClickListener = (View.OnClickListener) mOnClickListener.get(listenerInfo);

      // 创建 OnClickListener 代理对象
      HookedOnClickListener hookedOnClickListener = new HookedOnClickListener(originOnClickListener);
      // 为 mOnClickListener 属性重新赋值
      mOnClickListener.set(listenerInfo, hookedOnClickListener);
    } catch (NoSuchMethodException | IllegalAccessException | InvocationTargetException | ClassNotFoundException | NoSuchFieldException e) {
      e.printStackTrace();
    }
  }

  static class HookedOnClickListener implements View.OnClickListener {

    private final View.OnClickListener origin;

    HookedOnClickListener(View.OnClickListener origin) {
      this.origin = origin;
    }

    @Override
    public void onClick(View v) {
      Log.e("HookedOnClickListener", "onClick");
      if (origin != null) {
        origin.onClick(v);
      }
    }
  }
}
```

到这里，我们成功 Hook 了 OnClickListener，在点击之前和点击之后可以执行某些操作，达到了我们的目的。下面是调用的部分，在给 Button 设置 OnClickListener 后，执行 Hook 操作。

```java
btn_test.setOnClickListener(new View.OnClickListener() {
    @Override
    public void onClick(View v) {
        Toast.makeText(v.getContext(), "Button Click", Toast.LENGTH_SHORT).show();
    }
});

HookView.hookOnClickListener(btn_test);
```

## Native Hook

Android Native Hook 主要分为两种：PLT Hook、Inline Hook。

> 我对 Native 开发不熟，这里仅仅做下了解。以下章节摘自[Android Native Hook技术路线概述](https://gtoad.github.io/2018/07/05/Android-Native-Hook/)。

### PLT Hook

先来介绍一下 Android PLT Hook 的基本原理。Linux 在执行动态链接的 ELF 的时候，为了优化性能使用了一个叫延时绑定的策略。

延时绑定的策略是为了解决原本静态编译时要把各种系统 API 的具体实现代码都编译进当前 ELF 文件里导致文件巨大臃肿的问题。所以当在动态链接的 ELF 程序里调用共享库的函数时，第一次调用时先去查找 PLT 表中相应的项目，而 PLT 表中再跳跃到 GOT 表中希望得到该函数的实际地址，但这时 GOT 表中指向的是 PLT 中那条跳跃指令下面的代码，最终会执行 `_dl_runtime_resolve()` 并执行目标函数。

第二次调用时也是 PLT 跳转到 GOT 表，但是 GOT 中对应项目已经在第一次 `_dl_runtime_resolve()` 中被修改为函数实际地址，因此第二次及以后的调用直接就去执行目标函数，不用再去执行 `_dl_runtime_resolve()` 了。

因此，PLT Hook 通过直接修改 GOT 表，使得在调用该共享库的函数时跳转到的是用户自定义的 Hook 功能代码。

了解 PLT Hook 的原理后，可以进一步分析出这种技术的特点：

- 由于修改的是 GOT 表中的数据，因此修改后，所有对该函数进行调用的地方就都会被 Hook 到。这个效果的影响范围是该 PLT 和 GOT 所处的整个 so 库。因此，当目标 so 库中多行被执行代码都调用了该 PLT 项所对应的函数，那它们都会去执行 Hook 功能。
- PLT 与 GOT 表中仅仅包含本 ELF 需要调用的共享库函数项目，因此不在 PLT 表中的函数无法 Hook 到。

那么这些特点会导致什么呢？

- 可以大量 Hook 那些系统 API，但是难以精准 Hook 住某次函数调用。

这比较适用于开发者对于自家 App 性能监控的需求。比如 Hook 住 malloc 使其输出参数，这样就能大量统计评估该 App 对于内存的需求。

但是对于一些对 Hook 对象有一定精准度要求的需求来说很不利，比如说是安全测试或者逆向分析的工作需求，这些工作中往往需要对于目标 so 中的某些关键点有准确的观察。

- 对于一些 so 内部自定义的函数无法 Hook 到，因为这些函数不在 PLT 表和 GOT 表里。

这个缺点对于不少软件分析者来说可能是无法忍受的。因为许多关键或核心的代码逻辑往往都是自定义的。例如 NDK 中实现的一些加密工作，即使使用了共享库中的加密函数，但秘钥的保存管理等依然需要进一步分析，而这些工作对于自定义函数甚至是某行汇编代码的监控能力要求是远远超出 PLT Hook 所能提供的范围。

- 在回调原函数方面，PLT Hook 在 hook 目标函数时，如果需要回调原来的函数，那就在 Hook 后的功能函数中直接调用目标函数即可。

可能有点绕，详细解释一下：假设对目标函数 malloc() 的调用在 1.so 中，用户用 PLT Hook 技术开发的 HookMalloc() 功能函数在 2.so 中。（因为通常情况下目标函数与用户的自定义 Hook 功能函数不在一个 ELF 文件里）当 1.so 中调用 malloc() 时会去 1.so 的 PLT 表中查询，结果是执行流程进入了 2.so 中的 HookMalloc() 中。如果这时候 HookMalloc 中希望调用原目标函数 malloc()，那就直接调用 malloc() 就好了。因为这里的 malloc 会去 2.so 中的 PLT 表中查询，不受 1.so 中那个被修改过的 PLT 表的影响。

本技术路线的典型代表是爱奇艺开源的 [xHook](https://github.com/iqiyi/xHook) 工具库。xhook 是一个针对 Android 平台 ELF（可执行文件和动态库）的 PLT（Procedure Linkage Table）hook 库。从维护频率和项目标志设计来看这是一款产品级的开源工具。

### Inline Hook

Inline Hook 即内部跳转 Hook，通过替换函数开始处的指令为跳转指令，使得原函数跳转到自己的函数，通常还会保留原函数的调用接口。与 GOT 表 Hook 相比，Inline Hook 具有更广泛的适用性，几乎可以 Hook 任何函数，不过其实现更为复杂，考虑的情况更多，并且无法对一些太短的函数 Hook。

本技术路线的基本原理是在代码段中插入跳转指令，从而把程序执行流程引向用户需要的功能代码中去，以此达到 Hook 的效果，如下图所示：

![Inline Hook](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/plugin/03.png)

从上图中可以看出主要有如下几个步骤：

- 在想要 Hook 的目标代码处备份下面的几条指令，然后插入跳转指令，把程序流程转移到一个 stub 段上去。
- 在 stub 代码段上先把所有寄存器的状态保存好，并调用用户自定义的 Hook 功能函数，然后把所有寄存器的状态恢复并跳转到备份代码处。
- 在备份代码处把当初备份的那几条指令都执行一下，然后跳转到当初备份代码位置的下面接着执行程序。

由此可以看出使用 Inline Hook 有如下的 Hook 效果特点：

- 完全不受函数是否在 PLT 表中的限制，直接在目标 so 中的任意代码位置都可进行 Hook。这个 Hook 精准度是汇编指令级的。这对于逆向分析人员和安全测试人员来说是个非常好的特性！

- 可以介入任意函数的操作。由于汇编指令级的 Hook 精度，以及不受 PLT 表的限制，Inline Hook 技术可以去函数执行中的任意代码行间进行 Hook 功能操作，从而读取或修改任意寄存器，使得函数的操作流程完全可以被控制。

- 对 Hook 功能函数的限制较小。由于在第二步调用 Hook 功能函数前已经把所有之前的寄存器状态都进行保存了，因此此时的 Hook 功能函数几乎就是个独立的函数，它无需受限于原本目标函数的参数形式，完全都由自己说了算。并且执行完后也完全是一个正常的函数退出形式释放栈空间。

- 对于 PLT Hook 的强制批量 Hook 的特性，Native Hook 要灵活许多。当想要进行批量 Hook 一些系统 API 时也可以直接去找内存里对应的如 libc.so 这些库，对它们中的 API 进行 Hook，这样的话，所有对这个 API 的调用也就都被批量 Hook 了。

### 技术对比

根据以上的分析，我们发现这两种技术在原理和适用场景上的差别是相当大的。因此有必要进行一下对比，给那些有 Native Hook 需求的童鞋一些参考。

| Name     | PLT Hook                         | Native Hook                               |
| :------- | :------------------------------- | :---------------------------------------- |
| 精准度   | `中` 函数级                      | `高`汇编级                                |
| 范围     | `小` 出现在PLT表中的动态链接函数 | `大` 目标so内全部可执行代码               |
| 灵活性   | `差` 只能批量                    | `好` 单次或批量都可以                     |
| 技术难度 | `中` 涉及内存地址计算和修改等    | `高` 涉及寄存器计算、手写汇编、指令修复等 |

## 参考资料

- [理解 Android Hook 技术以及简单实战](https://www.jianshu.com/p/4f6d20076922)
- [Android Native Hook技术路线概述](https://gtoad.github.io/2018/07/05/Android-Native-Hook/)