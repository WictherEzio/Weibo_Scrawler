from Gui import *
if __name__ == '__main__':
    app = QApplication(sys.argv)  # 这是一种通过参数来选择启动脚本的方式。
    gui = UI()
    gui.show()
    

    sys.exit(app.exec())