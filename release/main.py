import sys
from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem
import sqlite3
from main_design import Ui_MainWindow as MainWindow
from addEditCoffeeForm import Ui_MainWindow as OtherWindow


class Gui(QMainWindow, MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.title = ['Название сорта', 'Степень обжарки', 'Молотый/в зернах',
                      'Описание вкуса', 'Цена', 'Объем упаковки']
        self.colomns = [f'"{i}"' for i in self.title]
        self.request = f'SELECT {", ".join(self.colomns)} FROM Menu'
        self.con = sqlite3.connect('coffee.sqlite')
        self.cur = self.con.cursor()
        self.initUI()

    def initUI(self):
        self.load_table()
        self.pushButton.clicked.connect(self.change_table)

    def load_table(self):
        result = self.cur.execute(self.request).fetchall()

        # устанавливаем кол-во столбцов в таблице
        self.tableWidget.setColumnCount(len(self.title))

        # отображаем горизонтальные заголовки
        self.tableWidget.setHorizontalHeaderLabels(self.title)

        # устанавливаем кол-во строк в таблице
        self.tableWidget.setRowCount(0)
        for i, row in enumerate(result):
            self.tableWidget.setRowCount(self.tableWidget.rowCount() + 1)
            for j, elem in enumerate(row):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(elem)))
                self.tableWidget.item(i, j).setFlags(self.tableWidget.item(i, j).flags()&~QtCore.Qt.ItemIsEditable)

        self.tableWidget.resizeColumnsToContents()

    def change_table(self):
        data_change = DataChange(self, self.cur, self.con)
        data_change.show()

    def closeEvent(self, event):
        # При закрытии программы потверждаем изменения в БД и закрываем её
        self.con.commit()
        self.con.close()
        event.accept()


class DataChange(QMainWindow, OtherWindow):
    def __init__(self, parent, cur, con):
        super().__init__(parent)
        self.setupUi(self)
        self.cur = cur
        self.con = con
        self.initUI()

    def initUI(self):
        self.comboBox.addItems([str(i) for i in range(
            1, len(self.cur.execute(self.parent().request).fetchall()) + 1)])

        self.radioButton_2.toggled.connect(self.disable_combo_box)
        self.comboBox.currentTextChanged.connect(self.load_string)
        self.pushButton.clicked.connect(self.confirm)

        self.tableWidget.setColumnCount(len(self.parent().title))
        self.tableWidget.setHorizontalHeaderLabels(self.parent().title)

        self.load_string()

    def disable_combo_box(self):
        if self.radioButton_2.isChecked():
            self.comboBox.setDisabled(True)
            self.tableWidget.setRowCount(0)
        else:
            self.comboBox.setDisabled(False)
        self.load_string()

    def load_string(self):
        if self.radioButton_2.isChecked():
            result = [['' for i in range(6)]]
        else:
            result = self.cur.execute(
                f'{self.parent().request} WHERE ID = {self.comboBox.currentText()}').fetchall()
        self.tableWidget.setRowCount(1)
        for j, elem in enumerate(result[0]):
            self.tableWidget.setItem(0, j, QTableWidgetItem(str(elem)))
        self.tableWidget.resizeColumnsToContents()

    def confirm(self):
        if not all([self.tableWidget.item(0, i).text() for i in range(6)]):
            self.statusBar.showMessage('Пустые ячейки не допустимы')
            return
        self.statusBar.showMessage('')
        if self.radioButton.isChecked():
            for i in range(6):
                self.cur.execute(
                    f'''UPDATE Menu 
                        SET {self.parent().colomns[i]} = '{self.tableWidget.item(0, i).text()}'
                        WHERE ID = {self.comboBox.currentText()}''')
        else:
            self.cur.execute(f"""INSERT INTO Menu({', '.join(self.parent().colomns)})
                                 VALUES({', '.join([self.tableWidget.item(0, i).text() for i in range(6)])})""")
        self.con.commit()
        self.parent().load_table()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


app = QApplication(sys.argv)
ex = Gui()
ex.show()
sys.excepthook = except_hook
sys.exit(app.exec_())
