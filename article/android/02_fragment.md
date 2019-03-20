# Fragment

## 简介

Fragment （简称碎片）是 Android 3.0（API 11）提出的。为了兼容低版本 support-v4 库中也开发了一套Fragment API 最低兼容到 Android 1.6 的版本。

过去 support-v4 库是一个 jar 包，从 24.2.0 版本开始，将 support-v4 库模块化为多个 jar 包。包含 support-fragment、 support-ui、support-media-compat 等。这么做是为了减少 APK 包大小，项目中需要用哪个模块就引入哪个模块。

```groovy
// 引入整个 support-v4 库
compile 'com.android.support:support-v4:24.2.1'
//只引入 support-fragment 库
compile 'com.android.support:support-fragment:24.2.1'
```

因为 support 库是不断更新的，因此推荐使用 support 库中的 `android.support.v4.app.Fragment`，而不要用系统自带的 `android.app.Fragment`。如果使用 support 库的 Fragment，Activity 就必须要继承 FragmentActivity（AppCompatActivity 是 FragmentActivity 的子类）。

### Fragment 的特点

- Fragment 是依赖于 Activity 的，不能独立存在的。

- 一个 Activity 里可以有多个 Fragment。

- 一个 Fragment 可以被多个 Activity 重用。

- Fragment 有自己的生命周期，并能接收输入事件。

- 可以在 Activity 运行时动态地添加或删除 Fragment。

### Fragment 的优势

- 模块化（Modularity）：我们不必把所有代码全部写在 Activity 中，可以把代码写在各自的 Fragment 中。
- 可重用（Reusability）：多个 Activity 可以重用一个 Fragment。
- 可适配（Adaptability）：根据硬件的屏幕尺寸、屏幕方向，能够方便地实现不同的布局，这样用户体验更好。

## 生命周期

Fragment 与 Activity 生命周期很相似，与 Activity 一样，Fragment 也有三种状态：

- Resumed：Fragment 在运行中的 Activity 中可见。
- Paused：另一个 Activity 处于最顶层，但是 Fragment 所在的 Activity 并没有被完全覆盖（顶层的 Activity 是半透明的或不占据整个屏幕）。
- Stoped：Fragment 不可见，可能是它所在的 Activity 处于 stoped 状态或是 Fragment 被删除并添加到后退栈中了，此状态的 Fragment 仍然存在于内存中。

![img](https://developer.android.com/images/activity_fragment_lifecycle.png?hl=zh-cn)

 Activity 直接影响它所包含的 Fragment 的生命周期，所以对 Activity 的某个生命周期方法的调用也会产生对Fragment 相同方法的调用。例如：当 Activity 的 onPause() 方法被调用时，它所包含的所有的 Fragment 的onPause() 方法都会被调用。

Fragment 比 Activity 还要多出几个生命周期回调方法，这些额外的方法是为了与 Activity 的交互，如下：

- onAttach()

当 Fragment 被加入到 Activity 时调用（在这个方法中可以获得所在的 Activity）。

- onCreateView()

当 Activity 要得到 Fragment 的 layout 时，调用此方法，Fragment 在其中创建自己的 layout (界面)。

- onActivityCreated()

当 Activity 的 onCreated() 方法返回后调用此方法。

- onDestroyView()

当 Fragment 的 layout 被销毁时被调用。

- onDetach()

当 Fragment 被从 Activity 中删掉时被调用。

一旦 Activity 进入 resumed 状态（也就是 running 状态），你就可以自由地添加和删除 Fragment 了。因此，只有当 Activity 在 resumed 状态时，Fragment 的生命周期才能独立的运转，其它时候是依赖于 Activity 的生命周期变化的。

## 使用方式

这里给出 Fragment 最基本的使用方式。首先，创建继承 Fragment 的类，名为 BlankFragment：

```java
public class BlankFragment extends Fragment {
    private static final String ARG_PARAM = "param_key";
    private String mParam;

    public BlankFragment() { }

    public static BlankFragment newInstance(String param) {
        BlankFragment fragment = new BlankFragment();
        Bundle args = new Bundle();
        args.putString(ARG_PARAM, param);
        fragment.setArguments(args);
        return fragment;
    }

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        if (getArguments() != null) {
            mParam = getArguments().getString(ARG_PARAM);
        }
    }

    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        View view = inflater.inflate(R.layout.fragment_blank, container, false);
        // View 初始化，findViewById() 等操作
        return view;
    }

    @Override
    public void onActivityCreated(@Nullable Bundle savedInstanceState) {
        super.onActivityCreated(savedInstanceState);
        // 初始化数据，加载数据等...
    }
}
```

### 静态添加

通过 xml 的方式添加，缺点是一旦添加就不能在运行时删除。

```xml
<fragment
    android:id="@+id/fg_content"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:name="com.jeanboy.text.ui.fragment.BlankFragment" />
```

### 动态添加

运行时添加，这种方式比较灵活，因此建议使用这种方式。

这里只给出动态添加的方式。首先 Activity 需要有一个容器存放 Fragment，一般是 FrameLayout，因此在 Activity 的布局文件中加入 FrameLayout：

```xml
<FrameLayout
    android:id="@+id/container"
    android:layout_width="match_parent"
    android:layout_height="match_parent" />
```

然后在 `onCreate()` 中，通过以下代码将 Fragment 添加进Activity中。

```java
getSupportFragmentManager().beginTransaction()
        .add(R.id.container, BlankFragment.newInstance("hello world"), "f1")
        .commit();
```

这里需要注意几点：

- 因为我们使用了support库的Fragment，因此需要使用 `getSupportFragmentManager()` 获取 FragmentManager。

- `add()` 是对 Fragment 众多操作中的一种，还有 `remove()`， `replace()` 等。

  第一个参数是根容器的 id（FrameLayout 的 id，即 `@id/container`），第二个参数是 Fragment 对象，第三个参数是 Fragment 的 tag 名，指定 tag 的好处是后续我们可以通过：

  ```
  Fragment1 frag = getSupportFragmentManager().findFragmentByTag("f1");
  ```

  从 FragmentManager 中查找 Fragment 对象。

- 在一次事务中，可以做多个操作，比如同时做 `add().remove().replace()`。

- `commit() ` 操作是异步的，内部通过 `mManager.enqueueAction()` 加入处理队列。

  对应的同步方法为 `commitNow()`，`commit()` 内部会有 `checkStateLoss()` 操作，如果开发人员使用不当（比如 `commit()` 操作在 `onSaveInstanceState()` 之后），可能会抛出异常。而 `commitAllowingStateLoss()` 方法则是不会抛出异常版本的 `commit()` 方法，但是尽量使用 `commit()`，而不要使用 `commitAllowingStateLoss()`。

- `addToBackStack("fname")` 是可选的。

  FragmentManager 拥有回退栈（BackStack），类似于 Activity 的任务栈，如果添加了该语句，就把该事务加入回退栈，当用户点击返回按钮，会回退该事务（回退指的是如果事务是 `add(frag1)`，那么回退操作就是 `remove(frag1)` ）；如果没添加该语句，用户点击返回按钮会直接销毁 Activity。

## Fragment 通信

### Fragment 向 Activity 传递数据

首先，在 Fragment中 定义接口，并让 Activity 实现该接口。

```java
public interface OnFragmentCallback {
    void onCallback(String value);
}
```

在 Fragment 的 `onAttach()` 中，将参数 Context 强转为 OnFragmentCallback 对象：

```java
@Override
public void onAttach(Context context) {
    super.onAttach(context);
    if (context instanceof OnFragmentCallback) {
        callback = (OnFragmentCallback) context;
    } else {
        throw new RuntimeException(context.toString()
                                   + " must implement OnFragmentCallback");
    }
}
```

### Activity 向 Fragment 传递数据

Activity 向 Fragment 传递数据比较简单，获取 Fragment 对象，并调用 Fragment 的方法即可。比如要将一个字符串传递给 Fragment，则在 Fragment 中定义方法：

```java
public void setString(String data) { 
    this.data = data;
}
```

并在 Activity 中调用 `fragment.setString("hello")` 即可。

### Fragment 之间通信

由于 Fragment 之间是没有任何依赖关系的，因此如果要进行 Fragment 之间的通信，建议通过 Activity 作为中介，不要 Fragment 之间直接通信。

## DialogFragment

DialogFragment 是 Android 3.0 提出的，代替了 Dialog，用于实现对话框。它的优点是：即使旋转屏幕，也能保留对话框状态。

如果要自定义对话框样式，只需要继承 DialogFragment，并重写 `onCreateView()`，该方法返回对话框 UI。这里我们举个例子，实现进度条样式的圆角对话框。

```java
public class ProgressDialogFragment extends DialogFragment {
    @Override
    public View onCreateView(LayoutInflater inflater, ViewGroup container,
                             Bundle savedInstanceState) {
        //消除Title区域
        getDialog().requestWindowFeature(Window.FEATURE_NO_TITLE);
        //将背景变为透明
        getDialog().getWindow()
            .setBackgroundDrawable(new ColorDrawable(Color.TRANSPARENT));
        //点击外部不可取消
        setCancelable(false);
        View root = inflater.inflate(R.layout.fragment_progress_dialog, container);
        return root;
    }

    public static ProgressDialogFragment newInstance() {
        return new ProgressDialogFragment();
    }
}
```

然后通过下面代码显示对话框：

```java
ProgressDialogFragment fragment = ProgressDialogFragment.newInstance();
fragment.show(getSupportFragmentManager(), "tag");//显示对话框
fragment.dismiss();//关闭对话框
```

