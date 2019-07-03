# ContentProvider

## 简介

ContentProvider 是 Android 的四大组件之一，可见它在 Android 中的作用非同小可。

它主要的作用是实现各个应用程序之间的（跨应用）数据共享，比如联系人应用中就使用了ContentProvider，你可以在自己的应用中可以读取和修改联系人的数据，不过需要获得相应的权限。

ContentProvider 可以理解为一个 Android 应用对外开放的接口，只要是符合它所定义的 URI 格式的请求，均可以正常访问执行操作。其他的 Android 应用可以使用 ContentResolver 对象通过与 ContentProvider 同名的方法请求执行，被执行的就是 ContentProvider 中的同名方法。

所以 ContentProvider 很多对外可以访问的方法，在 ContentResolver 中均有同名的方法，是一一对应的，如图：

![ContentProvider](https://raw.githubusercontent.com/jeanboydev/Android-ReadTheFuckingSourceCode/master/resources/images/android/basic/05_content_provider/01.jpg)

那么 ContentProvider 是怎么实现数据共享的呢？

## 统一资源标识符（URI）

URI 代表要操作的数据，可以用来标识每个 ContentProvider，这样你就可以通过指定的 URI 找到想要的 ContentProvider，从中获取或修改数据。

在 Android 中 URI 的格式如下：

> URI = `<schema>://<authority>/<path>/<id>`

例如：content://com.jeanboy.provider/User/1

- 主题（schema）

ContentProvider 的 URI 前缀，表示是一个Android 内容 URI，说明由 ContentProvider 控制数据，该部分是固定形式，不可更改。

- 授权信息（authority）

URI 的授权部分，是唯一标识符，用来定位 ContentProvider。格式一般是自定义 ContentProvider 类的完全限定名称，注册时需要用到。如：com.jeanboy.provider.TestProvider。

- 表名（path）

路径片段，一般用表的名字，指向数据库中的某个表名。

- 记录（id）

指向特定的记录，如表中的某个记录（若无指定，则返回全部记录）。

## MIME 数据类型

MIME 是指定某个扩展名的文件用一种应用程序来打开，就像你用浏览器查看 PDF 格式的文件，浏览器会选择合适的应用来打开一样。

Android 中的工作方式跟 HTTP 类似，ContentProvider 会根据 URI 来返回 MIME 类型， ContentProvider 会返回一个包含两部分的字符串。

MIME 组成 = 类型 + 子类型。

> text/html
> application/pdf
>
> ...

 ContentProvider 根据 URI 返回 MIME 类型

```java
ContentProvider.geType(uri) ；
```

Android 遵循类似的约定来定义 MIME 类型，每个内容类型的 Android MIME 类型有两种形式：多条记录（集合）和单条记录。

- 多条记录：`vnd.android.cursor.dir/<custom>`
- 单条记录：`vnd.android.cursor.item/<custom>`

vnd 表示这些类型和子类型具有非标准的、供应商特定的形式。Android 中类型已经固定好了，不能更改，只能区别是集合还是单条具体记录，子类型 vnd. 之后的内容可以按照格式随便填写。

在使用 Intent 时，会用到 MIME，根据 MIME Type 打开符合条件的 Activity。

```xml
<activity android:name=".TestActivity">
  <intent-filter>
    <category android:name="android.intent.category.DEFAULT" />
    <data android:mimeType="vnd.android.cursor.dir/jeanboy.first" />
  </intent-filter>
</activity>
```

## 创建 ContentProvider

接下来通过一个简单的 Demo，来学习怎么创建自定义的 ContentProvider。数据源可以选用 SQLite，最常用的是这个，当然也可以选用其他的，比如 SharedPreferences。

首先，创建一个类 TestContentProvider，继承 ContentProvider 并实现方法。

```java
public class TestContentProvider extends ContentProvider {

  @Override
  public boolean onCreate() {
    // TODO 做一些初始化操作
    return false;
  }

  @Override
  public Cursor query(Uri uri, String[] projection, String selection,
                      String[] selectionArgs, String sortOrder) {
    // TODO 查询
    return null;
  }

  @Override
  public String getType(Uri uri) {
    // TODO MIME Type
    return null;
  }

  @Override
  public Uri insert(Uri uri, ContentValues values) {
    // TODO 插入
    return null;
  }

  @Override
  public int delete(Uri uri, String selection, String[] selectionArgs) {
    // TODO 删除
    return 0;
  }

  @Override
  public int update(Uri uri, ContentValues values, String selection,
                    String[] selectionArgs) {
    // TODO 更新
    return 0;
  }
}
```

然后，需要在 `AndroidManifest.xml` 中注册。

```xml
<provider
	android:name=".ui.provider.TestProvider"
	android:authorities="com.jeanboy.testprovider" />
```

## 使用 ContentProvider

在第三方应用中，我们要如何利用 URI 来执行共享数据数的操作呢？就是使用 ContentResolver 这个类来完成的。

获取 ContentResolver 实例的方法为：

```java
ContentResolver resolver = getContentResolver();
```

ContentResolver 有下面几个数据库操作：查询、插入、更新、删除。

```java
public final Cursor query (Uri uri, String[] projection, String selection,
                           String[] selectionArgs, String sortOrder)
public final Uri insert (Uri url, ContentValues values)
public final int update (Uri uri, ContentValues values, String where, 
                         String[] selectionArgs)
public final int delete (Uri url, String where, String[] selectionArgs)
```

完整示例如下：

```java
public class ContentProviderActivity extends BaseActivity {

  private Uri uriUser = 
    Uri.parse("content://com.jeanboy.testprovider/user");

  @Override
  protected void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);
    setContentView(R.layout.activity_content_provider);
  }

  public void toInsert(View view) {
    ContentValues values = new ContentValues();
    values.put("id", 3);
    values.put("name", "张三");
    ContentResolver resolver = getContentResolver();
    resolver.insert(uriUser, values);
  }

  public void toUpdate(View view) {
    ContentValues values = new ContentValues();
    values.put("id", 3);
    values.put("name", "张三三");
    ContentResolver resolver = getContentResolver();
    resolver.update(uriUser, values, "id = ?", new String[]{"3"});
  }

  public void toSelect(View view) {
    ContentResolver resolver = getContentResolver();
    Cursor cursor = resolver.query(uriUser, new String[]{"id", "name"},
                                   null, null, null);
    while (cursor.moveToNext()) {
      Log.e(TAG, "=========== query :" + cursor.getInt(0) + "==" 
            + cursor.getString(1));
    }
    cursor.close();
  }

  public void toDelete(View view) {
    ContentResolver resolver = getContentResolver();
    resolver.delete(uriUser, "id = ?", new String[]{"3"});
  }
}
```

## ContentProvider 权限

在 AndroidManifest.xml 中 provider 标签中有三个额外的参数 permission、readPermission、writePermission。

先看下面这段代码：

```xml
<provider
		android:name=".ui.provider.TestProvider"
		android:authorities="com.jeanboy.testprovider"
		android:exported="true"
		android:readPermission="com.jeanboy.provider.permission.read"
		android:writePermission="com.jeanboy.provider.permission.write"
		android:permission="com.jeanboy.provider.permission"/>
```

在这段代码中有几个参数要特别注意一下：

- exported

这个属性用于指示该服务是否能被其他程序应用组件调用或跟他交互； 取值为（true | false）。

如果设置成true，则能够被调用或交互，否则不能；设置为 false 时，只有同一个应用程序的组件或带有相同用户ID的应用程序才能启动或绑定该服务。

- readPermission

使用 Content Provider 的查询功能所必需的权限，即使用 ContentProvider 里的 `query()` 函数的权限。

- writePermission

使用 ContentProvider 的修改功能所必须的权限，即使用 ContentProvider 的 `insert()`、`update()`、`delete()` 函数的权限。

- permission

客户端读、写 Content Provider 中的数据所必需的权限名称。

本属性为一次性设置读和写权限提供了快捷途径。 不过 readPermission 和 writePermission 属性优先于本设置。 

如果同时设置了 readPermission 属性，则其将控制对 Content Provider 的读取。 如果设置了 writePermission 属性，则其也将控制对 Content Provider 数据的修改。

也就是说如果只设置 permission 权限，那么拥有这个权限的应用就可以实现对这里的 ContentProvider 进行读写；如果同时设置了 permission 和 readPermission 那么具有 readPermission 权限的应用才可以读，拥有 permission 权限的才能写！也就是说只拥有 permission 权限是不能读的，因为 readPermission 的优先级要高于 permission；如果同时设置了 readPermission、writePermission、permission 那么 permission 就无效了。

## 权限使用

上面声明权限后需要在 application 标签同级目录中注册一下。

```xml
<manifest ...>
		<permission
				android:name="com.jeanboy.provider.permission.read"
				android:label="provider pomission"
				android:protectionLevel="normal" />
  <application ...>
    ...
  </application>
</manifest>
```

这样，我们的 permission 才会在系统中注册，在第三方应用中使用 `<uses-permission>` 来使用权限。

```xml
<uses-permission android:name="com.jeanboy.provider.permission.read"/>
```

## ContentObserver

ContentObserver 主要作用是监听指定 URI 上的数据库变化。

首先，创建一个 ContentObserver。

```java
public class DataObserver extends ContentObserver {
  public DataObserver(Handler handler) {
    super(handler);
  }

  @Override
  public void onChange(boolean selfChange) {
    super.onChange(selfChange);
    // TODO 监听到数据变化
  }
}
```

注册 ContentObserver。

```java

public class ContentProviderActivity extends BaseActivity {

  private Uri uriUser = 
    Uri.parse("content://com.jeanboy.myprovider/user");

  private DataObserver dataObserver;

  @Override
  protected String getTAG() {
    return ContentProviderActivity.class.getSimpleName();
  }

  @Override
  protected void onCreate(Bundle savedInstanceState) {
    super.onCreate(savedInstanceState);
    setContentView(R.layout.activity_content_provider);
		// 创建 DataObserver
    dataObserver = new DataObserver(new Handler());
    // 注册 DataObserver
    getContentResolver().registerContentObserver(uriUser, true, 
                                                 dataObserver);
  }

  @Override
  protected void onDestroy() {
    super.onDestroy();
    // 取消注册
    getContentResolver().unregisterContentObserver(dataObserver);
  }
}
```

最后看下 `registerContentObserver()` 注册监听函数的用法：

```java
public final void registerContentObserver(Uri uri, 
		boolean notifyForDescendents, ContentObserver observer)
```

- uri 

需要观察的 URI。

- notifyForDescendents

为 false 表示精确匹配，即只匹配该 URI； 为 true 表示可以同时匹配其派生的 URI。

好了到这里 ContentProvider 相关知识点介绍的差不多了，希望对大家有所帮助。