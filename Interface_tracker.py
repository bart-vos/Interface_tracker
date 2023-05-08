

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
from skimage import io
from matplotlib.patches import Rectangle
from scipy.ndimage import gaussian_filter


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
        uic.loadUi("Interface_tracker.ui", self)

        # setup gui elements
#        self.setupUi(self)

        # connect gui interactions such as clicked, triggered, returnPressed
        # to application slots
        
        self.actionQuit.triggered.connect(QtWidgets.QApplication.quit)
        
        self.fileButton = self.findChild(QtWidgets.QPushButton, "fileButton")
        self.fileButton.clicked.connect(self.selectFile)
        
        self.fileEdit = self.findChild(QtWidgets.QLineEdit, "fileEdit")
#        self.fileButton.changed.connect(self.selectFile)
        
        self.search_up = self.findChild(QtWidgets.QSpinBox, "search_up")
        self.search_down = self.findChild(QtWidgets.QSpinBox, "search_down")
        self.xlim0 = self.findChild(QtWidgets.QSpinBox, "xlim_0")
        self.xlim1 = self.findChild(QtWidgets.QSpinBox, "xlim_1")
        self.ylim0 = self.findChild(QtWidgets.QSpinBox, "ylim_0")
        self.ylim1 = self.findChild(QtWidgets.QSpinBox, "ylim_1")
        self.pos_guess = self.findChild(QtWidgets.QSpinBox, "pos_guess")
        self.drawRectButton = self.findChild(QtWidgets.QPushButton, "drawRectButton")
        
        self.xlim0.valueChanged.connect(self.plotTiffRect)
        self.xlim1.valueChanged.connect(self.plotTiffRect)
        self.ylim0.valueChanged.connect(self.plotTiffRect)
        self.ylim1.valueChanged.connect(self.plotTiffRect)
        self.pos_guess.valueChanged.connect(self.plotTiffRect)
        self.drawRectButton.clicked.connect(self.plotTiffRect)
        
        self.lightDarkSlider = self.findChild(QtWidgets.QSlider, "LightDarkSlider")
        self.gaussianFilter = self.findChild(QtWidgets.QDoubleSpinBox, "gaussianFilter")
        
        self.previewButton = self.findChild(QtWidgets.QPushButton, "previewButton")
        self.previewButton.clicked.connect(self.plotLineData)
        
        self.analyseButton = self.findChild(QtWidgets.QPushButton, "analyseButton")
        self.analyseButton.clicked.connect(self.analyseData)
        
        self.saveButton = self.findChild(QtWidgets.QPushButton, "saveButton")
        self.saveButton.clicked.connect(self.saveData)
        self.saveFile = self.findChild(QtWidgets.QLineEdit, "saveFile")
        
        self.saveArrayButton = self.findChild(QtWidgets.QPushButton, "saveArrayButton")
        self.saveArrayButton.clicked.connect(self.saveArrayData)
        self.saveArrayFile = self.findChild(QtWidgets.QLineEdit, "saveArrayFile")
        
        
        
        self.plot1tracker = 0
        self.plot2tracker = 0
        self.im_data = np.array([])     # Initialize; we'll check later if it is filled or not
    
    def QuitGui(self):
        QtWidgets.QApplication.quit
    
    
    def addmpl(self, fig):
        self.canvas1 = FigureCanvas(fig)
        self.mplvl.addWidget(self.canvas1)
        self.canvas1.draw()
#        self.toolbar = NavigationToolbar(self.canvas, self.mplwindow, coordinates=True)
#        self.mplvl.addWidget(self.toolbar)
    
    def rmmpl(self):
        self.mplvl.removeWidget(self.canvas1)
        self.canvas1.close()
#        self.mplvl.removeWidget(self.toolbar)
#        self.toolbar.close()
    
    def addmpl2(self, fig):
        self.canvas2 = FigureCanvas(fig)
        self.mplvl2.addWidget(self.canvas2)
        self.canvas2.draw()
    
    def rmmpl2(self):
        self.mplvl2.removeWidget(self.canvas2)
        self.canvas2.close()
    
    def plotTiff(self, im_data):
        
        if self.plot1tracker == 1:
            self.rmmpl()
        
        fig1 = Figure( tight_layout=True )
        ax1f1 = fig1.add_subplot(111)
        ax1f1.clear()
        ax1f1.imshow(im_data[0,:,:], cmap='Greys_r')
#        fig1.xlabel('Length / pixel')
#        fig1.ylabel('Length / pixel')
        self.addmpl(fig1)
        
        self.plot1tracker = 1
        
    def plotTiffRect(self):
        # Don't plot a rectangle unless the data file is loaded
        if self.im_data.size==0:
            text = 'Select an image file first'
            reply = QtWidgets.QMessageBox.information(None, "Warning", text, QtWidgets.QMessageBox.Ok )
            if reply == QtWidgets.QMessageBox.Ok:
                return      # Don't continue with the analysis
        
        # First clean the plot that is already there
        self.rmmpl()
        
        im_data = self.im_data
        xlim0 = self.xlim0.value()
        xlim1 = self.xlim1.value()
        ylim0 = self.ylim0.value()
        ylim1 = self.ylim1.value()
        pos_guess = self.pos_guess.value()
                
        fig1 = Figure( tight_layout=True )
        ax1f1 = fig1.add_subplot(111)
        ax1f1.imshow(im_data[0,:,:], cmap='Greys_r')
        rect = Rectangle( (xlim0, ylim0), xlim1-xlim0, ylim1-ylim0, linewidth=2, edgecolor='g',facecolor='none')
        fig1.gca().add_patch(rect)
        ax1f1.plot([pos_guess, pos_guess],[ylim0-10, ylim1+10])
        self.addmpl(fig1)
    
    def plotLineData(self):
        # Don't preview the data unless the data file is loaded
        if self.im_data.size==0:
            text = 'Select an image file first'
            reply = QtWidgets.QMessageBox.information(None, "Warning", text, QtWidgets.QMessageBox.Ok )
            if reply == QtWidgets.QMessageBox.Ok:
                return      # Don't continue with the analysis
        
        if self.plot2tracker == 1:
            self.rmmpl2()
        
        im_data = self.im_data
        num_files = self.num_files
        xlim0 = self.xlim0.value()
        xlim1 = self.xlim1.value()
        ylim0 = self.ylim0.value()
        ylim1 = self.ylim1.value()
        
        line_data_der = np.zeros([num_files, xlim1 - xlim0])
        for x in np.arange(num_files):
            line_temp = im_data[x, ylim0:ylim1, xlim0:xlim1]
            line_data_der[x,:] = np.mean(line_temp, axis = 0)
            line_data_der[x,:] = gaussian_filter(line_data_der[x,:], sigma=self.gaussianFilter.value())
            
            
        
        line_data_der = np.gradient(line_data_der, axis=1)
        
        time_array = np.arange(num_files)
        length_array = np.arange(xlim0,xlim1)
        
        
        fig2 = Figure( tight_layout=True )
        ax1f2 = fig2.add_subplot(111)
        ax1f2.contourf( time_array, length_array, np.transpose(line_data_der))
        ax1f2.set_xlabel('Time (a.u.)')
        ax1f2.set_ylabel('Position along pipette (pixel)')
        self.addmpl2(fig2)
        
        self.line_data_der = line_data_der
        self.plot2tracker = 1
        return line_data_der
        
        
        
    def analyseData(self):
        # Don't preview the data unless the data file is loaded
        if self.im_data.size==0:
            text = 'Select an image file first'
            reply = QtWidgets.QMessageBox.information(None, "Warning", text, QtWidgets.QMessageBox.Ok )
            if reply == QtWidgets.QMessageBox.Ok:
                return      # Don't continue with the analysis
        
        # First make sure that the line derivative data is there
#        t=self.plotLineData()
        
        self.rmmpl2()
        
        xlim0 = self.xlim0.value()
        xlim1 = self.xlim1.value()
        search_up = self.search_up.value()
        search_down = self.search_down.value()
        pos_guess = self.pos_guess.value()
        num_files = self.num_files
        line_data_der = self.line_data_der
        
        pos_data = np.zeros([num_files,2])
        pos_guess = pos_guess - xlim0
        
        
        
        if self.lightDarkSlider.value()==0:
            for x in np.arange(num_files):
                
                # Search in a region around the previous minimum
                temp = line_data_der[x, pos_guess-search_down : pos_guess+search_up]
                
                # Look for the position of the minimum
                min_pos = np.argmin(temp) + pos_guess
                
                # Update the guessed position for the next round
                pos_guess = min_pos - search_down
                
                # Now make sure that the guessed position never goes out of the selected region along the line
                if pos_guess <= search_down: pos_guess = search_down
                if pos_guess >= (xlim1-xlim0) - search_up: pos_guess = (xlim1-xlim0) - search_up
                
                # Better guess the actual, sub-pixel minimum
                tempx = [-2,-1,0,1,2]
                tempy = line_data_der[x,pos_guess-2:pos_guess+3]
                
                tempfit = np.polyfit(tempx, tempy,2)
                correction = -tempfit[1]/(2*tempfit[0]) 
                
                # Kick out the clearly-off values
                if np.abs(correction) >= 1: correction = 0
                
                # Put the position of the minimum and its value in an array
                pos_data[x,:] = [min_pos + correction, np.min(temp)]   
        
        if self.lightDarkSlider.value()==1:
            for x in np.arange(num_files):
                
                # Search in a region around the previous minimum
                temp = line_data_der[x, pos_guess-search_down : pos_guess+search_up]
                
                # Look for the position of the maximum
                max_pos = np.argmax(temp) + pos_guess
                
                # Update the guessed position for the next round
                pos_guess = max_pos - search_down
                
                # Now make sure that the guessed position never goes out of the selected region along the line
                if pos_guess <= search_down: pos_guess = search_down
                if pos_guess >= (xlim1-xlim0) - search_up: pos_guess = (xlim1-xlim0) - search_up
                
                # Better guess the actual, sub-pixel minimum
                tempx = [-2,-1,0,1,2]
                tempy = line_data_der[x,pos_guess-2:pos_guess+3]
                
                tempfit = np.polyfit(tempx, tempy,2)
                correction = -tempfit[1]/(2*tempfit[0]) 
                
                # Kick out the clearly-off values
                if np.abs(correction) >= 1: correction = 0
                
                # Put the position of the maximum and its value in an array
                pos_data[x,:] = [max_pos + correction, np.max(temp)]  
        
        time_array = np.arange(num_files)
        length_array = np.arange(xlim0,xlim1)
        
        fig2 = Figure( tight_layout=True )
        ax1f2 = fig2.add_subplot(111)
        ax1f2.contourf( time_array, length_array, np.transpose(line_data_der))
        ax1f2.plot(pos_data[:,0]+xlim0-search_down, '-k', alpha=0.5)
        
        ax1f2.set_xlabel('Time (a.u.)')
        ax1f2.set_ylabel('Position along pipette (pixel)')
        self.addmpl2(fig2)
        
        self.pos_data = pos_data
        return pos_data
    
    
    
    def selectFile(self):
        file_name = str(QtWidgets.QFileDialog.getOpenFileName()[0])
        self.fileEdit.setText(file_name)
        im_data = io.imread(file_name)
        num_files = np.shape(im_data)[0]
        
        self.plotTiff(im_data)
        
        self.im_data = im_data
        self.num_files = num_files
        return im_data, num_files
    
    def saveData(self):
        save_loc = self.saveFile.text()
        
        num_files = self.num_files
        pos_data = self.pos_data
        
        time_array = np.arange(num_files)
        
        
        t1 = np.transpose(np.vstack([time_array, pos_data[:,0]]))
        np.savetxt(save_loc, t1, fmt='%5.2f')
        
        
    def saveArrayData(self):
        save_loc = self.saveArrayFile.text()
        
        line_data_der = self.line_data_der
        
        np.savetxt(save_loc, line_data_der, fmt='%5.2f')
         
        
        
    

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
