import os
from datetime import datetime
#from diskManager import Space, File
import shutil


#____________________________________________________________________________________________________________________________________
#
#
#____________________________________________________________________________________________________________________________________

# def is_year_folder(path):
#     return os.path.isdir(path) and os.path.basename(path).isnumeric()
class Space:
    def __init__(self, byte, total_byte=-1):
        self.bytes = byte
        self.total_byte = total_byte
    
    def toBytes(self,):
        return self.bytes

    def toGB(self,):
        return self.bytes / (1024)**3

    def toMB(self,):
        return self.bytes / (1024)**2
    
    def toKB(self,):
        return self.bytes /1024
    
    def toPercent(self):
        return round(self.bytes/self.total_byte, 3) * 100
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

class FileInfo:

    @staticmethod
    def __correction_input__(inpt):
        if isinstance(input, str):
            return [File(inpt)]
        if isinstance( inpt, File):
            return [inpt]
        if isinstance(inpt, (list,File)):
            return inpt
        assert True, f'{inpt} Bad Argument'



    @staticmethod
    def __dir_size__(path) -> Space:
        total = Space(0)
        with os.scandir(path) as it:
            for entry in it:
                if entry.is_file():
                    total.bytes += entry.stat().st_size
                elif entry.is_dir():
                    total.bytes += FileInfo.__dir_size__(entry.path).bytes
        return total
    
    @staticmethod
    def __file_size__(path) -> Space:
        return Space(os.stat(path).st_size)
    

    def size(path) -> Space:
        if os.path.isfile(path):
            return FileInfo.__file_size__(path)
        else:
            return FileInfo.__dir_size__(path)
        
    @staticmethod
    def extention(path) -> str:
        _,extention = os.path.splitext(path)
        return extention
#____________________________________________________________________________________________________________________________________
#
#
#____________________________________________________________________________________________________________________________________

class File:
    
    def __init__(self, path, size=None) -> None:
        self.__path__ = path
        self._size_ = size
        self.__extention__ = None
        self.__name__ = None

    def size(self) -> Space:
        if self._size_ is None:
            self._size_ = FileInfo.size(self.__path__)
        return self._size_
    
    def extention(self) -> str :
        if self.__extention__ is None:
            self.__extention__ = os.path.splitext(self.__path__)[1]
        return self.__extention__
    
    def name(self) -> str :
        if self.__name__ is None:
            self.__name__ = os.path.basename(self.__path__)
        return self.__name__
    
    def path(self) -> str :
        return self.__path__

#____________________________________________________________________________________________________________________________________
#
#
#____________________________________________________________________________________________________________________________________
class FileAction:
    @staticmethod
    def move(path,  res_path):
        Manager.build_dir(res_path)
        shutil.move(path, res_path)
        

    @staticmethod
    def copy(path, res_path):
        Manager.build_dir(res_path)
        shutil.copy(path, res_path)
        

    @staticmethod
    def delete(path):
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)

#____________________________________________________________________________________________________________________________________
#
#
#____________________________________________________________________________________________________________________________________

    

#____________________________________________________________________________________________________________________________________
#
#
#____________________________________________________________________________________________________________________________________
class FileSort:
    @staticmethod
    def sort_by_creationtime(li: list[File], low_to_high=False):
        if isinstance( li[0], File):
            li.sort( key=lambda x:datetime.fromtimestamp(os.path.getctime(x.path)), reverse = low_to_high )
        if isinstance( li[0], str):
            li.sort( key=lambda x:datetime.fromtimestamp(os.path.getctime(x)), reverse = low_to_high )
        return li

    def sort_by_name(li: list[File], low_to_high=False):
        if isinstance( li[0], File):
            li.sort( key=lambda x:os.path.basename(x.path), reverse = low_to_high )
        if isinstance( li[0], str):
            li.sort( key=lambda x:os.path.basename(x), reverse = low_to_high )
        
        return li


#____________________________________________________________________________________________________________________________________
#
#
#____________________________________________________________________________________________________________________________________

class Scanner:
    def __init__(self):
        self.scan_results = []
        self.total_space = Space(0)
        self.flag = False
    

    def scan_by_depth(self, main_path, depth, extentions=None, reset=True ) -> list[File]:
        #if reset is False the new scan results append to previous scans
        if reset:
            self.scan_results =[]
        #-----------------------
        sub_paths = []
        if depth > 0:
            sub_paths = Manager.get_sub_paths(main_path, folder_only=True)
        else:
            sub_paths = Manager.get_sub_paths(main_path, folder_only=False)
        #-----------------------
        for path in sub_paths:
            if depth > 0:
                self.scan_results = self.scan_by_depth(path, depth=depth-1, reset=False)

            else:
                if extentions is None or File(path).extention() in extentions:
                    self.scan_results.append( File(path) )
            
        return self.scan_results
    

    def scan_size_limit(self, main_path, transfer_size: Space, depth, sorting_func=None,extentions=None, reset=True) -> tuple[list[File], bool, Space ]:
        #if reset is False the new scan results append to previous scans
        if reset:
            self.scan_results =[]
        
        #-----------------------
        sub_paths = []
        if depth > 0:
            sub_paths = Manager.get_sub_paths(main_path, folder_only=True)
        else:
            sub_paths = Manager.get_sub_paths(main_path, folder_only=False)

        #-----------------------
        if sorting_func:
            sub_paths = sorting_func(sub_paths)
        #-----------------------
        for path in sub_paths:
            if depth > 0:
                self.scan_results, self.flag, self.total_space = self.scan_size_limit(path, transfer_size, depth=depth-1, reset=False)
                if self.flag:
                    break

            else:
                if extentions is None or File(path).extention() in extentions:
                    file_size = FileInfo.size(path)
                    self.total_space.bytes += file_size.bytes
                    self.scan_results.append( File(path, size=file_size) )
                
                if (self.total_space.bytes > transfer_size.bytes):
                    self.flag = True
                    break
        
        return self.scan_results, self.flag, self.total_space 
#____________________________________________________________________________________________________________________________________
#
#
#____________________________________________________________________________________________________________________________________
class Manager:
    @staticmethod
    def remove_empty_folders(path):
        sub_paths = Manager.get_sub_paths(path, folder_only = False)
        could_be_empty = True
        if len(sub_paths) > 0:
            for sp in sub_paths:
                if os.path.isdir(sp):
                    Manager.remove_empty_folders(sp)
                else: 
                    could_be_empty = False
            if could_be_empty:
                sub_paths = Manager.get_sub_paths(path, folder_only = False)
        
        if len(sub_paths) == 0:
            FileAction.delete(path)
            



    @staticmethod
    def get_sub_paths(path, folder_only= True):
        fnames = os.listdir(path)
        sub_paths = list(map( lambda fn: os.path.join(path,fn), fnames ))
        if folder_only:
            sub_paths = list(filter(os.path.isdir, sub_paths))
        return sub_paths
    
    
    @staticmethod
    def build_dir(path):
        base_path = os.path.dirname(path)
        #sub_path = os.path.basename(path)
        if (not os.path.isdir(base_path)) and base_path != '':
            Manager.build_dir(base_path)

        if (not os.path.isdir(path)) and path !='' :
            os.mkdir(path)

#____________________________________________________________________________________________________________________________________
#
#
#____________________________________________________________________________________________________________________________________

class FileManager:
    action = FileAction
    sort = FileSort
    info = FileInfo
    scan = Scanner() #this is not an abstact class
    manage = Manager
    
            

    

                
if __name__ == '__main__':
    main_path = 'files'
    res_path = 'C:\\Users\\amir\\Desktop\\oxin-file-manager'
    transfer_size2 = Space(500*1e6)



    fm = FileManager()

    #-----------------copy older sheet
    # sheet_should_copy, flag, space_needed = fm.scan.scan_size_limit(main_path,
    #                                                                 transfer_size2,
    #                                                                 depth=3, 
    #                                                                 sorting_func= FileManager.sort.sort_by_creationtime)

    # for sheet_file in sheet_should_copy:
    #     print(sheet_file.path, sheet_file.size().toMB())
    #     #FileManager.action.move(sheet_file.path, res_path)



    #-----------------remove empty folders
    fm.manage.remove_empty_folders(main_path)

    #-----------------DataSet
    files = fm.scan.scan_by_depth(main_path,0)
    total = 0
    for f in files:
        res = fm.info.size(f.path)
        total+= res.bytes

    total = Space(total)
    print(total.toGB())
