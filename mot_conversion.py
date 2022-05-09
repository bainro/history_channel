'''Combines consecutive frames into one 3 channel image.'''
from tqdm import tqdm
import subprocess
import cv2
import sys
import os
import re

DIS_TQDM = False

# assumes MOT dataset is already present in $PWD
cwd = os.getcwd()
mot_dir = os.path.join(cwd, "data/mot")
gray_dir = os.path.join(cwd, "data/gray")
history_dir = os.path.join(cwd, "data/history")
rgb_dir = os.path.join(cwd, "data/rgb")

def bash_cmd(cmd_str):
    # print("[bash_cmd] " + cmd_str)
    process = subprocess.Popen(cmd_str.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()

train_dir = os.path.join(mot_dir, "MOT15/train")
train_subsets = os.listdir(train_dir)
assert len(train_subsets) == 11, "Can't find MOT15/train/ in $CWD"
for subset in tqdm(train_subsets, disable=DIS_TQDM):
    bash_cmd("mkdir -p " + os.path.join(history_dir, subset, "labels"))
    bash_cmd("mkdir -p " + os.path.join(gray_dir, subset, "labels"))
    bash_cmd("mkdir -p " + os.path.join(rgb_dir, subset, "labels"))
    subset_abs_path = os.path.join(train_dir, subset)
    gt_file = os.path.join(subset_abs_path, "gt/gt.txt")
    with open(gt_file) as gt_labels:
        gt_lines = gt_labels.readlines()
        frame_id = 0 
        img_dir = os.path.join(subset_abs_path, "img1")
        img_files = [os.path.join(img_dir, f) for f in os.listdir(img_dir)]
        # sort by fileneame
        img_files = sorted(img_files)
        for img_file in tqdm(img_files, disable=DIS_TQDM):
            img_name, img_ext = os.path.splitext(img_file)
            frame_id = img_name.split("/")[-1].lstrip("0")  
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

                rgb_file = os.path.join(rgb_dir, subset, "images", str(frame_id) + ".png")
                cv2.imwrite(rgb_file, new_frame.copy())
                history_file = os.path.join(history_dir, subset, "images", str(frame_id) + ".png")
                cv2.imwrite(history_file, history_frame)
                gray_file = os.path.join(gray_dir, subset, "images", str(frame_id) + ".png")
                cv2.imwrite(gray_file, gray_frame)

                gray_label_file = gray_file.replace(".png", ".txt")
                gray_label_file = gray_label_file.replace(".jpg", ".txt")
                gray_label_file = gray_label_file.replace(".jpeg", ".txt")
                gray_label_file = gray_label_file.replace("images", "labels")
                history_label_file = history_file.replace(".png", ".txt")
                history_label_file = history_label_file.replace(".jpg", ".txt")
                history_label_file = history_label_file.replace(".jpeg", ".txt")
                history_label_file = history_label_file.replace("images", "labels")
                rgb_label_file = rgb_file.replace(".png", ".txt")
                rgb_label_file = rgb_label_file.replace(".jpg", ".txt")
                rgb_label_file = rgb_label_file.replace(".jpeg", ".txt")
                rgb_label_file = rgb_label_file.replace("images", "labels")
                labels = []

                label = gt_lines.pop(0)
                label_values = label.split(",")
                label_frame_id = int(label_values[0])
                while (label_frame_id <= frame_id):
                    if label_frame_id == frame_id:
                        h, w, c = new_frame.shape
                        bbox_w = float(label_values[4]) / w
                        bbox_h = float(label_values[5]) / h
                        bbox_x = str(float(label_values[2]) / w + bbox_w / 2)
                        bbox_y = str(float(label_values[3]) / h + bbox_h / 2)
                        bbox_w = str(bbox_w)
                        bbox_h = str(bbox_h)
                        # labels.append("0 " + bbox_x + " " + bbox_y + " " + bbox_w + " " + bbox_h)
                    elif label_frame_id > frame_id:
                        # need to let the frame_id catch up; put back label
                        gt_lines = [label, gt_lines]
                        break
                    if not len(gt_lines) > 0: break
                    label = gt_lines.pop(0)
                    label_values = label.split(",")
                    label_frame_id = int(label_values[0])  

                with open(gray_label_file, 'w') as gf:
                    for l in labels:
                        gf.write("%s\n" % l)

                bash_cmd("cp " + gray_label_file + " " + history_label_file)
                bash_cmd("cp " + gray_label_file + " " + rgb_label_file)
