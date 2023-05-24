from PySide6.QtWidgets import *


class FileDialog(QFileDialog):
    def __init__(self, title, path):
        super().__init__()

        self.path = path
        self.setWindowTitle(title)
        self.setDirectory(self.path)
        self.setFileMode(QFileDialog.Directory)
        self.setOption(QFileDialog.DontUseNativeDialog, True)

        self.fixedHistoryButtons()

    def fixedHistoryButtons(self):
        backButton = self.findChild(QToolButton, 'backButton')
        forwardButton = self.findChild(QToolButton, 'forwardButton')
        fileNameEdit = self.findChild(QLineEdit, 'fileNameEdit')

        fileNameEdit.setEnabled(False)

        self.directoryEntered.connect(self.backOrForwardButtonClicked)
        self.directoryUrlEntered.connect(self.backOrForwardButtonClicked)
        backButton.clicked.connect(self.backOrForwardButtonClicked)
        forwardButton.clicked.connect(self.backOrForwardButtonClicked)

    def backOrForwardButtonClicked(self):
        if not self.selectedFiles()[0].startswith(self.path):
            self.setDirectory(self.path)
