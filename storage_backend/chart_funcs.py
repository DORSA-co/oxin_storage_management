"""
Template for drawing Pie Charts in Qt Application
"""


import sys
from collections import namedtuple

from PySide6 import QtCore, QtWidgets, QtGui
from PySide6 import QtCharts


class SimpleChart(QtCharts.QChart):
    """
    A bare minimum implementation of pie chart in Qt
    """

    def __init__(self, title, parent=None):
        """
        Initialization with layout and population
        """
        super(SimpleChart, self).__init__(parent)
        offset = 0
        pie_background_color = '#171145'
        pie_label_color = 'white'

        self.setTitle(title)
        self.setTitleBrush(QtGui.QColor(pie_label_color))
        self.setMargins(QtCore.QMargins(0, 0, 0, 0))
        self.setBackgroundBrush(QtGui.QColor(pie_background_color))
        self.legend().setVisible(True)
        self.legend().setAlignment(QtCore.Qt.AlignBottom)
        self.legend().setLabelBrush(QtGui.QColor(pie_label_color))
        self.setAnimationOptions(QtCharts.QChart.SeriesAnimations)

        self.__series = QtCharts.QPieSeries()
        self.__series.setPieStartAngle(offset)
        self.__series.setPieEndAngle(offset+360)
        self.__series.setPieSize(0.99)
        self.__series.setHoleSize(0.6)
        self.addSeries(self.__series)

    def clear(self):
        """
        Clear all slices in the pie chart
        """
        for slice_ in self.__series.slices():
            self.__series.take(slice_)

    def add_slice(self, name, value, color):
        """
        Add one slice to the pie chart

        :param name: str. name of the slice
        :param value: value. value of the slice (contribute to how much the
                      slice would span in angle)
        :param color: str. hex code for slice color
        """
        slice_ = QtCharts.QPieSlice(name, value)
        slice_.setColor(QtGui.QColor(color))
        slice_.setLabelBrush(QtGui.QColor(color))

        slice_.hovered.connect(lambda is_hovered: self.__explode(slice_, is_hovered))
        # slice_.percentageChanged.connect(lambda: self.__update_label(slice_, name))

        self.__series.append(slice_)

    @staticmethod
    def __update_label(slice_, title):
        """
        Update the label of a slice

        :param slice_: QPieSlice. the slice the label is applied
        :param title: str. title of the label
        """
        text_color = 'white'
        if slice_.percentage() > 0.1:
            slice_.setLabelPosition(QtCharts.QPieSlice.LabelInsideTangential)
        else:
            slice_.setLabelPosition(QtCharts.QPieSlice.LabelOutside)

        label = "<p align='center' style='color:{}'>{}<br>{}%</p>".format(
            text_color,
            title,
            round(slice_.percentage() * 100, 2))
        slice_.setLabel(label)
        slice_.setLabelArmLengthFactor(0.3)
        if slice_.percentage() > 0.03:
            slice_.setLabelVisible()

    def __explode(self, slice_, is_hovered):
        """
        Explode function slot for hovering effect

        :param slice_: QtChart.QPieSlice. the slice hovered
        :param is_hovered: bool. hover enter (True) or leave (False)
        """
        if is_hovered:
            start = self.__series.pieStartAngle()
            end = self.__series.pieEndAngle()
            self.__series.setPieStartAngle(start+90)
            self.__series.setPieEndAngle(end+90)


class SmartChart(QtCharts.QChart):
    """
    A slightly smarter implementation of pie chart in Qt, with
    double looped pie chart layout design and hover animation.
    """

    def __init__(self, title, parent=None):
        """
        Initialization with layout and population
        """
        super(SmartChart, self).__init__(parent)
        offset = 0
        pie_background_color = '#171145'
        pie_label_color = 'white'

        self.setTitle(title)
        self.setTitleBrush(QtGui.QColor(pie_label_color))
        self.setMargins(QtCore.QMargins(0, 0, 0, 0))
        self.setBackgroundBrush(QtGui.QColor(pie_background_color))
        self.legend().setVisible(True)
        self.legend().setAlignment(QtCore.Qt.AlignBottom)
        self.legend().setLabelBrush(QtGui.QColor(pie_label_color))
        self.setAnimationOptions(QtCharts.QChart.SeriesAnimations)

        self.__outer = QtCharts.QPieSeries()
        self.__inner = QtCharts.QPieSeries()
        self.__outer.setPieSize(0.99)
        self.__outer.setHoleSize(0.6)
        self.__outer.setPieStartAngle(offset)
        self.__outer.setPieEndAngle(offset+360)
        self.__inner.setPieSize(0.5)
        self.__inner.setHoleSize(0.3)
        self.__inner.setPieStartAngle(offset)
        self.__inner.setPieEndAngle(offset+360)

        self.addSeries(self.__outer)
        self.addSeries(self.__inner)
        
        self.setMargins(QtCore.QMargins(0,0,0,0))

    def clear(self):
        """
        Clear all slices in the pie chart
        """
        for slice_ in self.__outer.slices():
            self.__outer.take(slice_)

        for slice_ in self.__inner.slices():
            self.__inner.take(slice_)

    def add_slice_outer(self, name, value, color):
        """
        Add one slice to the pie chart

        :param name: str. name of the slice
        :param value: value. value of the slice (contribute to how much the
                      slice would span in angle)
        :param color: str. hex code for slice color
        """
        # outer
        outer_slice = QtCharts.QPieSlice(name, value)
        outer_slice.setColor(QtGui.QColor(color))
        outer_slice.setLabelBrush(QtGui.QColor(color))

        outer_slice.hovered.connect(lambda is_hovered: self.__explode(outer_slice, is_hovered))
        outer_slice.percentageChanged.connect(lambda: self.__update_label_outer(outer_slice, name))

        self.__outer.append(outer_slice)

    def add_slice_inner(self, name, value, color):
        # inner
        inner_color = self.__get_secondary_color(color)
        # inner_color = color
        inner_slice = QtCharts.QPieSlice(name, value)
        self.__inner.append(inner_slice)
        inner_slice.setColor(inner_color)
        inner_slice.setBorderColor(inner_color)
        self.legend().markers(self.__inner)[-1].setVisible(False)

    def set_legend_outer(self, labels):
        for i, lbl in enumerate(labels):
            self.legend().markers(self.__outer)[i].setLabel(lbl)

    def set_legend_inner(self, labels):
        for i, lbl in enumerate(labels):
            self.legend().markers(self.__inner)[i].setVisible(True)
            self.legend().markers(self.__inner)[i].setLabel(lbl)

    @staticmethod
    def __update_label_outer(slice_, title):
        """
        Update the label of a outer slice

        :param slice_: QPieSlice. the slice the label is applied
        :param title: str. title of the label
        """
        text_color = 'white'
        if slice_.percentage() > 0.1:
            slice_.setLabelPosition(QtCharts.QPieSlice.LabelInsideTangential)
        else:
            slice_.setLabelPosition(QtCharts.QPieSlice.LabelOutside)

        label = "<p align='center' style='color:{}'>{}<br>{}%</p>".format(
            text_color,
            title,
            round(slice_.percentage()*100, 2)
            )
        slice_.setLabel(label)
        slice_.setLabelFont(QtGui.QFont("Arial", 10, QtGui.QFont.Bold))

        if slice_.percentage() > 0.03:
            slice_.setLabelVisible()

    def __explode(self, slice_, is_hovered):
        """
        Explode function slot for hovering effect

        :param slice_: QtChart.QPieSlice. the slice hovered
        :param is_hovered: bool. hover enter (True) or leave (False)
        """
        if is_hovered:
            start = self.__inner.pieStartAngle()
            end = self.__inner.pieEndAngle()
            self.__inner.setPieStartAngle(start+90)
            self.__inner.setPieEndAngle(end+90)
            self.__outer.setPieStartAngle(start+90)
            self.__outer.setPieEndAngle(end+90)

    @staticmethod
    def __get_secondary_color(hexcode):
        """
        Get secondary color which is blended 50% with white
        to appear lighter

        :param hexcode: str. color hex code starting with '#'
                        eg. ('#666666')
        :return: QtGui.QColor
        """
        from storage_backend import color

        new_color = color.ColorRGB.from_hex(hexcode).blend(percent=0.3).hexcode
        return QtGui.QColor(new_color)


class SimpleChartView(QtCharts.QChartView):
    """
    A simple wrapper chart view, to be expanded
    """
    def __init__(self, chart):
        super(SimpleChartView, self).__init__(chart)

        self.setRenderHint(QtGui.QPainter.Antialiasing)
