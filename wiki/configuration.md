
[BACK HOME](https://github.com/MeirellesLab/AzureCustomTasks/tree/main/wiki/home.md)


# THE config.json FILE

The most important part of using **ACT** is the use of the configuration file. This file must contain all the details of the tasks that need to executed. This will provide the easy customization and access to most features of the Microsoft Azure Batch services.

This file must contain a few required configuration string and many optional string, bellow is a description of the existing configuration string for the current version of this tool:

**OBS.: The comments were added to clarify each configuration string by they are not valid in the .json format.**


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
| pool.nodeStorageContainers | --- | Used to mount storage containers in the compute nodes |
| pool.nodeStorageContainers.mount | bool | Specifies if the nodes should mount the following storage containers |
| pool.nodeStorageContainers.containers | vector | A list with all the containers to be mounted |
| pool.nodeStorageContainers.containers.name | string | The storage container name |
| pool.nodeStorageContainers.containers.blobfuseOptions | string | The blobfuse options to the container mount procedure |
| pool.nodeAutoScale | --- | Used to include auto scale property to the pool |
| pool.nodeAutoScale.include | bool | Specifies if the node should use an auto scale formula |
| pool.nodeAutoScale.evaluationInterval | integer | The autoscale evaluation interval |
| pool.nodeAutoScale.formula | vector [string] | A list of strings representing the autoscale formula |
| pool.applications | --- | Used to include applications on the compute nodes |
| pool.applications.include | bool | Specifies if the compute nodes should install the applications |
| pool.applications.references | vector | A list of references to the applications to be installed |
| pool.applications.references.id | string | The application ID |
| pool.applications.references.version | string | The application version |
| pool.startupTask | --- | Used to include a Startup Task to the compute nodes |
| pool.startupTask.include | bool | Specifies if the compute nodes should include an startup task |
| pool.startupTask.command | string | The command line of the startup task |
| job | --- | | Used to include the job configurations |
| job.id | string | The Job ID |
| tasks | --- | Used to include the tasks configurations |
| tasks.addCollectionStep | integer | The number of tasks to be included in each iteration |
| tasks.inputs | --- | --- |
| tasks.inputs.areBlobsInInputStorage | bool | Specifies if the inputs are to be collected from the input storage, if FALSE an input file should be provided in the execution arguments |
| tasks.inputs.inputFileExtension | string | The file extension of the blobs to be used as inputs |
| tasks.inputs.outputFileExtension | string | The file extension expected to be on the output blobs |
| tasks.inputs.filterOutExistingBlobInOutputStorage | bool | Specifies if should remove from input list the blobs that already have their correspondent output blob in the output storage |
| tasks.inputs.filterOutExistingTaskInCurrentJob | bool | Specifies if should remove from input list the blobs that already have a Task assigned with the same input |
| tasks.inputs.taskSlotFormula | vector [string] | Used to assign an specific formula to calculate the required task slot of each Task. This formula should be written using Python syntax, can read any configuration parameter. Using $ before it's name and a dot for each hyerarchical level like '$pool.dedicatedNodeCount'. Has as builtin parameters inputName and inputSize. |
| tasks.inputs.order | --- | --- |
| tasks.inputs.order.by | string | --- |
| tasks.inputs.order.type | string | --- |
| tasks.resources | --- | --- |
| tasks.resources.automaticInputsUpload | bool | --- |
| tasks.resources.automaticScriptsUpload | bool | --- |
| tasks.logs | --- | --- |
| tasks.logs.automaticUpload | bool | --- |
| tasks.logs.destinationPath | string | --- |
| tasks.outputs | --- | --- |
| tasks.outputs.automaticUpload | bool | --- |
| tasks.command | string | --- |
| tasks.retryCount | integer | --- |
| tasks.retentionTimeInMinutes | integer | --- |
| storage | --- | --- |
| storage.accountName | string | --- |
| storage.accountDomain | string | --- |
| storage.accountSASToken | string | --- |
| storage.scripts | --- | --- |
| storage.scripts.container | string | --- |
| storage.scripts.blobPrefix | string | --- |
| storage.input | --- | --- |
| storage.input.container | string | --- |
| storage.input.path | string | --- |
| storage.input.blobPrefix | string | --- |
| storage.output | --- | --- |
| storage.output.container | string | --- |
| storage.output.path | string | --- |
| storage.output.blobPrefix | string | --- |
| cleanup | --- | --- |
| cleanup.timeoutInMinutes | integer | --- |


[BACK HOME](https://github.com/MeirellesLab/AzureCustomTasks/tree/main/wiki/home.md)
