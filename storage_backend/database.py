import re
# from tkinter import EXCEPTION
from matplotlib.pyplot import flag
import mysql.connector
from mysql.connector import Error
from numpy import rec
# from tenacity import retry_if_exception


TABELS_NAME = {'coils_info':'images',
               }

CONNECTION_ERROR = 'Connection error'
SUCCESSFULL = 'True'
               

class dataBase:
    def __init__(self,username,password,host,database_name,logger_obj=None):
        pass
        self.user_name=username
        self.password=password
        self.host=host
        self.data_base_name=database_name
        self.logger_obj = logger_obj

        self.check_connection()



    def get_log(self, message='nothing', level=1):
        """
        this function is used to get log from database tasks

        Args:
            message (str, optional): _description_. Defaults to 'nothing'.
            level (int, optional): level of log. Defaults to 1.

        """
        if self.logger_obj != None:
            self.logger_obj.create_new_log(message=message, level=level)
    



    #--------------------------------------------------------------------------
    #--------------------------------------------------------------------------
    def connect(self):
            connection = mysql.connector.connect(host=self.host,
                                                database=self.data_base_name,
                                                user=self.user_name,
                                                password=self.password,
                                                auth_plugin='mysql_native_password')  
            cursor = connection.cursor()

            return cursor,connection     

    #--------------------------------------------------------------------------
    #--------------------------------------------------------------------------
    def check_connection(self):
        """
        this function is used to check if the connection to databse can be esablished

        Inputs: None

        Returns: a boolean value determining if the connecton is stablished or not
        """

        flag=False

        try: 
            cursor, connection = self.connect() # connect to database
            #
            flag=True
            #
            if connection.is_connected():
                db_Info = connection.get_server_info() # get informations of database
                # log
                self.get_log(message='Connected to MySQL Server version %s' % (db_Info))
                #

                cursor = connection.cursor()
                cursor.execute("select database();")
                record = cursor.fetchall()

                # log
                self.get_log(message='Connected to database %s' % (record))
                #
                return True

        except Exception as e:
            # log
            self.get_log(message='Error while connecting to MySQL', level=5)
            #
            return False

        finally:
            if flag and connection.is_connected():
                cursor.close()
                connection.close()

            # log
            self.get_log(message='MySQL connection is closed')
            #

    
    def execute_quary(self, quary, cursor, connection, need_data=False, close=False):
        """
        this function is used to execute a query on database

        Inputs:
            quary: the input query to execute
            cursor:
            connection:
            need_data: a bolean value
            close:
        
        Returns: None
        """
        
        try:
            if need_data:
                cursor.execute(quary, data)

            else:
                cursor.execute(quary)

            # connection.commit()
            if close:
                cursor.close()
            else:
                return cursor

        except Exception as e:
            # log
            self.get_log(message='Error while connecting to MySQL')
            #
        


    #--------------------------------------------------------------------------
    #--------------------------------------------------------------------------
    def add_record(self, data, table_name, parametrs, len_parameters):
        """this function is used to add a new record to table

        :param data: value of cols
        :type data: list
        :param table_name: name of th e table
        :type table_name: str
        :param parametrs: list of table cols
        :type parametrs: list
        :param len_parameters: number of cols/params
        :type len_parameters: int
        
        :return:
            result: boolean to determine result
        :rtype: bool
        """

        try:

            s ='%s,'*len_parameters
            s = s[:-1]
            s = '(' + s + ')'

            if self.check_connection:
                cursor,connection=self.connect()

                mySql_insert_query = """INSERT INTO {} {} 
                                    VALUES 
                                    {} """.format(table_name,parametrs,s)
                                    
                
                #print(mySql_insert_query)
                cursor.execute(mySql_insert_query,data)
                connection.commit()
                cursor.close()

                return SUCCESSFULL

            else:
                return CONNECTION_ERROR

        except Exception as e:
            return False, e


    #--------------------------------------------------------------------------
    #--------------------------------------------------------------------------

    def update_record(self,table_name,col_name,value,id_name,id_value):
        
        #print('id_value',table_name,col_name,value,id_name,id_value)
        if self.check_connection:
            cursor,connection=self.connect()

            mySql_insert_query = """UPDATE {} 
                                    SET {} = {}
                                    WHERE {} ={} """.format(table_name,col_name,("'"+value+"'"),id_name,("'"+id_value+"'"))
            ##print(mySql_insert_query)
            cursor.execute(mySql_insert_query)
            # mySql_insert_query=(mySql_insert_query,data)
            # self.execute_quary(mySql_insert_query, cursor, connection, close=False,need_data=True )
            connection.commit()
            #print(cursor.rowcount, "Record Updated successfully ")
            cursor.close()
            return True

        else:
            return False



    def remove_record(self, col_name, id, table_name):
        """
        this function is used to remove a record from table acourding to specified column value

        Inputs:
            col_name: name of the column to check for (in string)
            id: value of the column (in string)
            table_name: name of the table (in string)
        
        Returns:
            results: a boolean determining if the record is removed or not
        """
        
        try:
            if self.check_connection:
                cursor,connection=self.connect()

                mySql_delete_query = """DELETE FROM {} WHERE {}={};""".format(table_name,col_name,"'"+id+"'")

                self.execute_quary(mySql_delete_query, cursor, connection, False )
                connection.commit()
                ##print(cursor.rowcount, "Remove successfully from table {}".format(table_name))
                cursor.close()

                return True
            
            else:
                return False
        
        except:
            return False


    #--------------------------------------------------------------------------
    #--------------------------------------------------------------------------
    def report_last(self,table_name,parametr,count, side = 'DESC'):
        
        if self.check_connection:
            cursor,connection=self.connect()

            sql_select_Query = "select * from {} ORDER BY {} {} LIMIT {}".format(table_name,parametr,side, count)
            cursor=self.execute_quary(sql_select_Query, cursor, connection)
            # cursor.execute(sql_select_Query)
            records = cursor.fetchall()
            ##print("Total number of rows in table: ", cursor.rowcount)
            ##print(records)

            field_names = [col[0] for col in cursor.description]
            res = []

            connection.close()
            cursor.close()

            for record in records:
                    record_dict = {}
                    for i in range( len(field_names) ):
                        record_dict[ field_names[i] ] = record[i]
                    res.append( record_dict )

            return res


            return records


    #--------------------------------------------------------------------------
    #--------------------------------------------------------------------------

    def search(self, table_name, param_name, value, int_type=True):
        """this function is used to search in table

        :param table_name: table name
        :type table_name: str
        :param param_name: column names to search
        :type param_name: list or strs
        :param values: column values to search
        :type values: list
        :param int_type:
        :type int_type:
        
        :return:
            result: boolean to determine result
            table_content: list of dicts containing table records, if count==True: count of table
        :rtype: _type_
        """

        user_id=value

        try:
            if self.check_connection:
                cursor,connection=self.connect()

                if int_type:
                    sql_select_Query = "SELECT * FROM {} WHERE {} = {};".format(table_name,param_name,str(value))
                    cursor=self.execute_quary(sql_select_Query, cursor, connection)
                else:

                    sql_select_Query = """SELECT * FROM {} WHERE {} = {} """.format(table_name,param_name,("'"+str(value)+"'"))
                    cursor=self.execute_quary(sql_select_Query, cursor, connection)

                records = cursor.fetchall()
                
                field_names = [col[0] for col in cursor.description]
                res = []

                for record in records:
                    record_dict = {}
                    for i in range( len(field_names) ):
                        record_dict[ field_names[i] ] = record[i]
                    # #print('record_dict',record_dict)
                    
                    res.append( record_dict )
                
                return SUCCESSFULL, res


            return CONNECTION_ERROR, []

        except Exception as e:
            return e, []


    def search_with_range(self,table_name, col_names, values, limit=False, limit_size=20, offset=0, count=False):
        """this function is used to search in table by range and search parameters

        :param table_name: table name
        :type table_name: str
        :param col_names: column names to search
        :type col_names: list or strs
        :param values: column values to search
        :type values: list
        :param limit: boolean to determine returning a part of table rows, defaults to False
        :type limit: bool, optional
        :param limit_size: n returning rows (records), defaults to 20
        :type limit_size: int, optional
        :param offset: starting index to return n next rows, defaults to 0
        :type offset: int, optional
        :param count: boolean determining whether to get count of table, defaults to False
        :type count: bool, optional
        :return:
            result: boolean to determine result
            table_content: list of dicts containing table records, if count==True: count of table
        :rtype: _type_
        """

        # SELECT * FROM saba_database.binary_models where (algo_name,accuracy) = (0,0) and epochs between 2 and 4 and split_ratio between 20 and 30 and batch_size between 1 and 8
        try:
            if self.check_connection:
                cursor,connection=self.connect()

                if count:
                    sql_select_Query = "SELECT count(*) FROM {} WHERE ".format(table_name)
                else:
                    sql_select_Query = "SELECT * FROM {} WHERE ".format(table_name)

                # single values
                single_cols_query = '('
                single_vals_query = '('
            
                for i, col in enumerate(col_names):
                    if len(values[i]) == 1:
                        if i != 0:
                            single_cols_query += ','
                            single_vals_query += ','
                        single_cols_query += col
                        single_vals_query += str(values[i][0])
                single_cols_query += ')'
                single_vals_query += ')'
            
                # add single query yo main query
                if not single_cols_query == '()' and not single_vals_query == '()':
                    sql_select_Query = sql_select_Query + single_cols_query + '=' + single_vals_query + ' '

                # range values
                for i, col in enumerate(col_names):
                    if len(values[i]) > 1:
                        if i != 0:
                            sql_select_Query += "AND "
                        #
                        sql_select_Query += "{} BETWEEN {} AND {} ".format(col, str(values[i][0]), str(values[i][1]))
                

                if limit:
                    sql_select_Query += "LIMIT {} OFFSET {}".format(limit_size, offset)


                ##print(sql_select_Query)

                cursor=self.execute_quary(sql_select_Query, cursor, connection)

                records = cursor.fetchall()
                ##print("Total number of rows in table: ", cursor.rowcount)
                ##print(len(records),records)
                #----------------------------
                # #print(records)
                
                field_names = [col[0] for col in cursor.description]
                res = []
                for record in records:
                    record_dict = {}
                    for i in range( len(field_names) ):
                        record_dict[ field_names[i] ] = record[i]
                    res.append( record_dict )

                return SUCCESSFULL, res

            return CONNECTION_ERROR, []

        except Exception as e:
            return e, []

    
    def search_with_range_with_classes(self, table_name, col_names, values, limit=False, limit_size=20, offset=0, count=False):
        """this function is used to search in a table (classification models table actually/only) contatiing ability to search in target classses of defects

        :param table_name: name of the table
        :type table_name: str
        :param col_names: name of the cols
        :type col_names: list of str
        :param values: value of filtering cols
        :type values: list
        :param limit: boolean determinin gwhther to get part of records, defaults to False
        :type limit: bool, optional
        :param limit_size: determininng num records to return, defaults to 20
        :type limit_size: int, optional
        :param offset: sarting row index to get n next rows, defaults to 0
        :type offset: int, optional
        :param count: boolean determining count of filtered records, defaults to False
        :type count: bool, optional
        :return: _description_
        :rtype: _type_
        """

        # SELECT * FROM saba_database.binary_models where (algo_name,accuracy) = (0,0) and epochs between 2 and 4 and split_ratio between 20 and 30 and batch_size between 1 and 8
        try:
            if self.check_connection:
                cursor,connection=self.connect()

                if count:
                    sql_select_Query = "SELECT count(*) FROM {} WHERE ".format(table_name)
                else:
                    sql_select_Query = "SELECT * FROM {} WHERE ".format(table_name)

                # single values
                single_cols_query = '('
                single_vals_query = '('
                flag1 = False
                for i, col in enumerate(col_names):
                    if len(values[i]) == 1 and col != 'classes':
                        flag1 = True
                        if i != 0:
                            single_cols_query += ','
                            single_vals_query += ','
                        single_cols_query += col
                        single_vals_query += str(values[i][0])
                single_cols_query += ')'
                single_vals_query += ')'
            
                # add single query yo main query
                if not single_cols_query == '()' and not single_vals_query == '()':
                    sql_select_Query = sql_select_Query + single_cols_query + '=' + single_vals_query + ' '

                # range values
                for i, col in enumerate(col_names):
                    if len(values[i]) > 1 and col != 'classes':
                        flag1 = True
                        if i != 0:
                            sql_select_Query += "AND "
                        #
                        sql_select_Query += "{} BETWEEN {} AND {} ".format(col, str(values[i][0]), str(values[i][1]))

                # like values (for classes)
                # classes LIKE '%,22,%' or classes LIKE '%,33,%'
                for i, col in enumerate(col_names):
                    if col == 'classes':
                        if flag1:
                            sql_select_Query += "AND ("
                        else:
                            sql_select_Query += "("
                        # for loop in classes in list
                        flag = False
                        for j, cls in enumerate(values[i]):
                            flag = True
                            if j != 0:
                                sql_select_Query += "AND "
                            sql_select_Query += "{} LIKE '%,{},%' ".format(col, str(values[i][j]))
                        if flag:
                            sql_select_Query += ") "

                #
                if limit:
                    sql_select_Query += "LIMIT {} OFFSET {}".format(limit_size, offset)


                cursor=self.execute_quary(sql_select_Query, cursor, connection)

                records = cursor.fetchall()
                
                
                field_names = [col[0] for col in cursor.description]
                res = []
                for record in records:
                    record_dict = {}
                    for i in range( len(field_names) ):
                        record_dict[ field_names[i] ] = record[i]
                    res.append( record_dict )

                return SUCCESSFULL, res

            return CONNECTION_ERROR, []

        except Exception as e:
            return e, []

            
    #--------------------------------------------------------------------------
    #--------------------------------------------------------------------------

    def delete(self,db_name,table_name):
        try:
            if self.check_connection:
                cursor,connection=self.connect()
            sql_Delete_table = "DELETE FROM  {}.{};".format(db_name,table_name)
            cursor=self.execute_quary(sql_Delete_table, cursor, connection)       
            ##print('delete')     
            #                               
        except Exception as e:
            self.get_log(message='Error reading data from MySQL table', level=5)

    #--------------------------------------------------------------------------
    #--------------------------------------------------------------------------

    def get_col_name(self,table_name,param_name, value):
        if self.check_connection:
            cursor,connection=self.connect()
            

            cursor = connection.cursor()
            cursor.execute("select database();")

            field_names = [col[0] for col in cursor.description]

            #print(field_names)

        return field_names

    #--------------------------------------------------------------------------
    #--------------------------------------------------------------------------


    def get_all_content(self,table_name, count=False, limit=False, limit_size=20, offset=0, reverse_order=False):
        """this function is used to get all content of a table

        :param table_name: table name
        :type table_name: str
        :param count: boolean determinnig whether to return count of table, defaults to False
        :type count: bool, optional
        :param limit: boolean determining whether to return part of table, defaults to False
        :type limit: bool, optional
        :param limit_size: conut of table rows to reurn, defaults to 20
        :type limit_size: int, optional
        :param offset: starting row index to return n next roes, defaults to 0
        :type offset: int, optional
        :param reverse_order: boolean to reverse sorting the table, defaults to False
        :type reverse_order: bool, optional
        :return:
            result: boolean to determine result
            table_content: list of dicts containing table records, if count==True: count of table
        :rtype: _type_
        """
        
        sort_order = 'DESC' if reverse_order else 'ASC'

        try:
            if self.check_connection:
                cursor,connection=self.connect()

                if count:
                    sql_select_Query = "select count(*) from {}".format(table_name)
                else:
                    if not limit:
                        sql_select_Query = "select * from {} ORDER BY id {}".format(table_name, sort_order)
                    else:
                        sql_select_Query = "select * from {} ORDER BY id {} LIMIT {} OFFSET {}".format(table_name, sort_order, limit_size, offset)
                    
                cursor=self.execute_quary(sql_select_Query, cursor, connection)
                # cursor.execute(sql_select_Query)
                records = cursor.fetchall()
                ##print("Total number of rows in table: ", cursor.rowcount)
                ##print(records)

                field_names = [col[0] for col in cursor.description]

                connection.close()
                cursor.close()
                ##print("MySQL connection is closed")

                res = []
                for record in records:
                        record_dict = {}
                        for i in range( len(field_names) ):
                            record_dict[ field_names[i] ] = record[i]
                        res.append( record_dict )

                return SUCCESSFULL, res

            else:
                return CONNECTION_ERROR, []

        except Exception as e:
            return e, []


    def check_table_exist(self,table_name):

        try:
            if self.check_connection:
                cursor,connection=self.connect()
            sql_check_table = "SELECT * FROM {}.{};".format(self.data_base_name,table_name)
            cursor=self.execute_quary(sql_check_table, cursor, connection)       
            # #print('check')    
            return 'Exist'                              
        except mysql.connector.Error as e:
            pass
            #print("Error reading data from MySQL table", e)


if __name__ == "__main__":
    db=dataBase('root','root','localhost','saba_database')

    # db.get_col_name('996','camera_settings','id')

    # data=(0,)*10
    # data=(0,0,0,0,1920,1200,0,0,0,0,0)

    # x=db.get_all_content('defects_info')
    # #print(x)

    record = db.search( 'users' , 'user_name', 'testt')[0]
    #print(record)
    # table_name,parametrs,len_parameters)

    # db.add_record(data,'coils_info','(id,coil_number,heat_number,ps_number,pdl_number,length,width,operator,time,date,main_path)',11)
    # db.add_record(data,'camera_settings','(gain_top,gain_bottom,expo_top,expo_bottom,width,height,offset_x,offset_y,interpacket_delay,packet_size,id)',11)
 
    #db.add_record(data,'coils_info','(id,coil_number,heat_number,ps_number,pdl_number,length,width,operator,time,date,main_path)',11)

    #db.report_last('coils_info','id',30)

    # db.remove_record('1920', 'camera_settings')

    # db.report_last('coils_info','id',30) 

    # db.search('996','coils_info','id')



# report_last(self,table_name,parametr,count)



# CREATE SCHEMA `saba_database` ;


# CREATE TABLE `saba_database`.`coils_info` (
#   `id` INT NOT NULL,
#   `coil_number` VARCHAR(45) NOT NULL,
#   `heat_number` VARCHAR(45) NULL,
#   `ps_number` VARCHAR(45) NULL,
#   `pdl_number` VARCHAR(45) NULL,
#   `length` VARCHAR(45) NULL,
#   `width` VARCHAR(45) NULL,
#   `operator` VARCHAR(45) NULL,
#   `time` VARCHAR(45) NULL,
#   `date` VARCHAR(45) NULL,
#   PRIMARY KEY (`id`));
