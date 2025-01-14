import sys
import sqlite3
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import (QApplication, QMessageBox, QWidget, QStackedWidget, 
                            QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
                            QPushButton, QFrame)
from PyQt5.QtCore import Qt
from hashlib import sha256
from main import MainWindow

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setupUi()
        self.init_db()
        
    def setupUi(self):
        self.setWindowTitle("容器化部署网站工具")
        self.setFixedSize(800, 900)
        self.setStyleSheet("""
            QWidget {
                background-color: white;
                font-family: "Microsoft YaHei", sans-serif;
            }
        """)

        # 主布局
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        # 创建堆叠窗口
        self.stackedWidget = QStackedWidget()
        layout.addWidget(self.stackedWidget)

        # 创建登录和注册页面
        self.setup_login_page()
        self.setup_register_page()

    def setup_login_page(self):
        login_page = QWidget()
        login_layout = QVBoxLayout(login_page)
        login_layout.setSpacing(0)
        login_layout.setContentsMargins(0, 0, 0, 0)

        # 顶部装饰条 - 使用纯色而不是渐变
        top_bar = QWidget()
        top_bar.setFixedHeight(250)
        top_bar.setStyleSheet("""
            QWidget {
                background-color: #2ecc71;
                border-bottom-right-radius: 80px;
            }
        """)
        top_layout = QVBoxLayout(top_bar)
        top_layout.setAlignment(Qt.AlignCenter)
        top_layout.setContentsMargins(20, 20, 20, 40)  # 增加底部边距

        # Logo和标题
        logo_label = QLabel("🚀")
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setStyleSheet("""
            font-size: 72px;
            color: white;
            margin-bottom: 15px;
        """)
        top_layout.addWidget(logo_label)

        title_label = QLabel("容器化部署网站工具")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            font-size: 36px;
            font-weight: bold;
            color: white;
            letter-spacing: 2px;  /* 增加字间距 */
        """)
        top_layout.addWidget(title_label)

        subtitle_label = QLabel("快速部署，高效管理")  # 添加副标题
        subtitle_label.setAlignment(Qt.AlignCenter)
        subtitle_label.setStyleSheet("""
            font-size: 16px;
            color: rgba(255, 255, 255, 0.9);
            margin-top: 10px;
        """)
        top_layout.addWidget(subtitle_label)
        
        login_layout.addWidget(top_bar)

        # 主内容区域
        content_widget = QWidget()
        content_layout = QVBoxLayout(content_widget)
        content_layout.setSpacing(20)
        content_layout.setContentsMargins(50, 0, 50, 50)  # 调整上边距为0

        # 登录表单 - 简化样式
        form_widget = QFrame()
        form_widget.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 8px;
                margin-top: -50px;
            }
        """)
        form_layout = QVBoxLayout(form_widget)
        form_layout.setSpacing(25)  # 减小间距
        form_layout.setContentsMargins(30, 30, 30, 30)  # 减小内边距

        # 表单标题
        form_title = QLabel("欢迎回来")  # 更改标题文本
        form_title.setStyleSheet("""
            font-size: 28px;
            font-weight: bold;
            color: #2c3e50;
        """)
        form_title.setAlignment(Qt.AlignCenter)
        form_layout.addWidget(form_title)

        # 用户名输入
        username_container = self.create_input_field("用户名", "请输入用户名")
        self.lineEdit_username = username_container.findChild(QLineEdit)
        form_layout.addWidget(username_container)

        # 密码输入
        password_container = self.create_input_field("密码", "请输入密码", True)
        self.lineEdit_password = password_container.findChild(QLineEdit)
        form_layout.addWidget(password_container)

        # 登录按钮
        login_btn = QPushButton("登 录")
        login_btn.setStyleSheet(self.get_button_style("#2ecc71"))
        login_btn.setFixedHeight(50)
        login_btn.setCursor(Qt.PointingHandCursor)  # 添加手型光标
        login_btn.clicked.connect(self.login_user)
        form_layout.addWidget(login_btn)

        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background-color: #ecf0f1; margin: 10px 0;")
        form_layout.addWidget(line)

        # 注册链接
        register_link = QPushButton("还没有账号？点击注册")
        register_link.setCursor(Qt.PointingHandCursor)  # 添加手型光标
        register_link.setStyleSheet("""
            QPushButton {
                border: none;
                color: #2ecc71;
                text-align: center;
                padding: 10px;
                font-size: 16px;
            }
            QPushButton:hover {
                color: #27ae60;
                text-decoration: underline;  /* 添加下划线效果 */
            }
        """)
        register_link.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(1))
        form_layout.addWidget(register_link)

        content_layout.addWidget(form_widget)
        content_layout.addStretch()
        login_layout.addWidget(content_widget)

        self.stackedWidget.addWidget(login_page)

    def setup_register_page(self):
        register_page = QWidget()
        register_layout = QVBoxLayout(register_page)
        register_layout.setSpacing(20)

        # 返回按钮和标题
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        
        back_btn = QPushButton("← 返回")
        back_btn.setStyleSheet("""
            QPushButton {
                border: none;
                color: #2c3e50;
                font-size: 18px;
                text-align: left;
                padding: 8px;
            }
            QPushButton:hover {
                color: #34495e;
            }
        """)
        back_btn.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0))
        
        title = QLabel("创建新账号")
        title.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
        """)
        
        header_layout.addWidget(back_btn)
        header_layout.addWidget(title)
        header_layout.addStretch()
        register_layout.addWidget(header_widget)

        # 注册表单
        form_widget = QFrame()
        form_widget.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        form_layout = QVBoxLayout(form_widget)
        form_layout.setSpacing(15)

        # 输入字段
        new_username_container = self.create_input_field("👤 新用户名", "请设置用户名")
        self.lineEdit_new_username = new_username_container.findChild(QLineEdit)
        
        new_password_container = self.create_input_field("🔒 新密码", "请设置密码", True)
        self.lineEdit_new_password = new_password_container.findChild(QLineEdit)
        
        confirm_password_container = self.create_input_field("🔒 确认密码", "请再次输入密码", True)
        self.lineEdit_confirm_password = confirm_password_container.findChild(QLineEdit)

        form_layout.addWidget(new_username_container)
        form_layout.addWidget(new_password_container)
        form_layout.addWidget(confirm_password_container)

        # 注册按钮
        register_btn = QPushButton("注 册")
        register_btn.setStyleSheet(self.get_button_style("#2ecc71"))
        register_btn.setFixedHeight(60)
        register_btn.clicked.connect(self.register_user)
        form_layout.addWidget(register_btn)

        register_layout.addWidget(form_widget)
        register_layout.addStretch()

        self.stackedWidget.addWidget(register_page)

    def create_input_field(self, label_text, placeholder_text, is_password=False):
        container = QWidget()
        layout = QVBoxLayout(container)
        layout.setSpacing(5)
        layout.setContentsMargins(0, 0, 0, 0)

        # 标签
        label = QLabel(label_text)
        label.setStyleSheet("""
            color: #34495e;
            font-size: 16px;
            font-weight: bold;
        """)
        layout.addWidget(label)

        # 输入框
        input_field = QLineEdit()
        input_field.setPlaceholderText(placeholder_text)
        if is_password:
            input_field.setEchoMode(QLineEdit.Password)
        
        input_field.setStyleSheet("""
            QLineEdit {
                border: none;
                border-bottom: 2px solid #e0e0e0;
                padding: 8px 0px;
                font-size: 16px;
                background-color: white;
                min-width: 300px;
            }
            QLineEdit:focus {
                border-bottom: 2px solid #2ecc71;
            }
            QLineEdit::placeholder {
                color: #95a5a6;
            }
        """)
        input_field.setFixedHeight(40)
        layout.addWidget(input_field)

        return container

    def get_button_style(self, color):
        return """
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 16px;
                font-weight: bold;
                padding: 8px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:pressed {
                background-color: #219a52;
            }
        """

    def login_user(self):
        """ 处理用户登录逻辑 """
        username = self.lineEdit_username.text().strip()
        password = self.lineEdit_password.text()

        if not username or not password:
            QMessageBox.warning(self, "警告", "用户名和密码不能为空！", QMessageBox.Yes)
            return

        try:
            hashed_password = sha256(password.encode()).hexdigest()
            self.cursor.execute('SELECT * FROM users WHERE username=? AND password=?', 
                              (username, hashed_password))
            user = self.cursor.fetchone()

            if user:
                QMessageBox.information(self, "登录成功", "欢迎回来，{}！".format(username), 
                                      QMessageBox.Yes)
                self.open_main_window(username)
            else:
                QMessageBox.warning(self, "警告", "用户名或密码错误！", QMessageBox.Yes)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"登录过程中发生错误：{str(e)}", 
                               QMessageBox.Yes)

    def open_main_window(self, username):
        """ 打开主窗口 """
        self.main_window = MainWindow(username)
        self.main_window.show()
        self.hide()  # 隐藏登录窗口而不是关闭

    def register_user(self):
        """ 处理用户注册逻辑 """
        new_username = self.lineEdit_new_username.text()
        new_password = self.lineEdit_new_password.text()
        confirm_password = self.lineEdit_confirm_password.text()

        if not new_username or not new_password or not confirm_password:
            QMessageBox.warning(self, "警告", "用户名和密码不能为空！", QMessageBox.Yes)
            return

        if new_password != confirm_password:  # 检查密码是否一致
            QMessageBox.warning(self, "警告", "两次输入的密码不一致！", QMessageBox.Yes)
            return

        try:
            hashed_password = sha256(new_password.encode()).hexdigest()
            # 插入数据到数据库
            self.cursor.execute('INSERT INTO users (username, password) VALUES (?, ?)', (new_username, hashed_password))
            self.conn.commit()
            QMessageBox.information(self, "注册成功", "用户注册成功！", QMessageBox.Yes)
            self.lineEdit_new_username.clear()
            self.lineEdit_new_password.clear()
            self.lineEdit_confirm_password.clear()
        except sqlite3.IntegrityError:
            QMessageBox.warning(self, "警告", "用户名已存在！", QMessageBox.Yes)

    def init_db(self):
        """ 初始化数据库和用户表 """
        self.conn = sqlite3.connect('users.db')  # 连接或创建数据库
        self.cursor = self.conn.cursor()
        self.cursor.execute('''  
            CREATE TABLE IF NOT EXISTS users (  
                id INTEGER PRIMARY KEY AUTOINCREMENT,  
                username TEXT NOT NULL UNIQUE,  
                password TEXT NOT NULL  
            )  
        ''')
        self.conn.commit()

    def closeEvent(self, event):
        """ 处理窗口关闭事件 """
        try:
            self.conn.close()
        except:
            pass
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())