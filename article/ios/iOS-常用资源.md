# iOS 常用资源
## App 生命周期
- 程序启动顺序

1. 点击程序图标
2. 执行 main() 函数
3. 调用 UIApplicationMain() 函数
4. 初始化 UIApplication 对象并设置代理对象
    * applicationDidFinishLaunching()//程序载入后
    * applicationWillResignActive()//将要进入非活动状态
    * applicationDidBecomeActive()//程序进入活动状态
    * applicationDidEnterBackground()//程序进入后台
    * applicationWillEnterForeground()//程序从后台将要重新进入前台
    * applicationDidReceiveMemoryWaring()//内存警告，程序将要终止
    * applicationWillTerminate()//程序将要结束
5. UIApplication 对象开启 Event Loop 监听系统事件
6. 程序结束退出

- UIViewController 生命周期

1. initWithNibName()//非 storyBoard(xib 或非 xib)都走这个方法
2. initWithCoder()//如果连接了串联图 storyBoard 走这个方法
3. awakeFromNib()//xib 加载完成
4. loadView()//加载视图(默认从 nib)
5. viewDidLoad()//视图控制器中的视图加载完成，viewController 自带的 view 加载完成
6. viewWillAppear()//视图将要显示
7. viewWillLayoutSubviews()//视图将要布局子视图
8. viewDidLayoutSubviews()//子视图布局完成
9. viewDidAppear()//视图已经显示
10. viewWillDisappear()//视图将要消失
11. viewDidDisappear()//视图已经消失
12. didReceiveMemoryWarning()//内存警告
13. dealloc()//视图被销毁

## 基础
- UIKit//UI 控件
    - xib
    - storyboard
    - UIApplication
    - UIView
    - UIViewController
- Foundation//数据结构
## 网络交互
## 数据解析
## 数据存储
App-|-----MyApp.app//包含应用本身数据，包括资源文件和可执行文件，只读不会被 iTunes 同步
    |-----Documents//应用数据文件，会被 iTunes 同步
    |-----Library/Cache//缓存文件，不会被 iTunes 同步
    |-----tmp//临时文件，应用下次启动不需要的文件，随时可能被系统清理
    
- UserDefaults(Preference 偏好设置)
- KeyedArchiver(归档)
- SQLite 3
- CoreData(SQLite 的封装)
## 图片处理
## 国际化
## 手机功能
- 定位
- 地图
- 电话
- 短信
- 邮件
- 通讯录
- 相机
- 多媒体
- WebView
- 蓝牙
## 多线程，多任务，内存管理
- NSThread//手动控制线程
- GCD//苹果多核并行运算解决方案
- NSOperation & NSOperationQueue//GCD 的封装
## 触摸事件，手势处理，加速器
## 自定义控件
## Socket
## 热门技术
- 支付
- 即时通讯
- OCR
- 人脸识别
- 热修复
- 分享，社会化登录
- 推送服务
- HTML5
## 项目构建
- CocoaPods
- Swift & Objective-C 混编
- 版本控制 Git
- 单元测试
- 断点测试
## 开源库
- SnapKit//自动布局
- YYKit//iOS 组件
- MJRefresh//下拉刷新
- MBProgressHUD//loading
- SVProgressHUD//进度提示
- TYAttributedLabel//label 扩展
- FXBlurView//模糊效果
- TPKeyboardAvoiding//自动计算键盘高度
- pop Facebook//动画库
- lottie-ios//动画库
- AFNetworking//网络开源库
- Alamofire//AFNetworking 的 Swift 版本
- SDWebImage//图片处理
- YYWebImage//图片处理
- SwiftyUserDefaults//UserDefaults 封装库
- MagicalRecord//CoreData 封装库

## 参考资料
- http://blog.csdn.net/lerryteng/article/details/51207181
- http://www.jianshu.com/p/d60b388b19f5

