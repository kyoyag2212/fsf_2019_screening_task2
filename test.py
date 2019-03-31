import sys
from PyQt5.QtWidgets import QMainWindow, QAction, qApp, QApplication
from PyQt5 import QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5 import QtCore
import csv

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt


class Example(QMainWindow):

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.initMenu()
        self.csv_file_name = "testCSV.csv"

        # Create and use Grid layout
        self.grid_layout = QtWidgets.QGridLayout()
        centralWidget = QtWidgets.QWidget()
        centralWidget.setLayout(self.grid_layout)
        self.setCentralWidget(centralWidget)

        # Initialize the Table
        self.table = self.initTable(self.csv_file_name)
        vbox_sidewidgets = QtWidgets.QVBoxLayout()
        vbox_sidewidgets.addWidget(self.table)

        hbox_buttongroup = QtWidgets.QHBoxLayout()
        plot_line = QtWidgets.QPushButton("Plot line Chart", parent=self)
        plot_line.clicked.connect(lambda: self.plot_chart(type="line"))
        plot_scatter = QtWidgets.QPushButton("Plot scatter points", parent=self)
        plot_scatter.clicked.connect(lambda: self.plot_chart(type="scatter"))
        plot_scatter_line = QtWidgets.QPushButton("Plot scatter points with smooth line", parent=self)
        plot_scatter_line.clicked.connect(lambda: self.plot_chart(type="sline"))

        hbox_buttongroup.addWidget(plot_line)
        hbox_buttongroup.addWidget(plot_scatter)
        hbox_buttongroup.addWidget(plot_scatter_line)
        vbox_sidewidgets.addLayout(hbox_buttongroup)

        self.grid_layout.addLayout(vbox_sidewidgets, 0, 1)

        # Plotting the graph
        self.canvas, toolbar = self.initPlot()
        vbox_plot = QtWidgets.QVBoxLayout()
        vbox_plot.addWidget(toolbar)
        vbox_plot.addWidget(self.canvas)
        self.grid_layout.addLayout(vbox_plot, 0, 0)

        # Set the window properties
        self.setStyleSheet("background:#2b2b2b;color:white;font-size:20px;")
        self.setGeometry(300, 300, 600, 600)
        self.setWindowTitle('fsf_2019_screening_task2')
        # self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.show()

    def initMenu(self):
        menubar = self.menuBar()
        menubar.setStyleSheet("font-size:20px;color:white;")
        open = menubar.addMenu("Open")
        edit = menubar.addMenu("Edit")

        load = QAction("Load CSV", self)
        edit_ = QAction("Edit Table", self)

        open.addAction(load)
        edit.addAction(edit_)

    def initTable(self, csv_file_name):
        """
            Return QtTable with data filled from csv file

            Args:
                csv_file_name(str):File name of data to be extracted
            Return QtTableWidget

        """
        self.csv_data = self.get_csv_data(csv_file_name)
        csv_rows = len(self.csv_data) - 1
        csv_cols = len(self.csv_data[0])

        table = QtWidgets.QTableWidget(csv_rows, csv_cols)
        table.setHorizontalHeaderLabels(self.csv_data[0])
        _row = 0
        for i in self.csv_data[1:]:
            for _col in range(csv_cols):
                tabelItem = QtWidgets.QTableWidgetItem(i[_col])
                table.setItem(_row, _col, tabelItem)
            _row += 1

        table.horizontalHeader().setStyleSheet("::section{Background-color:#2b2b2b;}")
        table.verticalHeader().setStyleSheet("::section{Background-color:#2b2b2b;}")
        table.setStyleSheet("color:white;")

        return table

    def get_csv_data(self, csv_file_name=None):
        """
            Return the entire CSV data of given file in form of a list, which could be accessed by indexing

            Arguments:
                csv_file_name(str): The Location of the file to extract data from
            Return:
                data(List): The Data extracted form the CSV file
        """

        if csv_file_name == None:
            csv_file_name = self.csv_file_name
        csv_file = open(csv_file_name, "r")
        csv_reader = csv.reader(csv_file)
        csv_data = [i for i in csv_reader]
        return csv_data

    def initPlot(self):
        # a figure instance to plot on
        self.figure = plt.figure()

        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        canvas = FigureCanvas(self.figure)

        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        toolbar = NavigationToolbar(canvas, self)

        return canvas, toolbar

    def plot_chart(self, type="line"):
        """
            Plots the seleted columns of the QTableWidget, of given type(line,scatter)
            according to type provided
            Arguments:
                type(str): type of plot eg. line,scatter
            Return:
                None
        """

        anotationLabel = []

        if len(self.table.selectedRanges()) == 0:  # If no columns are selected
            return False

        csv_data = self.get_csv_data()

        selectedItemsByCols = {}
        for index in self.table.selectedIndexes():
            r = index.row() + 1  # Note that we have to ignore the First row which is the column names,hence +1
            c = index.column()
            if str(c) in selectedItemsByCols:
                selectedItemsByCols[str(c)].append(csv_data[r][c])
            else:
                anotationLabel.append(csv_data[0][c])
                selectedItemsByCols[str(c)] = [csv_data[r][c]]

        print("anotationLabel ", anotationLabel)

        self._plot_chart(selectedItemsByCols, "X-values", "Y values", anotationLabel[1:], type)

    def _plot_chart(self, plot_data, xLabel, yLabel, anotationLabel, chart='line'):
        """
            Plot the Data according to the chart type,labeling and anotating the chart

            Argument:
                plot_data(dict): Dictionary with Column as key and Rows of that column as Values
                xLabel(str): Label for the X-Axis( Usually the Column name of the given row)
                yLabel(str): Label for the Y-Axis
                anotationLabel(List): List containing the annotation labels for columns
                                    Note:- The first Column is assumed to lie on x-axis,
                                    so the variable should contain labelling for columns
                                    other then the first column in the dictionary.
                chart(str): Type of the plot, eg:- line,sline( scatter plot with smooth line),scatter.
            Return:
                None
        """

        self.figure.clear()
        # discards the old graph
        ax = self.figure.add_subplot(111)

        xLst = []  # store X axis values, which is the first column in the plot_data dictionary
        yLst = []  # store rest of col's values,followed by the marker :- https://matplotlib.org/api/_as_gen/matplotlib.pyplot.plot.html#Notes
        for col, value in plot_data.items():
            print(col, value)
            if xLst == []:
                xLst = value
            else:
                yLst.append(value)
                if chart == 'line':
                    yLst.append("b")
                elif chart == 'scatter':
                    yLst.append('bo')
                elif chart == 'sline':
                    yLst.append('bo-')

        # plot data
        if chart == 'line':
            ax.plot(xLst,
                    *yLst)  # unpack the list which is form of [ [y1,y2,y3],<marker_here>,[y1,y2,y3],<marker_here ] to [y1,y2,y3],<marker_here>,[y1,y2,y3],<marker_here
        elif chart == 'scatter':
            ax.plot(xLst, *yLst)
        elif chart == 'sline':
            print(yLst)
            ax.plot(xLst, *yLst)

        ax.set_xlabel(xLabel, fontsize=20)
        ax.set_ylabel(yLabel, fontsize=20)

        for an in range(len(anotationLabel)):
            ax.annotate(anotationLabel[an], xy=(0.1, yLst[an if an % 2 == 0 else an + 1][
                0]))  # x co-ordinate is fixed at 0.1 while y co-ordinate is the first value in the column
        self.canvas.draw()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())