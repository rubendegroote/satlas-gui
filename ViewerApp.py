from PyQt4 import QtCore,QtGui
from satlas.analysisIO import save,load
from PyQt4 import QtCore,QtGui
import matplotlib.pyplot as plt

class Viewer(QtGui.QMainWindow):
    def __init__(self):
        super(Viewer, self).__init__()
        self.analysis = None
        self.figs = []

        menubar = self.menuBar()

        self.splitter = QtGui.QSplitter()
        self.setCentralWidget(self.splitter)

        self.model = QtGui.QFileSystemModel()
        path = str(QtGui.QFileDialog.getExistingDirectory(self, "Select Directory"))
        self.model.setRootPath(path)
        filters = ["*.analysis"]
        self.model.setNameFilters(filters)
        self.model.setNameFilterDisables(False)
        
        self.view = QtGui.QTreeView()
        self.view.setModel(self.model)
        self.view.setRootIndex(self.model.index(path))
        self.view.setColumnHidden(1, True)
        self.view.setColumnHidden(2, True)
        self.view.setColumnHidden(3, True)
        self.view.doubleClicked.connect(self.open)
        self.view.setMaximumWidth(500)
        self.splitter.addWidget(self.view)

        self.tabs = QtGui.QTabWidget()
        self.splitter.addWidget(self.tabs)

        self.setGeometry(QtCore.QRect(128, 128, 800, 600))

        self.show()

    def open(self,index):
        self.tabs.clear()

        for f in self.figs:
            plt.close(f[0])

        path = self.model.filePath(index)
        self.analysisName = self.model.fileName(index)
        self.analysis = load(path)
        self.make_analysis_view()

    def make_analysis_view(self):
        for data_unit in self.analysis.data_units:
            try:
                self.make_approach_overview(data_unit)
            except FileNotFoundError:
                for i,p in enumerate(data_unit.files):
                    error = QtGui.QErrorMessage()
                    error.showMessage('Data File not found. Original location: {}'.format(p))
                    error.exec_()

                    filename = QtGui.QFileDialog.getOpenFileName(
                            self, 'Select missing data file', '')
                    data_unit.files[i] = filename
                    save(self.analysis,self.analysisName)

                try:
                    self.make_approach_overview()
                except FileNotFoundError as e:
                    error = QtGui.QErrorMessage()
                    error.showMessage(str(e))
                    error.exec_()

    def make_approach_overview(self,data_unit):
        fig, ax = data_unit.plot(show=False)
        self.figs.append((fig,ax))                
        self.tabs.addTab(ApproachOverview(data_unit,fig),data_unit.name)

from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar
class ApproachOverview(QtGui.QSplitter):
    def __init__(self,data_unit,fig):
        super(ApproachOverview,self).__init__()
        
        self.spectrum = data_unit.spectrum

        self.parWidget = QtGui.QTableWidget()
        self.addWidget(self.parWidget)
        self.populateTable()

        figureWidget = QtGui.QWidget()
        figureLayout = QtGui.QVBoxLayout(figureWidget)
        
        canvas = FigureCanvas(fig)
        toolbar = NavigationToolbar(canvas, self)
        figureLayout.addWidget(canvas)
        figureLayout.addWidget(toolbar)

        self.addWidget(figureWidget)

    def populateTable(self):
        names,values,errors = self.spectrum.vars()
        self.parWidget.setRowCount(len(names))
        self.parWidget.setColumnCount(3)
        for i,(n,v,ve) in enumerate(zip(names,values,errors)):
            self.parWidget.setItem(i,0,QtGui.QTableWidgetItem(n))
            self.parWidget.setItem(i,1,QtGui.QTableWidgetItem(str(v)))
            self.parWidget.setItem(i,2,QtGui.QTableWidgetItem(str(ve)))