import sys
import os
import datetime
import csv
import json
import time
import urllib
import urllib3
import webbrowser


from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

import matplotlib.pyplot as plt
plt.style.use('ggplot')


ccodes = []
wburl = "http://api.worldbank.org/v2/countries/"


class winMain(QtWidgets.QWidget):

    def connectionTest(self,urlstr):
        try:
            urllib.request.urlopen(urlstr,timeout=5)
            return True
        except urllib.request.URLError:
            return False

    def openBrowser(self):
        if self.lblSourceVal.text()=="-":
            QtWidgets.QMessageBox.critical(self,"WBFetch","Url not corrected!",QtWidgets.QMessageBox.Ok)
        else:
            try:
                webbrowser.open(self.lblSourceVal.text())
                return True
            except webbrowser.Error:
                QtWidgets.QMessageBox.critical(self,"WBFetch","Default browser not defined!",QtWidgets.QMessageBox.Ok)
                return False
        
    def showRowVal(self):
        global ccodes, wburl
        urlstr=''
        ccodes=[]
        # check time range
        dy = self.dateTo.date().getDate()[0]-self.dateFrom.date().getDate()[0]
        if dy<=0:
            QtWidgets.QMessageBox.critical(self,"WBFetch","Time Range not correct!",QtWidgets.QMessageBox.Ok)
            self.dateFrom.setFocus()
            return False
        # check all rows
        for i in range(self.tblCountry.rowCount()):
            if self.tblCountry.item(i,0).checkState()==2:
                itm = {'id':self.tblCountry.item(i,1).text(), 'value':self.tblCountry.item(i,2).text()}
                ccodes.append(itm)
        if len(ccodes)==0:
            QtWidgets.QMessageBox.critical(self,"WBFetch","Choose one or two countries in the list!",QtWidgets.QMessageBox.Ok)
            self.tblCountry.setFocus()
            self.tblCountry.setCurrentCell(0,0)
            return False
        # check cmbType
        if self.cmbType.currentText()=="-":
            QtWidgets.QMessageBox.critical(self,"WBFetch","Choose Type of Indicator!",QtWidgets.QMessageBox.Ok)
            self.cmbType.setFocus()
            return False
        # check Indicator
        if self.cmbIndicator.currentText()=="-":
            QtWidgets.QMessageBox.critical(self,"WBFetch","Choose indicator!",QtWidgets.QMessageBox.Ok)
            self.cmbIndicator.setFocus()
            return False
        # fetching data
        indic = self.cmbIndicator.currentText().split("-")
        yearFrom = self.dateFrom.date().getDate()[0]
        yearTo = self.dateTo.date().getDate()[0]
        cstr =""
        if len(ccodes)>1:
            for i in range(len(ccodes)):
                cstr=cstr+ccodes[i]['id']+";"
            cstr = cstr[:-1]
        else:
            cstr=ccodes[0]['id']
        http = urllib3.PoolManager()
        urlstr=wburl+cstr+"/indicators/"+indic[0]+"?date="+str(yearFrom)+":"+str(yearTo)+"&format=json"
        recv = http.request('GET', urlstr)
        dat = json.loads(recv.data.decode('utf-8'))
        # dat[1] containt all fetch data
        datToPlot = dat[1]
        self.ax.set_title(indic[1])
        for i in range(len(ccodes)):
            nx,ny = [],[]
            for j in range(len(datToPlot)):
                if ccodes[i]['id']==datToPlot[j]['country']['id']:
                    nx.append(int(datToPlot[j]['date']))
                    ny.append(datToPlot[j]['value'])
                    print(datToPlot[j]['country']['id']+";year:"+datToPlot[j]['date']+";value:"+str(datToPlot[j]['value'])+"\n")
            self.ax.plot(nx,ny,'o-', linestyle='solid', linewidth=2, markersize=10, label=ccodes[i]['value'])
            
        self.ax.legend(loc='best')
        self.canvas.draw()
        self.lblSourceVal.setText(urlstr)
        
    
            
    def showIndicators(self):
        self.cmbIndicator.clear()
        self.cmbIndicator.addItem("-")
        if (self.cmbType.currentText()=="-"):
            QtWidgets.QMessageBox.critical(self,"WBFetch","Choose type first!",QtWidgets.QMessageBox.Ok)
        else:
            # open json file for displaying "type of indicator"
            with open("conf/typeind.json") as jsonfile:
                dat = json.load(jsonfile)
                for i in range(len(dat)):
                    if dat[i]['type']==self.cmbType.currentText():
                        for j in range(len( dat[i]['indlist'] )):
                            self.cmbIndicator.addItem( dat[i]['indlist'][j]['c'] +"-"+ dat[i]['indlist'][j]['d'] )
    
    def __init__(self):
        super().__init__()
        self.initUI()
        
    def initUI(self):               
        
        if self.connectionTest("https://data.worldbank.org")==False:
            QtWidgets.QMessageBox.critical(self,"WBFetch","Error. Internet connection not available!",QtWidgets.QMessageBox.Ok)
            raise SystemExit
        
        self.setWindowTitle('WBFetch - World Bank Data') 
        self.winLayOut = QtWidgets.QGridLayout(self)

        # set font size
        qFont = QtGui.QFont()
        qFont.setPointSize(qFont.pointSize()+1)

        # create components
        self.lblCountry = QtWidgets.QLabel("Country List :")
        self.tblCountry = QtWidgets.QTableWidget()
        self.tblCountry.setStyleSheet('background-color:#fff')
        self.tblCountry.setColumnCount(3)
        self.tblCountry.setHorizontalHeaderLabels(["","Code","Country Name"])
        self.tblCountry.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        header = self.tblCountry.horizontalHeader()
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)
        self.lblType = QtWidgets.QLabel("Data Type :")
        self.lblType.setAlignment(QtCore.Qt.AlignRight)
        self.cmbType = QtWidgets.QComboBox()
        self.cmbType.setFont(qFont)
        self.lblIndicator = QtWidgets.QLabel("Indicator :")
        self.lblIndicator.setAlignment(QtCore.Qt.AlignRight)
        self.cmbIndicator = QtWidgets.QComboBox()
        self.cmbIndicator.setFont(qFont)
        self.lblFrom = QtWidgets.QLabel("From :")
        self.lblFrom.setAlignment(QtCore.Qt.AlignRight)
        self.lblTo = QtWidgets.QLabel("To :")
        self.lblTo.setAlignment(QtCore.Qt.AlignRight)
        self.dateFrom = QtWidgets.QDateEdit()
        self.dateFrom.setDisplayFormat("yyyy")
        self.dateFrom.setFont(qFont)
        self.btnFetch = QtWidgets.QPushButton("Fetch Data")
        self.btnFetch.setSizePolicy(QtWidgets.QSizePolicy.Ignored, QtWidgets.QSizePolicy.Expanding)
        self.dateTo = QtWidgets.QDateEdit()
        self.dateTo.setDate(QtCore.QDate.currentDate())
        self.dateTo.setDisplayFormat("yyyy")
        self.dateTo.setFont(qFont)
        self.fig = plt.figure(dpi=100)
        self.canvas = FigureCanvas(self.fig)
        self.toolbar = NavigationToolbar(self.canvas,self)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_xlabel("Year")
        self.ax.set_ylabel("Value")
        self.lblSourceUrl = QtWidgets.QLabel("Source :")
        self.lblSourceUrl.setAlignment(QtCore.Qt.AlignRight)
        self.lblSourceVal = QtWidgets.QLabel("-")
        self.lblSourceVal.setFont(qFont)
        self.lblSourceVal.setStyleSheet("background-color:rgb(50,50,50);color:rgb(200,200,0)")
        self.btnBrowser = QtWidgets.QPushButton("Open in browser")
        
        # event of btnFetch
        self.btnFetch.clicked.connect(self.showRowVal)
        # event of btnBrowser
        self.btnBrowser.clicked.connect(self.openBrowser)
        
        # add widgets
        self.winLayOut.addWidget(self.lblCountry,0,0)
        self.winLayOut.addWidget(self.lblFrom,0,4)
        self.winLayOut.addWidget(self.dateFrom,0,5)
        self.winLayOut.addWidget(self.lblTo,0,6)
        self.winLayOut.addWidget(self.dateTo,0,7)
        self.winLayOut.addWidget(self.btnFetch,0,8,3,1)
        self.winLayOut.addWidget(self.lblType,1,4)
        self.winLayOut.addWidget(self.cmbType,1,5,1,2)
        self.winLayOut.addWidget(self.lblIndicator,2,4)
        self.winLayOut.addWidget(self.cmbIndicator,2,5,1,3)
        self.winLayOut.addWidget(self.tblCountry,1,0,13,2)
        self.winLayOut.addWidget(self.toolbar,3,4,1,4)
        self.winLayOut.addWidget(self.canvas,4,4,8,5)
        self.winLayOut.addWidget(self.lblSourceUrl,12,4)
        self.winLayOut.addWidget(self.lblSourceVal,12,5,1,3)
        self.winLayOut.addWidget(self.btnBrowser,12,8)
        
        # read all countries's code
        inputfile = csv.reader(open('conf/countries3.csv','r'))
        countriesData = []
        for row in inputfile:
            # insert every data to table
            countriesData.append((row[0],row[1]))

        self.tblCountry.setRowCount(len(countriesData))
        # show code and name of every country in table
        r=0
        for i in countriesData:
            chkBox = QtWidgets.QTableWidgetItem()
            chkBox.setCheckState(QtCore.Qt.Unchecked)
            self.tblCountry.setItem(r,0, chkBox)
            self.tblCountry.setItem(r,1, QtWidgets.QTableWidgetItem(i[0]))
            self.tblCountry.setItem(r,2, QtWidgets.QTableWidgetItem(i[1]))
            r+=1
        
        self.cmbType.addItem("-")
        # open json file for displaying "type of indicator"
        with open("conf/typeind.json") as jsonfile:
            dat = json.load(jsonfile)
            for i in range(len(dat)):
                self.cmbType.addItem(dat[i]['type'])
            
        # event of cmbType
        self.cmbType.currentIndexChanged.connect(self.showIndicators)
        
        self.showMaximized()
        

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    winMain = winMain()
    sys.exit(app.exec_())
