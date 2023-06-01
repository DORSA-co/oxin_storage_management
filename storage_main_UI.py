import sys
import os
from PySide6.QtWidgets import *
from PySide6.QtCharts import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtUiTools import loadUiType
from storage_backend import texts, color
# from storage_backend import chart_funcs
from storage_backend.chart_funcs import SimpleChart, SmartChart, SimpleChartView
from storage_backend.FileDialog import FileDialog
from storage_api import storage_api
import storage_resources_rc

ui, _ = loadUiType(os.path.join(os.path.dirname(os.path.abspath(__file__)), "storage_UI/storage_main.ui"))
os.environ["QT_FONT_DPI"] = "96" # FIX Problem for High DPI and Scale above 100%

ANIMATION_DURATION = 300
HEIGHT_START_VALUE = 0
HEIGHT_STOP_VALUE = 200
ICON_MAIN_PATH = ':/icons/Icons'
DOWN_ICON = 'down.png'
UP_ICON = 'up.png'

class storage_management(QMainWindow, ui):
    global widgets
    widgets = ui
    x=0

    def __init__(self):
        super(storage_management, self).__init__()
        self.setupUi(self)
        flags = Qt.WindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.pos_ = self.pos()
        self.setWindowFlags(flags)
        title = "Storage Management"
        self.setWindowTitle(title)
        # annotated image
        self.activate_()
        self.center()
        self._old_pos = None
        self.stackedWidget.setCurrentIndex(0)

        self.language = 'en'

        self.storage_color = {'HDD': '#ff007f', 'SSD': '#55aaff'}
        self.used_free_color = {'Used': '#ff0000', 'Free': '#4dbf4d'}

        self.create_images_charts()
        self.create_datasets_charts()

    def showEvent(self, event):
        # print(self.visibleRegion().isEmpty())
        # self.function()
        # print(self.isVisible())
        super().showEvent(event)
        return 

    def function(self):
        for i in range(1000000):
            print(i)
        # import time
        # time.sleep(5)

    def create_images_charts(self):
        self.image_chart = SmartChart(title="Images")
        self.image_chart_view = SimpleChartView(self.image_chart)

        bpievbox = QVBoxLayout()
        bpievbox.addWidget(self.image_chart_view)
        bpievbox.setContentsMargins(0, 0, 0, 0)
        
        self.images_chart_frame.setLayout(bpievbox)
        self.images_chart_frame.layout().setContentsMargins(0, 0, 0, 0)

    def update_images_chart(self, input_info):
        # input_info = {'SSD': {'Used':100, 'Free': 200}, 'HDD': {'Used': 300, 'Free': 50}}
        for k in input_info:
            self.image_chart.add_slice_outer(k, sum(input_info[k].values()), self.storage_color[k])
            for kk in input_info[k]:
                self.image_chart.add_slice_inner(kk, input_info[k][kk], self.used_free_color[kk])

        self.image_chart.set_legend_outer(labels=input_info.keys())
        self.image_chart.set_legend_inner(labels=list(input_info.values())[0].keys())

    def clear_images_chart(self):
        self.image_chart.clear()

    def create_datasets_charts(self):
        self.ds_chart = SimpleChart(title="Datasets")
        self.ds_chart_view = SimpleChartView(self.ds_chart)

        bpievbox = QVBoxLayout()
        bpievbox.addWidget(self.ds_chart_view)
        bpievbox.setContentsMargins(0, 0, 0, 0)
        
        self.datasets_chart_frame.setLayout(bpievbox)
        self.datasets_chart_frame.layout().setContentsMargins(0, 0, 0, 0)

    def update_datasets_chart(self, free_space, files):
        # input_info = {'ds1':100, 'ds2': 200, 'ds3': 50}
        # free_space = 500

        self.ds_chart.add_slice('Free', free_space, self.used_free_color['Free'])

        percent = 1
        percent_step = percent / len(files)

        for file in files:
            percent -= percent_step
            self.ds_chart.add_slice(file.name(), 
                                    file.size().toGB(), 
                                    color.ColorRGB.from_hex(self.used_free_color['Used']).blend(percent=percent).hexcode
                                    )

    def clear_datasets_chart(self):
        self.ds_chart.clear()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._old_pos = event.pos()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._old_pos = None

    def mouseMoveEvent(self, event):
        if not self._old_pos:
            return
        delta = event.pos() - self._old_pos
        self.move(self.pos() + delta)

    def activate_(self):
        self.close_button.clicked.connect(self.close_win)
        self.mini_button.clicked.connect(self.minimize)
        self.maxi_button.clicked.connect(self.maxmize_minimize)

        self.main_page_btn.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.main_page))
        self.report_page_btn.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.report_page))
        self.settings_btn.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.settings_page))
        self.stackedWidget.currentChanged.connect(self.change_left_btns)
        self.advance_settings_btn.clicked.connect(self.show_hide_advance_settings)
        self.ssd_image_path_btn.clicked.connect(lambda: self.browse(self.ssd_image_path_lineEdit))
        self.ssd_ds_path_btn.clicked.connect(lambda: self.browse(self.ssd_ds_path_lineEdit))
        self.hdd_path_btn.clicked.connect(lambda: self.browse(self.hdd_path_lineEdit))

    def minimize(self):
        self.showMinimized()
    
    def maxmize_minimize(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

    def close_win(self):
        self.close()

    def center(self):
        frame_geo = self.frameGeometry()
        screen = self.window().screen()
        center_loc = screen.geometry().center()
        frame_geo.moveCenter(center_loc)
        self.move(frame_geo.topLeft())

    def change_left_btns(self, index):
        if index==0:
            self.main_page_btn.setStyleSheet('background-color: rgb(90, 83, 145);')
            self.report_page_btn.setStyleSheet('')
            self.settings_btn.setStyleSheet('')
        elif index==1:
            self.main_page_btn.setStyleSheet('')
            self.report_page_btn.setStyleSheet('background-color: rgb(90, 83, 145);')
            self.settings_btn.setStyleSheet('')
        elif index==2:
            self.main_page_btn.setStyleSheet('')
            self.report_page_btn.setStyleSheet('')
            self.settings_btn.setStyleSheet('background-color: rgb(90, 83, 145);')

    def show_report_page(self):
        self.stackedWidget.setCurrentWidget(self.report_page)
    
    def set_warning(self, label_obj, text, level=1):
        """Show warning with time delay 2 second , all labels for show warning has been set here"""

        if text != None:
            if level == 1:
                label_obj.setText(" " + text + " ")
                label_obj.setStyleSheet(
                    "background-color:#20a740;border-radius:2px;color:white"
                )

            if level == 2:
                label_obj.setText(
                    texts.WARNINGS["WARNING"][self.language] + text
                )
                label_obj.setStyleSheet(
                    "background-color:#FDFFA9;border-radius:2px;color:black"
                )

            if level >= 3:
                label_obj.setText(texts.ERRORS["ERROR"][self.language] + text)
                label_obj.setStyleSheet(
                    "background-color:#D9534F;border-radius:2px;color:black"
                )
            QTimer.singleShot(2000, lambda: self.set_warning(label_obj, None))
        else:
            label_obj.setText("")
            label_obj.setStyleSheet("")

    def change_background_color(self, obj, level=1):
        if not level:
            obj.setStyleSheet("")
        if level==1:
            obj.setStyleSheet(
                        "background-color:#20a740"
                    )
        elif level==2:
            obj.setStyleSheet(
                        "background-color:#FDFFA9"
                    )
        elif level==3:
            obj.setStyleSheet(
                        "background-color:#D9534F"
                    )
        QTimer.singleShot(2000, lambda: self.change_background_color(obj, None))

    def insert_into_table(self, files, operation, state):
        for file in files:
            rowPosition = self.report_table.rowCount()
            self.report_table.insertRow(rowPosition)

            table_item = QTableWidgetItem(file.name())
            table_item.setTextAlignment(Qt.AlignCenter)
            table_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            table_item.setCheckState(Qt.Checked) 
            self.report_table.setItem(rowPosition, 0, table_item)

            table_item = QTableWidgetItem(operation)
            table_item.setTextAlignment(Qt.AlignCenter)
            self.report_table.setItem(rowPosition, 1, table_item)

            table_item = QTableWidgetItem(state)
            table_item.setTextAlignment(Qt.AlignCenter)
            self.report_table.setItem(rowPosition, 2, table_item)

    def clear_table(self):
        self.report_table.clear()

    def get_table_checked_items(self):
        selected_file_names = {}
        for row in range(self.report_table.rowCount()): 
            if self.report_table.item(row, 0).checkState() == Qt.Checked:
                selected_file_names[self.report_table.item(row, 0).text()] = row

        return selected_file_names

    def change_table_status(self, row, status):
        self.report_table.item(row, 2).setText(status)

    def clear_table(self):
        self.report_table.clear()
        self.report_table.setRowCount(0)

    def show_hide_advance_settings(self):
        h = self.advance_frame.height()

        if h <= HEIGHT_START_VALUE:
            self.minHeight = QPropertyAnimation(self.advance_frame, b"minimumHeight")
            self.minHeight.setDuration(ANIMATION_DURATION)
            self.minHeight.setStartValue(h)
            self.minHeight.setEndValue(HEIGHT_STOP_VALUE)
            self.minHeight.setEasingCurve(QEasingCurve.InOutQuart)
            self.group = QParallelAnimationGroup()
            self.group.addAnimation(self.minHeight)

            self.maxHeight = QPropertyAnimation(self.advance_frame, b"maximumHeight")
            self.maxHeight.setDuration(ANIMATION_DURATION)
            self.maxHeight.setStartValue(h)
            self.maxHeight.setEndValue(HEIGHT_STOP_VALUE)
            self.maxHeight.setEasingCurve(QEasingCurve.InOutQuart)
            self.group.addAnimation(self.maxHeight)
            self.group.start()

            self.set_icon(self.advance_settings_btn, UP_ICON)

        else:
            self.minHeight = QPropertyAnimation(self.advance_frame, b"minimumHeight")
            self.minHeight.setDuration(ANIMATION_DURATION)
            self.minHeight.setStartValue(h)
            self.minHeight.setEndValue(HEIGHT_START_VALUE)
            self.minHeight.setEasingCurve(QEasingCurve.InOutQuart)
            self.group = QParallelAnimationGroup()
            self.group.addAnimation(self.minHeight)

            self.maxHeight = QPropertyAnimation(self.advance_frame, b"maximumHeight")
            self.maxHeight.setDuration(ANIMATION_DURATION)
            self.maxHeight.setStartValue(h)
            self.maxHeight.setEndValue(HEIGHT_START_VALUE)
            self.maxHeight.setEasingCurve(QEasingCurve.InOutQuart)
            self.group.addAnimation(self.maxHeight)
            self.group.start()

            self.set_icon(self.advance_settings_btn, DOWN_ICON)

    def set_icon(self, obj, icon_name):
        icon_path = os.path.join(ICON_MAIN_PATH, icon_name)
        obj.setIcon(QPixmap(icon_path))

    def set_settings(self, max_cleanup_percentage, min_cleanup_percentage, update_time, ssd_images_path, ssd_datasets_path, hdd_path):
        self.max_percent_spinBox.setValue(int(max_cleanup_percentage))
        self.min_percent_spinBox.setValue(int(min_cleanup_percentage))
        self.update_time_spinBox.setValue(int(update_time))

        self.ssd_image_path_lineEdit.setText(ssd_images_path)
        self.ssd_ds_path_lineEdit.setText(ssd_datasets_path)
        self.hdd_path_lineEdit.setText(hdd_path)

    def browse(self, lineedit_obj):
        path = self.open_file_dialog()
        lineedit_obj.setText(path)

    def open_file_dialog(self):
        select_path_dialog = FileDialog("Select Path", "/")
        selected = select_path_dialog.exec()

        if selected:
            dname = select_path_dialog.selectedFiles()[0]
            return dname
        return ''

if __name__ == "__main__":
    app = QApplication()
    win = storage_management()
    api = storage_api(win)
    win.show()
    sys.exit(app.exec())
