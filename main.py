import sys
from PyQt5 import QtGui
from PyQt5 import QtWidgets
from PyQt5 import QtCore
from facebook_scraper import get_posts
import requests
from bs4 import BeautifulSoup
import re
import mainUI
import time
from datetime import datetime,date
import csv




class ThreadClass(QtCore.QThread):
    mode =0
    limit=0
    posts=0
    days=0
    stop = False
    id=""
    myData = QtCore.pyqtSignal(list)
    stopJob = QtCore.pyqtSignal(str)
    stopSignal = QtCore.pyqtSignal(bool)
    def __init__(self,id,mode,limit,posts,days,parent = None):
        self.id=id
        self.mode = mode
        self.limit = limit
        self.posts=posts
        self.days=days
        super(ThreadClass,self).__init__(parent)

    def toggleStop(self,shouldI):
        self.stop=shouldI
        

    def run(self):
        self.stopSignal.connect(self.toggleStop)
        headers = {'User-Agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36"}
        try:
            count =0
            for post in get_posts(str(self.id), timeout=99999,pages=9999):
                try:
                    f_date =post['time']
                    l_date = datetime.now()
                    delta = l_date - f_date
                    count=count+1
                    if(self.limit==1):
                        if(count>self.posts):
                            self.stopJob.emit(str(count-1)+ " Post has been scrapped succesfully !")
                            break;
                    if(self.limit==2):
                        if(int(delta.days)>int(self.days)):
                            self.stopJob.emit(" Post from last " +str(self.days)+ " days been scrapped succesfully !")
                            break;

                        
                    print("Data :",str(post))
                    postData = ["-","-","-","-","-","-","-"]
                    #  ['Post Link','Date Published','Post Data','Likes','Comments','Shares','Type']
                    if(self.stop==True):
                        break; 
                    shares =0
                    print("Image :::",str(post['image']))
                    if(len(str(post['image']))<10):
                        cType = "Text"
                    else:
                        cType = "Image"
                    if(len(str(post['post_url']))<10):
                        post['post_url']="https://m.facebook.com/"+str(post['post_id'])

                    if(self.mode==1):
                       
                        try:
                            response = requests.request("GET", post['post_url'], headers=headers)
                            soup = BeautifulSoup(response.content, 'html.parser')
                            searchShare= re.compile(r'(share_count:)(\d+)')
                            searchVideo =re.compile(r'video_inline')
                            data = searchShare.search(str(soup.contents))
                            shares = data.group(2)
                            if(cType!='Image'):
                                splitedData = str(soup.contents).split("add_comment_switcher_placeholder")
                                isVideo = searchVideo.search(splitedData[0])
                                if(isVideo!=None):
                                    cType = "Video"
                        except:
                            print("error occured")
                        
                    
                    try:
                        print("COunt :",count)

                        # print(post['post_url'])  
                        # print(post['post_id']) 
                        # print(post['text'])
                        # print(post['likes'])
                        # print(post['time'])
                        # print(post['comments'])

                        postData[0]="https://"+str(post['post_url'])[10:]
                        postData[1]=str(post['time'])
                        postData[2]=str(post['text'])
                        postData[3]=str(post['likes'])
                        postData[4]=str(post['comments'])
                        postData[5]=str(shares)
                        postData[6]=str(cType)
                    except:
                        print("error")
                    self.myData.emit(postData)
                    
                except:
                    print("Error")
        except:
            print("Error JJ")


        
       

class MainUiClass(QtWidgets.QMainWindow,mainUI.Ui_MainWindow):

    def window(self):
        
        app = QtWidgets.QApplication(sys.argv)
        QtWidgets.QWidget
        win = QtWidgets.QWidget()
        button1 =  QtWidgets.QPushButton(win)
        button1.setText("Show dialog!")
        button1.move(50,50)
        button1.clicked.connect(showDialog)
        win.setWindowTitle("Click button")
        win.show()
        sys.exit(app.exec_())
	
    def showDialog(self,msg):
        
        msgBox =QtWidgets.QMessageBox()
        msgBox.setIcon(QtWidgets.QMessageBox.Information)
        msgBox.setText(msg)
        msgBox.setWindowTitle("Facebook Scrapper")
        msgBox.setStandardButtons(QtWidgets.QMessageBox.Ok | QtWidgets.QMessageBox.Cancel)
        # msgBox.buttonClicked.connect(msgButtonClick)

        returnValue = msgBox.exec()
        if returnValue == QtWidgets.QMessageBox.Ok:
            print('OK clicked')

    def getTableList(self):
        model = self.tableWidget.model()
        data = []
        for row in range(model.rowCount()):
            data.append([])
            for column in range(model.columnCount()):
                index = model.index(row, column)
                data[row].append(str(model.data(index)))
        return data



    def updateSortedTable(self,tableData):

        for rows in range(self.tableWidget.rowCount()):
            colm=0
            postData = tableData[rows]
            for values in postData:
                self.tableWidget.setItem(rows,colm,QtWidgets.QTableWidgetItem(values))
                colm =colm+1

        

        

       
        


    def writeCsv(self):
       
        path, _ = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File',  QtCore.QDir.homePath() + "/export.csv", "CSV Files(*.csv *.txt)")
        if path:
            with open(path, 'w') as stream:
                self.textEdit.setText(self.textEdit.toPlainText()+"\n"+"Creating CSV file..")
                headerData = ['Post Link','Date Published','Post','Likes','Comments','Shares','Type']
                writer = csv.writer(stream, delimiter=',')
                writer.writerow(headerData)
                for row in range(self.tableWidget.rowCount()):
                    rowdata = []
                    for column in range(self.tableWidget.columnCount()):
                        item = self.tableWidget.item(row, column)
                        if item is not None:
                            rowdata.append(item.text())
                        else:
                            rowdata.append('')
                    writer.writerow(rowdata)
            self.textEdit.setText(self.textEdit.toPlainText()+"\n"+"Success !")
            self.showDialog("CSV files has been succesfully creadted.")
            self.textEdit.moveCursor(QtGui.QTextCursor.End)
       
  
        
    def jobComplete(self,stopMsg):
        self.pushButton.setText("Start")
        self.textEdit.setText(self.textEdit.toPlainText()+"\n"+stopMsg)
        self.textEdit.moveCursor(QtGui.QTextCursor.End)

    

    def toggleStop(self,stop):
        if(stop==True):
            self.pushButton.setText("Start")

    def loadData(self):
        
        if(self.pushButton.text()=="Start"):
            mode =0
            limit=0
            posts=0
            days=0
            
            if(self.checkBox.isChecked()):
                mode =1
            if(self.radioButton.isChecked()==True):
                limit =0
            if(self.radioButton_2.isChecked()==True):
                limit=1
                posts=int(self.spinBox_2.value())
                print(str(posts))
            if(self.radioButton_3.isChecked()==True):
                limit=2
                days=int(self.spinBox.value())
                print(str(days))
            
            id=self.plainTextEdit.toPlainText()
            self.threadClass = ThreadClass(id,mode,limit,posts,days)
            self.pushButton.setText("Stop")
            self.threadClass.stopSignal.emit(False)
            self.threadClass.start()
            self.threadClass.stopJob.connect(self.jobComplete)
            self.threadClass.myData.connect(self.updateTable)
        else:
            
             self.threadClass.stopSignal.emit(True)
             self.toggleStop(True)
             self.threadClass.stopSignal.connect(self.toggleStop)
            
    def sortData(self,colm,comp):
        tableData = self.getTableList()

        for rows in range(self.tableWidget.rowCount()):
            print("Row :",rows)
            
            for counter in range(self.tableWidget.rowCount()):
                
                print(colm)
                selectedrow = tableData[rows]
                comparerow=tableData[counter]
                
                if(comp==0):
            
                    print(str(selectedrow[colm]), "and",str(comparerow[colm]))
                    if((selectedrow[colm])<(comparerow[colm])):
                        print(str(selectedrow[colm]), "<",str(comparerow[colm]))
                        tableData[rows],tableData[counter]=tableData[counter],tableData[rows]
                        
                else:
                    
                    print(str(selectedrow[colm]), "and",str(comparerow[colm]))
                    if((selectedrow[colm])>(comparerow[colm])):
                        print(str(selectedrow[colm]), ">",str(comparerow[colm]))
                        tableData[rows],tableData[counter]=tableData[counter],tableData[rows]
    
        self.updateSortedTable(tableData)
                   


    def sortData00(self):
        self.sortData(1,0)
    def sortData30(self):
        self.sortData(3,0)
    def sortData40(self):
        self.sortData(4,0)
    def sortData50(self):
        self.sortData(5,0)
    def sortData31(self):
        self.sortData(3,1)
    def sortData41(self):
        self.sortData(4,1)
    def sortData51(self):
        self.sortData(5,1)
    def sortData01(self):
        self.sortData(1,1)
    
    

    def __init__(self,parent=None):
        super(MainUiClass,self).__init__(parent)
        self.setupUi(self)
        self.pushButton.clicked.connect(self.loadData)
        self.tableWidget.setRowCount(0)
        self.tableWidget.setColumnCount(7)
        self.actionSave.triggered.connect(self.writeCsv)
        self.actionAscending.triggered.connect(self.sortData00)
        self.actionDescendinf.triggered.connect(self.sortData01)

        self.actionDescending_2.triggered.connect(self.sortData31)
        self.actionAscending_3.triggered.connect(self.sortData30)

        self.actionAscending_2.triggered.connect(self.sortData50)
        self.actionDescending.triggered.connect(self.sortData51)


        self.actionAscending_4.triggered.connect(self.sortData40)
        self.actionDescending_3.triggered.connect(self.sortData41)
       
   
        

        

    
        header = self.tableWidget.horizontalHeader()
        header.setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)
        header.setSectionResizeMode(1, QtWidgets.QHeaderView.ResizeToContents)
        # header.setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
        headerData = ['Post Link','Date Published','Post','Likes','Comments','Shares','Type']
        count =0
        for data in headerData:
            self.tableWidget.setHorizontalHeaderItem(count,QtWidgets.QTableWidgetItem(data))
            count=count+1

    def updateTable(self,postData):
            try:
                
                print("Update table")
                print(postData)
                count =self.tableWidget.rowCount()+1
                self.tableWidget.insertRow(count)
                self.tableWidget.setRowCount(count)
                print("Count",count)
                self.textEdit.setText(self.textEdit.toPlainText()+"\n"+"Scrapped Post #"+str(count)+ " from "+str(postData[0]))
                self.textEdit.setText(self.textEdit.toPlainText()+"\n"+"Scrapping Post #"+str(count+1))
                self.textEdit.moveCursor(QtGui.QTextCursor.End)
                self.tableWidget.scrollToBottom()
                
                colm=0
                for values in postData:
                   
                    self.tableWidget.setItem(count-1,colm,QtWidgets.QTableWidgetItem(values))
                    colm =colm+1
            except Exception:
                print(str(Exception))
                
            
           



if __name__ =='__main__':
    a =QtWidgets.QApplication(sys.argv)
    app=MainUiClass()
    app.show()
    a.exec_()





   
        # self.tableWidget.setHorizontalHeaderItem()
        
