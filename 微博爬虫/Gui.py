from PyQt5.QtWidgets import *
import sys
from PyQt5.QtGui import *
import time
from PyQt5.QtCore import *
from threading import *
import qtawesome

from weibo_Spider import *

import traceback
'''全局变量'''
id=0
name=''
info={}
contents=[]

def thread_it(func, *args):
    '''
    将函数打包进线程
    '''
    # 创建
    t = Thread(target=func, args=args)
    # 守护
    t.setDaemon(True)
    # 启动
    t.start()

class UI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui_init()


    def ui_init(self):
        self.setFixedSize(800,800)
        self.mainWidget=QWidget()     #设置主部件
        self.mainLayout=QGridLayout()

        self.setWindowTitle('东东的微博小爬虫')

        self.mainWidget.setLayout(self.mainLayout)




        '''以下是搜索框'''
        self.search_text=QLineEdit()
        self.search_text.setPlaceholderText('请输入微博用户的UID...')
        self.search_icon = QLabel('   '+chr(0xf002))
        self.search_icon.setFont(qtawesome.font('fa', 16))
        self.search_button=QPushButton('搜索')

        self.search_button.clicked.connect(lambda : thread_it(self.deal_event))     #按钮绑定  connect后面接函数名称不带括号，但是这里是有参数的，所以用lambda
        #self.search_button.clicked.connect(lambda  : thread_it(self.get_ori_weibo()))  #这里按钮绑定的函数是获取原创微博的2

        self.search_text.setStyleSheet('''QLineEdit{
                    border:1px solid gray;
                    width:300px;
                    border-radius:10px;
                    padding:2px 4px;
                    }''')
        self.search_button.setStyleSheet('''
                QPushButton{
                    border:1px solid gray;
                    width:60px;
                    border-radius:10px;
                    padding:4px 4px;
                }
                QPushButton:hover{
                    color:black;
                    border:1px solid #F3F3F5;
                    border-radius:10px;
                    background:LightGray;
                }
            ''')

        self.mainLayout.addWidget(self.search_icon,1,0,2,1)
        self.mainLayout.addWidget(self.search_text, 1, 1, 2, 6)
        self.mainLayout.addWidget(self.search_button,1,8,2,2)

        '''这里是生成词云的按钮'''
        self.wc_button=QPushButton('生成词云')
        self.wc_button.setDisabled(True)
        self.wc_button.clicked.connect(lambda :thread_it(self.wc_generate))
        self.wc_button.setStyleSheet('''
                QPushButton{
                    border:1px solid gray;
                    width:60px;
                    border-radius:10px;
                    padding:4px 4px;
                }
                QPushButton:hover{
                    color:black;
                    border:1px solid #F3F3F5;
                    border-radius:10px;
                    background:LightGray;
                }
            ''')
        self.mainLayout.addWidget(self.wc_button,2,7,2,3)

        '''这里是微博用户的信息   昵称  头像  微博数  关注数  粉丝数'''
        self.info_label1=QLabel('用户昵称:')
        self.info_label1.setStyleSheet('''
                    QLabel{font-size:16px; }
        ''')
        self.info_text1=QLineEdit()       #用户昵称的一行
        self.info_text1.setDisabled(True)
        self.info_text1.setStyleSheet('''QLineEdit{
                    border:1px solid gray;
                    border-radius:10px;
                    }''')

        self.info_label2=QLabel('用户头像')
        self.info_label2.setStyleSheet('''
                    QLabel{font-size: 16px;}
        ''')

        self.info_label3=QLabel()
        self.info_label3.setFixedSize(120,120)

        self.info_label3.setStyleSheet("QLabel{background:white;}"
                                 )   #QSS的内容   背景设为白色

        self.info_label3.setPixmap(QPixmap('./image/son.jpg').scaled(120,120))

        self.info_label4=QLabel('微博数目: ')
        self.info_label5=QLabel('关注数: ')
        self.info_label6=QLabel('粉丝数: ')

        self.mainLayout.addWidget(self.info_label1,2,12,1,1)
        self.mainLayout.addWidget(self.info_text1,2,13,1,5)
        self.mainLayout.addWidget(self.info_label2,3,12,1,1)
        self.mainLayout.addWidget(self.info_label3,4,12,3,3)
        self.mainLayout.addWidget(self.info_label4,7,12,1,3)
        self.mainLayout.addWidget(self.info_label5,7,15,1,1)
        self.mainLayout.addWidget(self.info_label6,8,12,1,3)
        '''这里是用户所有微博内容结果的部件 '''
        self.result_label=QLabel('该用户的所有微博: ')


        self.result=QTextEdit()

        self.result.setStyleSheet('''QTextEdit{
                    border:1px solid gray;
         
                    border-radius:10px;
                    padding:2px 4px;
                    }''')
        '''这里是所有原创微博内容结果的部件'''
        self.ori_result=QTextEdit()
        self.ori_result.setVisible(False)
        self.ori_result.setStyleSheet('''QTextEdit{
                    border:1px solid gray;
         
                    border-radius:10px;
                    padding:2px 4px;
                    }''')



        '''功能性按钮  清除微博内容'''
        self.clear_button = QPushButton('清除')
        self.clear_button.setStyleSheet('''
                        QPushButton{
                            border:1px solid gray;
                            width:60px;
                            border-radius:10px;
                            padding:4px 4px;
                        }
                        QPushButton:hover{
                            color:black;
                            border:1px solid #F3F3F5;
                            border-radius:10px;
                            background:LightGray;
                        }
                    ''')
        self.clear_button.clicked.connect(self.clear_weibo)
        self.mainLayout.addWidget(self.clear_button,26,18,1,1)

        '''功能性按钮，切换原创微博和所有微博'''
        self.change_button=QPushButton('切换')
        self.change_button.setStyleSheet('''
                        QPushButton{
                            border:1px solid gray;
                            width:60px;
                            border-radius:10px;
                            padding:4px 4px;
                        }
                        QPushButton:hover{
                            color:black;
                            border:1px solid #F3F3F5;
                            border-radius:10px;
                            background:LightGray;
                        }
                    ''')
        self.change_button.clicked.connect(lambda :thread_it(self.change_weibo))     #这里必须再启用一个线程  否则会卡死
        self.mainLayout.addWidget(self.change_button,10,18,1,1)


        self.mainLayout.addWidget(self.result_label,10,1,1,1)
        self.mainLayout.addWidget(self.result,11,0,15,20)        #此为所有微博的结果，默认显示
        self.mainLayout.addWidget(self.ori_result,11,0,15,20)    #此为原创微博的结果   默认设置为不显示
        self.setCentralWidget(self.mainWidget)   #设置主部件为中心部件

        self.setWindowOpacity(1)  # 设置窗口透明度
        #self.setAttribute(Qt.WA_TranslucentBackground)  # 设置窗口背景透明

        #self.setWindowFlag(Qt.FramelessWindowHint)  # 隐藏边框
        '''为了避免隐藏窗口边框后，左侧部件没有背景颜色和边框显示'''

        self.mainLayout.setSpacing(0)



    def deal_event(self):
        try:

            self.search_button.setDisabled(True)     #按钮变为不可用
            self.wc_button.setDisabled(True)
            #在搜索之前先把微博内容清空了


            wb = Spider(self.search_text.text())
            info = wb.get_info()
            name = wb.get_nickname()
            wb.get_pohto()

            pix = QPixmap('./image/{}.jpg'.format(wb.id))

            self.info_label3.setPixmap(pix.scaled(120, 120))
            self.info_text1.setText(name)
            self.info_label4.setText('微博数目:' + info['微博数目'])
            self.info_label5.setText('关注数:' + info['关注数'])
            self.info_label6.setText('粉丝数:' + info['粉丝数目'])
            '''contents = wb.get_content()
            #self.result.append(contents[0])
            for content in contents:
                self.result.append(' 内容: '+content+'\n')
                QApplication.processEvents()  # 刷新界面
                time.sleep(0.1)
                '''
            self.get_weibos()
            self.get_ori_weibo()
            self.search_button.setDisabled(False)
            self.wc_button.setDisabled(False)


        except Exception as e:
            time.sleep(0.1)
            self.search_text.setText('')
            self.search_button.setDisabled(False)
            print('error: '+e)

    '''生成词云的按钮绑定事件'''
    def wc_generate(self):
        try:
            self.wc_button.setDisabled(True)
            wb=Spider(self.search_text.text())
            wb.generateWC()
            self.wc_button.setDisabled(False)
        except Exception as e:
            self.search_text.setText('')
            self.wc_button.setDisabled(False)
            print('error: '+e)

    '''此为优化版的获取用户微博信息的方法'''
    def get_weibos(self):
        wb = Spider(self.search_text.text())
        pattern = r'\d+'  # 正则表达式 r的意思是不转义，即\表示原样的\。否则有可能被视图按\d为一个字符解析转义
        for count in range(1,11):
            myurl=wb.url.format(wb.id,0,count)
            soup=wb.deal_html(myurl)
            contents = soup.select('div.c ')

            contents.remove(contents[0])
            contents.remove(contents[len(contents) - 1])
            contents.remove(contents[len(contents) - 1])  # 第一个和最后两个都是无关内容
            for content in contents:
                content = content.text
                content = ''.join(content.split())
                weibo_footer = content[content.rfind(u'赞'):]
                weibo_footer = re.findall(pattern, weibo_footer, re.M)  # 正则表达式匹配
                content = content[:content.rfind(u'赞')]

                self.result.append(content)

                self.result.append('赞:' + weibo_footer[0])
                self.result.append('转发:' + weibo_footer[1])
                self.result.append('评论:' + weibo_footer[2])
                self.result.append('')
                QApplication.processEvents()  # 刷新界面
                time.sleep(0.1)
    '''此为爬取用户原创微博的方法'''
    def get_ori_weibo(self):
        wb = Spider(self.search_text.text())
        pattern = r'\d+'  # 正则表达式 r的意思是不转义，即\表示原样的\。否则有可能被视图按\d为一个字符解析转义
        for count in range(1, 11):
            myurl = wb.url.format(wb.id, 1, count)
            soup = wb.deal_html(myurl)
            contents = soup.select('div.c ')

            contents.remove(contents[0])
            contents.remove(contents[len(contents) - 1])
            contents.remove(contents[len(contents) - 1])  # 第一个和最后两个都是无关内容
            for content in contents:
                content = content.text
                content = ''.join(content.split())
                weibo_footer = content[content.rfind(u'赞'):]
                weibo_footer = re.findall(pattern, weibo_footer, re.M)  # 正则表达式匹配
                content = content[:content.rfind(u'赞')]

                self.ori_result.append(content)

                self.ori_result.append('赞:' + weibo_footer[0])
                self.ori_result.append('转发:' + weibo_footer[1])
                self.ori_result.append('评论:' + weibo_footer[2])
                self.ori_result.append('')
                QApplication.processEvents()  # 刷新界面
                time.sleep(0.1)


    '''为清除按钮绑定的事件处理'''
    def clear_weibo(self):
        self.result.clear()
        self.ori_result.clear()

    '''为改变微博内容按钮绑定的事件处理'''
    def change_weibo(self):
        if(self.result.isVisible()):
            self.result_label.setText('该用户的原创微博:')
            self.result.setVisible(False)
            self.ori_result.setVisible(True)
        else:
            self.result_label.setText('该用户的所有微博:')
            self.ori_result.setVisible(False)
            self.result.setVisible(True)






if __name__=='__main__':

    app=QApplication(sys.argv)   #这是一种通过参数来选择启动脚本的方式。
    gui = UI()
    gui.show()

    sys.exit(app.exec())

