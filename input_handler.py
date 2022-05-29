"""
Author: Pablo Viana
Version: 1.0
Created: 2021/12/26

Script to handle the user inputs. Parsing the arguments and dealing with
input queries.
"""
import argparse


def getArguments():
    """
    Parse the script arguments and return them as a SimpleNamespace object
    built up from attributes parsed out of the command line.

    :rtype: `types.SimpleNameSpace`
    :return: the command line attributes on a SimpleNamespace object.
    """
    # Create argument parser
    parser = argparse.ArgumentParser(description='Custom Azure Batch Tasks\n'\
                                     ' Uses Azure Batch Account to execute'\
                                     ' Batch Tasks based on customized'\
                                     ' configurations contained in the'\
                                     ' config.py file. This config file'\
                                     ' specifies the script to be executed,'\
                                     ' the Storage Containers to use, the path'\
                                     ' preffix of the blobs to be used as'\
                                     ' inputs and many other parameters. These'\
                                     ' parameters are used to create the Batch'\
                                     ' Pool, Job and Tasks to run '\
                                     ' asynchronously on the cloud.',
                                     usage= 'python3 %(prog)s [-hxslcderwfy]'\
                                     ' [-i INPUTS] [-j JSON] [-sI] [-sO] [-sS]'\
                                     ' [-sT]')
    # Optional arguments
    parser.add_argument('-x', '--exec', help='start all tasks'\
                        ' execution with parameters contained in the'\
                        ' configuration file.', action='store_true')
    parser.add_argument('-i', '--input', metavar='INPUTS', help='start all tasks'\
                        ' execution with parameters contained in the'\
                        ' configuration file and inputs provided in INPUT file.'\
                        ' if inputs are blobs they must be in the configured'\
                        ' storage input container.',
                        type=argparse.FileType('r'))
    parser.add_argument('-j', '--json', metavar='JSON', help='start all tasks'\
                        ' execution with parameters contained in the'\
                        ' configuration file supplied.', default='config.json',
                        type=argparse.FileType('r'))
    parser.add_argument('-s', '--show', help='start all tasks'\
                        ' execution with parameters contained in the'\
                        ' configuration file.', action='store_true')
    parser.add_argument('-sI', '--show-inputs', help='start all tasks'\
                        ' execution with parameters contained in the'\
                        ' configuration file.', action='store_true')
    parser.add_argument('-sO', '--show-outputs', help='start all tasks'\
                        ' execution with parameters contained in the'\
                        ' configuration file.', action='store_true')
    parser.add_argument('-sS', '--show-scripts', help='start all tasks'\
                        ' execution with parameters contained in the'\
                        ' configuration file.', action='store_true')
    parser.add_argument('-sT', '--show-tasks', help='start all tasks'\
                        ' execution with parameters contained in the'\
                        ' configuration file.', action='store_true')
    parser.add_argument('-dI', '--delete-inputs', help='start all tasks'\
                        ' execution with parameters contained in the'\
                        ' configuration file.', action='store_true')
    parser.add_argument('-l', '--list', help='list tasks by its states.',
                        action='store_true')
    parser.add_argument('-c', '--count', help='count tasks by its states.',
                        action='store_true')

    #Get the list of files for the storage account input container specified in
    #the configuration file.
    #If it's output is already in the output folder it is not included.')
    parser.add_argument('-d', '--disable', help='disable the job and all'\
                        ' associated tasks, returning the tasks that are'\
                        ' running to the end of the execution queue. Cannot'\
                        ' add new task while the Job is disabled.',
                        action='store_true')
    parser.add_argument('-e', '--enable', help='enable the job and all'\
                        ' associated tasks, restarting execution of the tasks'\
                        ' in the queue.', action='store_true')
    parser.add_argument('-r', '--reactivate', help='reactivate all failed' \
                        ' tasks to requeue them.', action='store_true')
    parser.add_argument('-w', '--wait', help='wait all tasks to complete.',
                        action='store_true')
    parser.add_argument('-f', '--free', help='terminate batch and free its'\
                        ' resources (delete all pools, jobs and tasks)',
                        action='store_true')
    parser.add_argument('-y','--yes', help='include it to -f command to'\
                        ' confirm deletion without the need to input yes.',
                        action='store_true')
    # Print version
    parser.add_argument('-v', '--version', action='version',
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


def query_yes_no(question, default=None):
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
