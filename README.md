# Weibo_Scrawler
一个简单的带GUI界面的微博信息爬虫程序<br>
需要cookie(定期更换)和用户的UID 
## 目前实现的功能:
* 获取微博用户的基本信息:<br>
  1.昵称<br>
  2.头像<br>
  3.粉丝数<br>
  4.关注数<br>
  5.微博总数<br>
* 获取该用户的所有微博以及原创微博( 附带转发数 评论数 点赞数)<br>
* 根据该用户的原创微博生成一张词云，词云的形状是根目录的心形背景<br>
## 获取Cookie
用浏览器登录[https://weibo.cn](https://weibo.cn), 按F12打开开发者工具，点击**network**然后刷新，在下面的**name**中找到**weibo.cn**<br>
在**weibo.cn**的**Headers**中的Request Headers下面可以找到cookie，复制下来即可。<br>
Cookie需要定时更换，cookie变量位于weibo_Spider.py中的Spider类
## 获取用户的UID
同样用浏览器登录[https://weibo.cn](https://weibo.cn), 找到你想要查询的用户，进入他的主页，点击他的个人简介下面的**资料**，然后在地址栏中的一串数字就是该用户的UID了
