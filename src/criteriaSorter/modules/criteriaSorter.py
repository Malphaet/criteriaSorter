import sys

import yaml
import argparse
import logging
import os
import time
import rich
from rich.logging import RichHandler
from criteriaSorter.modules.fileops import DirectoryHandler, FileHandler, ArtistHandler


def action_sort(argsp):
    # Load the config file
    with open(argsp.config, 'r') as stream:
        try:
            config = yaml.load(stream, Loader=yaml.FullLoader)
        except yaml.YAMLError as exc:
            logging.error(exc)
            sys.exit(1)

    # Load the operations
    try:
        if argsp.operations == "default_operations":
            logging.info("Loading default operations")
            operations_name = config["general"]['default_operations']
        else:
            operations_name = config[argsp.operation]
        operations_config = config["operations"][operations_name]
    except Exception:
        logging.error("Could not load operations")
        sys.exit(1)

    # Pick the right handler
    if config["general"]["handler"] == "FileHandler":
        Handler = FileHandler
    elif config["general"]["handler"] == "ArtistHandler":
        Handler = ArtistHandler
    else:
        logging.error("Could not load handler "+config["general"]["handler"])
        sys.exit(1)

    # Create the DirectorySorter
    directory_handler = DirectoryHandler(argsp.folder)

    # Get the list of Handler from the directory
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

    # Get the action to perform on each file from the handler and the operations
    operation_list = []
    for operation in operations_config["operation_order"].split("\n")[:-1]:
        try:
            logging.debug("[Operation list] Processing operation {}".format(operation))
            operation_list.append(operations_config[operation])
        except Exception as e:
            logging.error("[Operation list] Could not load operation {} : {}".format(operation, e))
            logging.debug(e, exc_info=True)
            # sys.exit(1)  # Unsure if this is the right thing to do

    # Find the default destination
    if "default_destination" in operations_config:
        default_destination = operations_config["default_destination"]["destination"]
    else:
        default_destination = None

    # Sort the files
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

    # Move the files
    list_of_operations = []
    for handler in handler_list:
        try:
            logging.debug("[File moving] Processing {}".format(handler.file_name))
            operation = handler.move(destination=argsp.output, dry_run=argsp.dry_run)
            if operation:
                list_of_operations.append(operation)
        except Exception as e:
            logging.error("[File moving] Could not move {}".format(handler.file_name))
            logging.error(e)
            logging.debug(e, exc_info=True)

    # Write a cancel file
    if not argsp.dry_run and len(list_of_operations) > 0 or argsp.verbose > 3:
        logging.info("Writing cancel file...")
        with open(os.path.join(argsp.output, argsp.cancel_file), "w", encoding="utf-8") as f:
            for origin, destination in list_of_operations:
                f.write("{} : {}\n".format(origin, destination))
            logging.info("Written " + argsp.cancel_file)

    logging.info("Done")


def action_list(argsp):
    logging.info("Listing operations")
    with open(argsp.config, 'r') as stream:
        try:
            config = yaml.load(stream, Loader=yaml.FullLoader)
        except yaml.YAMLError as exc:
            logging.error(exc)
            sys.exit(1)
    if argsp.verbose:
        rich.print(config["operations"])
    else:
        for line in config["operations"].keys():
            print(line)


# def action_help(argsp):
#     if argsp:
#         parser.parse_args(['-h'])  # This will print the help


def action_cancel(argsp):
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
    # Set up logging
    # _LOG_FORMAT = ' > [%(levelname)s:%(filename)s] - %(message)s'
    _LOG_FORMAT = '%(message)s'
    if argsp.verbose == 0:
        logging.basicConfig(level=logging.ERROR, format=_LOG_FORMAT, handlers=[RichHandler()])
    elif argsp.verbose == 1:
        logging.basicConfig(level=logging.WARNING, format=_LOG_FORMAT, handlers=[RichHandler()])
    elif argsp.verbose == 2:
        logging.basicConfig(level=logging.INFO, format=_LOG_FORMAT, handlers=[RichHandler()])
    else:
        logging.basicConfig(level=logging.DEBUG, format=_LOG_FORMAT, handlers=[RichHandler()])


def parse_args(argvp):
    if len(argvp) == 1:
        sys.argv.append('--help')

    # Parse arguments
    parser = argparse.ArgumentParser(description='A simple scrip to sort files according to a plethora of criteria.')
    parser.add_argument('-v', '--verbose', help='Verbose.', action="count", default=0)
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
    parser_sort.add_argument('-c', '--operations', help='The specific batch of operations to draw from.', default='default_operations')
    parser_sort.add_argument('--dry-run', help='Dry run.', action='store_true')

    args = parser.parse_args()
    return args


def main(argvp):
    """
    Main function
    :return:
    """
    # Parse arguments
    args = parse_args(argvp)

    # Configure logging
    config_log(args)

    # Execute the action
    _LIST_ACTIONS[args.action](args)
