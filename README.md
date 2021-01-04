# SmartHelmetWearingDetection
智能安全帽佩戴检测系统：使用系统前需要在本机环境下对darknet重新编译，以ubuntu为例。SystemUI.py为程序的入口。

0.在程序目录下使用make clean清除所有的编译信息。

1.打开Makefile文件，设置GPU = 1,CUDNN = 1，NVCC = /usr/local/你的cuda/bin/nvcc。OPENCV根据自身需要，如果需要在调用摄像头需要安装一下OPNECV，并设置OPENCV = 1。使用make命令进行编译。

2.调用python SystemUI.py即可打开本软件。
