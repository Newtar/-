import sys
import paramiko
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QLineEdit, QPushButton, QTextEdit, QFileDialog, QSizePolicy, QAction, QProgressDialog, QMessageBox, QHBoxLayout, QGroupBox, QFrame, QLabel
from PyQt5.QtCore import Qt
from port_configuration_dialog import PortConfigurationDialog
class DockerComposeWindow(QMainWindow):
    def __init__(self, ssh_client=None):
        super().__init__()
        self.ssh_client = ssh_client
        self.docker_compose_path = None
        self.buttons = {}  # 添加按钮字典来存储按钮引用
        self.initUI()
        self.init_menus()
        
        if not self.ssh_client:
            self.connect_to_vm(host='124.221.42.138', port=22, username='root', password='Wx523040!')

    def initUI(self):
        self.setWindowTitle('Docker Compose 项目部署')
        self.setGeometry(100, 100, 800, 600)

        # 创建中央部件
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # 顶部标题区域
        title_widget = QWidget()
        title_layout = QHBoxLayout(title_widget)
        
        icon_label = QLabel("🐳")
        icon_label.setStyleSheet("font-size: 36px;")
        title_layout.addWidget(icon_label)
        
        title_label = QLabel("Docker Compose 项目部署")
        title_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
            margin-left: 10px;
        """)
        title_layout.addWidget(title_label)
        title_layout.addStretch()
        main_layout.addWidget(title_widget)

        # 添加分隔线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background-color: #bdc3c7;")
        main_layout.addWidget(line)

        # 项目配置区域
        config_group = QGroupBox("项目配置")
        config_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                border: 2px solid #bdc3c7;
                border-radius: 6px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        config_layout = QVBoxLayout(config_group)

        # 路径输入框
        path_widget = QWidget()
        path_layout = QHBoxLayout(path_widget)
        path_layout.setContentsMargins(0, 0, 0, 0)
        
        self.port_input = QLineEdit()
        self.port_input.setPlaceholderText("输入解压目录的路径（默认为 /tmp/）...")
        self.port_input.setStyleSheet("""
            QLineEdit {
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                background-color: white;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #3498db;
            }
        """)
        path_layout.addWidget(self.port_input)
        config_layout.addWidget(path_widget)

        # 操作按钮区域
        buttons_widget = QWidget()
        buttons_layout = QHBoxLayout(buttons_widget)
        buttons_layout.setSpacing(10)

        # 定义按钮信息：(文本, 图标, 处理函数, 按钮ID)
        buttons_info = [
            ("上传文件", "📤", self.upload_and_extract_zip, 'upload_button'),
            ("修改端口", "🔧", self.open_port_configuration, 'modify_port_button'),
            ("部署项目", "🚀", self.quick_start_docker, 'quick_start_button'),
            ("停止运行", "⏹️", self.quick_stop_docker, 'stop_container_button')
        ]

        for text, icon, handler, btn_id in buttons_info:
            btn = QPushButton(f"{icon} {text}")
            btn.setMinimumHeight(40)
            btn.clicked.connect(handler)
            buttons_layout.addWidget(btn)
            self.buttons[btn_id] = btn  # 保存按钮引用

        config_layout.addWidget(buttons_widget)
        main_layout.addWidget(config_group)

        # 终端输出区域
        terminal_group = QGroupBox("终端输出")
        terminal_group.setStyleSheet(config_group.styleSheet())
        terminal_layout = QVBoxLayout(terminal_group)

        self.response_area = QTextEdit()
        self.response_area.setReadOnly(True)
        self.response_area.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #ffffff;
                border: none;
                border-radius: 5px;
                padding: 10px;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 13px;
            }
        """)
        terminal_layout.addWidget(self.response_area)

        # 命令输入区域
        command_widget = QWidget()
        command_layout = QHBoxLayout(command_widget)
        command_layout.setContentsMargins(0, 0, 0, 0)
        
        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("输入命令...")
        self.command_input.setStyleSheet(self.port_input.styleSheet())
        command_layout.addWidget(self.command_input)
        
        execute_btn = QPushButton("执行")
        execute_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        execute_btn.clicked.connect(self.execute_command)
        command_layout.addWidget(execute_btn)
        self.buttons['execute_button'] = execute_btn  # 保存执行按钮引用
        
        terminal_layout.addWidget(command_widget)
        main_layout.addWidget(terminal_group)

        # 应用整体样式
        self.apply_window_styles()
        
        # 检查 SSH 连接状态并更新按钮状态
        if not self.ssh_client:
            self.response_area.append("⚠️ 警告: SSH 连接未建立，部分功能可能无法使用")
        else:
            self.response_area.append("✅ SSH 连接已就绪")
        
        self.update_buttons_state()

    def apply_window_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f6fa;
            }
            QPushButton {
                background-color: #2ecc71;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-size: 14px;
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
        """)

    def connect_to_vm(self, host, port, username, password):
        """连接到虚拟机的 SSH 服务器"""
        self.ssh_client = paramiko.SSHClient()
        self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        try:
            self.ssh_client.connect(hostname=host, port=port, username=username, password=password)
            self.response_area.append("成功连接到虚拟机")
        except Exception as e:
            self.response_area.append(f"连接错误: {e}")

    def init_menus(self):
        menu_bar = self.menuBar()
        menu_bar.setStyleSheet("""  
                    QMenuBar {  
                        background-color: #f0f0f0; /* 背景颜色 */  
                    }  
                    QMenuBar::item {  
                        background-color: #f0f0f0; /* 默认项颜色 */  
                        padding: 5px 15px; /* 内边距 */  
                    }  
                     QMenu::item:selected {  
                    background-color: #4CAF50; /* 悬浮背景颜色 */  
                    }  
                """)
        # 文件菜单
        file_menu = menu_bar.addMenu('文件')
        exit_action = QAction('退出', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # 连接菜单
        connect_menu = menu_bar.addMenu('连接')
        reconnect_action = QAction('重新连接', self)
        reconnect_action.triggered.connect(self.reconnect)
        connect_menu.addAction(reconnect_action)

        # 项目菜单
        project_menu = menu_bar.addMenu('项目')
        open_project_action = QAction('上传文件', self)
        open_project_action.triggered.connect(self.open_project)
        project_menu.addAction(open_project_action)

        # 工具菜单
        tools_menu = menu_bar.addMenu('工具')
        save_log_action = QAction('保存日志', self)
        save_log_action.triggered.connect(self.save_log)
        tools_menu.addAction(save_log_action)

        clear_output_action = QAction('清除输出', self)
        clear_output_action.triggered.connect(self.clear_output)
        tools_menu.addAction(clear_output_action)

        # 帮助菜单
        help_menu = menu_bar.addMenu('帮助')
        about_action = QAction('关于', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)

    def save_log(self):
        """保存输出日志到文件"""
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getSaveFileName(self, "保存日志", "", "Text Files (*.txt)", options=options)
        if file_name:
            try:
                with open(file_name, "w") as file:
                    file.write(self.response_area.toPlainText())
                    self.response_area.append(f"日志已保存到: {file_name}")
            except Exception as e:
                self.show_error("保存错误", f"保存日志时发生错误: {e}")

    def clear_output(self):
        """清除响应区的输出"""
        self.response_area.clear()
        self.response_area.append("输出已清除。")

    def reconnect(self):
        """重新连接到指定虚拟机"""
        if self.ssh_client:
            self.ssh_client.close()
        self.connect_to_vm(host='124.221.42.138', port=22, username='root', password='Wx523040!')

    def open_project(self):
        """打开项目功能，上传文件到服务器的 /tmp 目录"""
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "打开项目文件", "", "All Files (*);;Text Files (*.txt)", options=options)
        if file_name:
            self.upload_file(file_name)

    def upload_file(self, local_file_path):
        """上传文件到服务器的 /tmp 目录"""
        remote_file_path = f"/tmp/{os.path.basename(local_file_path)}"
        try:
            # 显示进度对话框
            progress_dialog = QProgressDialog("上传中...", "取消", 0, 0, self)
            progress_dialog.setWindowModality(Qt.WindowModal)
            progress_dialog.setCancelButton(None)  # 隐藏取消按钮
            progress_dialog.show()

            # 使用 SFTP 上传文件
            sftp = self.ssh_client.open_sftp()
            sftp.put(local_file_path, remote_file_path)
            sftp.close()
            progress_dialog.close()  # 关闭进度对话框
            self.response_area.append(f"文件已上传到: {remote_file_path}")
        except Exception as e:
            self.show_error("上传错误", f"上传文件时发生错误: {e}")

    def show_about(self):
        """关于对话框"""
        QMessageBox.about(self, "关于", "本项目旨在开发一个基于PyQt5的容器化部署网站工具，提供用户友好的图形界面以简化容器化应用的管理和部署。该工具支持通过SSH连接到远程虚拟机，执行命令，并能够部署DockerCompose类项目。")

    def show_error(self, title, message):
        """显示错误对话框"""
        QMessageBox.critical(self, title, message)
    def execute_command(self):
        """执行用户输入的命令并返回结果"""
        command = self.command_input.text().strip()
        if not command or not self.ssh_client:
            self.response_area.append("请先连接到虚拟机或输入有效命令。")
            return

        try:
            stdin, stdout, stderr = self.ssh_client.exec_command(command)
            response = stdout.read().decode() + stderr.read().decode()
            if response:
                self.response_area.append(response)
            else:
                self.response_area.append("命令无输出。")
        except Exception as e:
            self.response_area.append(f"执行命令时出错: {e}")

    def upload_and_extract_zip(self):
        """选择 ZIP 文件并上传到服务器，随后解压到指定目录。"""
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "选择 ZIP 文件", "", "ZIP 文件 (*.zip)", options=options)
        if file_name:
            try:
                self.upload_file_to_server(file_name)
                remote_file_name = os.path.basename(file_name)
                extract_path = self.port_input.text().strip() or "/tmp"  # 默认解压到/tmp
                self.extract_zip_on_server(remote_file_name, extract_path)  # 解压缩
            except Exception as e:
                self.response_area.append(f"文件处理错误: {e}")

    def upload_file_to_server(self, local_file_path):
        """将文件上传到服务器"""
        if not self.ssh_client:
            self.response_area.append("SSH 客户端未连接。")
            return

        try:
            sftp_client = self.ssh_client.open_sftp()
            remote_file_path = f"/tmp/{os.path.basename(local_file_path)}"  # 上传到服务器的路径
            self.response_area.append(f"正在上传文件到: {remote_file_path}")
            sftp_client.put(local_file_path, remote_file_path)  # 上传文件
            sftp_client.close()
            self.response_area.append(f"成功上传文件到服务器: {remote_file_path}")
        except FileNotFoundError:
            self.response_area.append("文件未找到，请确认文件路径。")
        except PermissionError:
            self.response_area.append("权限错误，无法上传文件。")
        except Exception as e:
            self.response_area.append(f"文件上传错误: {e}")

    def extract_zip_on_server(self, remote_zip_file_name, extract_path):
        """在服务器上解压 ZIP 文件到指定的目录"""
        try:
            command = f"unzip /tmp/{remote_zip_file_name} -d {extract_path}"  # 解压缩到指定目录
            stdin, stdout, stderr = self.ssh_client.exec_command(command)
            response = stdout.read().decode() + stderr.read().decode()
            if response:
                self.response_area.append(f"解压结果:\n{response}")
            else:
                self.response_area.append("解压命令无输出。")
        except Exception as e:
            self.response_area.append(f"解压错误: {e}")

    def open_port_configuration(self):
        """打开端口配置对话框"""
        # 使用用户输入的解压路径查找 docker-compose.yml
        input_path = self.port_input.text().strip() or "/tmp"  # 如果没有输入，则使用默认路径/tmp
        find_command = f"find {input_path} -name 'docker-compose.yml' 2>/dev/null"  # 在用户指定的目录中查找并忽略错误输出

        try:
            self.response_area.append("正在查找 docker-compose 路径...")
            stdin, stdout, stderr = self.ssh_client.exec_command(find_command)
            self.docker_compose_path = stdout.read().decode().strip()  # 读取并清理路径
            if stderr.read().decode():  # 检查是否有错误输出
                self.response_area.append(f"查找 docker-compose 出错: {stderr.read().decode()}")
                return

            if not self.docker_compose_path:
                self.response_area.append("未找到 docker-compose.yml。")
                return

            self.response_area.append(f"找到 docker-compose.yml 在: {self.docker_compose_path}")

            if self.docker_compose_path:
                dialog = PortConfigurationDialog(self.docker_compose_path, self.ssh_client, self)
                dialog.exec_()
            else:
                self.response_area.append("未找到 docker-compose.yml 文件，请上传文件。")
        except Exception as e:
            self.response_area.append(f"查找 docker-compose.yml 失败: {e}")

    def quick_start_docker(self):
        """快速启动 Docker-compose"""
        if not self.ssh_client:
            self.response_area.append("未连接到SSH服务器，无法执行。")
            return

        try:
            # 确保 docker-compose 有执行权限
            chmod_command = f"chmod +x {self.docker_compose_path}"
            stdin, stdout, stderr = self.ssh_client.exec_command(chmod_command)
            if stderr.read().decode():  # 检查是否有错误输出
                self.response_area.append(f"授权 docker-compose 出错: {stderr.read().decode()}")
                return

            self.response_area.append(f"已成功授权 docker-compose 执行权限。")

            # 确定 docker-compose.yml 文件所在目录
            compose_dir = os.path.dirname(self.docker_compose_path)  # 获取父目录
            self.response_area.append(f"当前 docker-compose 路径: {self.docker_compose_path}")
            # 切换到 docker-compose 文件所在目录并启动服务
            command = f"cd {compose_dir} && docker-compose up -d"
            self.response_area.append(f"正在执行快速启动命令: {command}")

            stdin, stdout, stderr = self.ssh_client.exec_command(command)
            response = stdout.read().decode() + stderr.read().decode()

            if response:
                self.response_area.append(response)
                self.response_area.append("成功部署项目，您可以访问项目地址")  # 提示访问地址
            else:
                self.response_area.append("快速启动命令无输出。")
        except Exception as e:
            self.response_area.append(f"快速启动命令出错: {e}")

    def quick_stop_docker(self):
        """停止 Docker-compose"""
        if not self.ssh_client:
            self.response_area.append("未连接到SSH服务器，无法执行。")
            return

        try:
            command = f"cd {os.path.dirname(self.docker_compose_path)} && docker-compose down"
            self.response_area.append(f"正在执行停止命令: {command}")

            stdin, stdout, stderr = self.ssh_client.exec_command(command)
            response = stdout.read().decode() + stderr.read().decode()

            if response:
                self.response_area.append(response)
                self.response_area.append("成功停止项目。")
            else:
                self.response_area.append("停止命令无输出。")
        except Exception as e:
            self.response_area.append(f"停止项目时出错: {e}")

    def closeEvent(self, event):
        """关闭窗口时关闭 SSH 连接"""
        if self.ssh_client:
            self.ssh_client.close()
        event.accept()

    def create_style_sheet(self, bg_color, hover_color):
        """创建按钮样式表"""
        return f"""  
            QPushButton {{  
                background-color: {bg_color};  
                color: white;  
                padding: 10px;  
                border: none;  
                border-radius: 5px;  
                font-size: 16px;  
            }}  
            QPushButton:hover {{  
                background-color: {hover_color};  
            }}  
        """

    def update_buttons_state(self):
        """更新按钮状态"""
        has_connection = self.ssh_client is not None
        for btn in self.buttons.values():
            btn.setEnabled(has_connection)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    client = DockerComposeWindow()
    client.show()
    sys.exit(app.exec_())
