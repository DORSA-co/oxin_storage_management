#--------------------------------
# Powerd by: AmirHossein Malekzadeh
# start in: 1402/02/03
# Company: Dorsa-co
# Website: https://Dorsa-co.ir
#
#
#
#--------------------------------

import shutil
import numpy as np
import os
from datetime import datetime
from datetime import timedelta



#____________________________________________________________________________________________________________________________________
#
#                                       This Class is for store memory space
# method: toGB():
#   return space in GB
# method: toPercent():
#   return space ercent based on all space
#
#____________________________________________________________________________________________________________________________________
class Space:
    def __init__(self, byte, total_byte=-1):
        self.byte = byte
        self.total_byte = total_byte
    def toGB(self,):
        return self.byte / 1e9

    def toMB(self,):
        return self.byte / 1e6
    
    def toKB(self,):
        return self.byte /1e3
    
    def toPercent(self):
        return round(self.byte/self.total_byte, 3) * 100

#____________________________________________________________________________________________________________________________________
#
#
#____________________________________________________________________________________________________________________________________
class diskMemory():

    def __init__(self,path):
        self.path = path
        self.refresh()
    

    def refresh(self):
        self.disk_size_info = shutil.disk_usage(self.path)
        self.used = Space(self.disk_size_info.used, self.disk_size_info.total)
        self.total = Space(self.disk_size_info.total, self.disk_size_info.total)
        self.free = Space(self.disk_size_info.free, self.disk_size_info.total)

#____________________________________________________________________________________________________________________________________
#
#
#____________________________________________________________________________________________________________________________________
class fileParms:

    def __init__(self,path):
        self._path = path
        self._file_extention = None
        self._full_name = None
        self._file_name = None
        self._dir = None
        self._creation_date = None
        self._size = None
        self._lifetime = None


    #---------------------------------------------------------------------
    def __extract_names_info__(self,):
        if self._full_name is None:
            self._full_name = os.path.basename(self._path)
            dot_loc = self._full_name.find('.')
            if dot_loc>=0:
                self._file_extention = self._full_name[ dot_loc + 1 :]
                self._file_name = self._full_name[ : dot_loc]
            else:
                self._file_extention = ''
                self._file_name = self._full_name

    #---------------------------------------------------------------------
    def __calc_dir_size__(self, path):
        total = 0
        with os.scandir(path) as it:
            for entry in it:
                if entry.is_file():
                    total += entry.stat().st_size
                elif entry.is_dir():
                    total += self.__calc_dir_size__(entry.path)
        return total
    
    #---------------------------------------------------------------------
    def path(self):
        return self._path


    def name(self):
        self.__extract_names_info__()
        return self._file_name


    def extention(self):
        self.__extract_names_info__()
        return self._file_extention


    def full_name(self):
        self.__extract_names_info__()
        return self._full_name


    def dir(self):
        if self._dir is None:
            self._dir = os.path.dirname(self._path)
        return self._dir
    

    def creation_date(self):
        if self._creation_date is None:
            self._creation_date = datetime.fromtimestamp(os.path.getctime(self._path))
        return self._creation_date
    

    def size(self) -> Space:
        self.__extract_names_info__()
        if self._file_extention == '':
            self._size = Space(self.__calc_dir_size__(self._path))
        else:
            self._size = Space(os.path.getsize( self._path ))
        return self._size
    

    def lifetime(self) -> datetime:
        self.creation_date()
        if self._lifetime is None:
            self._lifetime = datetime.today() - self.creation_date()
        return self._lifetime
    

#____________________________________________________________________________________________________________________________________
#
#
#____________________________________________________________________________________________________________________________________

class FileAction:
    @staticmethod
    def move( res_path):
        def _move_(file:File):
            shutil.move(file.parms.path(), res_path)
        return _move_

    @staticmethod
    def copy( res_path):
        def _copy_(file:File):
            shutil.copy(file.parms.path(), res_path)
        return _copy_

    @staticmethod
    def delete():
        def _delete_(file:File):
            if file.is_folder():
                shutil.rmtree(file.parms.path())
            else:
                os.remove(file.parms.path())
        return _delete_
    
    #copy_and_shortcud
    #rename
    #shortuc

#____________________________________________________________________________________________________________________________________
#
#
#____________________________________________________________________________________________________________________________________
class File:    
    def __init__(self, path):
        assert os.path.exists(path), f'ERROR: path {path} not exist'
        self.path = path
        self.parms = fileParms(self.path)


    def is_folder(self):
        return os.path.isdir(self.parms.path())


class FileManager:
    def __init__(self):
        self.file = None
        #self.actions = FileAction()
        self.operations = []
        self.log = []

    def set_file(self, file:File):
        self.file = file

    def add_operation(self, condition, true_action=None, false_action=None ):
        opr = {'condition':condition, 'true_action':true_action, 'false_action':false_action}
        self.operations.append(opr)
    
    def run(self, log=True):
        assert self.file is not None, 'set a file before run'
        for opr in self.operations:
            if opr['condition'](self.file):
                if opr['true_action']:
                    opr['true_action'](self.file)
                    if log:
                        self.log.append([self.file.parms.path(), opr['true_action'].__name__ ])
                return True
            else:
                if opr['false_action']:
                    opr['false_action'](self.file)
                    if log:
                        self.log.append([self.file.parms.path(), opr['false_action'].__name__ ])

        return False



#____________________________________________________________________________________________________________________________________
#
#
#____________________________________________________________________________________________________________________________________

class Conditions:
    
    @staticmethod
    def bigger( parm , value):
        if parm > value:
            return True
        return False
    
    @staticmethod
    def samaller( parm , value):
        if parm < value:
            return True
        return False
    
    @staticmethod
    def bigger_and_equal( parm , value):
        if parm >= value:
            return True
        return False

    @staticmethod
    def samaller_and_equal( parm , value):
        if parm <= value:
            return True
        return False
    
    @staticmethod
    def samaller( parm , value):
        if parm < value:
            return True
        return False
    
    @staticmethod
    def equal( parm , value):
        if parm == value:
            return True
        return False
    
    def not_equal( parm , value):
        if parm != value:
            return True
        return False
    

    @staticmethod
    def contain( parm , value):
        if parm in value:
            return True
        return False
    
    @staticmethod
    def not_contain( parm , value):
        if parm not in value:
            return True
        return False

    @staticmethod
    def __set_condition_func__(cond_type):
        if isinstance(cond_type, str):
            return CONDITIONS[cond_type]
        return cond_type



CONDITIONS = {
        '>': Conditions.bigger,
        '<': Conditions.samaller,
        '>=': Conditions.bigger_and_equal,
        '<=': Conditions.samaller_and_equal,
        '==': Conditions.equal,
        '!=': Conditions.not_equal,
        'in': Conditions.contain,
        'not in': Conditions.not_contain,
    }





class FileCondition:
    #--------------------------------------------------------------
    @staticmethod
    def __append_calback__( inpt, func):
        if func is not None:
            try:
                return func(inpt)
            except:
                print('ERROR: an error occured when {} callback run on {}'.format(func, inpt))
                return inpt
        return inpt
    
    

    # @staticmethod
    # def condition(cond_type, value, input_callback=None):
    #     cond_type = Conditions.__set_condition_func__(cond_type) #convert str condtion to related function
    #     def func(inpt):
    #         inpt = FileCondition.__append_calback__(inpt, input_callback)
    #         return cond_type( inpt , value )
    #     return func

    #--------------------------------------------------------------
    @staticmethod
    def creation_time(cond_type, dt, input_callback=None):
        cond_type = Conditions.__set_condition_func__(cond_type) #convert str condtion to related function
        assert cond_type not in [Conditions.contain, Conditions.not_contain], " 'in' and 'not in' aren't availble for this condition"
        def func(file:File):
            inpt = FileCondition.__append_calback__(file.parms.creation_date(), input_callback)
            return cond_type( inpt , dt )
        return func

    #--------------------------------------------------------------
    @staticmethod
    def file_extention(cond_type, ex, input_callback = None):
        assert '.' not in ex, 'input extention without (.) char'
        cond_type = Conditions.__set_condition_func__(cond_type) #convert str condtion to related function
        assert cond_type in [Conditions.contain, Conditions.not_contain, Conditions.equal, Conditions.not_equal], " only 'in' , 'not in' , '==' and '!=' aren availble for this condition"

        def func(file:File):
            inpt = FileCondition.__append_calback__(file.parms.extention(), input_callback)
            return cond_type( inpt , ex )
        return func

    #--------------------------------------------------------------
    @staticmethod
    def file_lifetime(cond_type, age:datetime, input_callback = None):
        cond_type = Conditions.__set_condition_func__(cond_type) #convert str condtion to related function
        assert cond_type not in [Conditions.contain, Conditions.not_contain], " 'in' and 'not in' aren't availble for this condition"

        def func(file:File):
            inpt = FileCondition.__append_calback__(file.parms.lifetime(), input_callback)
            return cond_type( inpt , age )
        return func

    #--------------------------------------------------------------
    @staticmethod
    def file_name(cond_type, value, input_callback = None):
        cond_type = Conditions.__set_condition_func__(cond_type) #convert str condtion to related function

        def func(file:File):
            inpt = FileCondition.__append_calback__(file.parms.name(), input_callback)
            return cond_type( inpt , value )
        return func

    #--------------------------------------------------------------
    @staticmethod
    def is_file_name_numeric( input_callback = None):
        def func(file:File):
            inpt = FileCondition.__append_calback__(file.parms.name(), input_callback)
            return inpt.isnumeric()
        return func



#____________________________________________________________________________________________________________________________________
#
#
#____________________________________________________________________________________________________________________________________
#def scanner(path, deep=1):
    #pass
class Scanner:

    def __init__(self, file_manager: FileManager):
        self.file_manager = file_manager
        self.__scan_location_calback_func__ = None
        self.__scan_file_calback_func__ = None

    def __join_path__(self, fname, path):
        return os.path.join( path, fname )
    
    def set_scan_location_calback(self, func):
        self.__scan_location_calback_func__ = func

    def set_scan_file_calback(self, func):
        self.__scan_file_calback_func__ = func

    #----------------------------------------------------------------------
    #
    #
    #----------------------------------------------------------------------
    def count_items(self, path, deep=1):
        total = 0
        if deep >= 0:
            for fname in os.listdir(path):
                fpath = self.__join_path__(fname, path)
                total+=1
                if  os.path.isdir(fpath):
                    total += self.count_items(fpath, deep=deep-1)

        return total
    #----------------------------------------------------------------------
    #
    #
    #----------------------------------------------------------------------
    def advanced_count_items(self, path, deep=1, condition = lambda x:True):
        total = 0
        if deep >= 0:
            for fname in os.listdir(path):
                fpath = self.__join_path__(fname, path)
                file = File(fpath)
                if condition(file):
                    print(file.parms.name())
                    total+=1
                if  os.path.isdir(fpath):
                    total += self.advanced_count_items(fpath, deep=deep-1, condition=condition)

        return total

    #----------------------------------------------------------------------
    #
    #
    #----------------------------------------------------------------------
    def scan(self, path, deep=1):
        #------------------------ for Callback -----------------------
        if self.__scan_location_calback_func__:
            self.__scan_location_calback_func__(path)
        #-------------------------------------------------------------
        if deep >= 0:
            for fname in os.listdir(path):
                fpath = self.__join_path__(fname, path)

                #------------------------ for Callback -----------------------
                if self.__scan_file_calback_func__:
                    self.__scan_file_calback_func__(fpath)
                #-------------------------------------------------------------

                #print(fpath)
                file = File(fpath)
                self.file_manager.set_file(file)
                flag = self.file_manager.run()

                if (not flag) and file.is_folder():
                    self.scan(fpath, deep=deep-1)


#____________________________________________________________________________________________________________________________________
#
#
#____________________________________________________________________________________________________________________________________
# class myProjectConditions:

#     def __init__(self):
#         self.be_folder = FileCondition.file_extention('==', '')
#         self.be_image = FileCondition.file_extention('in', ['jpg', 'png', 'jpeg'])
#         self.name_older = FileCondition.file_name('>=', 2022, int)
#         self.numberic_name = FileCondition.is_file_name_numeric()

#     def condition_date_folder(self,file:File):
#             if self.be_folder(file) and self.numberic_name(file) :
#                 if self.name_older(file):
#                     return True
#                 return False
#             return False
    
#     def condition_img(self, file:File):
#         if self.be_image(file):
#             return True
#         return False
    

# def my_scan_file_calback(f):
#     print('Scanning:', f)


# #-------custom for yourself ----------
# my_cond = myProjectConditions()

# #dm = diskMemory('c:\\')
# main_path = 'files'
# fm = FileManager()
# fm.add_operation(my_cond.condition_date_folder, FileAction.delete())
# #----------------
# scanner = Scanner(fm)
# #scanner.set_scan_file_calback(my_scan_file_calback)
# scanner.scan(main_path, deep=3)


# print( scanner.count_items(main_path, deep=100))
# print( scanner.advanced_count_items(main_path, deep=100, condition=my_cond.be_image) )