# script to convert video into individual frames
import subprocess
import sys
import os

def main(args):
    assert len(args) == 2, "specify output directory & input video"
    output_dir = args[0]
    os.makedirs(output_dir, exist_ok=True)

    input_v = args[1]
    bash_cmd = f"ffmpeg -r 3 -pattern_type glob -i '{output_dir}/*.png'"
    bash_cmd += f" -vcodec libx264 -crf 10 -pix_fmt yuv420p {input_v}"
    bash_cmd = bash_cmd.split()
    process = subprocess.Popen(bash_cmd, stdout=subprocess.PIPE)
    output, error = process.communicate()
    print("output: ", output)
    print("error: ", error)

if __name__ == "__main__":
   main(sys.argv[1:])
