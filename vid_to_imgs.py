# script to convert video into individual frames
import subprocess
import sys
import os

def main(args):
    assert len(args) == 2, "specify output directory & input video"
    output_dir = args[0]
    os.makedirs(output_dir, exist_ok=True)

    input_v = args[1]
    # maintains aspect ratio
    res = "1920:-1"
    
    bash_cmg = f"ffmpeg -i {input_v} -vf scale='{res}'"
    bash_cmd += f"' {output_dir}/frame_%05d.jpg'"
    bash_cmd = bash_cmd.split()
    process = subprocess.Popen(bash_cmd, stdout=subprocess.PIPE)
    output, error = process.communicate()
    print("output: ", output)
    print("error: ", error)

if __name__ == "__main__":
   main(sys.argv[1:])
