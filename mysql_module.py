#!venv/Scripts/python.exe
# -*- coding: utf-8 -*-

import pymysql
import sys
from PyQt5 import QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QGridLayout, QLabel, QLineEdit, QMainWindow, QAction, QMessageBox, QPushButton, QStackedWidget, QVBoxLayout, qApp, QApplication, QDesktopWidget, QWidget)
from PyQt5.QtCore import Qt

class MySqlConnection:

	hostname = ""
	login = ""
	password = None

	def establish_connection(self):
		# try to establish connection or throw exception
		try:
			with pymysql.connect (
				host=self.hostname,
				user=self.login,
				password=self.password
			) as conn:
				self.connection = conn
				return True
		except pymysql.Error as err:
			return False
	
	def get_mysql_version(self):
		self.connection.ping()
		cursor = self.connection.cursor()
		cursor.execute('SELECT VERSION();')
		result = cursor.fetchone()[0]
		cursor.close() 
		return result
	

class MySqlApplication(QMainWindow):
	def __init__(self):
		super().__init__()

		self.connection = MySqlConnection()

		self.GUI_init()

		self.create_sub_windows()
		

	def GUI_init(self):

		# place main window
		center(self, 600, 600)

		# set window icon
		self.setWindowIcon(QIcon('static/py_db.png'))
		self.setWindowTitle('PyDB -- MySql')

		# connection menu
		self.connect_action = QAction(QIcon('static/link.png'), '&Connect', self)
		self.connect_action.setShortcut('Ctrl+Shift+c')
		self.connect_action.triggered.connect(self.open_connection_menu)

		self.check_version_action = QAction('&Get version', self)
		self.check_version_action.setShortcut('Ctrl+Shift+v')
		self.check_version_action.triggered.connect(self.get_version)
		
		self.disconnect_action = QAction('&Disconnect', self)
		self.disconnect_action.triggered.connect(self.disconnect)

		self.update_menu_disconnected()

		# set application main menu
		menu = self.menuBar()

		# add menu items
		fileMenu = menu.addMenu('&MySql')
		fileMenu.addAction(self.connect_action)
		fileMenu.addAction(self.disconnect_action)
		fileMenu.addAction(self.check_version_action)


		self.show()

	def get_version(self):
		message_box = QMessageBox()
		message_box.setIcon(QMessageBox.Information)
		message_box.setText(self.connection.get_mysql_version())
		message_box.exec_()

	def disconnect(self):
		self.connection = MySqlConnection()
		MsgUtils.msg_warn("Connection was canceled")
		# update menu items
		self.update_menu_disconnected()

	def create_sub_windows(self):
		# add layout box
		self.vbox = QVBoxLayout()
		# add new windows
		self.conn_window = MySqlConnectionWidget()
		self.conn_window.submit.clicked.connect(self.try_to_connect)

	def open_connection_menu(self, checked):
		if self.conn_window.isVisible():
			self.conn_window.hide()
		else:
			self.conn_window.show()

	def try_to_connect(self):
		w = self.conn_window

		if not w.hostname.text() or not w.user.text():
			MsgUtils.msg_warn("User and Hostname fields are required")
			return 0

		self.connection.hostname = w.hostname.text()
		self.connection.login = w.user.text()
		self.connection.password = w.password.text()

		if self.connection.establish_connection():
			MsgUtils.msg_info("Connection was successfully established")

			# update menu items
			self.update_menu_connected()

			self.conn_window.close()
		else:
			MsgUtils.msg_err(f"Error while trying to connect '{self.connection.login}'@'{self.connection.hostname}'")

	def closeEvent(self, event):
		QApplication.closeAllWindows()

	def update_menu_connected(self):
		self.connect_action.setEnabled(False)
		self.check_version_action.setEnabled(True)
		self.disconnect_action.setEnabled(True)
	
	def update_menu_disconnected(self):
		self.connect_action.setEnabled(True)
		self.disconnect_action.setEnabled(False)
		self.check_version_action.setEnabled(False)

class MySqlConnectionWidget(QWidget):
	"""
	This window responsble for mysql connection
	"""

	def __init__(self):
		super().__init__()

		center(self, 250, 150)

		self.setFixedHeight(150)
		self.setFixedWidth(250)

		self.init_UI()

	def init_UI(self):
		
		# create labels
		l_hostname = QLabel('Host')
		l_user = QLabel('User')
		l_password = QLabel('Password')

		# create form fields
		self.hostname = QLineEdit()
		self.user = QLineEdit()
		self.password = QLineEdit()
		self.password.setEchoMode(QLineEdit.Password)

		# create button
		self.submit = QPushButton('Connect', self)

		# create grid
		grid = QGridLayout()
		grid.setColumnStretch(0, 2)
		grid.setColumnStretch(1, 2)

		grid.addWidget(l_hostname, 1, 0, alignment=Qt.AlignCenter)
		grid.addWidget(self.hostname, 1, 1, alignment=Qt.AlignCenter)

		grid.addWidget(l_user, 2, 0, alignment=Qt.AlignCenter)
		grid.addWidget(self.user, 2, 1, alignment=Qt.AlignCenter)

		grid.addWidget(l_password, 3, 0, alignment=Qt.AlignCenter)
		grid.addWidget(self.password, 3, 1, alignment=Qt.AlignCenter)

		grid.addWidget(self.submit, 4, 1, alignment=Qt.AlignRight)

		self.setLayout(grid)
		self.setWindowTitle("Creating connection")


def center(widget, w, h):
	# get desktop obj
	desktop = QDesktopWidget().availableGeometry()
	# get center coords
	x, y = round(desktop.width() / 2), round(desktop.height() / 2)
	# center window
	widget.setGeometry(x - round(w / 2), y - round(h / 2), w, h)

class MsgUtils:
	@staticmethod
	def msg_warn(text):
		message_box = QMessageBox()
		message_box.setIcon(QMessageBox.Warning)
		message_box.setText(text)
		message_box.exec_()
		return message_box
	
	@staticmethod
	def msg_info(text):
		message_box = QMessageBox()
		message_box.setIcon(QMessageBox.Information)
		message_box.setText(text)
		message_box.exec_()
		return message_box

	@staticmethod
	def msg_err(text):
		message_box = QMessageBox()
		message_box.setIcon(QMessageBox.Critical)
		message_box.setText(text)
		message_box.exec_()
		return message_box
	

def main():
	app = QApplication(sys.argv)
	connection = MySqlConnection()
	mysql_window = MySqlApplication()
	sys.exit(app.exec_())

if __name__ == "__main__":
	main()