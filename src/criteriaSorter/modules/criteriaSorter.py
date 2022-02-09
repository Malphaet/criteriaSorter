import sys

import rich.pretty
import yaml
import argparse
import logging
import os
import time

from rich.logging import RichHandler
from criteriaSorter.modules.fileops import DirectoryHandler, FileHandler, ArtistHandler


def load_config(config_file):
    """
    Load the config file
    :param config_file: path to the config file
    :return: config (the loaded config)
    """
    with open(config_file, 'r') as stream:
        config = yaml.safe_load(stream)
    return config


def load_operations(operation_to_load, config):
    """
    Load the operations from the config file
    Operations are stored in a dictionary with the key being the operation name
    The operations are the various operations to perform on the files, according to a list of criteria
    :param operation_to_load: the operation to load (string) (default: default_operations)
    :param config: the config file (yaml)
    :return: operations (list of operations)
    """
    try:
        if operation_to_load == "default_operations":
            logging.info("Loading default operations")
            operations_name = config["general"]['default_operations']
        else:
            operations_name = config[operation_to_load]
        operations_config = config["operations"][operations_name]
    except Exception:
        logging.critical("Could not load operations")
        sys.exit(1)
    return operations_config


def load_handler(handler_name):
    """
    Pick the handler to use in the config or raises an error if it does not exist
    :param handler_name: The name of the handler to load
    :return: Handler (the Handler object)
    """
    if handler_name == "FileHandler":
        Handler = FileHandler
    elif handler_name == "ArtistHandler":
        Handler = ArtistHandler
    else:
        logging.critical("Could not load handler "+handler_name)
        sys.exit(1)
    return Handler


def create_handler_list(directory_handler, Handler, config):
    """
    Create a list of handlers for every file in the directory, recursively or not
    :param directory_handler: The directory handler
    :param Handler: The handler to use
    :param config: The config file
    :return: list of handlers for every file in the directory(ies)
    """
    handler_list = []
    for file in directory_handler.get_files():
        try:
            logging.debug("[Handler list] Processing {}".format(file))
            file_handler = Handler(file)
            handler_list.append(file_handler)
        except Exception as e:
            logging.error("[Handler list] Could not load file {}".format(file))
            logging.error(e)
            logging.debug(e, exc_info=True)
            # sys.exit(1)  # Unsure if this is the right thing to do
    if config["general"]["recursive"]:
        # for directory in directory_handler.get_directories():
        #     logging.debug("[Handler list] Processing directory {}".format(directory))
        #     directory_handler = DirectoryHandler(directory)
        #     handler_list.extend(create_handler_list(directory_handler, Handler, operations_config, config))
        pass
    return handler_list


def create_operation_list(operations_config, config):
    """
    Create a list of operations to perform on the files
    :param operations_config: The config file for the operations
    :param config: The general config file
    :return: list of operations to perform on the files
    """
    operation_list = []
    for operation in operations_config["operation_order"].split("\n")[:-1]:
        try:
            logging.debug("[Operation list] Processing operation {}".format(operation))
            operation_list.append(operations_config[operation])
        except Exception as e:
            logging.error("[Operation list] Could not load operation {} : {}".format(operation, e))
            logging.debug(e, exc_info=True)
            # sys.exit(1)  # Unsure if this is the right thing to do
    return operation_list


def execute_sorting(handler_list, operation_list, default_destination, argsp):
    """
    Execute the sorting process on all files
    :param handler_list: The list of handlers to use
    :param operation_list: The list of operations to perform (according to criteria)
    :param default_destination: The default destination for the files (if no operation found)
    :param argsp: The arguments passed to the program
    :return: None
    """
    for handler in handler_list:
        try:
            # rich.inspect(operation_list)
            logging.debug("[File sorting] Processing {}".format(handler.file_name))
            destination = handler.sort(operation_list, default=default_destination)
            logging.debug("[File sorting] {} -> {}".format(handler.file_name, destination))
        except Exception as e:
            logging.error("[File sorting] Could not sort {}".format(handler.file_name))
            logging.error(e)
            logging.debug(e, exc_info=True)


def execute_moves(handler_list, argsp, output_directory):
    list_of_moves = []
    for handler in handler_list:
        try:
            logging.debug("[File moving] Processing {}".format(handler.file_name))
            operation = handler.move(destination=output_directory, dry_run=argsp.dry_run)
            if operation:
                list_of_moves.append(operation)
        except Exception as e:
            logging.error("[File moving] Could not move {}".format(handler.file_name))
            logging.error(e)
            logging.debug(e, exc_info=True)
    return list_of_moves


def write_cancel_file(list_of_operations, output, verbose, dry_run):
    """
    Write the cancel file
    :param list_of_operations: The list of operations to cancel
    :param output: The output file to write to
    :param verbose: The verbosity of the program
    :param dry_run: Whether the program is in dry run mode
    :return: None
    """
    if not dry_run and len(list_of_operations) > 0 or verbose > 3:
        logging.info("Writing cancel file...")
        with open(output, "w", encoding="utf-8") as f:
            for origin, destination in list_of_operations:
                f.write("{} : {}\n".format(origin, destination))
            logging.info("Written " + output)


def action_sort(argsp):
    """
    Sort the files
    :param argsp: the arguments passed to the program
    :return: None
    """
    # Load the config file
    config = load_config(argsp.config)

    # Load the operations
    operations_config = load_operations(argsp.operations, config)

    # Pick the right handler
    Handler = load_handler(config["general"]["handler"])

    # Create the DirectorySorter
    directory_handler = DirectoryHandler(argsp.folder)

    # Get the list of Handler from the directory
    handler_list = create_handler_list(directory_handler, Handler, config)

    # Get the action to perform on each file from the handler and the operations
    operation_list = create_operation_list(operations_config, handler_list)

    # Find the default destination
    if "default_destination" in operations_config:
        default_destination = operations_config["default_destination"]["destination"]
    else:
        default_destination = None

    # Sort the files
    execute_sorting(handler_list, operation_list, default_destination, argsp)

    # Move the files
    list_of_moves = execute_moves(handler_list, argsp, default_destination)

    # Write a cancel file
    write_cancel_file(list_of_moves, os.path.join(argsp.output, argsp.cancel_file), argsp.verbose, argsp.dry_run)

    logging.info("All operations done")


def action_list(argsp):
    """
    List the sorting operations
    :param argsp: the arguments passed to the program
    :return: None
    """
    try:
        logging.info("Listing operations")
        with open(argsp.config, 'r') as stream:
            config = yaml.safe_load(stream)
        if argsp.verbose:
            rich.print(config["operations"])
        else:
            for line in config["operations"].keys():
                rich.print(line)
    except TypeError:
        logging.critical("No operations found in config file {}".format(argsp.config))
        sys.exit(1)
    except FileNotFoundError:
        logging.critical("Config {} file not found".format(argsp.config))
        sys.exit(1)

# def action_help(argsp):
#     if argsp:
#         parser.parse_args(['-h'])  # This will print the help


def action_cancel(argsp):
    """
    Cancel the operations done by the program, given a cancel file
    :param argsp: The arguments passed to the program
    :return: None
    """
    with open(os.path.join(argsp.cancel_file), "r") as f:
        for line in f:
            try:
                origin, destination = line.split(" : ")
                os.rename(destination, origin)
            except Exception as e:
                logging.error("Could not cancel {}".format(line))
                logging.error(e)
                logging.debug(e, exc_info=True)


_LIST_ACTIONS = {
    "sort": action_sort,
    # "help": action_help,
    "list": action_list,
    "cancel": action_cancel,
}


def config_log(argsp):
    """
    Configure the logging
    :param argsp: The arguments passed to the program
    :return: None
    """
    # Set up logging
    # _LOG_FORMAT = ' > [%(levelname)s:%(filename)s] - %(message)s'
    _LOG_FORMAT = '%(message)s'
    if argsp.silent:
        logging.basicConfig(level=logging.CRITICAL, format=_LOG_FORMAT)
    elif argsp.verbose == 0:
        logging.basicConfig(level=logging.ERROR, format=_LOG_FORMAT, handlers=[RichHandler()])
    elif argsp.verbose == 1:
        logging.basicConfig(level=logging.WARNING, format=_LOG_FORMAT, handlers=[RichHandler()])
    elif argsp.verbose == 2:
        logging.basicConfig(level=logging.INFO, format=_LOG_FORMAT, handlers=[RichHandler()])
    else:
        logging.basicConfig(level=logging.DEBUG, format=_LOG_FORMAT, handlers=[RichHandler()])


def parse_args(argvp):
    """
    Parse the arguments passed to the program
    :param argvp: The arguments passed to the program
    :return: argsp: The arguments, parsed as an object
    """
    if len(argvp) == 1:
        sys.argv.append('--help')

    # Parse arguments
    parser = argparse.ArgumentParser(description='A simple scrip to sort files according to a plethora of criteria.',
                                     prog='criteriaSorter')
    parser.add_argument('-v', '--verbose', help='Verbose.', action="count", default=0)
    parser.add_argument('-s', '--silent', help='Silent.', action="store_true", default=False)
    parser.add_argument('--version', action='version', version='%(prog)s 1.0')
    parser.add_argument('--config', help='The config file.', default='config.yaml')
    # parser.add_argument('--log', help='The log file.', default=None)
    # parser.add_argument('-r', '--recursive', help='Recursive.', action='store_true')
    # parser.add_argument('-f', '--force', help='Force.', action='store_true')
    # parser.add_argument('-e', '--exclude', help='Exclude.', type=str, default='', nargs='+')
    parser.add_argument("--cancel_file", help="The file to cancel the operation.", default="cancel_{}.txt".format(time.time()))

    subparsers = parser.add_subparsers(dest='action')
    parser_sort = subparsers.add_parser('sort', help='Sort files according to criteria')
    subparsers.add_parser('list', help='List criteria')  # parser_list
    # parser_help = subparsers.add_parser('help', help='Show help')
    subparsers.add_parser('cancel', help='Cancel')  # parser_cancel
    parser_sort.add_argument('folder', help='The folder to sort.')
    parser_sort.add_argument("-o", '--output', help='The output folder.', default=".")
    parser_sort.add_argument('-c', '--operations', help='The specific batch of operations to draw from.',
                             default='default_operations')
    parser_sort.add_argument('--dry-run', help='Dry run.', action='store_true')

    args = parser.parse_args(argvp)
    return args


def main(argvp):
    """
    Main function, called by __main__
    :return: None
    """
    # Parse arguments
    args = parse_args(argvp)

    # Configure logging
    config_log(args)

    # Execute the action
    _LIST_ACTIONS[args.action](args)
