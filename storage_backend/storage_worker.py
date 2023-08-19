from PySide6.QtCore import QObject as sQObject
from PySide6.QtCore import Signal as sSignal

class storage_worker(sQObject):
    """this class is worker for storage Qthred

    :param sQObject: _description_
    :type sQObject: _type_
    """

    finished = sSignal()
    update_table_status = sSignal(int, str)
    update_charts = sSignal()
    update_scrollbar = sSignal(int)

    def assign_parameters(self, storage_api_obj):
        self.s_api = storage_api_obj

    def run(self):
        try:
            print('start cleaning in thread')
            self.s_api.start_cleaning()
            print('finish cleaning in thread')
            self.finished.emit()
        except:
            self.finished.emit()