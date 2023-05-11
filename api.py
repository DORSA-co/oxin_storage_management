from backend import FileManager
import os
from PySide6.QtCore import *


# def datasets_space(path):
#     res = []
#     total = 0
#     fm = FileManager.FileManager()
#     files = fm.scan.scan_by_depth(path, 0, extentions=[''])
#     #-----------------DataSet
#     for file in files:
#         res.append({'name': file.name(), 'size': file.size() })
#         total+= file.size().bytes

#     #total = FileManager.Space(total)
#     return res


# main_path = 'files'
# res = datasets_space(main_path)
# print(res)

# READ FROM DB
SSD_IMAGE_PATH = '/home/reyhane/Desktop/Oxin_File_Manager/SSD'
SSD_DS_PATH = '/'
HDD_PATH = '/home/reyhane/Desktop/Oxin_File_Manager/HDD'


UP_TH = 15
DOWN_TH = 10

class API():
    def __init__(self, ui):
        self.ui = ui

        self.fm = FileManager.FileManager()
        self.ssd_ds_file_manager = FileManager.diskMemory(path=SSD_DS_PATH)
        self.ssd_image_file_manager = FileManager.diskMemory(path=SSD_IMAGE_PATH)
        self.hdd_file_manager = FileManager.diskMemory(path=HDD_PATH)
        ############################## CHANGE ###############################
        self.hdd_file_manager.free = FileManager.Space(500*1024*1024) 

        self.disks = {'SSD_DS': self.ssd_ds_file_manager, 'SSD_IMAGE': self.ssd_image_file_manager, 'HDD': self.hdd_file_manager}

        self.update_images_chart()
        self.update_datasets_chart()
        self.check_disks()

        self.ui.start_btn.clicked.connect(self.start_cleaning)

    def update_images_chart(self):
        input_info = {'SSD': {'Used':self.ssd_image_file_manager.used.toGB(), 
                              'Free': self.ssd_image_file_manager.free.toGB()}, 
                    'HDD': {'Used':self.hdd_file_manager.used.toGB(), 
                            'Free': self.hdd_file_manager.free.toGB()}
                    }
        self.ui.update_images_chart(input_info)

    def update_datasets_chart(self):
        

        #-----------------DataSet
        input_info = {}
        path = '/home/reyhane/Desktop/default_dataset'
        files = self.fm.scan.scan_by_depth(path, 0)
        # total = 0
        for f in files:
            name = f.name()
            size = f.size()
            input_info[name] = size.toGB()
            # total+= size.toGB()

        free = self.ssd_ds_file_manager.free.toGB()
        self.ui.update_datasets_chart(free, files)

    def check_disks(self):
        ssd_image_percent = self.ssd_image_file_manager.used.toPercent()
        if ssd_image_percent > UP_TH:
            clean_space_ssd = self.ssd_image_file_manager.total.toBytes() * (UP_TH - DOWN_TH) / 100
            

            self.ssd_sheet_should_clean, ssd_flag, ssd_space_needed = self.fm.scan.scan_size_limit(SSD_IMAGE_PATH,
                                                                    FileManager.Space(clean_space_ssd),
                                                                    depth=3, 
                                                                    sorting_func= FileManager.FileManager.sort.sort_by_creationtime)
            self.ui.insert_into_table(self.ssd_sheet_should_clean, 'Move', '-')

            free_hdd = self.hdd_file_manager.free.toBytes()

            if ssd_space_needed.toBytes() > free_hdd:
                self.hdd_sheet_should_clean, hdd_flag, hdd_space_needed = self.fm.scan.scan_size_limit(HDD_PATH,
                                                                    FileManager.Space(clean_space_ssd - free_hdd),
                                                                    depth=3, 
                                                                    sorting_func= FileManager.FileManager.sort.sort_by_creationtime)
                self.ui.insert_into_table(self.hdd_sheet_should_clean, 'Delete', '-')
            
    def start_cleaning(self):
        selected_file_names = self.ui.get_table_checked_items()
        for file in self.hdd_sheet_should_clean:
            if file.name() in selected_file_names:
                FileManager.FileManager.action.delete(file.path())

        for file in self.ssd_sheet_should_clean:
            if file.name() in selected_file_names:
                FileManager.FileManager.action.move(file.path(), res_path=HDD_PATH)


        # for sheet_file in sheet_should_copy:
    #     print(sheet_file.path, sheet_file.size().toMB())
    #     #FileManager.action.move(sheet_file.path, res_path)
        
        




        

        









