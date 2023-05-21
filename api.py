from backend import FileManager
import os
from PySide6.QtCore import *
from PySide6.QtCore import QTimer


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
SSD_IMAGE_PATH = '/home/reyhane/Desktop/oxin_file_manager/SSD'
SSD_DS_PATH = '/'
HDD_PATH = '/home/reyhane/Desktop/oxin_file_manager/HDD'


UP_TH = 15
DOWN_TH = 10
CHART_UPDATE_TIME = 15
DISKS_CHECK_TIME = 60

class API():
    def __init__(self, ui):
        self.ui = ui

        self.fm = FileManager.FileManager()
        self.ssd_ds_file_manager = FileManager.diskMemory(path=SSD_DS_PATH)
        self.ssd_image_file_manager = FileManager.diskMemory(path=SSD_IMAGE_PATH)
        self.hdd_file_manager = FileManager.diskMemory(path=HDD_PATH)
        ############################## CHANGE ###############################
        self.hdd_file_manager.free = FileManager.Space(500*1024*1024) 

        self.ssd_sheet_should_clean = []
        self.hdd_sheet_should_clean = []

        self.update_charts()
        self.check_disks()

        self.create_charts_timer()
        self.create_disks_timer()

        self.ui.start_btn.clicked.connect(self.start_cleaning)

    def create_charts_timer(self):
        self.update_charts_timer = QTimer()
        self.update_charts_timer.timeout.connect(self.update_charts)
        self.update_charts_timer.start(CHART_UPDATE_TIME*60*1000)

    def create_disks_timer(self):
        self.check_disks_timer = QTimer()
        self.check_disks_timer.timeout.connect(self.check_disks)
        self.check_disks_timer.start(DISKS_CHECK_TIME*60*1000)

    def update_charts(self):
        self.update_images_chart()
        self.update_datasets_chart()

    def update_images_chart(self):
        input_info = {'SSD': {'Used':self.ssd_image_file_manager.used.toGB(), 
                              'Free': self.ssd_image_file_manager.free.toGB()}, 
                    'HDD': {'Used':self.hdd_file_manager.used.toGB(), 
                            'Free': self.hdd_file_manager.free.toGB()}
                    }
        self.ui.clear_images_chart()
        self.ui.update_images_chart(input_info)

    def update_datasets_chart(self):
        path = '/home/reyhane/Desktop/default_dataset'
        files = self.fm.scan.scan_by_depth(path, 0)
        free = self.ssd_ds_file_manager.free.toGB()
        self.ui.update_datasets_chart(free, files)

    def check_disks(self):
        ssd_image_percent = self.ssd_image_file_manager.used.toPercent()
        if ssd_image_percent > UP_TH:
            clean_space_ssd = self.ssd_image_file_manager.total.toBytes() * (ssd_image_percent - DOWN_TH) / 100
            

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
                                                                    sorting_func= self.fm.sort.sort_by_creationtime)
                self.ui.insert_into_table(self.hdd_sheet_should_clean, 'Delete', '-')
            
    def start_cleaning(self):
        selected_file_names = self.ui.get_table_checked_items()
        for file in self.hdd_sheet_should_clean:
            if file.name() in selected_file_names:
                self.fm.action.delete(file.path())

        self.hdd_sheet_should_clean = []

        for file in self.ssd_sheet_should_clean:
            if file.name() in selected_file_names:
                path = self.fm.action.move(file.path(), res_path=HDD_PATH, replace_path=SSD_IMAGE_PATH)
                path = os.path.join( path, file.name() )
                print(path, file.dirpath())
                self.fm.action.shortcut_linux(path, file.path())

        self.ssd_sheet_should_clean = []
