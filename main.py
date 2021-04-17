from db_api import dbAPI as db
from PyQt6 import QtWidgets as qw
from ui import Ui_MainWindow
import sys


class TheWindow(qw.QMainWindow):
    def __init__(self):
        # инициализация основного окна
        super(TheWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # инициализация БД приложения
        self.db = db()

        # назначение действий пунктов меню
        self.ui.menu.aboutToShow.connect(self.close)

        # заполнение названий таблиц в ComboBox
        self.ui.comboBox.addItems(self.db.get_tables())
        self.ui.comboBox.currentIndexChanged.connect(self.load_table)

        # загрузка данных из первой по списку таблицы
        self.load_table()

    def load_table(self):
        


if __name__ == '__main__':
    app = qw.QApplication([])
    application = TheWindow()
    application.show()

    sys.exit(app.exec())


