#!/bin/bash

# Specify the directory containing the .fasta files
input_directory="$1"

# Ensure the input directory exists
if [ ! -d "$input_directory" ]; then
  echo "Error: Directory $input_directory does not exist."
  exit 1
fi

# Start time
start_time=$(date +%s)

# Debug information
echo "Starting the Prodigal processing at $(date)"
echo "Input directory: $input_directory"

# Iterate over all .fasta files in the specified directory
for fasta_file in "$input_directory"/*.fasta; do
  # Ensure the file exists
  if [ ! -f "$fasta_file" ]; then
    echo "Warning: No .fasta files found in the directory."
    break
  fi

  # Extract the base name of the file (without directory and extension)
  base_name=$(basename "$fasta_file" .fasta)

  # Define the output file name with .faa extension
  output_file="$input_directory/$base_name.faa"

  # Capture start time for this file
  file_start_time=$(date +%s)

  # Run Prodigal and redirect the output to /dev/null
  echo "Processing $fasta_file..."
  prodigal -i "$fasta_file" -a "$output_file" -p meta > /dev/null 2>&1

  # Capture end time for this file
  file_end_time=$(date +%s)

  # Calculate and display time taken for this file
  file_elapsed_time=$((file_end_time - file_start_time))
  echo "Completed $fasta_file in $file_elapsed_time seconds."
done

# End time
end_time=$(date +%s)

# Calculate and display total elapsed time
elapsed_time=$((end_time - start_time))
echo "Finished all processing at $(date)"
echo "Total time taken: $elapsed_time seconds."

