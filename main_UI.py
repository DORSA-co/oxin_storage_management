import sys
from PySide6.QtWidgets import *
from PySide6.QtCharts import *
from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtUiTools import loadUiType
import os
from backend import texts, color
from backend.chart_funcs import SimpleChart, SmartChart, SimpleChartView
from api import API

ui, _ = loadUiType("UI/main.ui")
os.environ["QT_FONT_DPI"] = "96" # FIX Problem for High DPI and Scale above 100%

class storage_management(QMainWindow, ui):
    global widgets
    widgets = ui
    x=0

    def __init__(self):
        super(storage_management, self).__init__()
        self.setupUi(self)
        flags = Qt.WindowFlags(Qt.FramelessWindowHint)
        self.pos_ = self.pos()
        self.setWindowFlags(flags)
        title = "Storage Management"
        self.setWindowTitle(title)
        # annotated image
        self.activate_()
        self.center()
        self._old_pos = None

        self.storage_color = {'HDD': '#ff007f', 'SSD': '#55aaff'}
        self.used_free_color = {'Used': '#ff0000', 'Free': '#4dbf4d'}

        self.create_images_charts()
        # self.update_images_chart()

        self.create_datasets_charts()
        # self.update_datasets_chart()

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

    def create_datasets_charts(self):
        self.ds_chart = SimpleChart(title="Datasets")
        self.ds_chart_view = SimpleChartView(self.ds_chart)

        bpievbox = QVBoxLayout()
        bpievbox.addWidget(self.ds_chart_view)
        bpievbox.setContentsMargins(0, 0, 0, 0)
        
        self.datasets_chart_frame.setLayout(bpievbox)
        self.datasets_chart_frame.layout().setContentsMargins(0, 0, 0, 0)

    def update_datasets_chart(self, free_space, input_info):
        # input_info = {'ds1':100, 'ds2': 200, 'ds3': 50}
        # free_space = 500

        self.ds_chart.add_slice('Free', free_space, self.used_free_color['Free'])

        percent = 0
        percent_step = (1-percent) / len(input_info)
        for k in input_info:
            percent += percent_step
            self.ds_chart.add_slice(k, 
                                    input_info[k], 
                                    color.ColorRGB.from_hex(self.used_free_color['Used']).blend(percent=percent).hexcode
                                    )

        # self.image_chart.set_legend_outer(labels=input_info.keys())
        # self.image_chart.set_legend_inner(labels=list(input_info.values())[0].keys())

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

        self.main_page_btn.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.page_1))
        self.report_page_btn.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.page_2))
        self.settings_btn.clicked.connect(lambda: self.stackedWidget.setCurrentWidget(self.page_3))
        self.stackedWidget.currentChanged.connect(self.change_left_btns)

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
    
    def set_warning(self, text, level=1):
        """Show warning with time delay 2 second , all labels for show warning has been set here"""

        if text != None:
            if level == 1:
                self.message_label.setText(" " + text + " ")
                self.message_label.setStyleSheet(
                    "background-color:#20a740;border-radius:2px;color:white"
                )

            if level == 2:
                self.message_label.setText(
                    texts.WARNINGS["WARNING"][self.language] + text
                )
                self.message_label.setStyleSheet(
                    "background-color:#FDFFA9;border-radius:2px;color:black"
                )

            if level >= 3:
                self.message_label.setText(texts.ERRORS["ERROR"][self.language] + text)
                self.message_label.setStyleSheet(
                    "background-color:#D9534F;border-radius:2px;color:black"
                )
            QTimer.singleShot(2000, lambda: self.set_warning(None))
        else:
            self.message_label.setText("")
            self.message_label.setStyleSheet("")

    def insert_into_table(self, files, operation, state):
        for file in files:
            rowPosition = self.report_table.rowCount()
            self.report_table.insertRow(rowPosition)

            table_item = QTableWidgetItem(file.name())
            table_item.setTextAlignment(Qt.AlignCenter)
            table_item.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
            table_item.setCheckState(Qt.Unchecked) 
            self.report_table.setItem(rowPosition, 0, table_item)

            table_item = QTableWidgetItem(operation)
            table_item.setTextAlignment(Qt.AlignCenter)
            self.report_table.setItem(rowPosition, 1, table_item)

            table_item = QTableWidgetItem(state)
            table_item.setTextAlignment(Qt.AlignCenter)
            self.report_table.setItem(rowPosition, 2, table_item)

    def get_table_checked_items(self):
        selected_file_names = []
        for row in range(self.report_table.rowCount()): 
            if self.report_table.item(row, 0).checkState() == Qt.Checked:
                selected_file_names.append(self.report_table.item(row, 0).text())

        return selected_file_names

    def clear_table(self):
        self.report_table.clear()
        self.report_table.setRowCount(0)


if __name__ == "__main__":
    app = QApplication()
    win = storage_management()
    api = API(win)
    win.show()
    sys.exit(app.exec())