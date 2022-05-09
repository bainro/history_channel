'''Combines consecutive frames into one 3 channel image.'''
from tqdm import tqdm
import subprocess
import cv2
import sys
import os
import re

DIS_TQDM = False

cwd = os.getcwd()
train_dir = os.path.join(cwd, "data/gfr")
train_subsets = os.listdir(train_dir)
gray_dir = os.path.join(cwd, "data/gfr_gray")
history_dir = os.path.join(cwd, "data/gfr_history")

def bash_cmd(cmd_str):
    # print("[bash_cmd] " + cmd_str)
    process = subprocess.Popen(cmd_str.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()

for subset in tqdm(train_subsets, disable=DIS_TQDM):
    bash_cmd("mkdir -p " + os.path.join(history_dir, subset))
    bash_cmd("mkdir -p " + os.path.join(gray_dir, subset))
    frame_id = 0
    img_dir = os.path.join(train_dir, subset)
    img_files = [os.path.join(img_dir, f) for f in os.listdir(img_dir)]
    # sort by fileneame
    img_files = sorted(img_files)
    for img_file in tqdm(img_files, disable=DIS_TQDM):
        img_name, file_ext = os.path.splitext(img_file)
        # skip label files
        if file_ext == ".txt": continue
        frame_id = img_name.split("/")[-1]
        frame_id = frame_id[6:].lstrip("0")
        # offset since filenames start at 1, not 0
        frame_id = int(frame_id) - 1
        new_frame = cv2.imread(img_file)

        case = frame_id % 3
        if case == 0:
            # green channel from frames {t-2, t-1, t} stacked to make a 3ch image.
            history_frame = new_frame.copy()
            # don't save yet in case we run out of frames soon
        elif case == 1:
            history_frame[:,:,1] = new_frame[:,:,0]
        elif case == 2:
            history_frame[:,:,2] = new_frame[:,:,0]
            gray_frame = new_frame.copy()
            # 3 channel gray made by broadcasting the green channel
            gray_frame[:,:,0] = gray_frame[:,:,1]
            gray_frame[:,:,2] = gray_frame[:,:,1]
            # save both gray & history frames

            history_file = os.path.join(history_dir, subset, str(frame_id) + ".png")
            cv2.imwrite(history_file, history_frame)
            gray_file = os.path.join(gray_dir, subset, str(frame_id) + ".png")
            cv2.imwrite(gray_file, gray_frame)

            # replacing all common image formats just to be sure
            rgb_label_file = img_file.replace(".png", ".txt")
            rgb_label_file = img_file.replace(".jpg", ".txt")
            rgb_label_file = img_file.replace(".jepg", ".txt")
            gray_label_file = gray_file.replace(".png", ".txt")
            gray_label_file = gray_label_file.replace(".jpg", ".txt")
            gray_label_file = gray_label_file.replace(".jpeg", ".txt")
            history_label_file = history_file.replace(".png", ".txt")
            history_label_file = history_label_file.replace(".jpg", ".txt")
            history_label_file = history_label_file.replace(".jpeg", ".txt")

            bash_cmd("cp " + rgb_label_file + " " + gray_label_file)
            bash_cmd("cp " + rgb_label_file + " " + history_label_file)
