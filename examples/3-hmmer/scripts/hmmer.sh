#!/bin/bash
:<<DOC
Author: Pablo Viana
Version: 1.0
Created: 2022/01/29

Script used to execute HMMER in the Azure Batch Tasks.

params $1 - Input file path
params $2 - Output Container SAS URL, where to save the output file
params $3 - File to be run as input
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
output_sas_url=$2
input_file=$3

resfams="./hmmer_resistoma/Resfams.hmm"
output_file=${input_file//.faa/_modelo.txt}
output_path=${input_file//$input_path/}
output_path=${output_path%%/*}
output_path=$input_path$output_path
input_size=$(stat -c %s "$input_file")
input_size=$(bc <<< "scale=3; $input_size/1000")

echo "Started resistoma code"

#echo "File system available space:"
echo $(df -h /)

echo "Task ID: $AZ_BATCH_TASK_ID"
echo "Node ID: $AZ_BATCH_NODE_ID"
echo "Resfam file: $resfams"
echo "Input file: $input_file"
echo "Input size: $input_size KB"
echo "Output SAS URL: $output_sas_url"
echo "Output file: $output_file"
echo "Output path: $output_path"

echo "Executing HMMER routine:"
init=$(date +%s.%N)
hmmscan --noali --cut_ga --cpu 0 -o /dev/null --tblout "$output_file" "$resfams" "$input_file"
end=$(date +%s.%N)
runtime=$(bc <<< "scale=3; ($end-$init)/60")
echo "Routine execution time: ${runtime} min"

echo "Deleting scripts"
rm -r "hmmer_resistoma/"
echo "Deleting input file"
rm $input_file

output_size=$(stat -c %s "$output_file")
output_size=$(bc <<< "scale=3; $output_size/1000")
echo "Output size: $output_size KB"

echo "Executing azcopy routine:"
init=$(date +%s.%N)
${AZ_BATCH_APP_PACKAGE_azcopy}/azcopy copy "$output_path" "$output_sas_url" --recursive
end=$(date +%s.%N)
runtime=$(bc <<< "scale=3; ($end-$init)/1")
echo "Routine execution time: ${runtime} s"

echo "Deleting output file"
rm $output_file

#echo "File system available space:"
echo $(df -h /)

end=$(date +%s.%N)
runtime=$(bc <<< "scale=3; ($end-$start)/60")
echo "Total elapsed time: ${runtime} min"
echo "Finished resistoma code"
