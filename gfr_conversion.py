'''Combines consecutive frames into one 3 channel image.'''
from tqdm import tqdm
import numpy as np
import subprocess
import cv2
import sys
import os
import re

DIS_TQDM = False
mse_threshold = 5500

cwd = os.getcwd()
train_dir = os.path.join(cwd, "data/gfr")
train_subsets = os.listdir(train_dir)
gray_dir = os.path.join(cwd, "data/gfr_gray")
history_dir = os.path.join(cwd, "data/gfr_history")

def bash_cmd(cmd_str):
    # print("[bash_cmd] " + cmd_str)
    process = subprocess.Popen(cmd_str.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    
# calulates the mean squared error between two images of same shape
def mse(img_1, img_2):
    err = np.sum((img_1.astype("float") - img_2.astype("float")) ** 2)
    err /= float(img_1.shape[0] * img_2.shape[1])
    return err    

# parallel lists for finding appropriate MSE threshold
# MSEs, paths = [], []
for subset in tqdm(train_subsets, disable=DIS_TQDM):
    img_dir = os.path.join(train_dir, subset)
    img_files = [os.path.join(img_dir, f) for f in os.listdir(img_dir)]
    bash_cmd("mkdir -p " + os.path.join(img_dir, "images"))
    bash_cmd("mkdir -p " + os.path.join(img_dir, "labels"))
    bash_cmd("mkdir -p " + os.path.join(history_dir, subset, "images"))
    bash_cmd("mkdir -p " + os.path.join(history_dir, subset, "labels"))
    bash_cmd("mkdir -p " + os.path.join(gray_dir, subset, "images"))
    bash_cmd("mkdir -p " + os.path.join(gray_dir, subset, "labels"))
    # sort by fileneame
    img_files = sorted(img_files)
    # specifically history img
    last_saved_img = None
    for img_file in tqdm(img_files, disable=DIS_TQDM):
        img_name, file_ext = os.path.splitext(img_file)
        # skip label files
        if file_ext == ".txt": continue
        frame_id = img_name.split("/")[-1]
        frame_id = frame_id[6:].lstrip("0")
        try:
            # offset since filenames start at 1, not 0
            frame_id = int(frame_id) - 1
        except:
            print("\n", img_name, "\n");exit()
        # the frame rate was 5 FPS
        frame_id = int(frame_id / 12)
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
            
            # ensure no two images are duplicates or too similar
            if type(last_saved_img) != type(None):
                difference = mse(history_frame, last_saved_img)
                # MSEs.append(difference)
                # paths.append(f"{subset}/{frame_id:05}")
                if difference > mse_threshold:
                    last_saved_img = history_frame
                else:
                    # skip this image because too similar to previous one
                    continue
            else:
                last_saved_img = history_frame
                
            # left pad with 0s to make sorting easier
            frame_id = f"{frame_id:05}"
            rgb_file = os.path.join(img_dir, "images", frame_id + ".png")
            bash_cmd("cp " + img_file + " " + rgb_file)
            # yolov5 repo I'm using requires parallel images/ & labels/ dir
            history_file = os.path.join(history_dir, subset, "images", frame_id + ".png")
            cv2.imwrite(history_file, history_frame)
            gray_file = os.path.join(gray_dir, subset, "images", frame_id + ".png")
            cv2.imwrite(gray_file, gray_frame)

            # replacing all common image formats just to be sure
            rgb_label_file = img_file.replace(".png", ".txt")
            rgb_label_file = rgb_label_file.replace(".jpg", ".txt")
            rgb_label_file = rgb_label_file.replace(".jpeg", ".txt")
            # yolov5 repo I'm using requires parallel images/ & labels/ dir
            rgb_label_file = rgb_label_file.replace("images", "labels")
            gray_label_file = gray_file.replace(".png", ".txt")
            gray_label_file = gray_label_file.replace(".jpg", ".txt")
            gray_label_file = gray_label_file.replace(".jpeg", ".txt")
            gray_label_file = gray_file.replace("images", "labels")
            history_label_file = history_file.replace(".png", ".txt")
            history_label_file = history_label_file.replace(".jpg", ".txt")
            history_label_file = history_label_file.replace(".jpeg", ".txt")
            history_label_file = history_label_file.replace("images", "labels")

            new_location = os.path.join(img_dir, "labels", frame_id + ".txt")
            bash_cmd("cp " + rgb_label_file + " " + new_location)
            bash_cmd("cp " + rgb_label_file + " " + gray_label_file)
            bash_cmd("cp " + rgb_label_file + " " + history_label_file)

"""
# sort based on MSE values but keep parallel
MSEs, paths = zip(*sorted(zip(MSEs, paths)))
MSEs = MSEs[:500]
paths = paths[:500]
print(MSEs)
print(paths)
"""
