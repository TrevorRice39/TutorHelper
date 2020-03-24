# Author: Trevor Rice
# Date: Tue Jul 23 10:33:53 EDT 2019


import MySQLdb
import os
class Connection:

    def __init__(self, host, user, passwd, database, newdatabase):
        """
        Constructor that initializes your database connection
        @params:
            host: hostname (str)
            user: username (str)
            passwd: user's password (str)
            database: database names (str)
            newdatabase: if True, creates a new database, if False, makes a
                         connection to an existing database (boolean)
        """
        self.host = host
        self.user = user
        self.passwd = passwd
        self.databasename = database
        if (newdatabase): # checks if you wish to create a new database
            self.database = MySQLdb.connect(host=self.host,user=self.user,passwd=self.passwd)
        else:
            self.database = MySQLdb.connect(host=self.host,user=self.user,passwd=self.passwd, database=self.databasename)
        self.cursor = self.database.cursor()
        self.createDatabase(self.databasename)
        self.cursor.execute('use ' + self.databasename)


    def close_connection(self):
        return
    def createDatabase(self, databasename):
        """
        Creates the database
        @params:
            databasename: name of database to be created (str)
        """
        self.cursor.execute('create database if not exists ' + databasename)

    def insert(self, tablename, labels, values):
        """
        Inserts a row into the database
        @params:
            tablename: name of table to insert into (str)
            labels: variable names in table (str)
            values: values to be inserted (list)
        """
        tables = self.cursor.execute('show tables like \'' + tablename + '\'')
        if (self.cursor.fetchone()): # if table exists
            sql = "insert ignore into " + tablename + " " + "(" + labels + ")" + " values " + "(%s, %s, %s)"
            self.cursor.executemany(sql, values)
            self.database.commit()
        else:
            print('Table ' + tablename + ' does not exist')

    def create_table(self, tablename, labels):
        """
        Creates a table within our database
        @params:
            tablename: name of table (str)
            labels: variable types and names
        """
        tables = self.cursor.execute('show tables like \'' + tablename + '\'')
        if (self.cursor.fetchone()): # if table exists
            print('Table \'' + tablename + '\'' + ' already exists')
        else :
            sql = "create table " + tablename + "(" + labels + ")"
            self.cursor.execute(sql)
            self.database.commit()

    def select(self, select, fr, where):
        """
        Selects data from the database
        @params:
            select: select statement (str)
            fr: table to search (str)
            where: where condition (str)
        """
        tables = self.cursor.execute('show tables like \'' + fr + '\'')
        if (self.cursor.fetchone()): # if table exists
            if (len(where) == 0):
                sql = "select " + select + " from " + fr
            else:
                sql = "select " + select + " from " + fr + " where " + where
                
            self.cursor.execute(sql)

            return self.cursor.fetchall()
        else:
            print('Table ' + fr + ' does not exist')

    def to_csv(self, tablename, into):
        """
        Dumps a table from the database into a csv file
        @params:
            tablename: name of table to dump from (str)
            into: name of the file that will be created, storing the data (str)
        """
        if os.path.exists(into):
            os.remove(into)
        sql = 'select * from ' + tablename + ' into outfile \'' + into + '\' fields terminated by ' + "','" +' lines terminated by ' + "'\n'"
        self.cursor.execute(sql)
