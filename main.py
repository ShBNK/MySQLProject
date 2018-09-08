#!/usr/bin/env python
# -*- coding: utf-8 -*-

import MySQLdb
from PyQt4.QtGui import *
from PyQt4.QtCore import pyqtSlot
import sys
import datetime

HOST = 'localhost'
USER = 'nekit'
PASSWORD = 'my_password'
DATABASE = 'mydatabase'
today = datetime.date.today()

class Database:
	def __init__(self, host, user, password, database):
		self.connection = MySQLdb.connect(HOST, USER, PASSWORD, DATABASE, charset='utf8')
		self.cursor = self.connection.cursor()

	def request(self, request):
		self.cursor.execute(request)
		return self.cursor.fetchall()

	def close(self):
		self.connection.close()

class Window(QWidget):
	app = QApplication(sys.argv)
	def __init__(self):
		super(Window, self).__init__()
		self.database = Database(HOST, USER, PASSWORD, DATABASE)

		self.resize(600, 400)
		self.lastNameTextBox = QLineEdit(u"Фамилия", self)
		self.lastNameTextBox.move(10, 10)
		self.firstNameTextBox = QLineEdit(u"Имя", self)
		self.firstNameTextBox.move(10, 45)
		self.patrNameTextBox = QLineEdit(u"Отчество", self)
		self.patrNameTextBox.move(10, 80)
		self.birthdateTextBox = QLineEdit(u"ГГГГ-ММ-ЧЧ", self)
		self.birthdateTextBox.move(10, 115)
		self.sexTextBox = QLineEdit(u"Пол", self)
		self.sexTextBox.move(10, 150)
		self.healthTextBox = QLineEdit(u"Полис ОМС", self)
		self.healthTextBox.move(10, 185)
		self.docsTextBox = QLineEdit(u"Документ", self)
		self.docsTextBox.move(10, 220)

		self.refreshdb = QPushButton("Refresh database", self)
		self.refreshdb.move(350, 10)
		self.refreshdb.resize(200, 50)

		@pyqtSlot()
		def refresh_on_click():
			self.database.close()
			self.database = Database(HOST, USER, PASSWORD, DATABASE)

		self.search = QPushButton("Search", self)
		self.search.move(350, 200)
		self.search.resize(200, 50)

		@pyqtSlot()
		def search_on_click():
			self.searchWin = SearchWindow(self.database, self.lastNameTextBox.text().toUtf8(),\
										  self.firstNameTextBox.text().toUtf8(),\
										  self.patrNameTextBox.text().toUtf8(),\
										  self.birthdateTextBox.text().toUtf8(),\
										  self.sexTextBox.text().toUtf8(), \
										  self.healthTextBox.text().toUtf8(), \
										  self.docsTextBox.text().toUtf8())

		self.refreshdb.clicked.connect(refresh_on_click)
		self.search.clicked.connect(search_on_click)

		self.show()
		self.app.exec_()

class SearchWindow(QWidget):
	def __init__(self, database, *params):
		super(SearchWindow, self).__init__()
		self.table = QTableWidget()
		self.table.setWindowTitle("Result table")
		self.table.resize(870, 500)
		self.table.setRowCount(1000)
		self.table.setColumnCount(8)
		self.table.setHorizontalHeaderLabels([u"Фамилия", u'Имя', u'Отчество',\
											  u"Дата рождения", u"Возраст", u"Пол",\
											  u"Полис ОМС", u"Документы"])
		self.request = "SELECT Client.id, lastName, firstName, patrName, birthdate,\
						sex, ClientPolicy.serial, ClientPolicy.number, \
						ClientDocument.serial, ClientDocument.number\
						FROM Client INNER JOIN ClientPolicy INNER JOIN\
						ClientDocument WHERE Client.id = ClientPolicy.client_id and\
						Client.id = ClientDocument.client_id"
		if str(params[0]).decode('utf-8') != '':
			self.request += " and BINARY lastName = '{}'"\
							.format(str(params[0]).decode('utf-8'))
		if str(params[1]).decode('utf-8') != '':
			self.request += " and BINARY firstName = '{}'"\
							.format(str(params[1]).decode('utf-8'))
		if str(params[2]).decode('utf-8') != '':
			self.request += " and BINARY patrName = '{}'"\
							.format(str(params[2]).decode('utf-8'))
		if str(params[3]).decode('utf-8') != '':
			self.request += " and birthdate = '{}'"\
							.format(str(params[3]).decode('utf-8'))
		if str(params[4]).decode('utf-8') != '':
			self.request += " and sex = " + \
							('1' if str(params[4]).decode('utf-8') == u'М' else '2')
		if str(params[5]).decode('utf-8') != '':
			parsed = str(params[5]).decode('utf-8').split(' ')
			self.request += (" and BINARY ClientPolicy.serial = '{}'\
							 and ClientPolicy.number = '{}'".format(*parsed))
		if str(params[6]).decode('utf-8') != '':
			parsed = str(params[6]).decode('utf-8').split(' ')
			self.request += (" and BINARY ClientDocument.serial = '{} {}' \
							 and ClientDocument.number = '{}'".format(*parsed))
		print(self.request)
		self.data = database.request(self.request)
		if not self.data is ():
			for i, data in enumerate(self.data):
				self.table.setItem(i, 0, QTableWidgetItem(data[1]))
				self.table.setItem(i, 1, QTableWidgetItem(data[2]))
				self.table.setItem(i, 2, QTableWidgetItem(data[3]))
				self.table.setItem(i, 3, QTableWidgetItem(str(data[4])))
				self.table.setItem(i, 4, QTableWidgetItem(str(today.year - data[4].year - \
														  ((today.month, today.day) < \
														  (data[4].month, data[4].day))) \
														   + u' лет'))
				self.table.setItem(i, 5, QTableWidgetItem(u'М' if data[5] == 1 else u'Ж'))
				self.table.setItem(i, 6, QTableWidgetItem(data[6] + ' ' + data[7]))
				self.table.setItem(i, 7, QTableWidgetItem(data[8]+ ' ' + data[9]))
			self.table.resizeColumnsToContents()
		self.table.show()

window = Window()