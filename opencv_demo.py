# coding: utf-8
import os
import cv2
import time

def cap_image(folder_t=time.localtime(), note='na'):
    folder_t_str = time.strftime("%Y_%m_%d", folder_t)

    file_t = time.localtime()
    file_t_str = time.strftime("%Y_%m_%d_%H_%M_%S", file_t)
    target_folder = f'{folder_t_str}'
    fname = f'{file_t_str}_{note}_{os.path.basename(__file__).split(".")[0]}.jpg'
    file = f'{target_folder}\\{fname}'

    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    # get a frame
    ret, frame = cap.read()

    if not os.path.isdir(target_folder):
        os.makedirs(target_folder)

    # cv2.imwrite(fname, frame) 使用该方法 中文路径会乱码 使用以下替代
    cv2.imencode('.jpg', frame)[1].tofile(file)
    cap.release()

t = time.localtime()
cap_image(folder_t=t, note='我是检查备注点1')
cap_image(folder_t=t, note='我是检查备注点2')
cap_image(folder_t=t, note='我是检查备注点3')
cap_image(note='我是检查备注点4')
cap_image(note='我是检查备注点5')
cap_image(note='我是检查备注点6')
