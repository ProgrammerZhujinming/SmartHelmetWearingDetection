import darknet
import os
import cv2

if __name__=='__main__':
    net = darknet.load_net(b"./cfg/yolov3-voc.cfg", b"./backup/yolov3-voc_final.weights", 0)
    meta = darknet.load_meta(b"./cfg/coco.data")

    fpathList = os.listdir("./Result_image")

    for fpath in fpathList:
        frame = cv2.imread("./Result_image/"+fpath)
        im = darknet.nparray_to_image(frame)
        boxes = darknet.detect(net, meta, im)

        fname = fpath[0:-4]
        with open('/home/fan60526/桌面/SmartHatDetection-v5/Result_text/' + fname + '.txt','w+') as file:
            for i in range(len(boxes)):
                score = boxes[i][1]
                label = boxes[i][0]
                xmin = boxes[i][2][0] - boxes[i][2][2] / 2
                ymin = boxes[i][2][1] - boxes[i][2][3] / 2
                xmax = boxes[i][2][0] + boxes[i][2][2] / 2
                ymax = boxes[i][2][1] + boxes[i][2][3] / 2
                file.write(str(label)[2:-1]+" "+str(score)[0:5]+" "+str(int(xmin))+".00 "+str(int(ymin))+".00 "+str(int(xmax))+".00 "+str(int(ymax))+".00\n")











