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

class waitDialog(QDialog):
    def __init__(self,parent=None):
        super(waitDialog, self).__init__(parent)
        self.resize(300,100)
        self.setWindowTitle("视频导出完成后，此窗口自动关闭，请勿操作!")

class CaptureDetectionThread(QThread): #摄像头检测的线程
    #定义信号 传递摄像头检测后保存的文件名
    capture_image = pyqtSignal(str)
    #定义图片的序号
    imageCount = 0
    
    def __init__(self,net,meta):# 通过构造函数拿到 待检测视频 网络 参数
        super(CaptureDetectionThread, self).__init__()
        self.net = net
        self.meta = meta

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
                cv2.putText(frame, str(label)[2:-1]+str(round(score,3)), (int(xmin), int(ymin)), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.8,
                            color=(0, 255, 255), thickness=2)
            frame = cv2.resize(frame, (1024, 900), interpolation=cv2.INTER_CUBIC)
            cv2.imwrite("./temps/temp" + str(self.imageCount) + ".jpg", frame)#检测后的图片保存
            self.capture_image.emit("./temps/temp" + str(self.imageCount) + ".jpg")#发送完成图片保存的信号
            time.sleep(0.05)
            self.imageCount+=1
            if cv2.waitKey(1) & 0xFF == ord('q'):  # 按键盘q就停止拍照
                break

class TestThread:

    def __init__(self,net,meta):
        self.net=net
        self.meta=meta

    def run(self,video_path):
        self.imageCount = 0
        self.capture = cv2.VideoCapture(video_path)
        while True:
            ret, frame = self.capture.read()
            if not ret:
                print("视频解析")
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
                cv2.putText(frame, str(label)+str(round(score,3)), (int(xmin), int(ymin)), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.8,
                            color=(0, 255, 255), thickness=2)
            frame=cv2.resize(frame, (1024, 900), interpolation=cv2.INTER_CUBIC)
            cv2.imwrite("./temps/temp" + str(self.imageCount) + ".jpg", frame)
            self.imageCount+=1
            print(self.imageCount)
        print("finish")

class VideoDetectionThred(QThread):
    #定义信号 传递文件名
    video_image = pyqtSignal(str)
    detection_finish=pyqtSignal()
    #定义图片的序列
    imageCount = 0

    def __init__(self,video_path,net,meta):# 通过构造函数拿到 待检测视频 网络 参数
        super(VideoDetectionThred, self).__init__()
        self.video_path = video_path
        self.net = net
        self.meta = meta

    def run(self):
        self.imageCount = 0
        self.capture = cv2.VideoCapture(self.video_path)
        while True:
            ret, frame = self.capture.read()
            if not ret:
                print("视频解析")
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
                cv2.putText(frame, str(label)[2:-1]+str(round(score,3)), (int(xmin), int(ymin)), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.8,
                            color=(0, 255, 255), thickness=2)
            frame=cv2.resize(frame, (1024, 900), interpolation=cv2.INTER_CUBIC)
            cv2.imwrite("./temps/temp" + str(self.imageCount) + ".jpg", frame)
            self.video_image.emit("./temps/temp" + str(self.imageCount) + ".jpg")
            time.sleep(0.02)
            self.imageCount+=1
        self.detection_finish.emit()#发送检测完成的信号

class Ui_MainWindow(QMainWindow):
    global detection_image, detection_video

    def __init__(self,parent=None):
        super(Ui_MainWindow,self).__init__()
        self.setupUi()
        self.net = darknet.load_net(b"./cfg/yolov3-voc.cfg", b"./backup/yolov3-voc_final.weights", 0)
        self.meta = darknet.load_meta(b"./cfg/coco.data")

    def setupUi(self):

        self.setObjectName("MainWindow")
        self.resize(1200, 1000)
        self.centralwidget = QtWidgets.QWidget(self)#中心窗口
        self.centralwidget.setObjectName("centralwidget")

        self.GlobalLayout=QHBoxLayout() #全局布局器 水平布局
        self.ButtonGroup=QWidget() #按钮组

        self.widget = QtWidgets.QWidget(self.centralwidget)
        self.widget.setGeometry(QtCore.QRect(620, 60, 49, 100))
        self.widget.setObjectName("widget")

        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")

        self.btn_captureDetection = QtWidgets.QPushButton()
        self.btn_captureDetection.setObjectName("btn_captureDetection")
        self.btn_captureDetection.clicked.connect(self.captureDetection)
        self.verticalLayout.addWidget(self.btn_captureDetection)

        self.btn_imageDetection = QtWidgets.QPushButton()
        self.btn_imageDetection.setObjectName("btn_imageDetection")
        self.btn_imageDetection.clicked.connect(self.imageDetection)
        self.verticalLayout.addWidget(self.btn_imageDetection)

        self.btn_videoDetection = QtWidgets.QPushButton()
        self.btn_videoDetection.setObjectName("btn_videoDetection")
        self.btn_videoDetection.clicked.connect(self.videoDetection)
        self.verticalLayout.addWidget(self.btn_videoDetection)

        self.btn_Exportvideo = QtWidgets.QPushButton()
        self.btn_Exportvideo.setObjectName("btn_Exportvideo")
        self.btn_Exportvideo.clicked.connect(self.Exportvideo)
        self.verticalLayout.addWidget(self.btn_Exportvideo)

        self.imgLabel = QLabel(self.widget)
        self.imgLabel.setFixedSize(1024,900)
        self.imgLabel.setStyleSheet("border:2px solid red")

        self.ButtonGroup.setLayout(self.verticalLayout)#给按钮组设置全局布局器
        self.GlobalLayout.addWidget(self.imgLabel)
        self.GlobalLayout.addWidget(self.ButtonGroup)

        self.centralwidget.setLayout(self.GlobalLayout)
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

    def showImage(self,fname):#显示图片
        pix = QPixmap(fname)
        self.imgLabel.setPixmap(pix)

    def captureDetection(self): #打开摄像头检测 抽象为逐帧照片 导出的时候写为视频流
        answer = QMessageBox.warning(self, "注意", "如果您上次使用了摄像头检测或视频检测后没有导出，当前操作会导致数据丢失，请确认是否要继续！",
                                     QMessageBox.No | QMessageBox.Yes, QMessageBox.Yes)
        if answer == QMessageBox.No: #选择了否 则不进行下一步
            return
        if os.path.exists("./temps"): # 如果临时文件夹存在 则删除后重建
            shutil.rmtree("./temps")
        os.mkdir("./temps")

        #开启摄像头检测的线程
        self.captureThread = CaptureDetectionThread(self.net,self.meta)
        self.captureThread.capture_image.connect(self.showImage)
        self.captureThread.start()

    def imageDetection(self):
        answer = QMessageBox.warning(self, "注意", "如果您上次使用了摄像头检测或视频检测后没有导出，当前操作会导致数据丢失，请确认是否要继续！",
                                     QMessageBox.No | QMessageBox.Yes, QMessageBox.Yes)
        if answer == QMessageBox.No:
            return
        if os.path.exists("./temps"):
            shutil.rmtree("./temps")
        os.mkdir("./temps")

        detection_image, _ = QFileDialog.getOpenFileName(self, '请选择图片文件', ".", "(*.jpg)")
        fnameSplit = detection_image.split('.')
        index = len(fnameSplit) - 1
        typeSuffix = fnameSplit[index]  # 文件名后缀
        
        if typeSuffix != "jpg":
            QMessageBox.critical(self, "文件类型错误", "您未指定图片或指定的文件不是jpg文件，请确认！", QMessageBox.Yes, QMessageBox.Yes)
        else:  # 正确的图片路径
            frame = cv2.imread(detection_image)
            im = darknet.nparray_to_image(frame)
            boxes = darknet.detect(self.net, self.meta, im)
            for i in range(len(boxes)):
                score = boxes[i][1]
                label = boxes[i][0]
                xmin = max(5,boxes[i][2][0] - boxes[i][2][2] / 2)#可以根据坐标关系调整文字位置
                ymin = max(5,boxes[i][2][1] - boxes[i][2][3] / 2)
                xmax = boxes[i][2][0] + boxes[i][2][2] / 2
                ymax = boxes[i][2][1] + boxes[i][2][3] / 2
                cv2.rectangle(frame, (int(xmin), int(ymin)), (int(xmax), int(ymax)), (0, 255, 0), 2)
                cv2.putText(frame, str(label)[2:-1]+str(round(score,3)), (int(xmin), int(ymin)), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.8,
                            color=(255, 0, 0), thickness=2)
            frame=cv2.resize(frame, (1024, 900), interpolation=cv2.INTER_CUBIC)
            cv2.imwrite("./temps/temp" + ".jpg", frame)#检测后的图片保存
            self.showImage("./temps/temp" + ".jpg")

    def videoDetection(self):
        answer = QMessageBox.warning(self, "注意", "如果您上次使用了摄像头检测或视频检测后没有导出，当前操作会导致数据丢失，请确认是否要继续！", QMessageBox.No | QMessageBox.Yes , QMessageBox.Yes)
        if answer == QMessageBox.No:
            return
        if os.path.exists("./temps"):
            shutil.rmtree("./temps")
        os.mkdir("./temps")

        fname, _ = QFileDialog.getOpenFileName(self, '请选择mp4文件', ".", "(*.mp4)")
        fnameSplit = fname.split('.')
        index = len(fnameSplit)-1
        typeSuffix=fnameSplit[index] #文件名后缀
        if typeSuffix!="mp4":
            QMessageBox.critical(self,"文件类型错误","您未指定视频或指定的文件不是mp4文件，请确认！",QMessageBox.Yes,QMessageBox.Yes)
        else :#正确的路径
            #test=TestThread(self.net,self.meta)
            #test.run(fname)
            self.btn_videoDetection.setEnabled(False)
            self.videoThread = VideoDetectionThred(fname,self.net,self.meta)
            self.videoThread.video_image.connect(self.showImage)
            self.videoThread.finished.connect(self.videDeteciontFinish)
            self.videoThread.start()

    def videDeteciontFinish(self):
        self.btn_videoDetection.setEnabled(True)
        print("解析完成")

    def Exportvideo(self):#做一个等待状态的对话框 要求用户等待
            # 读取图片
            fnameList = os.listdir("./temps")
            fnameList.sort(key=lambda x: int(x[4:-4]))

            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            videoWriter = cv2.VideoWriter('./videos/video.avi', fourcc, 24, (1024, 900))

            dialog = waitDialog(self)
            dialog.show()
            dialog.setModal(True)

            for fname in fnameList:
                img = cv2.imread('./temps/' + fname)
                videoWriter.write(img)
            videoWriter.release()

            dialog.reject()
            # 删除temps目录并重建
            if os.path.exists("./temps"):
                shutil.rmtree("./temps")
            os.mkdir("./temps")

if __name__=='__main__':
    app=QApplication(sys.argv)
    main_ui=Ui_MainWindow()
    main_ui.show()
    sys.exit(app.exec_())
