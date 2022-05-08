# script to convert video into individual frames
import subprocess as sp
import sys
import os

cmd='ffmpeg -i inputVideo outputFrames_%04d.sgi'
sp.call(cmd,shell=True)

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

if __name__ == "__main__":
   main(sys.argv[1:])
