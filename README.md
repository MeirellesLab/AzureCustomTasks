# ACT - Azure Custom Tasks - A tool to rapidly create custom tasks for the Microsoft Azure Batch service

## About

ACT is a software tool developed using Python v3.6, that can be used to easily support the creation and execution of parallelized tasks using the Microsoft Azure Batch service. This tool is perfect for developers that promptly need to take advantage of the parallellization of their tasks and, also, to fasten the deployment and make their tasks less error prone. Since, it's highly reusable and minimizes the code that needs to be done and includes a builtin log feature to help to keep track of the task events and profile the execution of the Task's commands.

## Usage

```bash
python3 azure_custom_tasks.py [-j JSON] [-i INPUT] [-hxlcedwfyvs] [-sI] [-sO] [-sS] [-sT]
```

ACT uses an existing Azure Batch Account to execute Batch Tasks based on customized configurations provided in a config.json file. This file specifies the script to be executed, the Storage Containers to use, the string prefix of the blobs to be used as inputs and many other parameters. These parameters are used to create the Batch Pool, Job and Tasks to run asynchronously on the Microsoft Azure Cloud environment.

### OPTIONAL ARGUMENTS

This Section explains in detail the possible arguments used with the ACT program, all arguments are optional and if not provided consider the default value:

- **-j or --json** : uses the specified JSON file as the configuration file. This file must be in the .json format and contain all the required configuration strings. If this parameter is not provided, the **default** is to consider the existence of a config.json in the current working directory, if it doesn't exist the program finishes with an error message. **You cannot run ACT without a configuration file.** This file and all it's configuration parameters are explained in its corresponding [section](#the-configjson-file).
- **-i or --input** : uses the strings in the INPUT file as inputs for each task that will be created. It's expected that each line contain one input description separated by comma, being the first string the input itself, the second the input size and the third the required task slots for this input, **only the first parameter is required, the input string itself, the other parameters are optional with default value 0 and 1 respectively**. This can be understood in more detail in the [examples]().
- **-x or --exec** : start the batch service Pool, Job and tasks execution with the parameters specified in the configuration file. If no other argument is supplied **(other then -j and -i)** this is considered the **default behavior of ACT**.
- **-s or --show** : show the blobs from the configured containers: input, output and scripts and the tasks commandLine attribute.
- **-sI or --show-inputs** : show the blobs from the configured container input.
- **-sO or --show-outputs** : show the blobs from the configured container output.
- **-sS or --show-scripts** : show the blobs from the configured container scripts.
- **-sT or --show-tasks** : show the task's commandLine for each task.
- **-l or --list** : list tasks by their states.
- **-c or --count** : count tasks by their states.
- **-d or --disable** : disable the current Job and all associated tasks, returning the tasks that are running to the end of the execution queue. Cannot add new tasks while the Job is disabled.
- **-e or --enable** : enable the current Job and all associated tasks, restarting the task's allocation to the execution queue.
- **-w or --wait** : wait all tasks to complete while shows the current progress.
- **-f or --free** : terminate the batch and free its resources (deleting all pools, jobs and tasks from the batch account).
- **-y or --yes** : include this to --free command to confirm deletion without requering the user reply.
- **-v or --version** : show program's version number and exit.
- **-h or --help** : show the help message and exit.

### THE config.json FILE

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





```json
{  "batch": {
    "accountName":"STRING",             #The name of the batch account on your Microsoft Azure Subscription to be used
    "accountKey":"STRING",              #The corresponding batch account key, found in the Azure portal
    "accountUrl":"STRING"               #The corresponding batch account url, found in the Azure portal
  },
  "pool": {
    "id":"STRING",                      #The ID that will be used to name the pool of compute nodes created
    "dedicatedNodeCount":"INTEGER",     #The number of dedicated compute nodes to be created in this pool
    "lowPriorityNodeCount":"INTEGER",   #The number of low priority compute nodes to be created in this pool
    "vmSize":"STRING",                  #The string representing the [VM size](https://docs.microsoft.com/en-us/azure/virtual-machines/sizes) to be used
    "vmConfiguration": {
        "imageReference": {             ##The [Virtual Machine image configuration](https://docs.microsoft.com/en-us/azure/virtual-machines/linux/cli-ps-findimage) to be used
            "publisher":"STRING",       #The VM Image publisher string
            "offer":"STRING",           #The VM Image offer description string
            "sku":"STRING",             #The VM Image operation system string
            "version":"STRING"          #The VM Image version string
        },
        "nodeAgentSKUId":"STRING"       #The VM Image Agent SKU ID to be used
    },
    "useEphemeralOSDisk":"BOOL",        #If the VM should use ephemeral OS Disks, can only be used if there are only dedicated nodes
    "nodeStorageContainers": {          #Used to mount storage containers in the compute nodes
      "mount":"BOOL",                   #Specifies if the nodes should mount the following storage containers
      "containers": [                   #A list with all the containers to be mounted
        {
          "name":"STRING",              #The storage container name
          "blobfuseOptions":"STRING"    #The blobfuse options to the container mount procedure
        }
      ]
    },
    "nodeAutoScale": {                  #Used to include auto scale property to the pool
      "include":"BOOL",                 #Specifies if the node should use an auto scale formula
      "evaluationInterval":"INTEGER",   #The autoscale evaluation interval
      "formula": [                      #A list of strings representing the autoscale formula
        "STRING",                       
        "STRING",                       
        "STRING"                        
      ]
    },
    "applications": {                   #Used to include applications on the compute nodes
      "include":"BOOL",                 #Specifies if the compute nodes should install the applications
      "references": [                   #A list of references to the applications to be installed
        {
          "id":"STRING",                #The application ID
          "version":"STRING"            #The application version
        }
      ]
    },
    "startupTask": {                    #Used to include a Startup Task to the compute nodes
      "include":"BOOL",                 #Specifies if the compute nodes should include an startup task
      "command":"STRING"                #The command line of the startup task
    }
  },
  "job": {                              #Used to include the job configurations
    "id":"STRING"                       #The Job ID
  },
  "tasks": {                            #Used to include the tasks configurations
    "addCollectionStep":"INTEGER",      #The number of tasks to be included in each iteration
    "inputs": {
      "areBlobsInInputStorage":"BOOL",              #Specifies if the inputs are to be collected from the input storage, if FALSE an input file should be provided in the execution arguments
      "inputFileExtension":"STRING",                #The file extension of the blobs to be used as inputs
      "outputFileExtension":"STRING",               #The file extension expected to be on the output blobs
      "filterOutExistingBlobInOutputStorage":"BOOL",#Specifies if should remove from input list the blobs that already have their correspondent output blob in the output storage
      "filterOutExistingTaskInCurrentJob":"BOOL",   #Specifies if should remove from input list the blobs that already have a Task assigned with the same input
      "taskSlotFormula": [                          #Used to assign an specific formula to calculate the required task slot of each Task
        "STRING",                                   #This formula should be written using Python syntax, can read any configuration parameter
        "STRING",                                   #using $ before it's name and a dot for each hyerarchical level like '$pool.dedicatedNodeCount'
        "STRING"                                    #has as builtin parameters inputName and inputSize.  
      ],
      "order": {
        "by":"STRING",                              #
        "type":"STRING"                             #
      }
    },
    "resources": {
      "automaticInputsUpload":"BOOL",               #
      "automaticScriptsUpload":"BOOL"               #
    },
    "logs": {
      "automaticUpload":"BOOL",                     #
      "destinationPath":"STRING",                   #
    },
    "outputs": {
      "automaticUpload":"BOOL"                      #
    },
    "command":"STRING",                             #
    "retryCount":"INTEGER",                         #
    "retentionTimeInMinutes":"INTEGER"              #
  },
  "storage": {
    "accountName":"STRING",                         #
    "accountDomain":"STRING",                       #
    "accountSASToken":"STRING",                     #
    "scripts": {
      "container":"STRING",                         #
      "blobPrefix":"STRING"                         #
    },
    "input": {
      "container":"STRING",                         #
      "path":"STRING",                              #
      "blobPrefix":"STRING"                         #
    },
    "output": {
      "container":"STRING",                         #
      "path":"STRING",                              #
      "blobPrefix":"STRING"                         #
    }
  },
  "cleanup": {
    "timeoutInMinutes":"INTEGER"                    #
}
```
