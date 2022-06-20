#!/bin/bash
:<<DOC
Author: Pablo Viana
Version: 1.0
Created: 2022/04/03

Script used to count orfs of prodigal output .faa file.

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
echo "Input path: $input_path"

echo "Go to input path location: cd $AZ_BATCH_NODE_MOUNTS_DIR/$input_path"
cd $AZ_BATCH_NODE_MOUNTS_DIR/$input_path

echo "Create the output folder structure: mkdir -p $AZ_BATCH_NODE_MOUNTS_DIR/$output_path"
mkdir -p $AZ_BATCH_NODE_MOUNTS_DIR/$output_path

output_file=${input_folder//\//_}
output_file="$AZ_BATCH_NODE_MOUNTS_DIR/${output_path}orf_count_${output_file}.csv"

echo "Output will be on file: $output_file"


echo "Execute orf count routine on each .faa file inside $input_folder:"
echo ""

printf "metagenome_file,orf_count\n" > $output_file

for input_file in $(find ./$input_folder -type f -name "*.faa"); do
    init=$(date +%s.%N)
    input_size=$(stat -c %s "$input_file")
    input_size=$(bc <<< "scale=3; $input_size/1000000")
    echo "Count orfs from file: $input_file   Size: $input_size MB"
    printf "$input_file,$(tr -cd '>' < $input_file | wc -c)\n" >> $output_file
    end=$(date +%s.%N)
    runtime=$(bc <<< "scale=3; ($end-$init)/1")
    echo "Count orf execution time: ${runtime} s"
    echo ""
done

end=$(date +%s.%N)
runtime=$(bc <<< "scale=3; ($end-$start)/60")
echo "Total elapsed time: ${runtime} min"
echo "Finished resistoma code"
