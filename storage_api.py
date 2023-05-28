from storage_backend import FileManager
import os
from PySide6.QtCore import *
from PySide6.QtCore import QTimer
from storage_backend import database_utils, texts


CHART_UPDATE_TIME = 15
DISKS_CHECK_TIME = 60

class storage_api():
    def __init__(self, ui):
        self.ui = ui
        
        self.db = database_utils.dataBaseUtils()
        self.read_settings_from_db()

        self.fm = FileManager.FileManager()
        self.ssd_ds_file_manager = FileManager.diskMemory(path=self.settings['ssd_datasets_path'])
        self.ssd_image_file_manager = FileManager.diskMemory(path=self.settings['ssd_images_path'])
        self.hdd_file_manager = FileManager.diskMemory(path=self.settings['hdd_path'])
        ############################## CHANGE ###############################
        # self.hdd_file_manager.free = FileManager.Space(500*1024*1024)
        #####################################################################

        self.ssd_sheet_should_clean = []
        self.hdd_sheet_should_clean = []

        # self.update_charts()
        # self.check_disks()

        # self.create_charts_timer()
        # self.create_disks_timer()

        self.ui.start_btn.clicked.connect(self.start_cleaning)
        self.ui.apply_settings_btn.clicked.connect(self.apply_settings)
        self.ui.revert_settings_btn.clicked.connect(self.read_settings_from_db)

    def read_settings_from_db(self):
        res, settings = self.db.load_storage_setting()
        if res:
            self.settings = settings
            self.ui.set_settings(self.settings['max_cleanup_percentage'], 
                                 self.settings['min_cleanup_percentage'],
                                 self.settings['update_time'],
                                 self.settings['ssd_images_path'],
                                 self.settings['ssd_datasets_path'],
                                 self.settings['hdd_path'])

    def apply_settings(self):
        max_cleanup_percentage = self.ui.max_percent_spinBox.value()
        min_cleanup_percentage = self.ui.min_percent_spinBox.value()
        update_time = self.ui.update_time_spinBox.value()

        ssd_images_path = self.ui.ssd_image_path_lineEdit.text()
        ssd_datasets_path = self.ui.ssd_ds_path_lineEdit.text()
        hdd_path = self.ui.hdd_path_lineEdit.text()

        if max_cleanup_percentage < min_cleanup_percentage:
            self.ui.set_warning(self.ui.settings_warning_label,
                                texts.WARNINGS['CLEANUP_PERCENTAGE_WARNING'][self.ui.language],
                                level=2)
            self.ui.change_background_color(obj=self.ui.max_percent_spinBox, level=2)
            self.ui.change_background_color(obj=self.ui.min_percent_spinBox, level=2)
            return       
        if not os.path.exists(ssd_images_path):
            self.ui.set_warning(self.ui.settings_warning_label,
                                texts.WARNINGS['PATH_NOT_EXISTS'][self.ui.language],
                                level=2)
            self.ui.change_background_color(obj=self.ui.ssd_image_path_lineEdit, level=2)
            return
        if not os.path.exists(ssd_datasets_path):
            self.ui.set_warning(self.ui.settings_warning_label,
                                texts.WARNINGS['PATH_NOT_EXISTS'][self.ui.language],
                                level=2)
            self.ui.change_background_color(obj=self.ui.ssd_ds_path_lineEdit, level=2)
            return
        if not os.path.exists(hdd_path):
            self.ui.set_warning(self.ui.settings_warning_label,
                                texts.WARNINGS['PATH_NOT_EXISTS'][self.ui.language],
                                level=2)
            self.ui.change_background_color(obj=self.ui.hdd_path_lineEdit, level=2)
            return

        self.db.set_storage_setting(
            max_cleanup_percentage,
            min_cleanup_percentage,
            update_time,
            ssd_images_path,
            ssd_datasets_path,
            hdd_path
        )

        self.settings['max_cleanup_percentage'] = max_cleanup_percentage 
        self.settings['min_cleanup_percentage'] = min_cleanup_percentage
        self.settings['update_time'] = update_time
        self.settings['ssd_images_path'] = ssd_images_path
        self.settings['ssd_datasets_path'] = ssd_datasets_path
        self.settings['hdd_path'] = hdd_path

        self.update_charts()

        self.ui.set_warning(self.ui.settings_warning_label,
                                texts.MESSEGES['APPLY_SUCCESSFULY'][self.ui.language],
                                level=1)

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
        self.ssd_image_file_manager.refresh()
        self.hdd_file_manager.refresh()
        input_info = {'SSD': {'Used':self.ssd_image_file_manager.used.toGB(), 
                              'Free': self.ssd_image_file_manager.free.toGB()}, 
                    'HDD': {'Used':self.hdd_file_manager.used.toGB(), 
                            'Free': self.hdd_file_manager.free.toGB()}
                    }
        self.ui.clear_images_chart()
        self.ui.update_images_chart(input_info)

    def update_datasets_chart(self):
        # path = '/home/reyhane/Desktop/default_dataset'
        self.ssd_ds_file_manager.refresh()
        files = self.fm.scan.scan_by_depth(self.settings['ssd_datasets_path'], 0)
        free = self.ssd_ds_file_manager.free.toGB()
        self.ui.clear_datasets_chart()
        self.ui.update_datasets_chart(free, files)

    def check_disks(self):
        ssd_image_percent = self.ssd_image_file_manager.used.toPercent()
        if ssd_image_percent > self.settings['max_cleanup_percentage']:
            clean_space_ssd = self.ssd_image_file_manager.total.toBytes() * (ssd_image_percent - self.settings['min_cleanup_percentage']) / 100
            

            self.ssd_sheet_should_clean, ssd_flag, ssd_space_needed = self.fm.scan.scan_size_limit(self.settings['ssd_images_path'],
                                                                    FileManager.Space(clean_space_ssd),
                                                                    depth=3, 
                                                                    sorting_func= FileManager.FileManager.sort.sort_by_creationtime)
            self.ui.insert_into_table(self.ssd_sheet_should_clean, 'Move', '-')

            free_hdd = self.hdd_file_manager.free.toBytes()

            if ssd_space_needed.toBytes() > free_hdd:
                self.hdd_sheet_should_clean, hdd_flag, hdd_space_needed = self.fm.scan.scan_size_limit(self.settings['hdd_path'],
                                                                    FileManager.Space(clean_space_ssd - free_hdd),
                                                                    depth=3, 
                                                                    sorting_func= self.fm.sort.sort_by_creationtime)
                self.ui.insert_into_table(self.hdd_sheet_should_clean, 'Delete', '-')
        self.ui.show_report_page()
        self.start_cleaning()
            
    def start_cleaning(self):
        selected_file_names = self.ui.get_table_checked_items()
        for file in self.hdd_sheet_should_clean:
            if file.name() in selected_file_names:
                self.ui.change_table_status(selected_file_names[file.name()], 'Doing...')
                self.fm.action.delete(file.path())
                self.ui.change_table_status(selected_file_names[file.name()], 'Done')

        self.hdd_sheet_should_clean = []

        for file in self.ssd_sheet_should_clean:
            if file.name() in selected_file_names:
                self.ui.change_table_status(selected_file_names[file.name()], 'Doing')
                path = self.fm.action.move(file.path(), res_path=self.settings['hdd_path'], replace_path=self.settings['ssd_images_path'])
                # path = os.path.join( path, file.name())
                self.db.change_sheet_main_path(self.settings['hdd_path'], file.name())
                self.ui.change_table_status(selected_file_names[file.name()], 'Done')

        self.ssd_sheet_should_clean = []
        # print('close')
        # self.ui.close_win()
