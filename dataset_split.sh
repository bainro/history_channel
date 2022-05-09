#!/bin/bash

# shuffles and splits a file containing all images
#  into a test and train txt file

cd ~/git/darknet
cat history_all.txt | sort -R > /tmp/all_shuffled.txt

data_split=0.85
num_lines=$(cat /tmp/all_shuffled.txt | wc -l)
num_train=$(echo "$num_lines*$data_split" | bc)
# cheap trick to round, because bc doesn't support it
num_train=$(echo ${num_train%%.*})
num_test=$(echo "$num_lines-$num_train" | bc)

echo "test/training data split: $data_split"
echo "number of images total: $num_lines"
echo "number in training: $num_train"
echo "number in testing: $num_test"

head -n $num_train /tmp/all_shuffled.txt > history_train.txt
tail -n $num_test /tmp/all_shuffled.txt > history_test.txt

echo "training and test split for history YOLOv5 done!"
# will replace prefixes using VSCode to create identical
# dataset but for rgb channel images instead :)
