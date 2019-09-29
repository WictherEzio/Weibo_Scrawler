from bs4 import BeautifulSoup
import requests
import traceback
import wordcloud
import matplotlib.pyplot as plt
import re
import jieba
import numpy as np
from PIL import Image







class Spider():
    url='https://weibo.cn/u/{}?filter={}&page={}?f=search_0'     #第一个变量为用户id   第二个变量为用户微博的第几个选项     第三个变量为页数
    cookie={'Cookies':'ALF=1569044865; SCF=AmqJwJrzaCo9YT7Ev0liIBQzJOzqh5r41xI49SenLVjm0pRvfd409hieK1uSPTSMGrkkrCoWXhf2UaJyUypGfIE.; SUB=_2A25wWl-ODeRhGeNM71MZ8C7KyDuIHXVTpWHGrDV6PUJbktANLRHikW1NTguRZQ0e7PkUdw1Z6QHDy_qSBXm3r8vx; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WF3m4BnZwgbCXZ8JewKQoF45JpX5K-hUgL.Fo-ESh2Reh5ce0M2dJLoIpjLxK-LBKML1-2LxKqL1-eL1h.LxKqLBoeLB-2t; SUHB=0oU4McbNwb6PP4; _T_WM=a07e99b7dbd80cdb772c041cc6e62b6b'}
    def __init__(self,id):
        self.id=id
        self.nickname=''   #用户昵称
        self.weibo_num=0   #用户微博总数
        self.followers=0   #粉丝数目
        self.follows=0     #他关注的人
        self.page=0        #用户微博的页数

    '''处理html，返回soup'''
    def deal_html(self,url):
        html=requests.get(url=url,cookies=self.cookie)
        html.encoding='utf-8'
        wbdata=html.text
        soup=BeautifulSoup(wbdata,'lxml')
        return soup



    '''获取用户的昵称'''
    def get_nickname(self):
        myurl=self.url.format(self.id,0,0)    #先获取第一页的url
        soup=self.deal_html(url=myurl)
        #nickname=soup.select('.ctt')[0].text
        nickname=soup.select_one('td > div.ut > span.ctt').text

        if nickname.__contains__('男'):
            nickname=nickname[:nickname.find('男')]
        else:
            nickname=nickname[:nickname.find('女')]

        nickname=''.join(nickname.split())

        return nickname
    '''获取用户的信息   微博数目  关注的人  粉丝'''
    def get_info(self):
        myurl=self.url.format(self.id,0,0) #先获取第一页的url
        soup=self.deal_html(url=myurl)
        self.weibo_num=soup.select('div.tip2 > span.tc')[0].text[3:-1]    #获取微博数目
        self.follows=soup.select('div.tip2 > a')[0].text[3:-1]            #获取微博关注数
        self.followers=soup.select('div.tip2 > a')[1].text[3:-1]          #获取微博粉丝数

        self.weibo_num=''.join(self.weibo_num.split())                      #去掉'/xa0'
        self.follows=''.join(self.follows.split())
        self.followers=''.join(self.followers.split())

        self.page=int(self.weibo_num)/10
        return {
            '微博数目': self.weibo_num,
            '关注数': self.follows,
            '粉丝数目': self.followers
        }



    '''获取微博的内容'''
    def get_content(self):
        weibos=[]                           #存储微博
        pattern=r'\d+'                      #正则表达式 r的意思是不转义，即\表示原样的\。否则有可能被视图按\d为一个字符解析转义
        if(int(self.page)>15):              #如果微博页数太多了，就只查找十页的微博
            page=10
        else:
            page=int(self.page)
        for count in range(1,page):                      #这里暂时设置查找十页的微博
            myurl=self.url.format(self.id,0,count)
            soup=self.deal_html(myurl)
            contents=soup.select('div.c ')

            contents.remove(contents[0])
            contents.remove(contents[len(contents)-1])
            contents.remove(contents[len(contents)-1])   #第一个和最后两个都是无关内容
            for content in contents:
                content=content.text
                content=''.join(content.split())
                weibo_footer=content[content.rfind(u'赞'):]
                weibo_footer=re.findall(pattern,weibo_footer,re.M)            #正则表达式匹配
                content=content[:content.rfind(u'赞')]

                print(content)
                print('赞:'+weibo_footer[0])
                print('转发:'+weibo_footer[1])
                print('评论:'+weibo_footer[2])
                weibos.append(content)

        return weibos


    '''获取头像的图片，下载到当地'''
    def get_pohto(self):
        photo_url='https://weibo.cn/{}/avatar?rl=0'.format(self.id)
        soup=self.deal_html(photo_url)
        photo_url=soup.select_one('div.c > img')['src']
        try:
            response=requests.get(photo_url)
            img=response.content            # 获取的文本实际上是图片的二进制文本
        # 将他拷贝到本地文件 w 写  b 二进制  wb代表写入二进制文本
            with open('./image/{}.jpg'.format(self.id),'wb') as f:
                f.write(img)

            print('头像获取成功!')

        except Exception as e:
            print('头像获取失败!')
            traceback.print_exc()


        '''在文本文件中写入用户的原创微博'''
    def write_weibos(self):
        #filter=1表示原创微博
        file='原创微博.txt'
        with open(file,'w',encoding='utf-8') as File:
            for count in range(1, 10):
                myurl = self.url.format(self.id, 1, count)
                soup = self.deal_html(myurl)
                contents = soup.select('div.c > div > span.ctt')
                for content in contents:
                    content = content.text
                    content = ''.join(content.split())
                    #print(content)
                    File.write(content)

    def generateWC(self):
        '''对该用户的原创微博生成词云'''
        self.write_weibos()   #首先获得将该用户的原创微博写入文本中
        im=Image.open('心形背景.jpg')   #此图片作为词云的mask
        bg=np.array(im)            #图像转换为numpy矩阵
        file=open('原创微博.txt','r',encoding='utf-8').read()
        extra='[原图][全文][超话]'
        file=re.sub(extra,'',file)            #剔除无关信息
        con=jieba.cut(file)
        words=' '.join(con)                    #分词之后插入空格
        wc=wordcloud.WordCloud(scale=4,font_path='simkai.ttf',mask=bg,background_color='white',width=600,height=400,margin=2,random_state=15,collocations=True).generate(words)

        plt.imshow(wc)
        plt.axis('off')
        plt.show()
        wc.to_file('词云.png')









