from storage_backend import FileManager
import os
from PySide6.QtCore import *
from PySide6.QtCore import QTimer, QThread
from storage_backend import database_utils, texts, storage_worker


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
        self.filters = []

        self.start()

        # self.create_charts_timer()
        # self.create_disks_timer()
        
        self.ui.apply_settings_btn.clicked.connect(self.apply_settings)
        self.ui.revert_settings_btn.clicked.connect(self.read_settings_from_db)

    def read_settings_from_db(self):
        res, settings = self.db.load_storage_setting()
        if res:
            self.settings = settings
            self.ui.set_settings(self.settings['storage_upper_limit'], 
                                 self.settings['storage_lower_limit'],
                                 self.settings['update_time'],
                                 self.settings['ssd_images_path'],
                                 self.settings['ssd_datasets_path'],
                                 self.settings['hdd_path'])

    def apply_settings(self):
        storage_upper_limit = self.ui.max_percent_spinBox.value()
        storage_lower_limit = self.ui.min_percent_spinBox.value()
        update_time = self.ui.update_time_spinBox.value()

        ssd_images_path = self.ui.ssd_image_path_lineEdit.text()
        ssd_datasets_path = self.ui.ssd_ds_path_lineEdit.text()
        hdd_path = self.ui.hdd_path_lineEdit.text()

        if storage_upper_limit < storage_lower_limit:
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
            storage_upper_limit,
            storage_lower_limit,
            update_time,
            ssd_images_path,
            ssd_datasets_path,
            hdd_path
        )

        self.settings['storage_upper_limit'] = storage_upper_limit 
        self.settings['storage_lower_limit'] = storage_lower_limit
        self.settings['update_time'] = update_time
        self.settings['ssd_images_path'] = ssd_images_path
        self.settings['ssd_datasets_path'] = ssd_datasets_path
        self.settings['hdd_path'] = hdd_path

        self.ssd_ds_file_manager = FileManager.diskMemory(path=self.settings['ssd_datasets_path'])
        self.ssd_image_file_manager = FileManager.diskMemory(path=self.settings['ssd_images_path'])
        self.hdd_file_manager = FileManager.diskMemory(path=self.settings['hdd_path'])

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

    def set_charts_animation(self, value):
        self.ui.set_animation_images_chart(value)
        self.ui.set_animation_datasets_chart(value)

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

    def add_filter(self, filter):
        self.filters.append(filter)

    def clear_filters(self):
        self.filters = []

    def check_disks(self):
        self.ui.clear_table()
        ssd_image_percent = self.ssd_image_file_manager.used.toPercent()
        if ssd_image_percent > self.settings['storage_upper_limit']:
            clean_space_ssd = self.ssd_image_file_manager.total.toBytes() * (ssd_image_percent - self.settings['storage_lower_limit']) / 100
            

            self.ssd_sheet_should_clean, ssd_flag, ssd_space_needed = self.fm.scan.scan_size_limit(self.settings['ssd_images_path'],
                                                                    FileManager.Space(clean_space_ssd),
                                                                    depth=3, 
                                                                    sorting_func= FileManager.FileManager.sort.sort_by_creationtime)

            self.ssd_sheet_should_clean = list(filter(lambda x: x not in self.filters, self.ssd_sheet_should_clean))
            # if self.ssd_sheet_should_clean:
            #     self.ssd_sheet_should_clean.pop()
            self.ui.insert_into_table(self.ssd_sheet_should_clean, 'Move', '-')

            free_hdd = self.hdd_file_manager.free.toBytes()
            print('ssd_space_needed: ', ssd_space_needed.toBytes(), 'free_hdd: ', free_hdd)
            if ssd_space_needed.toBytes() > free_hdd:
                self.hdd_sheet_should_clean, hdd_flag, hdd_space_needed = self.fm.scan.scan_size_limit(self.settings['hdd_path'],
                                                                    FileManager.Space(clean_space_ssd - free_hdd),
                                                                    depth=3, 
                                                                    sorting_func= self.fm.sort.sort_by_creationtime)
                self.ui.insert_into_table(self.hdd_sheet_should_clean, 'Delete', '-')
                print('hdd_sheet_should_clean: ', self.hdd_sheet_should_clean)
        self.ui.show_report_page()
            
    def start_cleaning(self):
        selected_file_names = self.ui.get_table_checked_items()
        for file in self.hdd_sheet_should_clean:
            if file.name() in selected_file_names:
                print('hdd file name: ', file.name())
                self.s_worker.update_scrollbar.emit(selected_file_names[file.name()])
                self.s_worker.update_table_status.emit(selected_file_names[file.name()], 'Doing...')
                self.fm.action.delete(file.path())
                self.s_worker.update_table_status.emit(selected_file_names[file.name()], 'Done')
                self.s_worker.update_charts.emit()

        self.hdd_sheet_should_clean = []
        
        for file in self.ssd_sheet_should_clean:
            if file.name() in selected_file_names:
                print('ssd file name: ', file.name())
                self.s_worker.update_scrollbar.emit(selected_file_names[file.name()])
                self.s_worker.update_table_status.emit(selected_file_names[file.name()], 'Doing...')
                print('start moving')
                try:
                    path = self.fm.action.move(file.path(), res_path=self.settings['hdd_path'], replace_path=self.settings['ssd_images_path'])
                    print('finish move')
                except Exception as e:
                    print(e)
                # path = os.path.join( path, file.name())
                print('update db')
                self.db.change_sheet_main_path(self.settings['hdd_path'], file.name())
                self.s_worker.update_table_status.emit(selected_file_names[file.name()], 'Done')
                self.s_worker.update_charts.emit()

        self.ssd_sheet_should_clean = []
        
    def start_cleaning_thread(self):
        self.s_thread = QThread()
        self.s_worker = storage_worker.storage_worker()
        self.s_worker.assign_parameters(
            storage_api_obj = self
        )

        self.s_worker.moveToThread(self.s_thread)
        
        self.s_thread.started.connect(self.s_worker.run)

        self.s_worker.finished.connect(self.s_thread.quit)
        self.s_worker.finished.connect(self.ui.close_win)
        self.s_worker.finished.connect(self.s_worker.deleteLater)

        self.s_thread.finished.connect(self.s_thread.deleteLater)
        
        self.s_worker.update_table_status.connect(self.ui.change_table_status)
        self.s_worker.update_charts.connect(self.update_charts)
        self.s_worker.update_scrollbar.connect(self.ui.update_scrollbar)
        
        self.s_thread.start()

    def start(self):
        # self.set_charts_animation(True)
        self.ssd_image_file_manager.refresh()
        self.hdd_file_manager.refresh()
        print('refresh file managers')
        self.update_charts()
        print('update charts')
        self.check_disks()
        print('check disks')
        # self.set_charts_animation(False)
        self.start_cleaning_thread()
        print('start_cleaning_thread') 