# ACT - Azure Custom Tasks - A tool to rapidly create custom tasks for the Microsoft Azure Batch service

## About

Act is software tool developed using Python v3.6 that can be used to readly allow the creation and execution of parallelized tasks using the Microsoft Azure Batch service. This tool is perfect for newcomers to the Microsoft Azure environment, that promptly need to take advantage of the parallellization of their tasks and even for more advanced users to fasten the deployment and make their tasks less error prone, since it's highly reusable and minimizes the code that needs to be done, it also has a builtin log feature to help you to easily keep track of the task events.

## Usage

```bash
python3 azure_custom_tasks.py [-j JSON] [-i INPUT] [-hxlcedwfyvs] [-sI] [-sO] [-sS] [-sT]
```

Act uses the configured Azure Batch Account to execute Batch Tasks based on customized configurations contained in a config.json file. This file specifies the script to be executed, the Storage Containers to use, the string prefix of the blobs to be used as inputs and many other parameters. These parameters are used to create the Batch Pool, Job and Tasks to run asynchronously on the Microsoft Azure Cloud.

### OPTIONAL ARGUMENTS

This Section explains in detail the possible arguments used with the Act program, all arguments are optional and if not provided consider the default value:

- **-j or --json** : uses the specified JSON file as the configuration file. This file must be in the .json format and contain all the required configuration strings. If this parameter is not provided, the **default** is to consider the existence of a config.json in the current working directory, if it doesn't exist the program finishes with an error message. **You cannot run Act without a configuration file.** This file and all it's configuration parameters are explained in its corresponding [section] ()
- **-i or --input** : uses the strings in the specied INPUT file as inputs for each task created. It's expected that each line contain one input description separated by comma, being the first string the input itself, the second the input size and the third the required task slots for this input, **only the first parameter is required, the input string itself, the other parameters are optional with default value 0 and 1 respectively**. This can be understood in more detail in the examples.
- **-x or --exec** : start the batch service Pool, Job and tasks execution with the parameters specified in the configuration file. If no other argument  is supplied **(other then -j and -i)** this is considered the **default behavior of Act**.
- **-s or --show** : show the blobs from the configured containers: input, output and scripts and the tasks commandLine attribute.
- **-sI or --show-inputs** : show the blobs from the configured container input.
- **-sO or --show-outputs** : show the blobs from the configured container output.
- **-sS or --show-scripts** : show the blobs from the configured container scripts.
- **-sT or --show-tasks** : show the task's commandLine for each task.
- **-l or --list** : list tasks by their states.
- **-c or --count** : count tasks by their states.
- **-d or --disable** : disable the current Job and all associated tasks, returning the tasks that are running to the end of the execution queue. Cannot add new tasks while the Job is disabled.
- **-e or --enable** : enable the current Job and all associated tasks, restarting the tasks in the execution queue.
- **-w or --wait** : wait all tasks to complete and show the current progress.
- **-f or --free** : terminate the batch and free its resources (deleting all pools, jobs and tasks).
- **-y or --yes** : include this to -f command to confirm deletion without requering to input yes.
- **-v or --version** : show program's version number and exit.
- **-h or --help** : show the help message and exit.

### THE config.json FILE

The most important part of using **Act** is the use of the configuration file. This file must contain all the details of the tasks that you need to execute. This will provide the easy customization and at the same time an easy use of most features of the Microsoft Azure Batch services.

This file contains a few required configuration string and many optional string, bellow is a description of the existing configuration string for the current version of this tool:

**OBS.: The comments were added to clarify each configuration string by they are not valid in the .json format.**

```json
{  "batch": {
    "accountName":"STRING",             #The name of the batch account on your Azure Subscription, that you want to use
    "accountKey":"STRING",              #The corresponding batch account key, found in the Azure portal
    "accountUrl":"STRING"               #The corresponding batch account url, found in the Azure portal
  },
  "pool": {
    "id":"STRING",                      #The ID that you want to use, to the computing nodes pool you are going to create
    "dedicatedNodeCount":"INTEGER",     #The
    "lowPriorityNodeCount":"INTEGER",   #
    "vmSize":"STRING",                  #
    "vmConfiguration": {
        "imageReference": {
            "publisher":"STRING",       #
            "offer":"STRING",           #
            "sku":"STRING",             #
            "version":"STRING"          #
        },
        "nodeAgentSKUId":"STRING"       #
    },
    "useEphemeralOSDisk":"BOOL",        #
    "nodeStorageContainers": {
      "mount":"BOOL",                   #
      "containers": [
        {
          "name":"STRING",              #
          "blobfuseOptions":"STRING"    #
        }
      ]
    },
    "nodeAutoScale": {
      "include":"BOOL",                 #
      "evaluationInterval":"INTEGER",   #
      "formula": [                      #
        "STRING",                       #
        "STRING",                       #
        "STRING"                        #
      ]
    },
    "applications": {
      "include":"BOOL",                 #
      "references": [
        {
          "id":"STRING",                #
          "version":"STRING"            #
        }
      ]
    },
    "startupTask": {
      "include":"BOOL",                 #
      "command":"STRING"                #
    }
  },
  "job": {
    "id":"STRING"                       #
  },
  "tasks": {
    "addCollectionStep":"INTEGER",      #
    "inputs": {
      "areBlobsInInputStorage":"BOOL",              #
      "inputFileExtension":"STRING",                #
      "outputFileExtension":"STRING",               #
      "filterOutExistingBlobInOutputStorage":"BOOL",#
      "filterOutExistingTaskInCurrentJob":"BOOL",   #
      "taskSlotFormula": [                          #
        "STRING",                                   #
        "STRING",                                   #
        "STRING"                                    #
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
