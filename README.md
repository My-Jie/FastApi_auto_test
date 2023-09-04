[![License](https://img.shields.io/badge/License-MulanPSL_2.0-red.svg "License")](LICENSE "License")
[![Python](https://img.shields.io/badge/Python-v3.8.6-red.svg)]()
[![FastApi](https://img.shields.io/badge/FastApi-v0.9.5-red.svg)]()
[![Vue](https://img.shields.io/badge/Vue-v3.2-red.svg)]()
[![Element_Plus](https://img.shields.io/badge/Element_Plus-v2.3.7-red.svg)]()


# 随便测测平台
**随心、随意、随景**

* api和ui自动化测试综合测试平台
* 非传统测试平台设计，无全局变量、环境变量、临时变量的设定
* 半自动一键关联数据上下级关系
* 操作简便、平铺式展开api所有内容，方便查看和预览
* 使用Playwright录制ui用例，可选的Selenoid远程浏览器，python在线代码编辑器
* allure测试报告
* 二次元Saber (二次元就是第一生产力！)

>自动化用例如何快速成型，呐！就是这个。
>
>在继续阅读前，心理上请预先接受2个设定：

    1.api自动化 倾向于业务流程
    2.ui自动化  倾向于界面交互
    
>在用例快速成型的目标前提下，我们需要约束好它们各自能力的范围
>
>“快速编写用例”，这正是这个平台设计的初衷。从测试人员的角度出发，使测试人员用的舒畅，写的舒服，不对软件使用的复杂度望而生畏，
>以此为目的再去完善周边功能
>
>让编写自动化用例，赶得上测试用例设计



## api测试用例流程
![image](img/api_test.jpg)
* 有模板-用例-数据集的概念，1个模板可以生成N个用例，1个用例可以挂载N个数据集
* 数据源来源于Swagger、charles.har (数据来源是可扩展的，按模板格式存入即可)

>数据来源的扩展：只需要针对性的去解析不同格式的文件，按统一的数据模板保存即可
> 
>如postman, jmeter, yapi 等
> 
>模板是可以任意组装的，数据来源只是收录api的不同方式

### 核心功能
![image](img/1689642391577.jpg)
>**参数提取和使用的核心操作页面，也仅有这个页面**
>
>红色为正确的阅读顺序，绿色为实际的操作步骤从上到下1.2.3步(你可能需要切换tab标签来查看不同参数位置的数据)，即可完成数据关联及参数替换
>
>无需记录变量值，抠破脑袋的想变量名；无需为参数应用于哪些接口而发愁；一切交给程序自动处理，只需要告诉它：你想替换什么

[随便测测-做接口测试](https://blog.csdn.net/yangj507/article/details/131395093)


## ui测试用例流程
![image](img/playwright.jpg)
* 有模板-数据集的概念，1个模板挂载N个数据集
* 没有采用POM设计 （我们确定了ui的测试范围：页面交互）

>为什么没有采用POM设计，在这里不需要
>
>界面交互通常情况下是点对点的测试，没有复杂的业务背景，也就不需要分层设计、数据剥离

    当改动较小，在线编辑修改脚本内容即可
    当改动较大，删除文本内容重新录制即可
    
### 核心功能
![image](img/1689643175120.jpg)
>**一个python在线编辑器，仅此而已**
>
>将录制好的playwright文本内容复制到在线编辑器中，提交保存，一份ui测试的脚本就完成了。已经是极致的便捷
>
>可以在页面上二次编辑二次开发脚本，为了让脚本更好的完成ui测试工作
>
>你甚至可以只打印 hello world 而不做任何事
    
[随便测测-做UI测试](https://blog.csdn.net/yangj507/article/details/131579327)

## v2.4.7ui用例也支持批量选择数据集执行了
![image](img/1693836296042.jpg)
* 和api用例几乎相同的操作模式
* 支持同步、并行异步执行ui用例(目前异步执行allure报告还有问题)

## v2.4.6Jsonpath数据引用追踪
![image](img/1693835948634.jpg)
* 可以看到一个jsonpath用在了哪些接口(number)的哪些位置(path\params\data\headers\check)
* 简单操作jsonpath(正在做...大概会有恢复数据、批量修改功能)

## v2.4.5增加cURL(bash)解析
![image](img/1692978076215.jpg)
* 后端python解析，返回到前端
* 填充到模板编辑窗口

## v2.4.4文件上传-har，支持选择charles和chrome
![image](img/1692942609447.jpg)
![image](img/1692942876768.jpg)
* charles的har过滤：按mimeType内容进行过滤js、css、image等
* chrome的har过滤: _resourceType字段值 != xhr

## v2.4.3jsonpath支持取第几个值
![image](img/1692777697683.jpg)
![image](img/1692777846519.jpg)
* 表达式：{{number.$.jsonpath?number}}
* 优化提示信息展示效果

## v2.4.2增加response-headers取值相关操作
![image](img/1692777440868.jpg)
* 解析har时，response-headers落库
* 上下接口数据关联时，支持选择response-headers进行匹配
* response的取值表达式：{{number.$.jsonpath}}；response-headers的取值表达式：{{number.h$.jsonpath}}

## v2.4.1简易的测试结果时序图
![image](img/1692595790992.jpg)
![image](img/1692597649791.jpg)
* 查看最新执行api用例后的测试结果
* 存在缓存中，需要运行一次用例后才能看到，重新后失效

## v2.4接口调试功能
![image](img/1688977872578.jpg)
* 在模板上进行调试操作
* 调试时可以使用系统通用的各种表达式取数据
> 其实我也不知道“调试功能”应该怎么做合适
>
> 这是直接按个人想法做的，简单粗暴只会返回json格式的数据，不包含html等

## v2.3全局配置|环境绑定功能
![image](img/1690611019895.jpg)
![image](img/1690611147413.jpg)
![image](img/1690611333390.jpg)
>配置——绑定——使用
* 全局配置包含：系统列表、域名列表、自定参数、数据库表、统一响应
* 环境组合包含：api用例绑定、ui用例绑定、域名绑定、自定参数绑定、数据库表绑定
* 应用场景：一条用例，多个被测环境运行；一条用例，多套环境组合；最大行自定义用例中可变的数据
* 统一响应：在转化用例时与response对比，自动添加到用例check中
* 系统列表：api用例、ui用例标识


## 一些文档地址

* 博客：https://blog.csdn.net/yangj507/category_12359965.html
* 前端：https://gitee.com/myjiee/auto_test_web
* 前端：https://github.com/My-Jie/auto_test_web
* 主页：http://localhost:8000/index.html
* swagger-ui: http://localhost:8000/docs


## 一些截图
![image](img/1689178463172.jpg)
![image](img/1689178210973.jpg)
![image](img/1689178307393.jpg)
![image](img/1689178325585.jpg)
![image](img/1688977578863.jpg)
![image](img/1688977598877.jpg)
![image](img/1688977622112.jpg)
![image](img/1688977709859.jpg)
![image](img/1692294855492.jpg)


## 部署方式

### Python 后端
* 未采用docker容器部署，可自行尝试
* 建议使用Python3.8以上版本
* 环境安装：pip install -r requirements.txt 或 pip3 install -r requirements.txt
* 创建一个目录，将项目文件拷贝到目录下
* 可使用python main.py 或 python3 main.py 直接启动
* 或使用命令：nohup uvicorn main:app --host 0.0.0.0 --port 9999(自定义端口)启动
* 若启动过程中提示还有未安装的库，请根据提示自行使用 pip 安装
* setting.py 文件夹需要设置：ALLURE_PATH(allure报告存放路径)、LOG_PATH(日志路径)、HOST(allure访问路径)
* 接口文档：http://ip:port/docs

### vue3 前端
* 前端编译环境：vite+vue3+element-plus
* 建议使用vscode编辑器，vite构建工具可自行搜索下载
* npm install 安装第三方库
* npm run dev 启动dev环境
* npm run build 打包，默认打包目录在同级文件目录下的 dist 文件夹
* 在 python 后端根目录下新建 static 文件夹
* 将 dist 文件夹内的3个文件，拷贝到 static 目录下
* 主页：http://ip:port/index.html

# QQ交流群: 599733338

# WeChat 交流群

![image](img/1693561940501.jpg)
