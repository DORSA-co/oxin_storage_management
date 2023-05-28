from tokenize import group
from storage_backend import database
import numpy as np
from datetime import datetime


class dataBaseUtils:
    """
    this class is used as an API to work with database

    Inputs:
        logger_obj: the logger object to take loggs

    Returns:
        database object
    """

    def __init__(self, logger_obj=None):
        # database object
        self.db = database.dataBase(
            "root", "Dorsa-1400", "localhost", "saba_database", logger_obj=logger_obj
        )

        # logger object
        self.logger_obj = logger_obj

        # table names
        self.storage_settings = "storage_settings"
        self.sheets_info = "sheets_info"

    def load_storage_setting(self):
        """This function is used to get storage settings from table

        :return: A flag that indicates the success of the task along with the settings.
        :rtype: tuple
        """

        res, settings = self.db.search(
            self.storage_settings, "id", "1"
        )
        if res == database.SUCCESSFULL:
            return True, settings[0]
        else:
            # Log Exception
            return False, settings

    def set_storage_setting(self, max_cleanup_percentage, min_cleanup_percentage, update_time, ssd_image_path, ssd_dataset_path, hdd_path):
        """This function set settings in database table

        :param max_cleanup_percentage: maximum percentage to cleanup.
        :type max_cleanup_percentage: int
        :param min_cleanup_percentage: minimum percentage to cleanup.
        :type min_cleanup_percentage: int
        :param ssd_image_path: path of images partition of ssd.
        :type ssd_image_path: str
        :param ssd_dataset_path: path of datasets partition of ssd.
        :type ssd_dataset_path: str
        :param hdd_path: path of hdd.
        :type hdd_path: str
        :return: True if all settings update successfully. False otherwise.
        :rtype: bool
        """
        res1 = self.db.update_record(self.storage_settings, "max_cleanup_percentage", str(max_cleanup_percentage), "id", "1")
        res2 = self.db.update_record(self.storage_settings, "min_cleanup_percentage", str(min_cleanup_percentage), "id", "1")
        res3 = self.db.update_record(self.storage_settings, "update_time", str(update_time), "id", "1")
        res4 = self.db.update_record(self.storage_settings, "ssd_images_path", str(ssd_image_path), "id", "1")
        res5 = self.db.update_record(self.storage_settings, "ssd_datasets_path", str(ssd_dataset_path), "id", "1")
        res6 = self.db.update_record(self.storage_settings, "hdd_path", str(hdd_path), "id", "1")

        return res1 and res2 and res3 and res4 and res5 and res6

    def change_sheet_main_path(self, new_main_path, sheet_id):
        res = self.db.update_record(self.sheets_info, "main_path", str(new_main_path), "sheet_id", sheet_id)
        return res


if __name__ == "__main__":
    db = dataBaseUtils()
    