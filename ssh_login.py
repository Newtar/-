import sys
import re
from PyQt5.QtWidgets import (QApplication, QDialog, QVBoxLayout, QLineEdit,
                             QPushButton, QMessageBox, QLabel, QSpacerItem, QSizePolicy)
from PyQt5.QtGui import QIcon, QFont
from PyQt5.QtCore import Qt
from main import MyWindow  # 导入 MyWindow 类

class ConnectionDialog(QDialog):
    """对话框类，用于获取SSH连接信息"""

    def __init__(self):
        """初始化连接对话框"""
        super().__init__()
        self.setWindowTitle("连接到虚拟机")
        self.setGeometry(200, 200, 400, 300)

        self.layout = QVBoxLayout(self)

        # 设置字体和居中标题
        title_label = QLabel("服务器连接", self)
        title_label.setFont(QFont("微软雅黑", 24, QFont.Bold))  # 使用更好看的字体
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2E8B57;")  # 改变字体颜色
        self.layout.addWidget(title_label)

        # 添加上方间隔
        self.layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # 输入框
        self.host_input = QLineEdit(self)
        self.host_input.setPlaceholderText("主机 IP")
        self.host_input.setStyleSheet("font-size: 16px; padding: 10px;")
        self.layout.addWidget(self.host_input)

        self.port_input = QLineEdit(self)
        self.port_input.setPlaceholderText("端口号")
        self.port_input.setStyleSheet("font-size: 16px; padding: 10px;")
        self.layout.addWidget(self.port_input)

        self.username_input = QLineEdit(self)
        self.username_input.setPlaceholderText("用户名")
        self.username_input.setStyleSheet("font-size: 16px; padding: 10px;")
        self.layout.addWidget(self.username_input)

        self.password_input = QLineEdit(self)
        self.password_input.setPlaceholderText("密码")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setStyleSheet("font-size: 16px; padding: 10px;")
        self.layout.addWidget(self.password_input)

        # 连接按钮
        self.connect_button = QPushButton("连接", self)
        self.connect_button.clicked.connect(self.connect)
        self.connect_button.setStyleSheet("""  
            QPushButton {  
                background-color: #66CDAA;  
                color: white;  
                border-radius: 5px;  
                font-size: 16px;  
                padding: 10px;  
            }  
            QPushButton:hover {  
                background-color: #4CAF50;  
            }  
        """)
        self.layout.addWidget(self.connect_button)

        # 添加底部间隔
        self.layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # 设置背景颜色
        self.setStyleSheet("""  
            QDialog {  
                background-color: #F5F5F5;  
            }  
        """)

        self.setLayout(self.layout)

    def is_valid_ip(self, ip):
        pattern = r'^(?:[0-9]{1,3}\.){3}[0-9]{1,3}$'
        return re.match(pattern, ip) is not None

    def connect(self):
        """连接到虚拟机并返回输入信息"""
        host = self.host_input.text().strip()
        port = self.port_input.text().strip()
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if host and self.is_valid_ip(host) and port.isdigit() and 1 <= int(port) <= 65535 and username and password:
            self.accept()
            self.start_main_window(host, int(port), username, password)
        else:
            QMessageBox.warning(self, "输入错误", "请填写所有字段，并确保 IP 地址和端口号有效。")

    def start_main_window(self, host, port, username, password):
        """启动主窗口并传递连接信息"""
        self.main_window = MyWindow(host, port, username, password)
        self.main_window.show()
        self.close()


def main():
    app = QApplication(sys.argv)
    dialog = ConnectionDialog()
    if dialog.exec_() == QDialog.Accepted:
        pass
    else:
        sys.exit()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()