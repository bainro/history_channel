# script to convert video into individual frames
import subprocess as sp
import sys
import os

def main(args):
    assert len(args) == 2, "specify output directory & input video"
    output_dir = args[0]
    os.makedirs(output_dir, exist_ok=True)

    input_v = args[1]
    # maintains aspect ratio
    res = "1920:-1"
    
    bash_cmd = f"ffmpeg -i \"{input_v}\" -vf scale=\"{res}\""
    bash_cmd += f" \"{output_dir}/frame_%05d.jpg\""
    print("bash command: ", bash_cmd)
    sp.call(bash_cmd, shell=True)
    
    # source is 60 frame per second
    imgs = os.listdir(output_dir)
    imgs = sorted(imgs)
    for i in range(len(imgs)):
        # only keep every 12th, so 5 FPS
        if i % 12:
            bye = os.path.join(output_dir, imgs[i])
            os.remove(bye)

if __name__ == "__main__":
   main(sys.argv[1:])
