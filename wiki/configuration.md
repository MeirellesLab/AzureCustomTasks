
[BACK HOME](home.md)


# THE config.json FILE

The most important part of using **ACT** is the use of the configuration file. This file must contain all the details of the tasks that need to executed. This will provide the easy customization and access to most features of the Microsoft Azure Batch Services.

This file must contain a few required configuration strings and many optional ones. Bellow is a description of the current configuration strings of this tool:


| Configuration attribute | Type | Description |
| --- | --- | --- |
| batch.accountName | string | The name of the batch account on your Microsoft Azure Subscription to be used |
| batch.accountKey | string | The corresponding batch account key, found in the Azure portal |
| batch.accountUrl | string | The corresponding batch account url, found in the Azure portal |
| pool | --- | --- |
| pool.id | string | The ID that will be used to name the pool of compute nodes created |
| pool.dedicatedNodeCount | integer | The number of dedicated compute nodes to be created in this pool |
| pool.lowPriorityNodeCount | integer | The number of low priority compute nodes to be created in this pool |
| pool.vmSize | string | The string representing the [VM size](https://docs.microsoft.com/en-us/azure/virtual-machines/sizes) to be used |
| pool.vmConfiguration | --- | --- |
| pool.vmConfiguration.imageReference | --- | The [Virtual Machine image configuration](https://docs.microsoft.com/en-us/azure/virtual-machines/linux/cli-ps-findimage) to be used |
| pool.vmConfiguration.imageReference.publisher | string | The VM Image publisher string |
| pool.vmConfiguration.imageReference.offer | string | The VM Image offer description string |
| pool.vmConfiguration.imageReference.sku | string | The VM Image operation system string |
| pool.vmConfiguration.imageReference.version | string | The VM Image version string |
| pool.vmConfiguration.nodeAgentSKUId | string | The VM Image Agent SKU ID to be used |
| pool.useEphemeralOSDisk | bool | If the VM should use ephemeral OS Disks, can only be used if there are only dedicated nodes |
| pool.nodeStorageContainers | --- | Used to mount storage containers in the compute nodes.  It’s important to note that if different Tasks use one blob in the same container, this can cause synchronizing problems that have to be considered, for more details see the [blobfusion specifications](https://github.com/Azure/azure-storage-fuse/). |
| pool.nodeStorageContainers.mount | bool | Specifies if the nodes should mount the following storage containers |
| pool.nodeStorageContainers.containers* | vector | A list with all the containers to be mounted |
| pool.nodeStorageContainers.containers.name* | string | The storage container name |
| pool.nodeStorageContainers.containers.blobfuseOptions* | string | The blobfuse options to the container mount procedure |
| pool.nodeAutoScale | --- | Used to include auto scale property to the pool |
| pool.nodeAutoScale.include | bool | Specifies if the node should use an auto scale formula |
| pool.nodeAutoScale.evaluationInterval* | integer | The autoscale evaluation interval |
| pool.nodeAutoScale.formula* | vector [string] | A list of strings representing the autoscale formula |
| pool.applications | --- | Used to include applications on the compute nodes |
| pool.applications.include | bool | Specifies if the compute nodes should install the applications |
| pool.applications.references* | vector | A list of references to the applications to be installed |
| pool.applications.references.id* | string | The application ID |
| pool.applications.references.version* | string | The application version |
| pool.startupTask | --- | Used to include a Startup Task to the compute nodes |
| pool.startupTask.include | bool | Specifies if the compute nodes should include an startup task |
| pool.startupTask.command* | string | The command line of the startup task |
| job | --- | | Used to include the job configurations |
| job.id | string | The Job ID |
| tasks | --- | Used to include the tasks configurations |
| tasks.addCollectionStep | integer | The number of tasks to be included in each iteration |
| tasks.inputs | --- | --- |
| tasks.inputs.areBlobsInInputStorage | bool | Specifies if the inputs are to be collected from the input storage, if FALSE an input file should be provided in the execution arguments |
| tasks.inputs.inputFileExtension* | string | The file extension of the blobs to be used as inputs |
| tasks.inputs.outputFileExtension* | string | The file extension expected to be on the output blobs |
| tasks.inputs.filterOutExistingBlobInOutputStorage* | bool | Specifies if should remove from input list the blobs that already have their correspondent output blob in the output storage |
| tasks.inputs.filterOutExistingTaskInCurrentJob | bool | Specifies if should remove from input list the blobs that already have a Task assigned with the same input |
| tasks.inputs.taskSlotFormula | vector [string] | Used to assign an specific formula to calculate the required task slot of each Task. This formula should be written using Python syntax, can read any configuration parameter. Using $ before it's name and a dot for each hyerarchical level like '$pool.dedicatedNodeCount'. Has as builtin parameters inputName and inputSize |
| tasks.inputs.order* | --- | Used to define the sorting order of the input list |
| tasks.inputs.order.by* | string | Attribute to use to sort the list. Possible values are: **name, size or slot count**, the **default value is to order by name** |
| tasks.inputs.order.type* | string | Used to define the sorting method, possible values are **asc or desc**, the **default value is asc** |
| tasks.resources | --- | Used to define if resources should be copied to the Task node automatically |
| tasks.resources.automaticInputsUpload | bool | Define if the input blobs should be copied to the Task working directory |
| tasks.resources.automaticScriptsUpload | bool | Define if the script blobs should be copied to the Task working directory |
| tasks.logs | --- | Used to define what to do with log files after the Task goes to **completed state** |
| tasks.logs.automaticUpload | bool | Define if logs are to be copied out of the Tasks when they finish |
| tasks.logs.destinationPath | string |  Define the destination path where to copy the logs from Tasks when they finish |
| tasks.outputs | --- | Used to define what to do with the output after the Task goes to **successfully completed  state** |
| tasks.outputs.automaticUpload | bool | Define if ouptut blobs are to be copied out of the Tasks when they finish |
| tasks.command | string | Define the Task commandLine |
| tasks.retryCount | integer | Define the retry count of the Tasks |
| tasks.retentionTimeInMinutes | integer | Define the time in minutes to retain the Task files in the compute node |
| storage | --- | --- |
| storage.accountName | string | The name of the storage account you are going to use |
| storage.accountDomain | string | The storage account domain you are going to use |
| storage.accountSASToken | string | The storage account SAS Token you are going to use |
| storage.scripts | --- | Used to define where are the scripts in the storage |
| storage.scripts.container | string | Define the container name where are the scripts |
| storage.scripts.blobPrefix | string | Define the blobPrefix of the scripts in the specified storage container |
| storage.input | --- | Used to define where are the inputs in the storage |
| storage.input.container | string | Define the container name where are the inputs |
| storage.input.path | string | Define the path of the inputs in the specified storage container |
| storage.input.blobPrefix | string | Define the blobPrefix of the inputs in the specified storage container |
| storage.output | --- | Used to define where are the outputs in the storage |
| storage.output.container | string | Define the container name where are the outputs |
| storage.output.path | string | Define the path of the outputs in the specified storage container |
| storage.output.blobPrefix | string | Define the blobPrefix of the outputs in the specified storage container |
| cleanup | --- | Used when call the free resources argument |
| cleanup.timeoutInMinutes | integer | Defines the time-out in minutes for the clean up proccess. Terminate the proccess after this time, if it doesn't finish before that |


[BACK HOME](home.md)
