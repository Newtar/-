import sys
import paramiko
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QPushButton, 
                            QLabel, QDialog, QLineEdit, QMessageBox, QGridLayout,
                            QTableWidget, QTableWidgetItem, QHeaderView, QHBoxLayout,
                            QTextEdit, QFileDialog, QComboBox, QFrame)
from PyQt5.QtCore import Qt
from DockerCompose import DockerComposeWindow
import os
from datetime import datetime

class ServerConnectDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        self.apply_styles()
        
    def init_ui(self):
        self.setWindowTitle('连接服务器')
        self.setFixedSize(400, 450)  # 固定对话框大小
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # 添加图标和标题
        title_layout = QHBoxLayout()
        icon_label = QLabel("🔌")
        icon_label.setStyleSheet("font-size: 48px;")
        title_layout.addWidget(icon_label)
        
        title_text = QLabel("连接到服务器")
        title_text.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
            margin-left: 10px;
        """)
        title_layout.addWidget(title_text)
        title_layout.addStretch()
        layout.addLayout(title_layout)

        # 添加分隔线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background-color: #bdc3c7; margin: 10px 0px;")
        layout.addWidget(line)

        # 创建表单布局
        form_layout = QGridLayout()
        form_layout.setSpacing(10)

        # 主机地址输入
        host_label = QLabel('主机地址:')
        self.host_input = QLineEdit()
        self.host_input.setPlaceholderText('例如: 192.168.1.100')
        form_layout.addWidget(host_label, 0, 0)
        form_layout.addWidget(self.host_input, 0, 1)

        # 端口输入
        port_label = QLabel('端口:')
        self.port_input = QLineEdit()
        self.port_input.setText('22')
        self.port_input.setPlaceholderText('SSH端口')
        form_layout.addWidget(port_label, 1, 0)
        form_layout.addWidget(self.port_input, 1, 1)

        # 用户名输入
        username_label = QLabel('用户名:')
        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText('SSH用户名')
        form_layout.addWidget(username_label, 2, 0)
        form_layout.addWidget(self.username_input, 2, 1)

        # 密码输入
        password_label = QLabel('密码:')
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setPlaceholderText('SSH密码')
        form_layout.addWidget(password_label, 3, 0)
        form_layout.addWidget(self.password_input, 3, 1)

        layout.addLayout(form_layout)

        # 添加快速连接选项
        quick_connect_label = QLabel("快速连接配置")
        quick_connect_label.setStyleSheet("""
            font-size: 16px;
            font-weight: bold;
            color: #2c3e50;
            margin-top: 10px;
        """)
        layout.addWidget(quick_connect_label)

        # 快速连接按钮
        quick_connect_layout = QHBoxLayout()
        
        local_btn = QPushButton("本地测试")
        local_btn.clicked.connect(lambda: self.quick_connect("localhost"))
        
        cloud_btn = QPushButton("云服务器")
        cloud_btn.clicked.connect(lambda: self.quick_connect("124.221.42.138"))
        
        quick_connect_layout.addWidget(local_btn)
        quick_connect_layout.addWidget(cloud_btn)
        layout.addLayout(quick_connect_layout)

        # 添加连接按钮
        self.connect_btn = QPushButton('连接服务器')
        self.connect_btn.setMinimumHeight(50)
        self.connect_btn.clicked.connect(self.accept)
        layout.addWidget(self.connect_btn)
        
        self.setLayout(layout)

    def quick_connect(self, host):
        """快速连接预设"""
        self.host_input.setText(host)
        self.port_input.setText("22")
        if host == "124.221.42.138":
            self.username_input.setText("root")
            self.password_input.setText("Wx523040!")
        else:
            self.username_input.setText("root")
            self.password_input.setText("")

    def apply_styles(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #f5f6fa;
            }
            QLabel {
                color: #2c3e50;
                font-size: 14px;
            }
            QLineEdit {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                background-color: white;
                font-size: 14px;
                min-height: 25px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                font-weight: bold;
                min-height: 35px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:pressed {
                background-color: #219a52;
            }
            #connect_btn {
                background-color: #3498db;
                margin-top: 15px;
                font-size: 16px;
            }
            #connect_btn:hover {
                background-color: #2980b9;
            }
        """)

class ContainerManager(QDialog):
    def __init__(self, ssh_client, parent=None):
        super().__init__(parent)
        self.ssh_client = ssh_client
        self.init_ui()
        
        # 检查 SSH 连接
        if not self.ssh_client or not self.ssh_client.get_transport() or not self.ssh_client.get_transport().is_active():
            QMessageBox.critical(self, '错误', 'SSH连接已断开，请重新连接')
            self.reject()
            return
            
        self.refresh_containers()
        
    def init_ui(self):
        self.setWindowTitle('容器管理')
        self.setGeometry(100, 100, 800, 400)
        
        layout = QVBoxLayout()
        
        # 创建容器列表表格
        self.container_table = QTableWidget()
        self.container_table.setColumnCount(5)
        self.container_table.setHorizontalHeaderLabels(['容器ID', '名称', '状态', '镜像', '端口'])
        header = self.container_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.container_table)
        
        # 添加操作按钮
        button_layout = QVBoxLayout()
        buttons = [
            ('刷新列表', self.refresh_containers),
            ('启动容器', self.start_container),
            ('停止容器', self.stop_container),
            ('删除容器', self.remove_container)
        ]
        
        for text, handler in buttons:
            btn = QPushButton(text)
            btn.clicked.connect(handler)
            button_layout.addWidget(btn)
            
        layout.addLayout(button_layout)

        # 添加确定和取消按钮
        button_box = QHBoxLayout()
        
        ok_button = QPushButton("确定")
        ok_button.clicked.connect(self.accept)
        cancel_button = QPushButton("取消")
        cancel_button.clicked.connect(self.reject)
        
        button_box.addWidget(ok_button)
        button_box.addWidget(cancel_button)
        
        layout.addLayout(button_box)
        self.setLayout(layout)
        
    def refresh_containers(self):
        try:
            stdin, stdout, stderr = self.ssh_client.exec_command('docker ps -a --format "{{.ID}}\t{{.Names}}\t{{.Status}}\t{{.Image}}\t{{.Ports}}"')
            containers = stdout.read().decode().strip().split('\n')
            
            self.container_table.setRowCount(len(containers))
            for i, container in enumerate(containers):
                if container:  # 确保不是空行
                    data = container.split('\t')
                    for j, value in enumerate(data):
                        self.container_table.setItem(i, j, QTableWidgetItem(value))
        except Exception as e:
            QMessageBox.critical(self, '错误', f'获取容器列表失败: {str(e)}')
            
    def get_selected_container(self):
        selected = self.container_table.selectedItems()
        if not selected:
            QMessageBox.warning(self, '警告', '请先选择一个容器')
            return None
        return selected[0].text()  # 返回容器ID
        
    def start_container(self):
        container_id = self.get_selected_container()
        if container_id:
            try:
                self.ssh_client.exec_command(f'docker start {container_id}')
                QMessageBox.information(self, '成功', '容器已启动')
                self.refresh_containers()
            except Exception as e:
                QMessageBox.critical(self, '错误', f'启动容器失败: {str(e)}')
                
    def stop_container(self):
        container_id = self.get_selected_container()
        if container_id:
            try:
                self.ssh_client.exec_command(f'docker stop {container_id}')
                QMessageBox.information(self, '成功', '容器已停止')
                self.refresh_containers()
            except Exception as e:
                QMessageBox.critical(self, '错误', f'停止容器失败: {str(e)}')
                
    def remove_container(self):
        container_id = self.get_selected_container()
        if container_id:
            reply = QMessageBox.question(self, '确认', '确定要删除该容器吗？',
                                       QMessageBox.Yes | QMessageBox.No)
            if reply == QMessageBox.Yes:
                try:
                    self.ssh_client.exec_command(f'docker rm -f {container_id}')
                    QMessageBox.information(self, '成功', '容器已删除')
                    self.refresh_containers()
                except Exception as e:
                    QMessageBox.critical(self, '错误', f'删除容器失败: {str(e)}')

class MainWindow(QMainWindow):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.ssh_client = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('容器化部署网站工具')
        self.setGeometry(100, 100, 1000, 700)  # 调整窗口大小

        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(20)  # 增加组件间距
        main_layout.setContentsMargins(30, 30, 30, 30)  # 设置边距

        # 顶部欢迎区域
        welcome_widget = QWidget()
        welcome_layout = QHBoxLayout(welcome_widget)
        
        # 添加logo标签
        logo_label = QLabel("🚀")
        logo_label.setStyleSheet("""
            font-size: 48px;
            margin-right: 20px;
        """)
        welcome_layout.addWidget(logo_label)

        # 欢迎文本区域
        welcome_text = QWidget()
        welcome_text_layout = QVBoxLayout(welcome_text)
        
        welcome_label = QLabel(f"欢迎回来, {self.username}")
        welcome_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
        """)
        
        # 状态和重连按钮的水平布局
        status_layout = QHBoxLayout()
        
        status_label = QLabel("未连接到服务器")
        status_label.setStyleSheet("""
            font-size: 14px;
            color: #95a5a6;
        """)
        self.status_label = status_label
        status_layout.addWidget(status_label)
        
        # 添加重连按钮
        reconnect_btn = QPushButton("重新连接")
        reconnect_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px 10px;
                font-size: 12px;
                font-weight: bold;
                max-width: 80px;
                max-height: 25px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #2475a8;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        reconnect_btn.clicked.connect(self.reconnect_server)
        reconnect_btn.setEnabled(False)  # 初始状态禁用
        self.reconnect_btn = reconnect_btn  # 保存引用
        status_layout.addWidget(reconnect_btn)
        
        welcome_text_layout.addWidget(welcome_label)
        welcome_text_layout.addLayout(status_layout)
        welcome_layout.addWidget(welcome_text)
        welcome_layout.addStretch()
        
        main_layout.addWidget(welcome_widget)

        # 添加分隔线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background-color: #bdc3c7;")
        main_layout.addWidget(line)

        # 功能按钮区域
        buttons_widget = QWidget()
        buttons_layout = QGridLayout(buttons_widget)
        buttons_layout.setSpacing(15)  # 设置按钮之间的间距

        # 定义按钮信息：(文本, 图标, 处理函数, 描述)
        buttons_info = [
            ("连接服务器", "🔌", self.connect_server, "连接到远程服务器"),
            ("部署新网站", "🌐", self.deploy_website, "使用Docker Compose部署网站"),
            ("管理容器", "📦", self.manage_containers, "管理Docker容器"),
            ("查看日志", "📋", self.view_logs, "查看容器运行日志"),
            ("退出登录", "🚪", self.logout, "退出当前账号")
        ]

        # 创建并添加按钮
        for i, (text, icon, handler, desc) in enumerate(buttons_info):
            button_widget = QWidget()
            button_layout = QVBoxLayout(button_widget)
            
            # 创建按钮
            btn = QPushButton(f"{icon} {text}")
            btn.setMinimumHeight(80)
            btn.clicked.connect(handler)
            
            # 创建描述标签
            desc_label = QLabel(desc)
            desc_label.setStyleSheet("""
                color: #7f8c8d;
                font-size: 12px;
            """)
            desc_label.setAlignment(Qt.AlignCenter)
            
            button_layout.addWidget(btn)
            button_layout.addWidget(desc_label)
            
            # 将按钮添加到网格布局
            row = i // 2
            col = i % 2
            buttons_layout.addWidget(button_widget, row, col)

        main_layout.addWidget(buttons_widget)
        
        # 添加状态栏
        self.statusBar().showMessage('准备就绪')
        
        # 应用整体样式
        self.apply_styles()

    def apply_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f6fa;
            }
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 15px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
            QPushButton:pressed {
                background-color: #219a52;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
            QLabel {
                color: #2c3e50;
            }
            QStatusBar {
                background-color: #2ecc71;
                color: white;
                padding: 5px;
            }
            QMessageBox {
                background-color: #f5f6fa;
            }
            QMessageBox QPushButton {
                min-width: 100px;
                min-height: 30px;
            }
        """)

    def connect_server(self):
        dialog = ServerConnectDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            try:
                # 如果已经存在连接，先关闭它
                if self.ssh_client:
                    self.ssh_client.close()
                
                # 创建新的 SSH 连接
                self.ssh_client = paramiko.SSHClient()
                self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                self.ssh_client.connect(
                    hostname=dialog.host_input.text(),
                    port=int(dialog.port_input.text()),
                    username=dialog.username_input.text(),
                    password=dialog.password_input.text(),
                    timeout=10  # 添加超时设置
                )
                
                # 测试连接是否有效
                stdin, stdout, stderr = self.ssh_client.exec_command('echo "test"')
                if stdout.channel.recv_exit_status() != 0:
                    raise Exception("SSH connection test failed")
                
                # 保存连接信息
                self.last_connection = {
                    'host': dialog.host_input.text(),
                    'port': int(dialog.port_input.text()),
                    'username': dialog.username_input.text(),
                    'password': dialog.password_input.text()
                }
                # 启用重连按钮
                self.reconnect_btn.setEnabled(True)
                
                QMessageBox.information(self, '成功', '服务器连接成功！')
                self.status_label.setText(f"已连接到: {dialog.host_input.text()}")
                self.status_label.setStyleSheet("color: #27ae60; font-size: 14px;")
                self.statusBar().showMessage('服务器连接成功')
            except Exception as e:
                QMessageBox.critical(self, '错误', f'连接服务器失败: {str(e)}')
                if self.ssh_client:
                    self.ssh_client.close()
                self.ssh_client = None
                self.status_label.setText("连接失败")
                self.status_label.setStyleSheet("color: #e74c3c; font-size: 14px;")

    def deploy_website(self):
        """打开网站部署窗口"""
        if not self.ssh_client:
            QMessageBox.warning(self, '警告', '请先连接到服务器')
            return
        
        try:
            # 检查并安装必要的工具
            if not self.check_and_install_requirements(self.ssh_client):
                QMessageBox.warning(self, '警告', '缺少必要的工具，无法继续部署')
                return
            
            # 创建 DockerCompose 窗口，传入现有的 SSH 连接
            docker_window = DockerComposeWindow(ssh_client=self.ssh_client)
            # 保持窗口引用，防止被垃圾回收
            self.docker_window = docker_window
            docker_window.show()
        except Exception as e:
            QMessageBox.critical(self, '错误', f'打开部署窗口失败: {str(e)}')

    def manage_containers(self):
        if not self.ssh_client:
            QMessageBox.warning(self, '警告', '请先连接到服务器')
            return
        
        container_manager = ContainerManager(self.ssh_client, self)
        container_manager.exec_()

    def view_logs(self):
        """查看容器日志"""
        try:
            if not self.ssh_client or not self.ssh_client.get_transport() or not self.ssh_client.get_transport().is_active():
                QMessageBox.warning(self, '警告', '服务器连接已断开，请重新连接')
                self.ssh_client = None
                return
                
            # 直接获取容器列表
            stdin, stdout, stderr = self.ssh_client.exec_command('docker ps -a --format "{{.Names}}"')
            containers = stdout.read().decode().strip().split('\n')
            
            if not containers or not containers[0]:
                QMessageBox.warning(self, '警告', '没有找到任何容器')
                return
                
            # 创建日志查看对话框
            log_dialog = LogViewerDialog(self.ssh_client, containers, self)
            log_dialog.exec_()
                
        except paramiko.SSHException as e:
            QMessageBox.critical(self, '错误', f'SSH连接错误: {str(e)}')
            self.ssh_client = None
        except Exception as e:
            QMessageBox.critical(self, '错误', f'查看日志失败: {str(e)}')

    def logout(self):
        from login import LoginWindow
        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()

    def closeEvent(self, event):
        """关闭窗口时确保关闭 SSH 连接"""
        try:
            if self.ssh_client:
                self.ssh_client.close()
        except:
            pass
        event.accept()

    def refresh_containers(self):
        """刷新容器列表"""
        try:
            if not self.ssh_client:
                QMessageBox.warning(self, '警告', '请先连接到服务器')
                return
                
            stdin, stdout, stderr = self.ssh_client.exec_command('docker ps -a --format "{{.Names}}\t{{.Status}}"')
            containers = stdout.read().decode().strip().split('\n')
            
            self.container_table.setRowCount(0)  # 清空表格
            for container in containers:
                if not container:  # 跳过空行
                    continue
                    
                name, status = container.split('\t')
                row = self.container_table.rowCount()
                self.container_table.insertRow(row)
                self.container_table.setItem(row, 0, QTableWidgetItem(name))
                self.container_table.setItem(row, 1, QTableWidgetItem(status))
                
        except Exception as e:
            QMessageBox.critical(self, '错误', f'刷新容器列表失败: {str(e)}')

    def reconnect_server(self):
        """重新连接到上一次的服务器"""
        try:
            if hasattr(self, 'last_connection'):
                # 如果已经存在连接，先关闭它
                if self.ssh_client:
                    self.ssh_client.close()
                    
                # 创建新的 SSH 连接
                self.ssh_client = paramiko.SSHClient()
                self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                self.ssh_client.connect(
                    hostname=self.last_connection['host'],
                    port=self.last_connection['port'],
                    username=self.last_connection['username'],
                    password=self.last_connection['password'],
                    timeout=10
                )
                
                # 测试连接
                stdin, stdout, stderr = self.ssh_client.exec_command('echo "test"')
                if stdout.channel.recv_exit_status() != 0:
                    raise Exception("SSH connection test failed")
                    
                QMessageBox.information(self, '成功', '服务器重新连接成功！')
                self.status_label.setText(f"已连接到: {self.last_connection['host']}")
                self.status_label.setStyleSheet("color: #27ae60; font-size: 14px;")
                self.statusBar().showMessage('服务器连接成功')
                
            else:
                QMessageBox.warning(self, '警告', '没有找到上一次的连接信息，请使用连接服务器功能')
                
        except Exception as e:
            QMessageBox.critical(self, '错误', f'重新连接失败: {str(e)}')
            if self.ssh_client:
                self.ssh_client.close()
            self.ssh_client = None
            self.status_label.setText("连接失败")
            self.status_label.setStyleSheet("color: #e74c3c; font-size: 14px;")

    def check_and_install_requirements(self, ssh_client):
        """检查 unzip 工具是否已安装"""
        try:
            # 检查 unzip
            stdin, stdout, stderr = ssh_client.exec_command('which unzip')
            if stdout.read().decode().strip() == '':
                message = "请先安装 unzip 工具：\n\n"
                message += "• Ubuntu/Debian 系统：\n"
                message += "  sudo apt-get update\n"
                message += "  sudo apt-get install -y unzip\n\n"
                message += "• CentOS/RHEL 系统：\n"
                message += "  sudo yum install -y unzip\n"
                
                QMessageBox.warning(
                    self,
                    '缺少 unzip 工具',
                    message
                )
                return False

            return True

        except Exception as e:
            QMessageBox.critical(self, '错误', f'检查 unzip 工具安装状态失败: {str(e)}')
            return False

class LogViewerDialog(QDialog):
    def __init__(self, ssh_client, containers, parent=None):
        super().__init__(parent)
        self.ssh_client = ssh_client
        self.containers = containers
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle('容器日志查看器')
        self.setGeometry(100, 100, 1000, 700)
        
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # 顶部控制区域
        control_layout = QHBoxLayout()
        
        # 容器选择下拉框
        container_label = QLabel('选择容器:')
        container_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        control_layout.addWidget(container_label)
        
        self.container_combo = QComboBox()
        self.container_combo.addItems(self.containers)
        self.container_combo.setStyleSheet("""
            QComboBox {
                padding: 5px;
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                min-width: 200px;
                min-height: 30px;
            }
            QComboBox:focus {
                border-color: #2ecc71;
            }
        """)
        self.container_combo.currentIndexChanged.connect(self.load_logs)
        control_layout.addWidget(self.container_combo)
        
        # 日志行数输入
        tail_label = QLabel('显示行数:')
        tail_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        control_layout.addWidget(tail_label)
        
        self.tail_input = QLineEdit()
        self.tail_input.setPlaceholderText('默认 100 行')
        self.tail_input.setText('100')
        self.tail_input.setStyleSheet("""
            QLineEdit {
                padding: 5px;
                border: 2px solid #bdc3c7;
                border-radius: 4px;
                min-width: 100px;
                min-height: 30px;
            }
            QLineEdit:focus {
                border-color: #2ecc71;
            }
        """)
        control_layout.addWidget(self.tail_input)
        
        # 按钮组
        refresh_btn = QPushButton('刷新')
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 15px;
                font-weight: bold;
                min-width: 80px;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        refresh_btn.clicked.connect(self.refresh_logs)
        control_layout.addWidget(refresh_btn)
        
        export_btn = QPushButton('导出')
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 15px;
                font-weight: bold;
                min-width: 80px;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        export_btn.clicked.connect(self.export_logs)
        control_layout.addWidget(export_btn)
        
        control_layout.addStretch()
        layout.addLayout(control_layout)
        
        # 日志显示区域
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                font-family: Consolas, Monaco, monospace;
                font-size: 13px;
                padding: 10px;
                border-radius: 4px;
            }
        """)
        layout.addWidget(self.log_text)
        
        self.setLayout(layout)
        
        # 初始加载日志
        self.load_logs()
        
    def load_logs(self):
        """加载容器日志"""
        try:
            if not self.ssh_client:
                raise Exception("SSH 连接未建立")
                
            tail_lines = self.tail_input.text() or '100'
            command = f'docker logs --tail {tail_lines} {self.container_combo.currentText()}'
            
            # 添加超时处理
            stdin, stdout, stderr = self.ssh_client.exec_command(command, timeout=10)
            logs = stdout.read().decode() + stderr.read().decode()
            
            # 清空并设置新日志
            self.log_text.clear()
            self.log_text.append(logs)
            
            # 滚动到底部
            scrollbar = self.log_text.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
            
        except Exception as e:
            QMessageBox.critical(self, '错误', f'加载日志失败: {str(e)}')
            
    def refresh_logs(self):
        """刷新日志"""
        try:
            self.load_logs()
            QMessageBox.information(self, '成功', '日志已刷新')
        except Exception as e:
            QMessageBox.critical(self, '错误', f'刷新日志失败: {str(e)}')
            
    def export_logs(self):
        """导出日志到文件"""
        container = self.container_combo.currentText()
        if not container:
            return
            
        try:
            # 生成文件名
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{container}_logs_{timestamp}.txt"
            
            options = QFileDialog.Options()
            file_name, _ = QFileDialog.getSaveFileName(
                self,
                "导出日志",
                filename,
                "Text Files (*.txt);;All Files (*)",
                options=options
            )
            
            if file_name:
                with open(file_name, 'w', encoding='utf-8') as f:
                    f.write(self.log_text.toPlainText())
                QMessageBox.information(self, '成功', f'日志已导出到: {file_name}')
        except Exception as e:
            QMessageBox.critical(self, '错误', f'导出日志失败: {str(e)}')