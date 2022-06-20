#!/bin/bash
:<<DOC
Author: Pablo Viana
Version: 1.0
Created: 2022/01/30

Script used to split files calling an awk proccess.
Split files with 500MB on lines starting with character '>', wich means
the beggining of a protein description.


params $1 - Input file path
params $2 - Output file path
params $3 - Folder with files to be run as input
DOC
# create alias to echo command to log time at each call
echo() {
    command echo "$(date +"%Y-%m-%dT%H:%M:%S%z"): $@"
}
# exit when any command fails
set -e
# keep track of the last executed command
trap 'last_command=$current_command; current_command=$BASH_COMMAND' DEBUG
# echo an error message before exiting
trap 'echo "\"${last_command}\" command ended with exit code $?."' EXIT
# start datetime profile
start=$(date +%s.%N)

input_path=$1
output_path=$2
input_folder=$3

echo "Started resistoma code"

#echo "File system available space:"
echo $(df -h /)

echo "Task ID: $AZ_BATCH_TASK_ID"
echo "Node ID: $AZ_BATCH_NODE_ID"
echo "Input path: $input_folder"

echo "Go to input path location: cd $AZ_BATCH_NODE_MOUNTS_DIR/$input_path"
cd $AZ_BATCH_NODE_MOUNTS_DIR/$input_path

echo "Create the output folder structure: mkdir -p $AZ_BATCH_NODE_MOUNTS_DIR/$output_path$input_folder"
mkdir -p $AZ_BATCH_NODE_MOUNTS_DIR/$output_path$input_folder

echo "Execute split files routine on each .faa file inside $input_folder:"
echo ""

for input_file in $(ls $input_folder/*.faa); do
    init=$(date +%s.%N)
    input_size=$(stat -c %s "$input_file")
    input_size=$(bc <<< "scale=3; $input_size/1000000")
    echo "Splitting file: $input_file   Size: $input_size MB"
    awk -f $AZ_BATCH_TASK_WORKING_DIR/splitfiles.awk $input_file
    end=$(date +%s.%N)
    runtime=$(bc <<< "scale=3; ($end-$init)/1")
    echo "Split execution time: ${runtime} s"
    #echo "File system available space:"
    echo $(df -h /)
    echo ""
done

end=$(date +%s.%N)
runtime=$(bc <<< "scale=3; ($end-$start)/60")
echo "Total elapsed time: ${runtime} min"
echo "Finished resistoma code"
