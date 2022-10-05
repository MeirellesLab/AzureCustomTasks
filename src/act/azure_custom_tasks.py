"""
Author: Pablo Viana
Version: 1.0
Created: 2021/11/15

Azure custom tasks - Act v1.0

usage: python3 azure_custom_tasks.py  [-j JSON] [-i INPUT] [-xslcedrwfyvh] [-sI] [-sO] [-sS] [-sT] [-dI]

Azure Custom Tasks - ACT v1.0 - Uses Azure Batch Account to execute Batch Tasks
based on customized parameters contained in the configurations file. This file
specifies the script to be executed, the Storage Containers to use, the string
preffix of the blobs to be used as inputs and many other parameters. These
parameters are used to create the Batch Pool, Job and Tasks to run
asynchronously on the Microsoft Azure cloud environment.

options:
  -h, --help            show this help message and exit
  -j JSON, --json JSON  use the specified JSON file as the configuration file.
                        This file must be in the .json format and contain all
                        the required configuration strings. If you do not
                        provide this parameter, the default value is to consider
                        the existence of a file named config.json in the current
                        working directory. If the JSON file does not exist, the
                        program finishes with an error message. You cannot run
                        ACT without a configuration file.
  -x, --exec            start the Batch Service, Pool, Job and Tasks, execution
                        with the parameters specified in the configuration file.
                        If you do not supply any argument (other than -j and -i)
                        this is the default behavior of ACT.
  -i INPUTS, --input INPUTS
                        use the strings in the INPUTS file as inputs for the
                        Tasks. It is expected that each line of this file
                        contains one input description separated by comma, (1)
                        the input string itself, (2) the input size, and (3) the
                        required computing slots for this input, only the first
                        parameter is required, the other parameters are optional
                        with default value 0 and 1, respectively.
  -s, --show            show the debug information about the current execution:
                        inputs, outputs, scripts and Tasks’ commands.
  -sI, --show-inputs    show the corresponding blobs from the configured input.
  -sO, --show-outputs   show the corresponding blobs from the configured output.
  -sS, --show-scripts   show the corresponding blobs from the configured scripts.
  -sT, --show-tasks     show the Tasks’ commandLine for each Task.
  -dI, --delete-inputs  delete the corresponding blobs from configured input.
  -l, --list            list Tasks by their states.
  -c, --count           count Tasks by their states.
  -d, --disable         disable the current Job and all associated Tasks,
                        returning the Tasks that are running to the end of the
                        execution queue. Cannot add new Tasks while the Job is
                        disabled.
  -e, --enable          enable the current Job and all associated Tasks,
                        restarting the Task’s allocation to the execution queue
                        and the execution of the Tasks in the queue.
  -r, --reactivate      reactivate all failed Tasks to re-queue them.
  -w, --wait            wait all tasks to complete while showing the current
                        progress.
  -f, --free            terminate the batch and free its resources (deleting all
                        Pools, Jobs and Tasks from the Batch Account)
  -y, --yes             include this to --free command to confirm deletion
                        without requiring user confirmation.
  -v, --version         show ACT version number and exit.

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

import argparse

import copy
import json
import random
from types import SimpleNamespace
import azure.storage.blob as blobstorage

import time
import datetime
import azure.batch.models as batchmodels
from azure.batch import BatchServiceClient
from azure.batch.batch_auth import SharedKeyCredentials
from azure.batch.models import (
    OutputFileUploadCondition,
    AzureBlobFileSystemConfiguration as BlobFileSysConfig
    )


class AzureBatchUtils:
    """
    Author: Pablo Viana
    Version: 1.0
    Created: 2021/12/13

    Utility class to create Azure Batch pool, jobs and tasks.
    """
    def __init__(self, config):
        """
        Azure Batch constructor.
        """
        self.config = config
        # Create a Batch service client. We'll now be interacting with
        # the Batch service
        batch_credentials = SharedKeyCredentials(self.config.batch.accountName,
                                                 self.config.batch.accountKey)
        batch_client = BatchServiceClient(credentials=batch_credentials,
                                          batch_url=self.config.batch.accountUrl)
        self.batch_service_client = batch_client


    def get_config_pool(self):
        """
        Check if exists a pool with the configured id.
        :rtype: `azure.batch.models.CloudPool`
        :return: The configured Pool object or None if it doesn't exist.
        """
        for pool in self.batch_service_client.pool.list():
            if (pool.id == self.config.pool.id):
                return pool
        return None


    def create_pool(self):
        """
        Create a pool of compute nodes with the specified configuration options.
        """
        # Check if already exists a pool with the configured id, exits if True
        if self.get_config_pool():
            print(f'Pool [{self.config.pool.id}] already exists...')
            print()
            return

        print(f'Creating pool [{self.config.pool.id}]...')
        # Create a new pool of Linux compute nodes using an Azure Virtual
        # Machines Marketplace image. For more information about creating pools
        # of Linux nodes, see:
        # https://azure.microsoft.com/documentation/articles/batch-linux-nodes/
        new_pool = batchmodels.PoolAddParameter(
            id=self.config.pool.id,
            vm_size=self.config.pool.vmSize,
            target_dedicated_nodes=self.config.pool.dedicatedNodeCount,
            target_low_priority_nodes=self.config.pool.lowPriorityNodeCount,
            task_slots_per_node=self.config.pool.taskSlotsPerNode
            )
        # Set the Virtual Machine Configuration for the pool nodes
        vmConfiguration = self.config.pool.vmConfiguration
        virtual_machine_configuration=batchmodels.VirtualMachineConfiguration(
            image_reference=batchmodels.ImageReference(
                publisher=vmConfiguration.imageReference.publisher,
                offer=vmConfiguration.imageReference.offer,
                sku=vmConfiguration.imageReference.sku,
                version=vmConfiguration.imageReference.version,
                ),
            node_agent_sku_id=vmConfiguration.nodeAgentSKUId
            )
        # If configured to use Ephemeral OS Disk set it on the VM configuration
        if self.config.pool.useEphemeralOSDisk:
            virtual_machine_configuration.os_disk=batchmodels.OSDisk(
                ephemeral_os_disk_settings=batchmodels.DiffDiskSettings(
                    placement=batchmodels.DiffDiskPlacement.cache_disk
                    )
                )
        # Add the Virtual Machine Configuration to the pool
        new_pool.virtual_machine_configuration = virtual_machine_configuration

        # Set node auto scale parameters
        nodeAutoScale = self.config.pool.nodeAutoScale
        if nodeAutoScale.include:
            new_pool.enable_auto_scale = nodeAutoScale.include
            new_pool.auto_scale_formula = ";".join(nodeAutoScale.formula)
            interval = datetime.timedelta(
                minutes=nodeAutoScale.evaluationIntervalInMinutes
                )
            new_pool.auto_scale_evaluation_interval = interval

        # Configure the storage mount for the pool
        nodeStorage = self.config.pool.nodeStorageContainers
        if nodeStorage.mount:
            mount_configurations = []
            for node_container in nodeStorage.containers:
                mount_configurations.append(batchmodels.MountConfiguration(
                    azure_blob_file_system_configuration = BlobFileSysConfig(
                        account_name = self.config.storage.accountName,
                        sas_key = self.config.storage.accountSASToken,
                        container_name = node_container.name,
                        relative_mount_path = node_container.name,
                        blobfuse_options = node_container.blobfuseOptions
                        )
                    )
                )
            new_pool.mount_configuration = mount_configurations
        # Add Applications
        if self.config.pool.applications.include:
            applications = []
            for config_application in self.config.pool.applications.references:
                applications.append(batchmodels.ApplicationPackageReference(
                    application_id = config_application.id,
                    version = config_application.version
                    )
                )
            new_pool.application_package_references = applications
        # Configure the start task for the pool
        if self.config.pool.startupTask.include:
            new_pool.start_task=batchmodels.StartTask(
                command_line=f'/bin/bash -c "'\
                             f'{self.config.pool.startupTask.command}"',
                wait_for_success=True,
                user_identity=batchmodels.UserIdentity(
                    auto_user=batchmodels.AutoUserSpecification(
                        scope=batchmodels.AutoUserScope.pool,
                        elevation_level=batchmodels.ElevationLevel.admin
                        )
                    )
                )
        # Add the pool on the Batch Account
        self.batch_service_client.pool.add(new_pool)
        print('Pool created!')
        print()


    def get_config_job(self):
        """
        Check if exists a job with the configured id.
        :rtype: `azure.batch.models.CloudJob`
        :return: The configured Job object or None if it doesn't exist.
        """
        for job in self.batch_service_client.job.list():
            if (job.id == self.config.job.id):
                return job
        return None


    def create_job(self):
        """
        Create a job with the configured id and associate with configured pool.
        """
        # Check if already exists a job with the configured id, exits if True
        if self.get_config_job():
            print(f'Job [{self.config.job.id}] already exists...')
            print()
            return

        print(f'Creating job [{self.config.job.id}]...')
        # Create the job associating it with the configured pool
        job = batchmodels.JobAddParameter(
            id=self.config.job.id,
            pool_info=batchmodels.PoolInformation(pool_id=self.config.pool.id)
            )
        # Add the job on the Batch Account
        self.batch_service_client.job.add(job)
        print('Job created!')
        print()


    def enable_job_tasks(self):
        """
        Enable the job with configured id to receive new Tasks and starts
        execution.
        """
        if not self.get_config_job():
            print(f"Job [{self.config.job.id}] doesn't exists...")
            print()
            return
        # Enable the job on the Batch Account
        self.batch_service_client.job.enable(job_id=self.config.job.id)


    def disable_job_tasks(self):
        """
        Disable the job with configured id, halting the Tasks execution,
        requeueing them and stoping it from receiving new Tasks.
        """
        if not self.get_config_job():
            print(f"Job [{self.config.job.id}] doesn't exists...")
            print()
            return
        # Disable the job on the Batch Account
        self.batch_service_client.job.disable(
            job_id=self.config.job.id,
            disable_tasks=batchmodels.DisableJobOption.requeue)


    def reactivate_job_failed_tasks(self):
        """
        Reactivate the failed tasks on the job with configured id,
        requeueing them.
        """
        if not self.get_config_job():
            print(f"Job [{self.config.job.id}] doesn't exists...")
            print()
            return
        # Set filter option to failed Tasks (ne -> not equals)
        count_reactivated_tasks = 0
        filter_option = "executionInfo/exitCode ne 0"
        options = batchmodels.TaskListOptions(filter=filter_option)
        batch_tasks = self.batch_service_client.task
        for task in batch_tasks.list(job_id=self.config.job.id,
                                     task_list_options=options):
            count_reactivated_tasks += 1
            print(f"{task.id}: {task.command_line}")
            self.batch_service_client.task.reactivate(job_id=self.config.job.id,
                                                      task_id=task.id)
        return count_reactivated_tasks


    def get_job_task_counts(self):
        """
        Count the Tasks on the job with configured id.
        :rtype: `azure.batch.models.TaskCounts`
        :return: The TaskCounts object from the configured job
        """
        if self.get_config_job():
            count = self.batch_service_client.job.get_task_counts(
                job_id=self.config.job.id).task_counts
        else:
            count = batchmodels.TaskCounts(active=0, running=0, completed=0,
                                           succeeded=0, failed=0)
        count.total = count.active + count.running + count.completed
        return count


    def count_job_tasks(self):
        """
        Get count information about tasks on the configured Job.

        :rtype: (int, int)
        :return: total task count and completed task count.
        """
        # Get the tasks count on the configured JOB_ID
        task_counts = self.get_job_task_counts()
        return (task_counts.total, task_counts.completed)


    def filter_input_list_by_existing_tasks(self, input_list):
        """
        Filter the input list, removing the inputs that are already set on an
        existing Task.
        :params input_list: the original input list
        :type input_list: list<tuple(str, int, int)>
        :rtype: list<tuple(str, int, int)>
        :return: The filtered input list.
        """
        all_tasks_command = {}
        cfg_job = self.get_config_job()
        # Set all_tasks_command with commands of all tasks on the configured job
        if cfg_job:
            for task in self.batch_service_client.task.list(job_id=cfg_job.id):
                all_tasks_command[task.command_line] = task.id

        # Creates a filtered input list removing the inputs that already have a
        # task running the associated command
        filtered_input_list = []
        for input in input_list:
            cmd = f'/bin/bash -c "{self.config.tasks.command} \'{input[0]}\'"'
            if cmd in all_tasks_command:
                print(f'* Already exists in {all_tasks_command[cmd]} the '\
                      f'command: {cmd}')
            else:
                filtered_input_list.append(input)
        print()
        time.sleep(5)
        # returns the filtered list
        return filtered_input_list


    def create_task_output_file(self, file_pattern, destination_path,
                                upload_condition):
        """
        Create an OutputFile to retrieve files from computing nodes after
        Task execution.

        :params str file_pattern: pattern to match the files to retrieve.
        :params str destination_path: path on configured output container to
        place the files.
        :params upload_condition: condition to upload the output file,
        must be task_completion, task_success or task_failure.
        :type upload_condition: `azure.batch.models.OutputFileUploadCondition`
        :rtype: `azure.batch.models.OutputFile`
        :return: the OutputFile to include in Tasks for retrieval.
        """
        return batchmodels.OutputFile(
            file_pattern=file_pattern,
            destination=batchmodels.OutputFileDestination(
                container=batchmodels.OutputFileBlobContainerDestination(
                    container_url=self.config.output_container_url,
                    path=destination_path
                    )
                ),
            upload_options=batchmodels.OutputFileUploadOptions(
                upload_condition=upload_condition
                )
            )


    def create_task_collection(self, input_list, ini_id, end_id, execute_tasks):
        """
        Create Tasks with specified command.
        Add them to the Batch Service to be queued for execution.
        Cannot include too many Tasks at once because of resources limitation.

        :params int ini_id: initial index on input list to create and add Task.
        :params int end_id: final index on input list to create and add Task.
        :param bool execute_tasks: if True include tasks to be executed,
        otherwise just create the task list to be showed.
        """
        # Add one task for each given input file
        task_list = list()
        for idx in range(ini_id, end_id):
            input_file = input_list[idx][0]
            input_slots = input_list[idx][2]
            taskId = f'Task{idx+self.start_id:0{self.tasks_id_len}}'
            command = f"{self.config.tasks.command} '{input_file}' "\
                      f"{self.config.tasks.commandSuffix}"
            if self.config.argument.showTasks:
                print(f'{taskId} command: {command}')

            resource_files=[]
            if self.config.tasks.resources.automaticScriptsUpload:
                resource_files.append(
                    batchmodels.ResourceFile(
                        blob_prefix=self.config.storage.scripts.blobPrefix,
                        storage_container_url=self.config.scripts_container_url
                        )
                    )
            if self.config.tasks.resources.automaticInputsUpload:
                resource_files.append(
                    batchmodels.ResourceFile(
                        blob_prefix=input_file,
                        storage_container_url=self.config.input_container_url
                        )
                    )
            output_files=[]
            if self.config.tasks.logs.automaticUpload:
                logUpload = self.config.tasks.logs
                output_files.append(self.create_task_output_file(
                    file_pattern=logUpload.pattern,
                    destination_path=f'{logUpload.destinationPath}{taskId}',
                    upload_condition=OutputFileUploadCondition.task_completion
                    )
                )
            if self.config.tasks.outputs.automaticUpload:
                outputUpload = self.config.tasks.output
                output_files.append(self.create_task_output_file(
                    file_pattern=outputUpload.pattern,
                    destination_path=f'{outputUpload.destinationPath}',
                    upload_condition=OutputFileUploadCondition.task_success
                    )
                )

            # Create the Task with specified id, command,
            # resource files (inputs) and output files
            task_list.append(batchmodels.TaskAddParameter(
                id=taskId,
                command_line=command,
                required_slots=input_slots,
                constraints=batchmodels.TaskConstraints(
                    retention_time=datetime.timedelta(
                        minutes=self.config.tasks.retentionTimeInMinutes
                        ),
                    max_task_retry_count=self.config.tasks.retryCount,
                    ),
                resource_files=resource_files,
                output_files=output_files
                )
            )
        # Add the Tasks to be executed on the Batch Account
        if execute_tasks:
            self.batch_service_client.task.add_collection(
                self.config.job.id, task_list)
            print(f'{len(task_list)} tasks included!')
            time.sleep(5)


    def create_tasks(self, input_list, execute_tasks):
        """
        Add a task for each input file in the collection to the configured job.
        If the flag filterOutExistingTaskInCurrentJob is True, only add
        inputs that don't exist in the Tasks from the configured Job.

        :param input_files: A collection of input files. One task
        will be created for each input file. Each input is a tuple with a
        string representing the input item, the input size and the input
        required slots.
        :type input_list: list<tuple(str, int, int)>
        :param bool execute_tasks: if True include tasks to be executed,
        otherwise just create the task list to be showed.
        """
        if execute_tasks:
            if not self.get_config_job():
                print(f"Job [{self.config.job.id}] doesn't exists...")
                print()
                return
            print(f'Adding tasks to job [{self.config.job.id}]...')

        if self.config.tasks.inputs.filterOutExistingTaskInCurrentJob:
            # Filter input list removing existing inputs in current Tasks
            input_list = self.filter_input_list_by_existing_tasks(input_list)
        print(f'Adding {len(input_list)} tasks!')

        # Set Task id length to include trailing zeros in TaskId
        existing_tasks_in_job, _ = self.count_job_tasks()
        total = len(input_list) + existing_tasks_in_job
        self.start_id = existing_tasks_in_job + 1
        self.tasks_id_len = f'{len(str(total))}'

        # Add all tasks to the batch, a few at a time.
        # Each Task with a given input file.
        # Cannot include too many Tasks at once because of resources limitation.
        added_tasks = 0
        total_tasks = len(input_list)
        while (added_tasks < total_tasks):
            ini = added_tasks
            end = ini + self.config.tasks.addCollectionStep
            if(end > total_tasks):
                end = total_tasks
            self.create_task_collection(input_list, ini, end, execute_tasks)
            added_tasks += end-ini

        if execute_tasks:
            print()
            print('All tasks created!!')
            time.sleep(10)
            print()


    def wait_job_tasks_completion(self):
        """
        Wait for all tasks in the configured job to reach the Completed state,
        printing progress information.
        """
        time.sleep(30)
        total_tasks, completed_tasks = self.count_job_tasks()
        progress = ''

        while (completed_tasks < total_tasks):
            time.sleep(2)
            total_tasks, completed_tasks = self.count_job_tasks()
            # Print progress
            progress = '.' if (len(dot) > 4) else progress+'.'
            print(f'Progress {completed_tasks:03d}/{total_tasks:03d} ' \
                  f'{progress: <10}', end='\r')
        print()
        print()
        print("All tasks reached the 'Completed' state")
        print()


    def list_resources(self):
        """
        List Batch resources. Prints all Pools, Jobs and Tasks.
        """
        # Get all pools
        for pool in self.batch_service_client.pool.list():
            print(f'Pool: {pool.id}')
        print()
        # Get all jobs
        for job in self.batch_service_client.job.list():
            print(f'Job: {job.id}')
            for task in self.batch_service_client.task.list(job_id=job.id):
                print(f'   {task.id} command: {task.command_line}')
            print()
        print()


    def delete_resources(self):
        """
        Delete Batch resources. Terminate and delete Tasks, Jobs and Pools.
        """
        # Set the expiration timeout with configured timeout
        timeout_expiration = datetime.datetime.now() + datetime.timedelta(
            minutes=self.config.cleanup.timeoutInMinutes)

        # Get all jobs and mark for deletion
        for job in self.batch_service_client.job.list():
            self.batch_service_client.job.delete(job.id)
            print(f'Deleting Job: {job.id}')
        time.sleep(2)
        print()

        # Get all pools and mark for deletion
        for pool in self.batch_service_client.pool.list():
            self.batch_service_client.pool.delete(pool.id)
            print(f'Deleting Pool: {pool.id}')
        time.sleep(2)
        print()

        # While haven't finish, the cleanup process keeps printing
        # progress information
        dot = ''
        timeout = self.config.cleanup.timeoutInMinutes
        while(len(list(self.batch_service_client.job.list())) > 0 or
              len(list(self.batch_service_client.pool.list())) > 0):
            time.sleep(2)
            dot = '.' if (len(dot) > 4) else dot+'.'
            print(f'Cleaning up resources{dot: <10}', end='\r')
            # if reach the timeout expiration time raise an exception
            if(datetime.datetime.now() > timeout_expiration):
                raise RuntimeError(f'ERROR: Cleanup did not finish within '\
                                   f'timeout period of {timeout} min.')
        print()
        print('Cleanup completed!')


    def print_batch_exception(self, batch_exception):
        """
        Print the contents of the specified Batch exception.

        :param batch_exception: the occurring exception.
        :type batch_exception: `azure.batch.models.BatchErrorException`
        """
        print('-------------------------------------------')
        print('Exception encountered:')
        if (batch_exception.error and
            batch_exception.error.message and
            batch_exception.error.message.value):
            print(batch_exception.error.message.value)
            if batch_exception.error.values:
                print()
                for mesg in batch_exception.error.values:
                    print('{mesg.key}:\t{mesg.value}')
        print('-------------------------------------------')


class ConfigurationReader():
    """
    Author: Pablo Viana
    Version: 1.0
    Created: 2022/02/03

    Class to read the configuration file and the corresponding storage
    containers and the input list.
    """
    config = None

    def __init__(self, json_file):
        """
        Create the Configuration utility

        :params str json_file: string containing the json file data.
        """
        self.load_config(json_file)


    def get_config(self):
        """
        Get the configuration attributes

        :rtype: `azure_batch.config_reader.ConfigurationReader.config`
        :return: configuration object with json attributes as object attributes.
        """
        return self.config


    def load_config(self, json_file):
        """
        Load the configuration from the specified json file and returns the
        corresponding configuration object.

        :params str json_file: string containing the json file data.
        :rtype: `azure_batch.config_reader.Configuration.config`
        :return: configuration object with json attributes as object attributes.
        """
        self.config = None
        # read the JSON file
        with json_file as data:
            # parse data into an object with attributes
            # corresponding to the dict keys
            hook = lambda d: SimpleNamespace(**d)
            self.config = json.load(data, object_hook=hook)

        # set default values
        if not hasattr(self.config.tasks.inputs, 'taskSlotFormula'):
            self.config.tasks.inputs.taskSlotFormula = []
        if not hasattr(self.config.tasks, 'commandSuffix'):
            self.config.tasks.commandSuffix = ""
        if not hasattr(self.config.tasks.inputs, 'filterOutExistingTaskInCurrentJob'):
            self.config.tasks.inputs.filterOutExistingTaskInCurrentJob = False

        # update the configuration with new attributes for storage sas url
        i = self.config.storage.input
        o = self.config.storage.output
        s = self.config.storage.scripts
        self.config.input_container_url = self.get_sas_url(i.container)
        self.config.output_container_url = self.get_sas_url(o.container)
        self.config.scripts_container_url = self.get_sas_url(s.container)

        # creates calculteTaskSlots function
        self.calculateTaskSlots = self.create_function_calculate_task_slots()

        return self.config


    def set_show_arguments(self, show, show_inputs, show_outputs,
                           show_scripts, show_tasks):
        """
        Load the show attributes from the arguments and set these attributes
        in the configuration object.

        :params bool show: parameter specifying to show all elements.
        :params bool show_inputs: parameter specifying to show inputs.
        :params bool show_outputs: parameter specifying to show outputs.
        :params bool show_scripts: parameter specifying to show scripts.
        :params bool show_tasks: parameter specifying to show tasks.
        """
        self.config.argument = SimpleNamespace()
        self.config.argument.showInputs = show or show_inputs
        self.config.argument.showOutputs = show or show_outputs
        self.config.argument.showScripts = show or show_scripts
        self.config.argument.showTasks = show or show_tasks


    def get_sas_url(self, fullpath):
        """
        Create a shared access signature URL granting access for the container
        path with the given string.

        :params str fullpath: full container path name to map.
        :rtype: str
        :return: URL with permission to access the container path files.
        """
        return 'https://{}.{}/{}{}'.format(
            self.config.storage.accountName,
            self.config.storage.accountDomain,
            f'{fullpath}',
            self.config.storage.accountSASToken
            )


    def create_function_calculate_task_slots(self):
        """
        Create the user defined function, from the taskSlotFormula in the
        configuration file, to calculate the required slot count for
        each task, according to the input name and input size.
        The default value is 1.

        The statements must be in Python code, but the user can use only a
        limited set of built in functions.

        :rtype: <function>
        :return: the user defined function to calculate task required slot
        """
        # get the statements from the configured taskSlotFormula
        statements = '\n'.join([ '    ' + line for line in
                                self.config.tasks.inputs.taskSlotFormula])

        # if statements contain the string 'self' or 'config' raise an exception
        if('self' in statements or 'config' in statements):
            raise ValueError("Can't use 'self' or 'config' in taskSlotFormula!")

        # replaces the symbol '$' with a call to a configured attribute
        statements = statements.replace('$','config.')

        # the template that will be compiled with the configured formulas
        template = ["def calculateTaskRequiredSlots(input_name, input_size):",
                    "    requiredSlots = 1",
                    "{}",
                    "    return requiredSlots"]
        code = '\n'.join(template).format(statements)

        # allowed builtin functions that can be used in the formulas
        safe_list = {'abs':abs, 'all':all, 'any':any, 'bin':bin, 'bool':bool,
                     'chr':chr, 'filter':filter, 'format':format, 'float':float,
                     'hash':hash, 'int':int, 'len':len, 'max':max, 'min':min,
                     'ord':ord, 'range':range, 'reversed':reversed, 'str':str,
                     'round':round, 'sorted':sorted, 'sum':sum}

        my_global_scope = {}
        my_global_scope['__builtins__'] = safe_list
        # include a copy of the configured attributes in the used scope
        my_global_scope['config'] = copy.deepcopy(self.config)

        local_scope = {}
        # compile the code with the specified scope
        exec(code, my_global_scope, local_scope)

        # returns the created function
        return local_scope['calculateTaskRequiredSlots']


    def order_input_list(self, input_list):
        """
        Order the input list with the configured specifications.

        :param input_files: A collection of input files. Each input is a tuple
        with a string representing the input item, the input size and the input
        required slots.
        :type input_list: list<tuple(str, int, int)>
        """
        sort_attr = {"name":0, "size":1, "slots":2}
        sort_rev = {"asc":False, "desc":True}
        config_order = None
        config_reverse = False
        try:
            # try to get the order configured attributes, if they don't exist
            # use the default values, defined previously
            config_order = self.config.tasks.inputs.order.by
            config_reverse = sort_rev[self.config.tasks.inputs.order.type]
        except:
            pass

        print(f'order:{config_order}, reverse:{config_reverse}')
        if config_order == "random":
            # Shuffle the input list to randomize the execution of input files
            random.shuffle(input_list)
            print("shuffled!")

        if config_order in sort_attr:
            config_attr = sort_attr[config_order]
            # sorts the input list with the configured attributes
            input_list.sort(key=lambda x:x[config_attr], reverse=config_reverse)
            print("sorted!")


    def load_inputs(self, input_dict={}):
        """
        Load the list of inputs accordingly with the current configuration
        and set the config.inputs attribute.

        :params input_dict: Input items to be added.
        :type input_dict: Dictionary<str:tuple(str, int, int)>
        :rtype: list<tuple(str, int, int)>
        :return: list of input items.
        """
        # show scripts
        if self.config.argument.showScripts:
            print('Script files:')
            scr_container = blobstorage.ContainerClient.from_container_url(
                container_url=self.config.scripts_container_url)
            scr_prefix = f'{self.config.storage.scripts.blobPrefix}'
            for blob in scr_container.list_blobs(name_starts_with=scr_prefix):
                print(f'{blob.name},{blob.size}')
            print()

        # get inputs
        input_list = []
        if self.config.tasks.inputs.areBlobsInInputStorage:
            input_list = self.get_input_list_from_storage(input_dict)
        else:
            input_list = self.get_input_list_locally(input_dict)

        print('Inputs:')
        # order input list
        self.order_input_list(input_list)

        # show inputs
        if self.config.argument.showInputs:
            for input in input_list:
                print(f'{input[0]},{input[1]},{input[2]}')
        print(f'Input list ({len(input_list)})')
        print()

        self.config.inputs = input_list
        return self.config.inputs


    def get_input_list_locally(self, input_dict={}):
        """
        Get the list of input items from the given dictionary.

        :params input_dict: Input items to be added.
        :type input_dict: Dictionary<str:tuple(str, int, int)>
        :rtype: list<tuple(str, int, int)>
        :return: list of input items.
        """
        input_list = []
        for item_name in input_dict:
            if not item_name.startswith('#'):
                item = input_dict[item_name]
                item_size,item_slot = 0,1
                if len(item) > 1:
                    item_size = int(item[1])
                if len(item) > 2:
                    item_slot = item[2]
                else:
                    # calculate task slots required for this input blob size
                    item_slot = self.calculateTaskSlots(item_name, item_size)
                    if (item_slot > self.config.pool.taskSlotsPerNode):
                        print(f'File "{item_name}" is too big (requires '\
                              f'{item_slot} slots)! Cannot be executed '\
                              f'with current configuration.')
                        continue

                input_list.append((item_name, item_size, item_slot))
        return input_list


    def get_input_list_from_storage(self, input_dict={}):
        """
        Get the list of input files for the tasks from the storage.
        If input_dict is provided, blobs are added only if they are in the
        dictionary and exist in the Input Storage.
        If the flag filterOutExistingBlobInOutputStorage is True, only add
        blobs that don't exist in the Output Storage Container.

        :params input_dict: Blobs to be added. If empty, all blobs from the
        configured Input Storage Container are added.
        :type input_dict: Dictionary<str:tuple(str, int, int)>
        :rtype input_list: list<tuple(str, int, int)>
        :return: list of input items.
        """
        output_dict = {}
        if (self.config.tasks.inputs.filterOutExistingBlobInOutputStorage or
            self.config.argument.showOutputs):
            if self.config.argument.showOutputs:
                print('Output files:')
            # Create the output Blob Container Client to see if the output blobs
            # already exists on our output container.
            out_container = blobstorage.ContainerClient.from_container_url(
                container_url=self.config.output_container_url)
            out_prefix = f'{self.config.storage.output.path}'\
                         f'{self.config.storage.output.blobPrefix}'
            out_path_len = len(self.config.storage.output.path)
            out_extension = self.config.tasks.inputs.outputFileExtension
            out_extension_len = len(out_extension)
            for blob in out_container.list_blobs(name_starts_with=out_prefix):
                if blob.name.endswith(out_extension):
                    # removes prefix and extension
                    name = blob.name[out_path_len:-out_extension_len]
                    output_dict[name] = blob
                    #print outputs
                    if self.config.argument.showOutputs:
                        print(f'{blob.name[out_path_len:]},{blob.size}')
            print(f'Output list ({len(output_dict)})')
            print()

        # create the input Blob Container Client to get blobs from our container
        input_container = blobstorage.ContainerClient.from_container_url(
            container_url=self.config.input_container_url)

        # Define prefix to get blobs
        input_prefix = f'{self.config.storage.input.path}'\
                       f'{self.config.storage.input.blobPrefix}'
        input_path_len = len(self.config.storage.input.path)
        input_extension = self.config.tasks.inputs.inputFileExtension
        input_extension_len = len(input_extension)

        # get all blobs in the input container whose name starts with prefix
        input_list = []
        for blob in input_container.list_blobs(name_starts_with=input_prefix):
            # if blobs doesn't ends with the expected extension don't add it
            if not blob.name.endswith(input_extension):
                continue
            # add all listed input blobs if input_dict is empty otherwise
            # only add if the blob is in the input_dict
            if (len(input_dict) > 0 and blob.name not in input_dict):
                continue
            # if True checks blob's existence in output container
            if self.config.tasks.inputs.filterOutExistingBlobInOutputStorage:
                output_name = blob.name[input_path_len:-input_extension_len]
                # if blob exists in output container don't add to input list
                if output_name in output_dict:
                    print(f'File already exists in output container: '\
                          f'{blob.name}')
                    continue

            # calculate task slots required for this input blob size
            required_slots = self.calculateTaskSlots(blob.name, blob.size)
            if (required_slots > self.config.pool.taskSlotsPerNode):
                print(f'File "{blob.name}" is too big (requires '\
                      f'{required_slots} slots)! Cannot be executed '\
                      f'with current configuration.')
                continue
            input_list.append((blob.name, blob.size, required_slots))
        print()

        return input_list


    def delete_config_input_blobs(self):
        """
        Delete all blobs with the configured input specifications.
        """
        # create the input Blob Container Client to get blobs from our container
        input_container = blobstorage.ContainerClient.from_container_url(
            container_url=self.config.input_container_url)

        # Define prefix to get blobs
        input_prefix = f'{self.config.storage.input.path}'\
                       f'{self.config.storage.input.blobPrefix}'

        # get all blobs in the input container whose name starts with prefix
        for blob in input_container.list_blobs(name_starts_with=input_prefix):
            # delete all specified blobs
            input_container.delete_blob(blob, delete_snapshots='include')


class InputHandler:
    """
    Author: Pablo Viana
    Version: 1.0
    Created: 2021/12/26

    Class to handle the user inputs. Parsing the arguments and dealing with
    input queries.
    """
    def __init__(self):
        pass

    def getArguments(self):
        """
        Parse the script arguments and return them as a SimpleNamespace object
        built up from attributes parsed out of the command line.

        :rtype: `types.SimpleNameSpace`
        :return: the command line attributes on a SimpleNamespace object.
        """
        # Create argument parser
        parser = argparse.ArgumentParser(description='Azure Custom Tasks - ACT'\
                                         ' v1.0 - Uses Azure Batch Account to'\
                                         ' execute Batch Tasks based on'\
                                         ' customized parameters contained in'\
                                         ' the configuration file. This file'\
                                         ' specifies the script to be executed,'\
                                         ' the Storage Containers to use, the'\
                                         ' string preffix of the blobs to be'\
                                         ' used as inputs and many other'\
                                         ' parameters. These parameters are'\
                                         ' used to create the Batch Pool, Job'\
                                         ' and Tasks to run asynchronously on'\
                                         ' the Microsoft Azure cloud'\
                                         ' environment.',
                                         usage= 'python3 %(prog)s  [-j JSON]'\
                                         ' [-i INPUT] [-xslcedrwfyvh] [-sI]'\
                                         ' [-sO] [-sS] [-sT] [-dI]')
        # Optional arguments
        parser.add_argument('-j', '--json', metavar='JSON', help='use the'\
                            ' specified JSON file as the configuration file.'\
                            ' This file must be in the .json format and contain'\
                            ' all the required configuration strings. If you'\
                            ' do not provide this parameter, the default value'\
                            ' is to consider the existence of a file named'\
                            ' config.json in the current working directory. If'\
                            ' the JSON file does not exist, the program'\
                            ' finishes with an error message. You cannot run'\
                            ' ACT without a configuration file.',
                            default='config.json', type=argparse.FileType('r'))
        parser.add_argument('-x', '--exec', help='start the Batch Service,'\
                            ' Pool, Job and Tasks, execution with the'\
                            ' parameters specified in the configuration file.'\
                            ' If you do not supply any argument (other than -j'\
                            ' and -i this is the default behavior of ACT.',
                            action='store_true')
        parser.add_argument('-i', '--input', metavar='INPUTS', help='use the'\
                            ' strings in the INPUTS file as inputs for the'\
                            ' Tasks. It is expected that each line of this'\
                            ' file contains one input description separated by'\
                            ' comma, (1) the input string itself, (2) the'\
                            ' input size, and (3) the required computing slots'\
                            ' for this input, only the first parameter is'\
                            ' required, the other parameters are optional with'\
                            ' default value 0 and 1, respectively.',
                            type=argparse.FileType('r'))
        parser.add_argument('-s', '--show', help='show the debug information'\
                            ' about the current execution: inputs, outputs,'\
                            ' scripts and Tasks’ commands.', action='store_true')
        parser.add_argument('-sI', '--show-inputs', help='show the corresponding'\
                            ' blobs from the configured input.', action='store_true')
        parser.add_argument('-sO', '--show-outputs', help='show the'\
                            ' corresponding blobs from the configured output.',
                            action='store_true')
        parser.add_argument('-sS', '--show-scripts', help='show the'\
                            ' corresponding blobs from the configured scripts.',
                            action='store_true')
        parser.add_argument('-sT', '--show-tasks', help='show the Tasks’'\
                            ' commandLine for each Task.', action='store_true')
        parser.add_argument('-dI', '--delete-inputs', help='delete the'\
                            ' corresponding blobs from configured input.',
                            action='store_true')
        parser.add_argument('-l', '--list', help='list Tasks by their states.',
                            action='store_true')
        parser.add_argument('-c', '--count', help='count Tasks by their states.',
                            action='store_true')
        parser.add_argument('-d', '--disable', help='disable the current Job'\
                            ' and all associated Tasks, returning the Tasks'\
                            ' that are running to the end of the execution'\
                            ' queue. Cannot add new Tasks while the Job is'\
                            ' disabled.', action='store_true')
        parser.add_argument('-e', '--enable', help='enable the current Job and'\
                            ' all associated Tasks,restarting the Task’s'\
                            ' allocation to the execution queue and the'\
                            ' execution of the Tasks in the queue.',
                            action='store_true')
        parser.add_argument('-r', '--reactivate', help='reactivate all failed' \
                            ' Tasks to re-queue them.', action='store_true')
        parser.add_argument('-w', '--wait', help='wait all tasks to complete'\
                            ' while showing the current progress.',
                            action='store_true')
        parser.add_argument('-f', '--free', help='terminate the batch and free'\
                            ' its resources (deleting all Pools, Jobs and'\
                            ' Tasks from the Batch Account)',
                            action='store_true')
        parser.add_argument('-y','--yes', help='include this to --free command'\
                            ' to confirm deletion without requiring user'\
                            ' confirmation.', action='store_true')
        # Print version
        parser.add_argument('-v', '--version', help='show ACT version number'\
                            ' and exit.', action='version',
                            version='Azure Custom Tasks - Act v1.0')

        args = parser.parse_args()

        args.execute = False

        if not args.free:
            args.yes = False

        # create show any attribute
        args.show_any = (args.show or args.show_inputs or args.show_outputs or
                         args.show_scripts or args.show_tasks)

        allValues = list()
        for key in args.__dict__:
            if not key == "json":
                allValues.append(args.__dict__[key])

        if (args.exec or not any(allValues)):
            args.execute = True

        # Raw print arguments
        print("Script is running with arguments:")
        for a in args.__dict__:
            print(str(a) + ": " + str(args.__dict__[a]))
        print()

        return args


    def query_yes_no(self, question, default=None):
        """
        Prompts the user for yes/no input, displaying the specified question text.

        :param str question: The text of the prompt for input.
        :param str default: The default if the user hits <ENTER>. Acceptable values
        are 'yes', 'no', and None.

        :rtype: str
        :return: 'yes' or 'no'
        """
        valid = {'y': 'yes', 'n': 'no'}
        if default is None:
            prompt = ' [y/n] '
        elif default == 'yes':
            prompt = ' [Y/n] '
        elif default == 'no':
            prompt = ' [y/N] '
        else:
            raise ValueError(f"Invalid default answer: '{default}'")

        while 1:
            choice = input(question + prompt).lower()
            if default and not choice:
                return default
            try:
                return valid[choice[0]]
            except (KeyError, IndexError):
                print("Please respond with 'yes' or 'no' (or 'y' or 'n').\n")


class AzureCustomTasks:
    """
    Author: Pablo Viana
    Version: 1.0
    Created: 2022/08/12

    Class main to run application.
    """
    def __init__(self):
        pass

    def main(self):
        """
        Create the classes to run using the specified configuration with the
        arguments received.
        """

        start_time = datetime.datetime.now().replace(microsecond=0)
        print('Starting Custom Azure Batch Script')
        print(f'Start time: {start_time}')
        print()

        # Parse the arguments
        ihandler = InputHandler()
        args = ihandler.getArguments()
        # Get customized configurations
        config = ConfigurationReader(args.json)
        config.set_show_arguments(args.show, args.show_inputs, args.show_outputs,
                                  args.show_scripts, args.show_tasks)
        # Create Batch Utils class
        azure_batch = AzureBatchUtils(config.get_config())
        ############################################################################
        try:
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
                config.delete_config_input_blobs()

            input_dict = {}
            if (args.input):
                # Get inputs from the file
                with args.input as file:
                    for line in file:
                        line = line.strip().split(',')
                        input_dict[line[0]] = line

            if (args.execute or args.show_any):
                # set input list with configured parameters
                input_list = config.load_inputs(input_dict)
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
                    ihandler.query_yes_no('Delete batch resources?') == 'yes'):
                    azure_batch.delete_resources()

        except batchmodels.BatchErrorException as err:
            azure_batch.print_batch_exception(err)
            raise

        print()
        ########################################################################
        # Print out some timing info
        end_time = datetime.datetime.now().replace(microsecond=0)
        print(f'Script end: {end_time}')
        print(f'Elapsed time: {end_time-start_time}')
        print()



if __name__ == '__main__':
    """
    Redirects the main execution to the main function.
    """
    AzureCustomTasks().main()
