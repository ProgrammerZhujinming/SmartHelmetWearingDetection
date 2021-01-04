# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'SystemUI.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import sys
import cv2
import time
import os
import darknet
import shutil

class CaptureThred(QThread):
    #定义信号 传递文件名
    add_image = pyqtSignal(str)
    #定义图片的序列
    imageCount = 0
    net = darknet.load_net(b"./cfg/yolov3-voc.cfg", b"./backup/yolov3-voc_final.weights", 0)
    meta = darknet.load_meta(b"./cfg/coco.data")

    def run(self):
        self.capture = cv2.VideoCapture(0)
        self.imageCount = 0
        while True:
            ret, frame = self.capture.read()
            if not ret:
                break
            im = darknet.nparray_to_image(frame)
            boxes = darknet.detect(self.net, self.meta, im)
            for i in range(len(boxes)):
                score = boxes[i][1]
                label = boxes[i][0]
                xmin = boxes[i][2][0] - boxes[i][2][2] / 2
                ymin = boxes[i][2][1] - boxes[i][2][3] / 2
                xmax = boxes[i][2][0] + boxes[i][2][2] / 2
                ymax = boxes[i][2][1] + boxes[i][2][3] / 2
                cv2.rectangle(frame, (int(xmin), int(ymin)), (int(xmax), int(ymax)), (0, 255, 0), 2)
                cv2.putText(frame, str(label), (int(xmin), int(ymin)), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.8,
                            color=(0, 255, 255), thickness=2)

            cv2.imwrite("./temps/temp" + str(self.imageCount) + ".jpg", frame)
            self.add_image.emit("./temps/temp" + str(self.imageCount) + ".jpg")
            time.sleep(0.05)
            self.imageCount+=1
            if cv2.waitKey(1) & 0xFF == ord('q'):  # 按键盘q就停止拍照
                break

class VideoThred(QThread):
    #定义信号 传递文件名
    add_image = pyqtSignal(str)
    #定义图片的序列
    imageCount = 0
    net = darknet.load_net(b"./cfg/yolov3-voc.cfg", b"./backup/yolov3-voc_final.weights", 0)
    meta = darknet.load_meta(b"./cfg/coco.data")

    def __init__(self,video_path,net,meta):# 通过构造函数拿到 待检测视频 网络 参数
        self.video_path = video_path
        self.net = net
        self.meta = meta

    def run(self):
        self.imageCount = 0
        self.capture = cv2.VideoCapture(self.video_path)
        while True:
            ret, frame = self.capture.read()
            if not ret:
                break
            im = darknet.nparray_to_image(frame)
            boxes = darknet.detect(self.net, self.meta, im)
            for i in range(len(boxes)):
                score = boxes[i][1]
                label = boxes[i][0]
                xmin = boxes[i][2][0] - boxes[i][2][2] / 2
                ymin = boxes[i][2][1] - boxes[i][2][3] / 2
                xmax = boxes[i][2][0] + boxes[i][2][2] / 2
                ymax = boxes[i][2][1] + boxes[i][2][3] / 2
                cv2.rectangle(frame, (int(xmin), int(ymin)), (int(xmax), int(ymax)), (0, 255, 0), 2)
                cv2.putText(frame, str(label), (int(xmin), int(ymin)), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.8,
                            color=(0, 255, 255), thickness=2)

            cv2.imwrite("./temps/temp" + str(self.imageCount) + ".jpg", frame)
            self.add_image.emit("./temps/temp" + str(self.imageCount) + ".jpg")
            time.sleep(0.05)
            self.imageCount+=1

class Ui_MainWindow(QMainWindow):
    global detection_image, detection_video

    def __init__(self,parent=None):
        super(Ui_MainWindow,self).__init__()
        self.setupUi()

    def setupUi(self):

        self.GlobalLayout=QHBoxLayout() #全局布局器
        self.ButtonGroup=QWidget() #按钮组

        self.setObjectName("MainWindow")
        self.resize(800, 600)
        self.centralwidget = QtWidgets.QWidget(self)
        self.centralwidget.setObjectName("centralwidget")

        self.widget = QtWidgets.QWidget(self.centralwidget)
        self.widget.setGeometry(QtCore.QRect(620, 60, 95, 401))
        self.widget.setObjectName("widget")

        self.verticalLayout = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")

        self.btn_captureDetection = QtWidgets.QPushButton(self.widget)
        self.btn_captureDetection.setObjectName("btn_captureDetection")
        self.btn_captureDetection.clicked.connect(self.captureDetection)
        self.verticalLayout.addWidget(self.btn_captureDetection)

        self.btn_imageDetection = QtWidgets.QPushButton(self.widget)
        self.btn_imageDetection.setObjectName("btn_imageDetection")
        self.btn_imageDetection.clicked.connect(self.imageDetection)
        self.verticalLayout.addWidget(self.btn_imageDetection)

        self.btn_videoDetection = QtWidgets.QPushButton(self.widget)
        self.btn_videoDetection.setObjectName("btn_videoDetection")
        self.btn_videoDetection.clicked.connect(self.videoDetection)
        self.verticalLayout.addWidget(self.btn_videoDetection)

        self.btn_Exportvideo = QtWidgets.QPushButton(self.widget)
        self.btn_Exportvideo.setObjectName("btn_Exportvideo")
        self.btn_Exportvideo.clicked.connect(self.Exportvideo)
        self.verticalLayout.addWidget(self.btn_Exportvideo)

        self.imgLabel = QLabel(self)
        self.imgLabel.move(0,0)
        self.imgLabel.setStyleSheet("border:2px solid red")

        #self.ButtonGroup.setLayout(self.verticalLayout)
        #self.GlobalLayout.addWidget(self.imgLabel)
        #self.GlobalLayout.addWidget(self.ButtonGroup)
        #self.setLayout(self.GlobalLayout)

        #self.verticalLayout.addWidget(self.imgLabel)
        self.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(self)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 31))
        self.menubar.setObjectName("menubar")
        self.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(self)
        self.statusbar.setObjectName("statusbar")
        self.setStatusBar(self.statusbar)

        self.retranslateUi()
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("MainWindow", "智能安全帽检测程序"))
        self.btn_captureDetection.setText(_translate("MainWindow", "摄像头检测"))
        self.btn_imageDetection.setText(_translate("MainWindow", "图片检测"))
        self.btn_videoDetection.setText(_translate("MainWindow", "视频检测"))
        self.btn_Exportvideo.setText(_translate("MainWindow","导出视频"))

    def showCaptureImage(self,fname):#显示摄像头读取到的照片
        pix = QPixmap(fname)
        self.imgLabel.setFixedSize(pix.width(), pix.width())
        self.imgLabel.setPixmap(pix)

    def captureDetection(self): #打开摄像头检测 抽象为逐帧照片 导出的时候写为视频流
        answer = QMessageBox.warning(self, "注意", "如果您上次使用了摄像头检测或视频检测后没有导出，当前操作会导致数据丢失，请确认是否要继续！",
                                     QMessageBox.No | QMessageBox.Yes, QMessageBox.Yes)
        if answer == QMessageBox.No:
            return
        if os._exists("./temps"):
            shutil.rmtree("./temps")
        os.mkdir("./temps")

        #开启摄像头检测的线程
        self.captureThread = CaptureThred()
        self.captureThread.add_image.connect(self.showCaptureImage)
        self.captureThread.start()

    def imageDetection(self):
        answer = QMessageBox.warning(self, "注意", "如果您上次使用了摄像头检测或视频检测后没有导出，当前操作会导致数据丢失，请确认是否要继续！",
                                     QMessageBox.No | QMessageBox.Yes, QMessageBox.Yes)
        if answer == QMessageBox.No:
            return
        if os.path.exists("./temps"):
            shutil.rmtree("./temps")
            print("???")
        os.mkdir("./temps")

        detection_image, _ = QFileDialog.getOpenFileName(self, '请选择图片文件', ".", "(*.jpg)")
        fnameSplit = detection_image.split('.')
        index = len(fnameSplit) - 1
        typeSuffix = fnameSplit[index]  # 文件名后缀
        if typeSuffix != "jpg":
            QMessageBox.critical(self, "文件类型错误", "您未指定图片或指定的文件不是jpg文件，请确认！", QMessageBox.Yes, QMessageBox.Yes)
        else:  # 正确的图片路径
            # 开启存储图片的线程
            self.imageThread = ImageThred()
            self.imageThread.detection_image_singal.connect(self.showImage)
            self.imageThread.start()

    def showImage(self,fname):
        pix = QPixmap(fname)
        self.imgLabel.setFixedSize(pix.width(), pix.width())
        self.imgLabel.setPixmap(pix)

    def videoDetection(self):
        answer = QMessageBox.warning(self, "注意", "如果您上次使用了摄像头检测或视频检测后没有导出，当前操作会导致数据丢失，请确认是否要继续！", QMessageBox.No | QMessageBox.Yes , QMessageBox.Yes)
        if answer == QMessageBox.No:
            return
        if os._exists("./temps"):
            shutil.rmtree("./temps")
        os.mkdir("./temps")

        fname, _ = QFileDialog.getOpenFileName(self, '请选择图片文件', ".", "(*.mp4)")
        fnameSplit = fname.split('.')
        index = len(fnameSplit)-1
        typeSuffix=fnameSplit[index] #文件名后缀
        if typeSuffix!="mp4" :
            QMessageBox.critical(self,"文件类型错误","您未指定视频或指定的文件不是mp4文件，请确认！",QMessageBox.Yes,QMessageBox.Yes)
        else :#正确的图片路径
            cap=cv2.VideoCapture(fname)
            while True:
                ret , frame = cap.read()
                if ret:
                    im = darknet.nparray_to_image(frame)
                    r = darknet.detect(self.net, self.meta, im)
                else:
                    break
            cap.release()
            cv2.destroyAllWindows()
            #pix=QPixmap(fname)
            #print(pix)
            #imgLabel=QLabel(self)
            #imgLabel.setStyleSheet("border:2px solid red")
            #imgLabel.setGeometry(0,0,100,200)
            #self.verticalLayout.addWidget(imgLabel)

    def Exportvideo(self):#做一个等待状态的对话框 要求用户等待
        #读取图片
        fnameList = os.listdir("./temps")
        fnameList.sort(key=lambda x:int(x[4:-4]))

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        videoWriter = cv2.VideoWriter('./videos/video1.mp4', fourcc, 24, (640, 480))

        for fname in fnameList:
            img=cv2.imread('./temps/'+fname)
            videoWriter.write(img)
            print(fname)
        videoWriter.release()

        # 删除temps目录并重建

if __name__=='__main__':
    app=QApplication(sys.argv)
    main_ui=Ui_MainWindow()
    main_ui.show()
    sys.exit(app.exec_())