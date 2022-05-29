"""
Author: Pablo Viana
Version: 1.0
Created: 2021/12/13

Utility script to create Azure Batch pool, jobs and tasks.
"""
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
            command = f'/bin/bash -c "{self.config.tasks.command} ' \
                      f'\'{input_file}\'"'

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
            print()


    def wait_job_tasks_completion(self):
        """
        Wait for all tasks in the configured job to reach the Completed state,
        printing progress information.
        """
        dot = ''
        total_tasks, completed_tasks = self.count_job_tasks()

        while (completed_tasks < total_tasks):
            time.sleep(2)
            total_tasks, completed_tasks = self.count_job_tasks()
            # Print progress
            dot = '.' if (len(dot) > 4) else dot+'.'
            print(f'Progress {completed_tasks:03d}/{total_tasks:03d} ' \
                  f'{dot: <10}', end='\r')
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
