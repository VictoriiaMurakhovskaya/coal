import sqlite3

class dbAPI:
    db_path = r'assets/coal.db'

    def __init__(self):
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute("pragma foreign_keys")
        cur = self.conn.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS coal_table(
                        id STRING PRIMARY KEY,
                        ash_content REAL,
                        humidity_percentage INT,
                        combustion REAL,
                        cost REAL);
                    """)

        cur.execute("""CREATE TABLE IF NOT EXISTS areas(
                       code INT PRIMARY KEY,
                       name STRING,
                       area REAL,
                       height REAL,
                       master STRING REFERENCES employees(code));
                    """)

        cur.execute("""CREATE TABLE IF NOT EXISTS employees(
                       code STRING PRIMARY KEY,
                       full_name STRING,
                       area_code INT,
                       position_code INT,
                       RNN STRING,
                       SIK STRING,
                       pf_code STRING,
                       address STRING,
                       phone STRING);
                    """)

        cur.execute("""CREATE TABLE IF NOT EXISTS production(
                       id INT PRIMARY KEY,
                       date DATE,
                       shift INT,
                       area_code INT REFERENCES areas(code),
                       coal_id STRING REFERENCES coal_table(id),
                       volume REAL);
                    """)

        cur.execute("""CREATE TABLE IF NOT EXISTS spending(
                       id INT PRIMARY KEY,
                       date DATE,
                       area_code INT REFERENCES areas(code),
                       shift INT,
                       electricity REAL,
                       fuel REAL)
                    """)

        cur.execute("""CREATE TABLE IF NOT EXISTS h_report(
                       id INT PRIMARY KEY,
                       date DATE,
                       area_code INT,
                       shift INT,
                       emp_code STRING,
                       hours INT);
                    """)

        cur.execute("""CREATE TABLE IF NOT EXISTS pf(
                       id INT PRIMARY KEY,
                       name STRING);
                    """)

        cur.execute("""CREATE TABLE IF NOT EXISTS position(
                       id INT PRIMARY KEY,
                       name STRING);
                    """)

        cur.execute("""CREATE TABLE IF NOT EXISTS limits(
                       area_code STRING PRIMARY KEY,
                       plan REAL,
                       volume REAL,
                       removal_plan REAL,
                       removal_volume REAL,
                       electricity_plan REAL,
                       electricity_spending REAL,
                       fuel_plan REAL,
                       fuel_spending REAL,
                       month INT,
                       year INT);
                    """)

        self.conn.commit()

    def get_tables(self):
        """
        Получение списка SQL таблиц
        :return: Возвращает list названий таблиц в используемой схеме БД
        """
        cur = self.conn.cursor()
        cur.execute("""SELECT name FROM sqlite_master
                       WHERE type = 'table';""")
        return [item[0] for item in cur.fetchall()]