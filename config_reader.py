"""
Author: Pablo Viana
Version: 1.0
Created: 2022/02/03

Script to read the configuration file and the corresponding storage containers
and the input list.
"""
import copy
import json
import random
from types import SimpleNamespace
import azure.storage.blob as blobstorage


class ConfigurationReader():

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

        # update the configuration with new attributes for storage sas url
        i = self.config.storage.input
        o = self.config.storage.output
        s = self.config.storage.scripts
        self.config.input_container_url = self.get_sas_url(i.container)
        self.config.output_container_url = self.get_sas_url(o.container)
        self.config.scripts_container_url = self.get_sas_url(s.container)

        # creates calculteTaskSlots function
        self.calculateTaskSlots = self.createFunctionCalculateTaskSlots()

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


    def createFunctionCalculateTaskSlots(self):
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
                    "%s",
                    "    return requiredSlots"]
        code = '\n'.join(template) % statements

        # allowed builtin functions that can be used in the formulas
        safe_list = ['abs', 'all', 'any', 'bin', 'bool', 'chr', 'float', 'str',
                     'hash', 'int', 'len', 'max', 'min', 'ord', 'range', 'sum',
                     'reversed', 'round', 'sorted', 'filter', 'format']
        builtins = globals()['__builtins__']
        my_global_scope = dict([ (k, builtins[k]) for k in safe_list ])

        # remove any other builtin function from the used scope
        my_global_scope['__builtins__'] = None
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
                    item_size = item[1]
                if len(item) > 2:
                    item_slot = item[2]
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


    def deleteConfigInputBlobs(self):
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
