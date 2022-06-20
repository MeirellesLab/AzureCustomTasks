"""
Author: Pablo Viana
Version: 1.0
Created: 2021/11/15

Azure custom tasks - Act v1.0
usage: python3 azure_custom_tasks.py [-x [FILE]] [-hxlcedwfyv]

Uses Azure Batch Account to execute Batch Tasks based on customized
configurations contained in the config.py file. This file specifies the script
to be executed, the Storage Containers to use, the string preffix of the
blobs to be used as inputs and many other parameters. These parameters are used
to create the Batch Pool, Job and tasks to run asynchronously on the cloud.

optional arguments:
  -h, --help            show this help message and exit
  -j  JSON              uses the specified file as the configuration file.
                        This file must contain all the required configuration
                        strings.
  -x, --exec            start the batch service pool, job and tasks execution
                        with the parameters specified in the configuration file.
  -i  FILE              start all tasks   If FILE is supplied, uses the
                        blobs specified in it as input (all blobs must be in
                        the STORAGE_CONTAINER_INPUT specified in the
                        configuration file).
  -s, --show            show the blobs from the configured containers: input,
                        output and scripts and the tasks commandLine attribute.
  -sI, --show-inputs    show the blobs from the configured container input.
  -sO, --show-outputs   show the blobs from the configured container output.
  -sS, --show-scripts   show the blobs from the configured container scripts.
  -sT, --show-tasks      show the tasks commandLine for each task
  -l, --list            list tasks by its states.
  -c, --count           count tasks by its states.
  -d, --disable         disable the job and all associated tasks, returning
                        the tasks that are running to the end of the execution
                        queue. Cannot add new task while the Job is disabled.
  -e, --enable          enable the job and all associated tasks, restarting
                        execution of the tasks in the queue.
  -w, --wait            wait all tasks to complete and show progress.
  -f, --free            terminate batch and free its resources (deleting all
                        pools, jobs and tasks)
  -y, --yes             include this to -f command to confirm deletion without
                        requering to input yes.
  -v, --version         show program's version number and exit
"""
################################################################################
#   IMPORTANT!!!
################################################################################
# Update the Batch and Storage account credential strings in config file with
# values unique to your accounts. These are used when constructing connection
# strings for the Batch and Storage client objects.
# The Storage Account SAS has to the valid throughout all the Tasks execution!!
# Also update the Pool, Job and Task strings for the specific scripts to be run.
################################################################################
import datetime
import batch_utils
import input_handler
import config_reader

from azure.batch.models import BatchErrorException


def main():
    """
    Create the pool, job and tasks to run using specified configuration
    """
    start_time = datetime.datetime.now().replace(microsecond=0)
    print('Starting Custom Azure Batch Script')
    print(f'Start time: {start_time}')
    print()

    # Parse the arguments
    args = input_handler.getArguments()
    # Get customized configurations
    reader = config_reader.ConfigurationReader(args.json)
    reader.set_show_arguments(args.show, args.show_inputs, args.show_outputs,
                              args.show_scripts, args.show_tasks)
    ############################################################################
    try:
        azure_batch = batch_utils.AzureBatchUtils(reader.get_config())

        if (args.reactivate):
            print("Reactivating Failed Tasks:")
            sum = azure_batch.reactivate_job_failed_tasks()
            print(f"Reactivated {sum} Tasks.")
            print()

        if (args.enable):
            print("Enabling Job and Tasks:")
            azure_batch.enable_job_tasks()
            print()

        if (args.disable):
            print("Disabling Job and Tasks:")
            azure_batch.disable_job_tasks()
            print()

        if (args.execute):
            # Create the pool that will contain the compute nodes that
            # will execute the tasks.
            azure_batch.create_pool()
            # Create the job that will run the tasks.
            azure_batch.create_job()

        if (args.delete_inputs):
            # delete blobs configured as inputs
            reader.deleteConfigInputBlobs()

        input_dict = {}
        if (args.input):
            # Get inputs from the file
            with args.input as file:
                for line in file:
                    line = line.strip().split(',')
                    input_dict[line[0]] = line

        if (args.execute or args.show_any):
            # set input list with configured parameters
            input_list = reader.load_inputs(input_dict)
            # Creates the tasks to be executed or showed
            azure_batch.create_tasks(input_list, args.execute)

        if (args.list):
            azure_batch.list_resources()

        if (args.count):
            task_counts = azure_batch.count_job_tasks()
            print(f'Total Tasks: {task_counts.total}')
            print(f'  Active    Tasks: {task_counts.active}')
            print(f'  Running   Tasks: {task_counts.running}')
            print(f'  Completed Tasks: {task_counts.completed}')
            print(f'    Succeeded Tasks: {task_counts.succeeded}')
            print(f'    Failed    Tasks: {task_counts.failed}')
            print()

        if (args.wait):
            azure_batch.wait_job_tasks_completion()

        # Free Batch resources (if the user confirms to do so).
        if (args.free):
            if (args.yes or
                input_handler.query_yes_no('Delete batch resources?') == 'yes'):
                azure_batch.delete_resources()

    except BatchErrorException as err:
        azure_batch.print_batch_exception(err)
        raise

    print()
    ############################################################################
    # Print out some timing info
    end_time = datetime.datetime.now().replace(microsecond=0)
    print(f'Script end: {end_time}')
    print(f'Elapsed time: {end_time-start_time}')
    print()



if __name__ == '__main__':
    """
    Redirects the main execution to the main function.
    """
    main()
