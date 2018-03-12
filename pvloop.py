 
import numpy as np
#import pandas as pd
#from shutil import copyfile
 
from guidata.qt.QtGui import QMainWindow, QSplitter

from guidata.dataset.datatypes import DataSet
from guidata.dataset.dataitems import FileOpenItem
from guidata.configtools import get_icon
from guidata.qthelpers import create_action, add_actions, get_std_icon
 

import sys
import pyqtgraph as PG
from PyQt4 import QtGui
from PyQt4 import QtCore
#from PyQt4.QtGui import * 
#from PyQt4.QtCore import *

import ode_solver

 
#-----------------------------------
class SmoothGUI(DataSet):

    fname = FileOpenItem("Open file", ("txt", "csv"), "")
    
  
#-----------------------------------
class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.setWindowIcon(get_icon('python.png'))
        self.setWindowTitle("PV Loop Simulation")
        
        pal=QtGui.QPalette()
        role = QtGui.QPalette.Background
        pal.setColor(role, QtGui.QColor(255, 255, 255))
        self.setPalette(pal)
       
        self.textEdit = QtGui.QLabel('None')

        self.loadButton = QtGui.QPushButton("Load")
        self.loadButton.clicked.connect(self.on_click)
        self.buttonSave = QtGui.QPushButton('Clear Plot', self)
        self.buttonSave.clicked.connect(self.clearPlots)
         #self.connect(self.smoothGB, SIGNAL("apply_button_clicked()"),
         #self.update_window)
        self.table1 = QtGui.QTableWidget()
        self.table2 = QtGui.QTableWidget()
         
        self.fileName = ''
        self.lastClicked = []
        self.number_plots = 0       

        
        self.pw1 = PG.PlotWidget(name='VTC')
        self.pw1.setLabel('left', 'Volume', units='mL')
        self.pw1.setLabel('bottom', 'Time', units='s')
        self.pw1.setBackground((255,255,255))
        
        self.pw2 = PG.PlotWidget(name='VTC')
        self.pw2.setBackground((255,255,255))
        self.pw2.setLabel('left', 'Pressure', units='mmHg')
        self.pw2.setLabel('bottom', 'Time', units='s')
        
        self.pw3 = PG.PlotWidget(name='PV')
        self.pw3.setBackground((255,255,255))
        self.pw3.setLabel('left', 'Pressure', units='mmHg')
        self.pw3.setLabel('bottom', 'Volume', units='ml')
        
        #horizontalLayout = QtGui.QHBoxLayout(self)
        splitter = QSplitter(QtCore.Qt.Vertical)
        splitter2 = QSplitter(QtCore.Qt.Vertical)
        splitterH = QSplitter(QtCore.Qt.Horizontal)
        

        splitter.addWidget(self.loadButton)
        splitter.addWidget(self.pw1)
        splitter.addWidget(self.pw2)
        splitter.addWidget(self.pw3)
        
        splitter2.addWidget(self.table1)
        splitter2.addWidget(self.table2)
        splitter2.addWidget(self.buttonSave)
        
        splitterH.addWidget(splitter)
        splitterH.addWidget(splitter2)
        
        self.table1.setRowCount(5)
        self.table1.setColumnCount(2)
        
        self.table2.setRowCount(8)
        self.table2.setColumnCount(2)
        

        self.table1.setItem(0,0, QtGui.QTableWidgetItem("Number of Loops [-]"))
        self.table1.setItem(0,1, QtGui.QTableWidgetItem("4"))
        self.table1.setItem(1,0, QtGui.QTableWidgetItem("HR [bpm]"))
        self.table1.setItem(1,1, QtGui.QTableWidgetItem("70"))
        self.table1.setItem(2,0, QtGui.QTableWidgetItem("V (LV) start [ml]"))
        self.table1.setItem(2,1, QtGui.QTableWidgetItem("135"))
        self.table1.setItem(3,0, QtGui.QTableWidgetItem("Pa start [mmHg]"))
        self.table1.setItem(3,1, QtGui.QTableWidgetItem("96"))
        self.table1.setItem(4,0, QtGui.QTableWidgetItem("Pv start [mmHg]"))
        self.table1.setItem(4,1, QtGui.QTableWidgetItem("6"))
        
        self.table2.setItem(0,0, QtGui.QTableWidgetItem("Rp"))
        self.table2.setItem(0,1, QtGui.QTableWidgetItem("1.3"))
        self.table2.setItem(1,0, QtGui.QTableWidgetItem("Ra"))
        self.table2.setItem(1,1, QtGui.QTableWidgetItem("0.1"))
        self.table2.setItem(2,0, QtGui.QTableWidgetItem("Rin"))
        self.table2.setItem(2,1, QtGui.QTableWidgetItem("0.08782"))
        self.table2.setItem(3,0, QtGui.QTableWidgetItem("Ca"))
        self.table2.setItem(3,1, QtGui.QTableWidgetItem("1.601"))
        self.table2.setItem(4,0, QtGui.QTableWidgetItem("Cv"))
        self.table2.setItem(4,1, QtGui.QTableWidgetItem("1.894"))
        self.table2.setItem(5,0, QtGui.QTableWidgetItem("Vd"))
        self.table2.setItem(5,1, QtGui.QTableWidgetItem("1.123"))
        self.table2.setItem(6,0, QtGui.QTableWidgetItem("Emax"))
        self.table2.setItem(6,1, QtGui.QTableWidgetItem("1.5"))
        self.table2.setItem(7,0, QtGui.QTableWidgetItem("Emin"))
        self.table2.setItem(7,1, QtGui.QTableWidgetItem("0.037"))

        
        self.setCentralWidget(splitterH)
 
        self.setContentsMargins(10, 5, 10, 5)
        self.setGeometry(100, 100, 1000, 800)
        
         # File menu
        file_menu = self.menuBar().addMenu("File")
        quit_action = create_action(self, "Quit",
        shortcut="Ctrl+Q",
        icon=get_std_icon("DialogCloseButton"),
        tip="Quit application",
        triggered=self.close)
        add_actions(file_menu, (quit_action, ))

        
    def clearPlots(self):
        self.pw1.clear()
        self.pw2.clear()
        self.pw3.clear()
         
         
    def on_click(self):
        start_v = float(self.table1.item(2,1).text())
        start_pa = float(self.table1.item(3,1).text())
        start_pv =float(self.table1.item(4,1).text())
        
        HR = float(self.table1.item(1,1).text())        
        HC = 1/HR*60
        
        number_of_HC = float(self.table1.item(0,1).text()) 
        t = np.linspace(0, HC*number_of_HC, 1000*number_of_HC)
        Rp = float(self.table2.item(0,1).text())  
        Ra = float(self.table2.item(1,1).text())
        Rin = float(self.table2.item(2,1).text())
        Ca = float(self.table2.item(3,1).text())
        Cv = float(self.table2.item(4,1).text())
        Vd = float(self.table2.item(5,1).text())
        Emax = float(self.table2.item(6,1).text())
        Emin = float(self.table2.item(7,1).text())
        
        print(HC,Rp,Ra,Rin,Ca,Cv,Vd,Emax,Emin)  
        
        glob_para = ode_solver.init_glob_para(HC)        
        pv_model= ode_solver.compute_ode(Rp,Ra,Rin,Ca,Cv,Vd,Emax,Emin,t,start_v,start_pa,start_pv)
        Plv_vector = [ode_solver.Plv(v, Vd, Emax, Emin, x) for x,v in zip(t,pv_model[0])]
        #print(pv_model[0])
        
        col = ["b", "r", "k", "c", "m"]
        mypen = PG.mkPen(col[self.number_plots], width=3)
        
        self.pw1.plot(t, np.array(pv_model[0]),pen=mypen)
        self.pw2.plot(t, np.array(Plv_vector),pen=mypen)
        self.pw3.plot(np.array(pv_model[0]), np.array(Plv_vector),pen=mypen)
        
        if self.number_plots < 4:
            self.number_plots += 1
        else:
            self.number_plots = 0
             
        print('PV loop computed')

        
if __name__ == '__main__':
    from guidata.qt.QtGui import QApplication
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())