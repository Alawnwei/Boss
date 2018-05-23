# Boss
基于Python3的找工作利器--Boss直聘来消息邮件通知, 自动发送简历脚本，O(∩_∩)O~
无聊写的，因为有时候觉得找工作心急如焚，想自动回复自动发简历啊有木有~~~

# 效果图

程序运行日志图

![image.png](https://upload-images.jianshu.io/upload_images/6053915-8db6bc90ceb88015.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

邮件展示图

![image.png](https://upload-images.jianshu.io/upload_images/6053915-2ff7b38430f459bd.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

![image.png](https://upload-images.jianshu.io/upload_images/6053915-6aac0f3ca850444f.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1240)

# 快速开始

### 下载
- ```git clone https://github.com/wuranxu/Boss.git```

- 下载zip文件并解压

### 修改json配置文件

百度API文字识别(每日500次免费)，进入[官网](http://ai.baidu.com/tech/ocr/general)申请并配置。

- app_id

- api_key

- secret_key

用户密码配置

- user(boss直聘手机号)

- password(boss直聘登录密码)

邮箱配置

- sender(发件人邮箱账号，需要选择126邮件, 否则需要更改```host='smtp.126.com'```)

- sender_pwd(发件人邮箱密码)

- receiver(收件人)

### 使用

进入boss目录, 执行命令


```
pip install -r requirements.txt

python boss.py

```

(如果出现安装失败, 请及时升级pip)

其他配置说明:

- retry(百度ocr识别出错时重试等待时间)

- delay(获取boss消息等待时间, 单位: 分钟)

- auto_resume(是否自动发送简历)

- black_list(黑名单配置)

- 其他url(抓取职位及消息所用)

# 原理

- requests生成session, 访问boss直聘网页版

- 利用beautifulsoup解析网站, 获取到图片验证码

- 调用百度ocr的图片识别api, 识别网站验证码

- 模拟用户登录(为什么不用selenium或者phantomJs, 因为比较笨重)

- 持续监听历史消息, 有新消息且不是自己发送时，发邮件通知收件人(包括职位, 薪资等信息)

- 当配置里的自动发简历为true时会在手动boss消息时自动调用发简历的接口

# 问题

- 百度识别率不是很高哦

- 由于boss直聘防止骚扰，所以在只有双方都有回复时才会成功发送简历

- 有多条消息同时到来时只会读取一条消息

- 由于邮件限制, 当消息火爆时邮件可能被视为垃圾邮件而导致发不出去

- 由于boss的聊天协议采取的是websocket并加密，所以不太好揣测它的规则，导致无法自动回复消息(简历也会受影响)


# TODO

- 薪资配置(低于多少K咱直接不看他)

- 心动公司(大厂)设置

- 多个百度Key轮流使用

