import yaml  # 确保安装了 pyyaml 库: pip install pyyaml
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QLabel, QMessageBox, QComboBox


class PortConfigurationDialog(QDialog):
    def __init__(self, docker_compose_path, ssh_client, parent=None):
        super().__init__(parent)
        self.docker_compose_path = docker_compose_path
        self.ssh_client = ssh_client
        self.initUI()
        self.load_current_ports()  # 加载当前端口

    def initUI(self):
        self.setWindowTitle("修改 Docker Compose 端口")
        self.setGeometry(200, 200, 400, 200)  # 增加高度以适应更多控件

        layout = QVBoxLayout()
        form_layout = QFormLayout()

        self.service_name_input = QComboBox(self)  # 使用下拉框选择服务
        self.service_name_input.setPlaceholderText("选择服务名")
        form_layout.addRow(QLabel("服务名:"), self.service_name_input)

        self.port_input = QLineEdit(self)
        self.port_input.setPlaceholderText("输入新主机端口 (例如: 3000)")
        form_layout.addRow(QLabel("新主机端口:"), self.port_input)

        layout.addLayout(form_layout)

        self.submit_button = QPushButton("更新端口", self)  # 更明确的按钮标签
        self.submit_button.clicked.connect(self.save_ports)
        layout.addWidget(self.submit_button)

        self.status_label = QLabel("", self)  # 添加状态消息标签
        layout.addWidget(self.status_label)

        self.setLayout(layout)

        # 设置控件的样式
        self.setStyleSheet("""  
            QDialog {  
                background-color: #E8F0F2;  
            }  
            QPushButton {  
                background-color: #66CDAA;  
                color: white;  
                border: none;  
                padding: 10px;  
                border-radius: 5px;  
                margin: 5px;  
            }  
            QPushButton:hover {  
                background-color: #4CAF50;  
            }  
            QLabel {  
                font-weight: bold;  
                color: #333;  
            }  
            QLineEdit {  
                border: 1px solid #ccc;  
                border-radius: 5px;  
                padding: 5px;  
                font-size: 14px;  
                color: #333;  
            }  
            QComboBox {  
                border: 1px solid #ccc;  
                border-radius: 5px;  
                padding: 5px;  
                font-size: 14px;  
                color: #333;  
            }  
        """)

    def load_current_ports(self):
        """加载当前端口设置"""
        try:
            with self.ssh_client.open_sftp() as sftp:
                with sftp.open(self.docker_compose_path, 'r') as file:
                    compose_data = yaml.safe_load(file)

            # 假设服务定义在 compose_data['services'] 中
            for service in compose_data['services'].keys():
                self.service_name_input.addItem(service)

            # 默认选择第一个服务
            self.service_name_input.setCurrentIndex(0)
            self.update_port_input()  # 更新端口输入框

        except Exception as e:
            QMessageBox.critical(self, "加载当前端口错误", str(e))

    def update_port_input(self):
        """更新端口输入框"""
        service_name = self.service_name_input.currentText()
        if service_name:
            try:
                with self.ssh_client.open_sftp() as sftp:
                    with sftp.open(self.docker_compose_path, 'r') as file:
                        compose_data = yaml.safe_load(file)

                existing_ports = compose_data['services'][service_name].get('ports', [])
                if existing_ports:
                    host_port = existing_ports[0].split(':')[0]  # 获取主机端口
                    self.port_input.setText(host_port)
                else:
                    self.port_input.clear()  # 未找到端口时清空
            except Exception as e:
                QMessageBox.warning(self, "错误", f"无法加载端口设置: {str(e)}")

    def validate_port(self, port):
        """验证端口格式是否正确"""
        return port.isdigit() and 0 < int(port) <= 65535  # 端口范围 1-65535

    def save_ports(self):
        new_host_port = self.port_input.text().strip()
        service_name = self.service_name_input.currentText()

        if not service_name:
            QMessageBox.warning(self, "警告", "请选择服务名。")
            return

        if not self.validate_port(new_host_port):
            QMessageBox.warning(self, "输入错误", "请输入有效的主机端口 (1-65535)。")
            return

        try:
            if self.ssh_client is None or not self.ssh_client.get_transport().is_active():
                QMessageBox.warning(self, "连接错误", "SSH连接已关闭或未连接，请重新连接。")
                return

            # 给 docker-compose.yml 文件添加可写权限
            chmod_command = f"chmod +w {self.docker_compose_path}"
            stdin, stdout, stderr = self.ssh_client.exec_command(chmod_command)
            if stderr.read().decode():
                QMessageBox.warning(self, "权限错误", f"无法修改权限: {stderr.read().decode()}")
                return

            # 读取 docker-compose.yml 文件
            with self.ssh_client.open_sftp() as sftp:
                with sftp.open(self.docker_compose_path, 'r') as file:
                    compose_data = yaml.safe_load(file)

            # 更新指定服务的主机端口
            if service_name in compose_data['services']:
                existing_ports = compose_data['services'][service_name].get('ports', [])
                if existing_ports:
                    container_port = existing_ports[0].split(':')[1]  # 获取容器端口
                    compose_data['services'][service_name]['ports'] = [f"{new_host_port}:{container_port}"]  # 更新主机端口
                else:
                    QMessageBox.warning(self, "错误", "未找到任何端口设置。")
                    return
            else:
                QMessageBox.warning(self, "错误", f"未找到服务名为 '{service_name}' 的配置。")
                return

            # 将更新后的内容写回到 docker-compose.yml 文件
            with self.ssh_client.open_sftp() as sftp:
                with sftp.open(self.docker_compose_path, 'w') as file:
                    yaml.dump(compose_data, file)

            QMessageBox.information(self, "成功", "主机端口已成功更新。")
            self.status_label.setText(f"主机端口已更新为: {new_host_port}")

        except Exception as e:
            QMessageBox.critical(self, "保存端口错误", str(e))


