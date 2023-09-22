#!/usr/bin/env python

"""MOB.py: automates joining process of google meetings."""

__author__      = "Jayson Ruzario"
__copyright__   = "GNU GENERAL PUBLIC LICENSE"


import sys
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtCore import * 
from PyQt5 import QtTest
from PyQt5 import QtCore
from PyQt5.QtGui import QMovie, QPainter, QPixmap
from backports import configparser
from PyQt5.QtGui import QIcon
##--custum scripts
from WebEnginePage import WebEnginePage
from js import jsloader
from configManager import ConfigManager
import time
from datetime import datetime
import queue
from PyQt5.QtGui import QPalette

#userconfigs


class backgroundView(QGraphicsView):
    def __init__ (self,movie):
        super(backgroundView,self).__init__()
        self.movie=movie
        self.display_pixmap=movie.currentPixmap()
        self.setStyleSheet('QGraphicsView {background-color: rgb(0,0,0);}')

    def paintEvent(self,event):
        self.display_pixmap = self.movie.currentPixmap().scaled(self.my_size)
        painter=QPainter()
        painter.begin(self.viewport())
        painter.fillRect(event.rect(),self.palette().color(QPalette.Window))
        x = (self.width() - self.display_pixmap.width())/2
        y = (self.height() - self.display_pixmap.height())/2
        painter.drawPixmap(x, y, self.display_pixmap)
        painter.end()

    def resizeEvent(self, event):
        self.my_size=event.size()


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self,parent=None):
        super(MainWindow, self).__init__(parent) # Call the inherited classes __init__ method
        uic.loadUi('basic.ui', self) # Load the .ui file
        
        # self.movie = QMovie('./giffs/oncall.gif')
        # view=backgroundView(self.movie)
        # mainLayout=QVBoxLayout()
        # self.setCentralWidget(view)
        # view.setLayout(mainLayout)
        # button=QPushButton('Button')
        # mainLayout.addWidget(button)
        # self.movie.frameChanged.connect(view.update)
        # self.movie.start()
        

        self.show() # Show the GUI
        print(self.size(),self.pos())
        self.move(QtCore.QPoint(906, 59))
        self.config = configparser.ConfigParser()
        self.configManager = ConfigManager()
        self.settings = QSettings('MeetoBot','App state')
        self.TODAY = self.dateToQdate(datetime.today().strftime('%Y-%m-%d'))
        self.TOTIME = self.timeTOQtime(datetime.today().strftime('%H:%M:%S'))
        print(datetime.today().strftime('%H:%M:%S'))

        try:
            ####
            #loads application previous state like size n position 
            ###
            self.updateconfig()
            self.resize(self.settings.value('window size'))
            self.move(self.settings.value('window position'))
        except :
            print("updating location failed")
            pass
        self.DateEdit = self.findChild(QDateEdit,"dateEdit")
        self.DateEdit.setDate(self.TODAY)
        self.timeEdit_Start.setTime(self.TOTIME)
        self.timeEdit_End.setTime(self.TOTIME)
        
        ## defining webview
        self.browser = self.findChild(QWebEngineView,"webEngineView") # webengineview
        self.page = WebEnginePage()
        self.browser.setPage(self.page)
        self.browser.setUrl(QUrl("https://projects.21n78e.net/mob/app/mob-app.html"))# default url
        # self.browser.loadFinished.connect(self.onLoadFinished)
        self.threadpool = QtCore.QThreadPool()	
        self.threadpool.setMaxThreadCount(1)
        self.worker = None #-|custom flags
        self.go_on = False #-|custom flags
        self.q = queue.Queue(maxsize=20)
        ## buttons 
        self.button_Apply = self.findChild(QPushButton,"pushButton_Apply") # Apply Button
        self.button_Apply.clicked.connect(self.onApply)
        self.button_reset = self.findChild(QPushButton,"pushButton_Reset") # Reset Button
        self.button_reset.clicked.connect(self.onReset)
        self.button_start = self.findChild(QPushButton,"pushButton_Start") # Start Button
        self.button_start.clicked.connect(self.start_worker)
        self.button_stop = self.findChild(QPushButton,"pushButton_Stop")  # Stop Button
        self.button_stop.clicked.connect(self.stop_worker)
        # self.button_test = self.findChild(QPushButton,"pushButton_TEST")  # test Button
        # self.button_test.clicked.connect(self.joinChat)
        self.timelabel = self.findChild(QtWidgets.QLabel,"timelabel") #welcome qLabel
        # self.timelabel.setStyleSheet("border: 1px solid black;") 
        # self.timelabel.setSizePolicy(QSizePolicy.Expanding, 
        #     QSizePolicy.Expanding)
        self.timelabel.setScaledContents(0)

        # self.timelabel.setMovie(self.gif)
        # self.timelabel.setMovie(self.gif)
        # self.gif.start()          
        #  #GIFF FUNCTIONALITY
        self.bg_label = self.findChild(QtWidgets.QLabel,"bg_image_label")
        self.logo_label = self.findChild(QtWidgets.QLabel,"logo_label")
        # # self.gif = QMovie('./statics/giffs/pika.gif')
        # self.gif = QMovie('./statics/giffs/timelabel.gif')
        # self.logo_label.setMovie(self.gif )
        # self.timelabel.setMovie(self.gif)
        # self.gif.start() 
        self.initUI()
        

    def initUI(self):
        # # creating a QGraphicsDropShadowEffect object
        # self.shadow = QGraphicsDropShadowEffect()

        # # setting blur radius (optional step)
        # self.shadow.setBlurRadius(2)
        # self.button_reset.setGraphicsEffect(self.shadow )
        shadow = QGraphicsDropShadowEffect(blurRadius=5, xOffset=3, yOffset=3)
        self.button_reset.setGraphicsEffect(shadow)
        shadow = QGraphicsDropShadowEffect(blurRadius=5, xOffset=3, yOffset=3)
        self.button_Apply.setGraphicsEffect(shadow)
        shadow = QGraphicsDropShadowEffect(blurRadius=5, xOffset=3, yOffset=3)
        self.button_start.setGraphicsEffect(shadow)
        shadow = QGraphicsDropShadowEffect(blurRadius=5, xOffset=3, yOffset=3)
        self.button_stop.setGraphicsEffect(shadow)
        shadow = QGraphicsDropShadowEffect(blurRadius=5, xOffset=3, yOffset=3)
        # self.timelabel.setGraphicsEffect(shadow)
        self.setWindowTitle('MOB')
        self.setWindowIcon(QIcon('./statics/app_icon.png')) 

    def callback_function(self,html):
        print('-->',html)
        if html != None:
            print('Debug: folks are less then threshold --> stoping')
            self.stop_worker()

    def stop_worker(self):
        self.go_on=True
        try:
            self.LeaveCall()
        except :
            pass
        # QtTest.QTest.qWait(10000)
        self.browser.setUrl(QUrl("https://projects.21n78e.net/mob/app/mob-app.html"))

    
    def start_worker(self):
        self.onApply()
        self.go_on=False
        y = self.meetingduration
        x = self.timetilmeet
        print(x,y)
        if x < 0 or y < 0 :
            self.timelabel.setText("Please check if date/time is set correctly.")
            QtTest.QTest.qWait(2000)
            self.stop_worker()

        print("starting countdown")#                                                                                 | starts countdown 
        for i in range(x,0,-1):
            if self.go_on:
                self.timelabel.setText('welcome to Meet-O-Bot')
                break
            QtTest.QTest.qWait(1000)
            print(i)
            self.timelabel.setText("Time Remaining: "+str(i))
            if i == 1:
                if self.go_on:
                    self.timelabel.setText('welcome to Meet-O-Bot')
                    
                print("starting meeting")
                self.timelabel.setText("starting meeting")
                self.browser.setUrl(QUrl(self.lineEdit_meetingLink.text()))
                # self.browser.loadFinished.connect(self.onLoadFinished) # meeting has been joined 
                self.onLoadFinished()
                for j in range(y,0,-1):#
                    if self.go_on:
                        self.timelabel.setText('welcome to Meet-O-Bot')
                        break
                    self.timelabel.setText('(meeting duration:%s)'%(j))
                    print(j,y/2,j%2)
                    QtTest.QTest.qWait(1000)
                    if (self.checkbox1.isChecked() and  (j < y/2)):
                        print("run js that checks if ppl are less then min threshold")
                        self.browser.page().runJavaScript(self.jsloader.minthresholdFunc,self.callback_function)
                    if j == 1:
                        print("meeting duration ended!")
                        self.timelabel.setText('welcome to Meet-O-Bot')
                        self.LeaveCall()
                        self.stop_worker()
                        



#------------------------------------------------------------------------------------------------
    # @QtCore.pyqtSlot(bool)
    # def onLoadFinished(self, ok):
    def onLoadFinished(self):
        # if not ok:
        #     return
        QtTest.QTest.qWait(10000)
        self.browser.page().runJavaScript("""console.log("page loading has finished");""")
        self.muteMic()
        QtTest.QTest.qWait(2000)
        self.muteCam()
        QtTest.QTest.qWait(10000)
        self.joinNow()
        QtTest.QTest.qWait(10000)
        self.toggleCaps()
        QtTest.QTest.qWait(2000)
        self.joinChat()
        QtTest.QTest.qWait(2000)
        if self.CheckBox_autoGreet.isChecked():
            self.greetings()
        QtTest.QTest.qWait(10000)
        if self.CheckBox_autoresponse.isChecked():
            self.autochat()
        QtTest.QTest.qWait(2000)
        self.autochatCaption()

    def redirectToUrl(self):
        self.browser.setUrl(QUrl(self.lineEdit_meetingLink.text()))
        
    def toggleCaps(self):
        self.timelabel.setText('toggling captions')
        self.browser.page().runJavaScript("""
        var turnOnCaps = document.getElementsByClassName("NPEfkd RveJvd snByac")[5].firstChild
        turnOnCaps.click()""")
    def autochatCaption(self):
        print("Debug: autochat from caps enabled")
        self.timelabel.setText('autochat from captions enabled')
        self.browser.page().runJavaScript(self.jsloader.autoChat_captions)
    def greetings(self):
        print("Debug: greeting ppl")
        self.timelabel.setText('greeting folks')
        self.browser.page().runJavaScript(self.jsloader.greet)
    def autochat(self):
        print("Debug: autochat enabled")
        self.timelabel.setText('autochat enabled')
        self.browser.page().runJavaScript(self.jsloader.autoChat)
    def joinChat(self):
        print("Debug: opening chat window")
        self.timelabel.setText('opening chat window')
        self.browser.page().runJavaScript(self.jsloader.joinChat)  
    def closeChat(self):
        print("Debug: closing chat window")
        self.timelabel.setText('closing chat window')
        self.browser.page().runJavaScript(self.jsloader.closeChat)        
    def muteCam(self):
        print("Debug: muting cam")
        self.timelabel.setText('muting cam')
        self.browser.page().runJavaScript(self.jsloader.muteCam)
    def muteMic(self):
        print("Debug: muting mic")
        self.timelabel.setText('muting mic')
        self.browser.page().runJavaScript(self.jsloader.muteMic)
    def joinNow(self):
        print("Debug: joining call ")
        self.timelabel.setText('joining call')
        self.browser.page().runJavaScript(self.jsloader.joinnow)
    def LeaveCall(self):
        print("Debug: Leaving call ")
        self.timelabel.setText('Leaving call')
        self.browser.page().runJavaScript(self.jsloader.leavenow)
        QtTest.QTest.qWait(2000)
        self.timelabel.setText('welcome  to Meet-O-Bot')
        self.browser.setUrl(QUrl("https://projects.21n78e.net/mob/app/mob-app.html"))

    def closeEvent(self,event):
        '''
        this method is executed when exiting app
        '''

        close = QMessageBox.question(self,
                                    "QUIT",
                                    "Are you sure want to stop process?",
                                    QMessageBox.Yes | QMessageBox.No)
        if close == QMessageBox.Yes:
            event.accept()
            self.go_on=True
        else:
            event.ignore()
        print(self.size(),self.pos())
        self.settings.setValue("window size", self.size())
        self.settings.setValue("window position", self.pos())

        
        
    def onApply(self):
        '''
        creates dictionary of values that user has provided and writes to config file using configmanager
        '''
        d = {'GoogleMeetLink': self.lineEdit_meetingLink.text(),'Date':self.DateEdit.date().toPyDate(),
            'startTime':self.timeEdit_Start.time().toString(),'endTime':self.timeEdit_End.time().toString(),
            'minThreshold_ischecked': str(self.checkbox1.isChecked()),'minThreshold_value':self.spinbox1.value(),
            "autoResponse_ischecked":  str(self.CheckBox_autoresponse.isChecked()),
            "Alias": self.lineEdit_Alias.text(),
            "Messages": self.lineEdit_Message.text(),
            "autoGreet_ischecked":  str(self.CheckBox_autoGreet.isChecked()),
            "Greetings": self.QPlainTextEdit_Greeting.toPlainText(),
        }
        self.configManager.setUserconfig(d)
        self.configManager.setDeltaTime()
        self.updateconfig()
        self.pushButton_Apply.setText('Apply')
    def onReset(self):
        '''
        overwrites user config reseting it to default
        '''
        self.configManager.resetConfig()
        try:
            self.updateconfig()

        except:
            pass
        self.DateEdit = self.findChild(QDateEdit,"dateEdit")
        self.DateEdit.setDate(self.TODAY)
        self.timeEdit_Start.setTime(self.TOTIME)
        self.timeEdit_End.setTime(self.TOTIME)
    def timeTOQtime(self,_time):
        '''
        takes time of type str eg.04:03:00 and return Qtime(04,03,00)
        '''
        d=_time.split(":")
        return QTime(int(d[0]),int(d[1]),int(d[2]))
    def dateToQdate(self,_date):
        '''
        takes date of type str eg 2020-12-31 and return Qdate(2020,12,31)
        ''' 
        d=_date.split("-")
        return QDate(int(d[0]),int(d[1]),int(d[2]))
    def updateconfig(self):
        #####
        #Loads userconfig from file if it is available 
        #####
        # self.jsloader.alias = self.config["UserConfig"]["alias"]
        # self.jsloader.greeting = self.config["UserConfig"]["greetings"]
        
        self.config.read('config.ini')
        #----defining interface
        self.lineEdit_meetingLink = self.findChild(QLineEdit,"lineEdit_meetingLink")
        self.DateEdit = self.findChild(QDateEdit,"dateEdit")
        self.timeEdit_Start = self.findChild(QTimeEdit,"timeEdit_Start")
        self.timeEdit_End = self.findChild(QTimeEdit,"timeEdit_End")
        self.checkbox1 = self.findChild(QCheckBox,"checkBox1")
        self.spinbox1 = self.findChild(QSpinBox,"spinBox1")
        self.CheckBox_autoresponse = self.findChild(QCheckBox,"check_autoresponse")
        self.lineEdit_Alias = self.findChild(QLineEdit,"lineEdit_Alias")
        self.lineEdit_Message = self.findChild(QLineEdit,"lineEdit_Message")
        self.CheckBox_autoGreet = self.findChild(QCheckBox,"check_autoGreet")
        self.QPlainTextEdit_Greeting = self.findChild(QPlainTextEdit,"lineEdit_greetings")

        print('configs : defining interface succesful')
        #----update interface
        self.lineEdit_meetingLink.setText(self.config["UserConfig"]["googlemeetlink"])
        self.DateEdit.setDate(self.dateToQdate(self.config["UserConfig"]['date']))
        self.DateEdit.setDate(self.dateToQdate(str(datetime.today().strftime('%Y-%d-%m'))))
        self.timeEdit_Start.setTime(self.timeTOQtime(self.config["UserConfig"]['starttime']))
        self.timeEdit_End.setTime(self.timeTOQtime(self.config["UserConfig"]['endtime']))
        self.jsloader = jsloader(self.config["UserConfig"]["alias"],self.config["UserConfig"]["greetings"],self.config['UserConfig']['minthreshold_value']) # updating variable for js
        if self.config['UserConfig']['minthreshold_ischecked'] == "True":
            self.checkbox1.setChecked(True)
            
        else:
            self.checkbox1.setChecked(False)
        self.spinbox1.setValue(int(self.config['UserConfig']['minthreshold_value']))
        #
        if self.config['UserConfig']['autoresponse_ischecked'] == "True":
            self.CheckBox_autoresponse.setChecked(True)
            
        else:
            self.CheckBox_autoresponse.setChecked(False)
        self.lineEdit_Alias.setText(self.config["UserConfig"]["alias"])
        self.lineEdit_Message.setText(self.config["UserConfig"]["messages"])

        if self.config['UserConfig']['autogreet_ischecked'] == "True":
            self.CheckBox_autoGreet.setChecked(True)
            
        else:
            self.CheckBox_autoGreet.setChecked(False)
        self.QPlainTextEdit_Greeting.setPlainText(self.config["UserConfig"]["greetings"])

        print('configs : updating interface succesful')
        #---update variables 
        self.meeting_link= self.config["UserConfig"]['googlemeetlink']
        #--update Delta timings
        self.meetingduration = int(self.config["timings"]["meetingduration"])
        self.timetilmeet = int(self.config["timings"]["timetilmeet"])
        # self.timeLabel.setText('welcome to LazyMeet')
        
        print('configs : updating variables succesful')
        #-----------------------------------------------
file = open("./mob.qss")

#-----------------------------------------------------------------------------------
app = QtWidgets.QApplication(sys.argv) # Create an instance of QtWidgets.QApplication
with file:
    qss=file.read()
    app.setStyleSheet(qss)


window = MainWindow() # Create an instance of our class
sys.exit(app.exec_()) # Start the application

