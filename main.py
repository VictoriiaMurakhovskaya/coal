from db_api import dbAPI
from PyQt6 import QtWidgets as qw
from PyQt6.QtSql import QSqlTableModel, QSqlDatabase, QSqlQueryModel, QSqlQuery
from ui import Ui_MainWindow
from sql_res import Ui_Form as q_form
from report import Ui_Dialog as r_form
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
        self.ui.action_8.triggered.connect(self.on_exit)

        for item in [self.ui.action, self.ui.action_2, self.ui.action_3,
                     self.ui.action_4, self.ui.action_5]:
            item.triggered.connect(self.query)

        for item in [self.ui.action_6, self.ui.action_7, self.ui.action_9]:
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
        """
        Осуществление запроса и отображение результатов запроса
        :return: None
        """

        query_name = self.sender().text()
        qry = QSqlQuery()

        # определение данных запроса параметра
        if query_name == 'Объем добычи':
            p_name = 'Номер месяца'
            p_func = QInputDialog.getInt
        elif query_name == 'Список должностей':
            p_name = 'Номер участка'
            p_func = QInputDialog.getInt
        elif query_name == 'Начисление зарплаты':
            p_name = 'Номер сотрудника'
            p_func = QInputDialog.getText
        elif query_name == 'Список ПФ':
            p_name = 'Номер участка'
            p_func = QInputDialog.getInt
        elif query_name == 'Список работников':
            p_name = 'Префикс номера'
            p_func = QInputDialog.getText
        else:
            raise ValueError("Недопустимое название отчета")

        # диалог запроса параметра
        value, ok = p_func(self, 'Ввод параметра', p_name)

        # если нажато Ок - формируется и осуществляется запрос, выводится результат
        if ok:
            if query_name == 'Объем добычи':
                qry.prepare("""SELECT date, SUM(volume) FROM production
                               WHERE strftime('%m', date) is :param
                               GROUP BY date
                               """)
                qry.bindValue(':param', '0' + str(value) if value < 10 else str(value))
            elif query_name == 'Список должностей':
                qry.prepare("""SELECT position_code, name FROM employees
                               INNER JOIN position on position.id = employees.position_code
                               WHERE area_code is :param
                               GROUP BY position_code
                               """)
                qry.bindValue(':param', str(value))
            elif query_name == 'Начисление зарплаты':
                qry.prepare("""SELECT full_name, date, SUM(volume), cost, SUM(volume) * cost FROM employees
                               INNER JOIN production on production.area_code = employees.area_code
                               INNER JOIN coal_table on coal_table.id = production.coal_id
                               WHERE strftime('%m', date) is strftime('%m', 'now') AND code is :param
                               GROUP BY date
                               """)
                qry.bindValue(':param', str(value))
            elif query_name == 'Список ПФ':
                qry.prepare("""SELECT name FROM employees
                               INNER JOIN pf on pf.id = employees.pf_code
                               WHERE area_code is :param
                               GROUP BY pf_code
                               """)
                qry.bindValue(':param', value)
            elif query_name == 'Список работников':
                qry.prepare("""SELECT full_name, phone FROM employees
                               WHERE phone LIKE :param
                               """)
                qry.bindValue(':param', value+'%')
            qry.exec()
            sqlq = QSqlQueryModel(self)
            qui = TheQResult(self)
            qui.ui.tableView.setModel(sqlq)
            sqlq.setQuery(qry)
            qui.ui.tableView.show()
            qui.show()

    def report(self):
        report_name = self.sender().text()
        qry = QSqlQuery()
        if report_name == 'Табель':
            rui = TheReport(self, query=qry, text1='Месяц', text2='Участок')
            qry.prepare("""SELECT date, full_name, hours from h_report                          
                           INNER JOIN employees on employees.code = h_report.emp_code
                           WHERE strftime('%m', date) is :param1 AND h_report.area_code is :param2
                           ORDER BY date
                        """)
        elif report_name == 'Добыча':
            rui = TheReport(self, query=qry, text1='Участок')
            qry.prepare("""SELECT date, coal_id, SUM(volume) FROM production
                           WHERE area_code is :param1 AND strftime('%m', date) is strftime('%m', 'now')
                           GROUP BY date
                           ORDER BY date, coal_id
                        """)
        elif report_name == 'Лимиты':
            rui = TheReport(self, query=qry, text1='Месяц')
            qry.prepare("""SELECT area_code, plan, removal_plan FROM limits
                           WHERE month is :param1
                           ORDER BY area_code
                        """)
        rui.show()

    def on_exit(self):
        try:
            self.qtbd.close()
        except:
            pass
        sys.exit(0)


class TheQResult(qw.QDialog):
    """
    Представление результатов выполнения запроса (Запросы)
    """

    def __init__(self, parent):
        qw.QDialog.__init__(self, parent=parent)
        self.ui = q_form()
        self.ui.setupUi(self)
        self.ui.pushButton.clicked.connect(self.close)


class TheReport(qw.QDialog):
    """
    Представление результатов выполнения запросов (Отчеты)
    """
    def __init__(self, parent, query=None, **kwargs):
        qw.QDialog.__init__(self, parent=parent)
        self.ui = r_form()
        self.ui.setupUi(self)
        self.ui.label.setText(kwargs['text1'])

        self.query = query

        self.kwargs = kwargs

        if 'text2' in kwargs.keys():
            self.ui.label_2.setText(kwargs['text2'])
        else:
            self.ui.label_2.setVisible(False)
            self.ui.lineEdit_2.setVisible(False)
        self.ui.execButton.clicked.connect(self.go_query)
        self.ui.closeButton.clicked.connect(self.close)

    def go_query(self):
        value1 = self.ui.lineEdit.text()
        if 'text2' in self.kwargs.keys():
            value2 = self.ui.lineEdit_2.text()
            self.query.bindValue(':param2', value2)
        if self.kwargs['text1'] == 'Месяц':
            if len(value1) == 1:
                value1 = '0' + value1
        self.query.bindValue(':param1', value1)
        self.query.exec()

        sqlq = QSqlQueryModel(self)
        sqlq.setQuery(self.query)
        self.ui.tableView.setModel(sqlq)
        self.ui.tableView.show()


if __name__ == '__main__':
    app = qw.QApplication([])
    application = TheWindow()
    application.show()

    sys.exit(app.exec())


