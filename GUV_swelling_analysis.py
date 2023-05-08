

# QtCore: core modules, such as QSize, ...
# QtGui: e.g. QIcon
# QtWidgets: e.g. QPushButton, QLineEdit, ...
from PyQt5 import QtCore, QtGui, QtWidgets, uic#, QtFileDialog
# This will be the main plotting area
#from guiqwt.plot import CurveWidget


# Notice that the generic pyplot module is not imported — do not use the functions from this module
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import (
    FigureCanvasQTAgg as FigureCanvas,
    NavigationToolbar2QT as NavigationToolbar)
import numpy as np
from scipy.optimize import curve_fit

import sys

class MyApplication(QtWidgets.QMainWindow):
    """
    Your main thread handling the gui among with its user interactions such as mouse clicks etc.
    """
    def __init__(self, parent=None):
        """
        Initialise the GUI
        Connect signals with slots, e.g. button-clicks with functions etc.

        Always add
        > super(MyApplication, self).__init__(parent)
        > self.setupUi(self)
        
        """
        # initialize gui when creating the application
        super(MyApplication, self).__init__()
        uic.loadUi("GUV_swelling_analysis.ui", self)

        # setup gui elements
#        self.setupUi(self)

        # connect gui interactions such as clicked, triggered, returnPressed
        # to application slots
        
        self.actionQuit.triggered.connect(QtWidgets.QApplication.quit)
        
        self.fileButton = self.findChild(QtWidgets.QPushButton, "fileButton")
        self.fileButton.clicked.connect(self.selectFile)
        self.fileEdit = self.findChild(QtWidgets.QLineEdit, "fileEdit")
        
        self.timestampButton = self.findChild(QtWidgets.QPushButton, "timestampButton")
        self.timestampButton.clicked.connect(self.selectTimestamp)
        self.timestampEdit = self.findChild(QtWidgets.QLineEdit, "timestampEdit")
        
        self.xmin = self.findChild(QtWidgets.QSpinBox, "xmin")
        self.xmax = self.findChild(QtWidgets.QSpinBox, "xmax")
        
        self.check_minmax = self.findChild(QtWidgets.QCheckBox, "check_minmax")
        self.check_fitExponent = self.findChild(QtWidgets.QCheckBox, "check_fitExponent")
        
        self.result1Edit = self.findChild(QtWidgets.QLineEdit, "result1Edit")
        self.result2Edit = self.findChild(QtWidgets.QLineEdit, "result2Edit")
        
        self.analyseButton = self.findChild(QtWidgets.QPushButton, "analyseButton")
        self.analyseButton.clicked.connect(self.analyseData)
        
        self.get_min_coords = self.findChild(QtWidgets.QPushButton, "get_min_coords")
        self.get_max_coords = self.findChild(QtWidgets.QPushButton, "get_max_coords")
        self.get_min_coords.clicked.connect(self.set_xmin)
        self.get_max_coords.clicked.connect(self.set_xmax)
        
#        self.saveButton = self.findChild(QtWidgets.QPushButton, "saveButton")
#        self.saveButton.clicked.connect(self.saveData)
#        self.saveFile = self.findChild(QtWidgets.QLineEdit, "saveFile")
        
        self.plot1tracker = 0       # Track if the figure already has been plotted
        self.data = np.array([])    # Initialize; we'll check later if it is filled or not
        self.timedata = np.array([])
        self.xcoord = 0
        
        
    def QuitGui(self):
        QtWidgets.QApplication.quit
    
    
    def addmpl(self, fig):
        self.canvas1 = FigureCanvas(fig)
        self.mplvl.addWidget(self.canvas1)
        self.canvas1.draw()
#        self.toolbar = NavigationToolbar(self.canvas, self.mplwindow, coordinates=True)
#        self.mplvl.addWidget(self.toolbar)
        self.canvas1.mpl_connect("button_press_event", self.on_press)
    
    def rmmpl(self):
        self.mplvl.removeWidget(self.canvas1)
        self.canvas1.close()
#        self.mplvl.removeWidget(self.toolbar)
#        self.toolbar.close()
    
    def selectFile(self):
        file_name = str(QtWidgets.QFileDialog.getOpenFileName()[0])
        self.fileEdit.setText(file_name)
        self.data = np.loadtxt(file_name)
        
        if self.plot1tracker == 1:
            self.rmmpl()
        
        fig1 = Figure( tight_layout=True )
        ax1f1 = fig1.add_subplot(111)
        ax1f1.plot(self.data[:,0], self.data[:,1], 'k')
        ax1f1.set_xlabel('Time (frame)')
        ax1f1.set_ylabel('Intensity (a.u.)')
#        fig1.tight_layout()
        self.addmpl(fig1)
        
        
        self.plot1tracker = 1
    
    def on_press(self, event):
        
        self.xcoord = event.xdata
        
        # First remove the existing figure, then add the new figure with a dot
        # on the clicked locaion
        self.rmmpl()
        fig1 = Figure( tight_layout=True )
        ax1f1 = fig1.add_subplot(111)
        ax1f1.plot(self.data[:,0], self.data[:,1], 'k')
        ax1f1.set_xlabel('Time (frame)')
        ax1f1.set_ylabel('Length (pixel)')
        ax1f1.plot(event.xdata, event.ydata , 'r', marker = 'o')
#        ax1f1.tight_layout()
        self.addmpl(fig1)
    
    def set_xmin(self):
        xcoord = int(np.round(self.xcoord))
        self.xmin.setValue(xcoord)
        
    def set_xmax(self):
        xcoord = int(np.round(self.xcoord))
        self.xmax.setValue(xcoord)
        
        
        
    
    def selectTimestamp(self):
        file_name = str(QtWidgets.QFileDialog.getOpenFileName()[0])
        self.timestampEdit.setText(file_name)
        self.timedata = np.loadtxt(file_name)
    
    def analyseData(self):
        
        # Don't analyse the data unless the data file is loaded
        if self.data.size==0:
            text = 'Select a data file first'
            reply = QtWidgets.QMessageBox.information(None, "Warning", text, QtWidgets.QMessageBox.Ok )
            if reply == QtWidgets.QMessageBox.Ok:
                return      # Don't continue with the analysis
        
        # Now load the data
        data = self.data
        xmax = self.xmax.value()
        xmin = self.xmin.value()
        
        # Remove the existing plot, and start assembling a new one
        self.rmmpl()
        fig1 = Figure( tight_layout=True )
        ax1f1 = fig1.add_subplot(111)
        ax1f1.plot(data[:,0], data[:,1], 'k')
        
        # First do the min-max analysis
        if self.check_minmax.isChecked() == True:
            dif = np.round(np.mean(data[xmax-5:xmax,1]) - np.mean(data[xmin-5:xmin,1]),1)
            
            # Write down the result
            self.result1Edit.setText(str(dif))
            # And plot the result
            ax1f1.axhline(np.mean(data[xmax-5:xmax,1]) , linestyle='--', color='b')
            ax1f1.axhline(np.mean(data[xmin-5:xmin,1]) , linestyle='--', color='b')
        
        # Now do the exponential fitting
        if self.check_fitExponent.isChecked() == True:
            # Don't analyse the data unless the data file is loaded
            if self.timedata.size==0:
                text = 'Select a timestamp file first'
                reply = QtWidgets.QMessageBox.information(None, "Warning", text, QtWidgets.QMessageBox.Ok )
                if reply == QtWidgets.QMessageBox.Ok:
                    return      # Don't continue with the analysis
            
            # Load the timestamp data
            timedata = self.timedata
            
            def exponent(x,a,x0, tau):
                return a * np.exp(-(x-x0)/tau) + y0
            
            # First get the correct time-axis
            data_x = timedata[xmin:xmax,1] - timedata[xmin,1]
            
            # And the corresponding position values
            data_y = data[xmin:xmax,1]
            
            # Guess the final position
            y0 = np.mean(data[xmax-5:xmax,1])
            
            # The actual fitting
            popt,pcov = curve_fit(exponent, data_x, data_y, p0 = [-0.1, 40., 100.])
            
            # Write down the result
            self.result2Edit.setText(str(np.round(popt[2])))
            # And plot the result
            ax1f1.plot(data[xmin:xmax,0], exponent(data_x, popt[0], popt[1], popt[2]), 'r')
            
        ax1f1.set_xlabel('Time (frame)')
        ax1f1.set_ylabel('Length (pixel)')
        self.addmpl(fig1)
        
#    def saveData(self):
#        save_loc = self.saveFile.text()
#        
#        num_files = self.num_files
#        pos_data = self.pos_data
#        
#        time_array = np.arange(num_files)
#        
#        
#        t1 = np.transpose(np.vstack([time_array, pos_data[:,0]]))
#        np.savetxt(save_loc, t1, fmt='%5.2f')
        
        
        

    

if __name__ == "__main__":
    
    
    # create an application instance
    app = QtWidgets.QApplication(sys.argv)
    # delete gui elements when application is about to be close
    app.aboutToQuit.connect(app.deleteLater)
    # actual application window
    window = MyApplication()
    
    
    
    
    window.show()
    
    # execute application
    app.exec_()
#    sys.exit(app.exec_())
