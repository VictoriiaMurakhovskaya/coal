from db_api import dbAPI
from PyQt6 import QtWidgets as qw
from PyQt6.QtSql import QSqlTableModel, QSqlDatabase, QSqlQueryModel
from ui import Ui_MainWindow
from sql_res import Ui_Form as q_form
import sys
from PyQt6.QtWidgets import QInputDialog


class TheWindow(qw.QMainWindow):
    """
    Класс графического интерфейса программы
    """
    def __init__(self):
        """
        Конструктор основного окна программы
        """
        # инициализация основного окна
        super(TheWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # инициализация БД приложения (работа с PyQt)
        self.qtdb = QSqlDatabase.addDatabase('QSQLITE')
        self.qtdb.setDatabaseName('assets/coal.db')
        if not self.qtdb.open():
            print(self.qtdb.lastError().text())
            sys.exit(1)

        # инициализация модели (MVC паттерн)
        self.model = QSqlTableModel(self)
        self.model.setEditStrategy(QSqlTableModel.EditStrategy.OnManualSubmit)
        self.model.setTable('coal_table')
        self.model.select()

        # инициализация представления (MVC паттерн)
        self.ui.tableView.setModel(self.model)
        self.ui.tableView.show()

        # назначение действий пунктов меню
        self.ui.menu.aboutToShow.connect(self.on_exit)

        for item in [self.ui.action, self.ui.action_2, self.ui.action_3,
                     self.ui.action_4, self.ui.action_5]:
            item.triggered.connect(self.query)

        for item in [self.ui.action_6, self.ui.action_7]:
            item.triggered.connect(self.report)

        # заполнение ComboBox с таблицами, создание слота
        db = dbAPI()
        self.ui.comboBox.addItems(db.get_tables())
        self.ui.comboBox.currentIndexChanged.connect(self.load_table)

        # назначение действия кнопок
        self.ui.createButton.clicked.connect(self.insert_row)
        self.ui.readButton.clicked.connect(self.read_db)
        self.ui.updateButton.clicked.connect(self.update_db)
        self.ui.deleteButton.clicked.connect(self.delete_row)

    def load_table(self):
        """
        Загрузка таблицы данных инструментами PyQt
        :return: None
        """
        self.model.setTable(self.ui.comboBox.currentText())
        self.model.select()
        self.ui.tableView.setModel(self.model)
        self.ui.tableView.show()

    def insert_row(self):
        """
        Операция CREATE
        :return: None
        """
        self.model.insertRow(self.model.rowCount())

    def read_db(self):
        """
        Чтение данных из выбранной таблицы
        Несохраненные (UPDATE) изменения в БД теряются
        :return: None
        """
        self.model.select()

    def update_db(self):
        """
        Обновление БД согласно представления
        :return: None
        """
        self.model.submitAll()

    def delete_row(self):
        """
        Пометка на удаление записи
        Окончательное удаление происходит после UPDATE
        :return: None
        """
        self.model.removeRow(self.ui.tableView.currentIndex().row())

    def query(self):
        query_name = self.sender().text()
        if query_name == 'Объем добычи':
            p_name = 'Номер месяца'
            p_func = QInputDialog.getInt
        elif query_name == 'Список должностей':
            p_name = 'Номер участка'
            p_func = QInputDialog.getInt
        elif query_name == 'Начисление зарплаты':
            p_name = 'Номер месяца'
            p_func = QInputDialog.getText
        elif query_name == 'Список ПФ':
            p_name = 'Номер участка'
            p_func = QInputDialog.getInt
        elif query_name == 'Список работников':
            p_name = 'Префикс номера'
            p_func = QInputDialog.getText
        else:
            raise ValueError("Недопустимое название отчета")
        value, ok = p_func(self, 'Ввод параметра', p_name)
        if ok:
            sqlq = QSqlQueryModel(self)
            qui = TheQResult(self)
            qui.ui.tableView.setModel(sqlq)
            sqlq.setQuery("SELECT id from coal_table")
            qui.ui.tableView.show()
            qui.show()

    def report(self):
        print(self.sender().text())

    def on_exit(self):
        self.qtbd.close()
        sys.exit(0)


class TheQResult(qw.QDialog):
    def __init__(self, parent):
        qw.QDialog.__init__(self, parent=parent)
        self.ui = q_form()
        self.ui.setupUi(self)
        self.ui.pushButton.clicked.connect(self.close)


if __name__ == '__main__':
    app = qw.QApplication([])
    application = TheWindow()
    application.show()

    sys.exit(app.exec())


