# swift

//var 变量 可变
//let 常量	不可变
//option + click 查看变量当前类型
var x = 20
let y = 30
//自动推导
let z = x + y

let num1 = 1
let num2 = 1.5
//强制转换
let num3 = Double(num1) + num2
//指定类型
let i: Double = 10

//if语句
let num = 20
/* 没有()，必须有{}，没有非零即真 */
if num > 10 {
	print("大于10")
}

let a = 10
let b = 20
//三目
let c = a > b ? 100 : -100

//optional 可选的，可能有值，可以为nil(0)
//init? 说明有可能无法实例化
let url = NSURL(string:"http://www.baidu.com/中文")
// ! 强行解包，认为这里 url 一定有值，一旦崩溃，就会停在这里
let request = NSURLRequest(URL:url!)
//更安全的写法
if url != nill {
	let request = NSURLRequest(URL:url!)
}

//if let 判断并且设置数值
//确保 myUrl 一定有值，才会进入分支
if let myUrl = url {
	//myUrl 一定有值
	print(myUrl)
}

var oName: String? ="张三"
var oAge: Int? = 18
if let name = oName, age = oAge {
	print(name + String(age))
}
//?? 操作符，如果 oName 为 nil 使用 ?? 后面的字符串，否则使用 oName 结果
let cName = oName ?? "abc"

var dataList: [String]?//数组
//dataList? 表示 dataList 可能为 nil
//如果为 nil，.count 不会报错，仍然返回 nil
//如果不为 nil，.count 执行并且返回数组计数
let count = dataList?.count ?? 0

//switch 不需要break

let name="张三"
switch name{
	case "张三":
		let age=80
		print("hi \(age)")
	case "李四","王五"
	default:
}

//String 继承结构体，效率高，支持遍历
var str:String = "hello"

for c in str.characters {
	print(c)
}

let name = "张三"
let age = 80
let title = "小菜"
//\(变量名) 自动转换拼接
print("\(name)\(age)\(title)")

let name:String? = "张三"//可为空
//字符串格式化
let time = String(format:"%02d:%02d:%02d",arguments":[1,2,3])

//Rang subString 如果碰到 range 最好把String改成NSString
(str as NSString).subStringWithRange(NSMakeRange(2,2))

//for 循环
for i in 0..<10 {//0-9
	print(i)
}

for i in 0...10 {//0-10
	print(i)
}

//数组

let array = ["",""]//let 不可变

for name in array {
	print(name)
}
//可以放任何类型 不需要包装 NSObject
var array2 = ["张三", 18, UIView()]//var 可变
array2.append("王")
array2.removeFirst()
array2.removeAll()
array2.removeAll(keepCapacity:true)//
array2.removeAtIndex(1)
array2//打印
array2.capacity//容量

//count初始容量，repeatedValue 默认值
var arrayM = [String](count:32, repeatedValue:0)	//实例化一个只能放字符串的数组，并且实例化
var arrayM2:[String]	//定义一个数组类型
arrayM2 = [String]()	//实例化
//数组拼接
var arrayM3 = arrayM + arrayM2

//字典相当于 map
var dict = ["name":"zhangsan", "age":18]
dict["height"] = 1.5	//添加，存在key覆盖值，不存在新建key

for (k,v) int dict {
	print("key\(k) value\(v))
}

//字典合并
let dict2 = ["title":"lisi", "age":18]
for (k,v) int dict2 {
	dict[k] = v
}

//函数
func sum(x: Int, y: Int) -> Int{
	return x + y;
}

sum(10, y: 20)

//外部参数 num1, num2 供外部程序调用参考用，x,y内部参数
func sum(num1 x: Int, num2 y: Int) -> Int{
	return x + y;
}

sum(num1: 10, num2: 20)

//没有返回值
func demo() {
	print("haha")
}

func demo2 -> Void {
	print("haha")
}

func demo3() -> (){
	print("haha")
}

//闭包 一组预先准备好的代码，可以当做参数传递，在需要的时候使用
//类似于匿名函数

func sum(num1 x: Int,num2 y: Int) -> Int {
	return x + y
}
//sum(10, y: 20)
sum(num1: 10, num2: 20)

let sumFunc = sum

//sumFunc(5, y: 6)
sumFunc(num1: 5, num2: 6)

//闭包的定义 可以做为参数传递相当于callback
let demoFunc = {
	print("demo")
}
//执行闭包
demoFunc()
//in 区分函数定义和代码实现
let demoFunc2 = { (x: Int, y: Int) -> Int in
	return x + y
}

//构造函数 init()
class Person extends NSObject{
	
	var name: String? {
		get{
			return ""
		}
		set{
			
		}
	}
	var age: Int = 0
	
	override init() {
		
	}
	//便捷构造函数可返回 nil 非便捷构造函数不能返回 nil
	convenience init? (name: String, age: Int){
		if age < 0 || age > 100 {
			return nil
		}
		self.init()
	}
	
	//析构函数 没有func 没有() 不能被调用
	deinit {
		
	}
}
//debug -> lldb
//便捷构造函数

//懒加载，闭包只会执行一次
//lazy的用处，如果没有lazy，视图控制器一旦被创建，datalist就会被初始化
lazy var dataList: [String] = {
	print("懒加载")
	return ["zhangsan","lisi"]
}()
//简单结果
lazy var dataList: [String] = ["zhangsan","lisi"]

//didSet 设置model数值时设置UI界面
var model: String? {
	didSet {
		print("更新UI")
	}
}
//只读属性
var model: String? {
	return "只读属性"
}
//解决循环引用
//weak 弱引用不会强引用，对象被释放地址自动设置为nil
//unowned self 会记录self的地址，不会强引用，对象被释放程序会崩溃


//多语言
NSLocalizedString(key:String, bundle:Bundle, comment:String)//调用系统的标准翻译
NSLocalizedString(key:"Delete", bundle:Bundle(UIButton.classForCode()), "")
//其他非标准多语言
let title:String = "请输入内容"
NSLocalizedString(key:String, comment:String)
NSLocalizedString(key:title, comment:"something")


