from tokenize import group
from backend import database
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
            "root", "Dorsa1400@", "localhost", "saba_database", logger_obj=logger_obj
        )

        # logger object
        self.logger_obj = logger_obj

        # table names
        self.storage_settings = "storage_settings"

    def load_storage_setting(self):
        """
        this function is used to get general-settings params from table

        Args:
            is_mutitaskiing_params (bool, optional): a boolean determining wheather to load multitasing params from multitasking table. Defaults to False.

        Returns:
            record: list of one dict
        """

        res, settings = self.db.search(
            self.storage_settings, "id", "1"
        )
        if res == database.SUCCESSFULL:
            return True, settings
        else:
            # Log Exception
            return False, settings

    def set_storage_setting(self, max_cleanup_percentage, min_cleanup_percentage, ssd_image_path, ssd_dataset_path, hdd_path):
        res1 = self.db.update_record(self.storage_settings, "max_cleanup_percentage", str(max_cleanup_percentage), "id", "1")
        res2 = self.db.update_record(self.storage_settings, "min_cleanup_percentage", str(min_cleanup_percentage), "id", "1")
        res3 = self.db.update_record(self.storage_settings, "ssd_images_path", str(ssd_image_path), "id", "1")
        res4 = self.db.update_record(self.storage_settings, "ssd_datasets_path", str(ssd_dataset_path), "id", "1")
        res5 = self.db.update_record(self.storage_settings, "hdd_path", str(hdd_path), "id", "1")

        return res1 and res2 and res3 and res4 and res5


if __name__ == "__main__":
    db = dataBaseUtils()
    