import sys
from PyQt5 import uic, QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem
import sqlite3


class MyWidget(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main.ui', self)
        self.load_table()

    def load_table(self):
        con = sqlite3.connect('coffee.sqlite')
        cur = con.cursor()
        result = cur.execute('SELECT * FROM Menu').fetchall()
        con.close()

        # получаем первую строку из csv-файла
        title = ['ID', 'название сорта', 'степень обжарки', 'молотый/в зернах',
                 'описание вкуса', 'цена', 'объем упаковки']

        # устанавливаем кол-во столбцов в таблице
        self.tableWidget.setColumnCount(len(title))

        # отображаем горизонтальные заголовки
        self.tableWidget.setHorizontalHeaderLabels(title)

        # устанавливаем кол-во строк в таблице
        self.tableWidget.setRowCount(0)
        for i, row in enumerate(result):
            self.tableWidget.setRowCount(self.tableWidget.rowCount() + 1)
            for j, elem in enumerate(row):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(elem)))
                self.tableWidget.item(i, j).setFlags(self.tableWidget.item(i, j).flags()&~QtCore.Qt.ItemIsEditable)

        self.tableWidget.resizeColumnsToContents()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


app = QApplication(sys.argv)
ex = MyWidget()
ex.show()
sys.excepthook = except_hook
sys.exit(app.exec_())
