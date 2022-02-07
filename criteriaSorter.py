import sys

import yaml
import argparse
import logging
import rich
from fileops import DirectoryHandler, FileHandler, ArtistHandler


if __name__ == '__main__':
    if len(sys.argv) == 1:
        sys.argv.append('--help')
    parser = argparse.ArgumentParser(description='A simple scrip to sort files according to a plethora of criteria.')
    parser.add_argument('folder', help='The folder to sort.')
    parser.add_argument("-o", '--output', help='The output folder.', default=None)
    parser.add_argument('-c', '--operations', help='The specific batch of operations to draw from.', default='default_operations')
    parser.add_argument('--dry-run', help='Dry run.', action='store_true')
    parser.add_argument('-v','--verbose', help='Verbose.', action="count", default=0)
    parser.add_argument('--version', action='version', version='%(prog)s 1.0')
    parser.add_argument('--config', help='The config file.', default='config.yaml')
    # parser.add_argument('--log', help='The log file.', default=None)
    # parser.add_argument('-r', '--recursive', help='Recursive.', action='store_true')
    # parser.add_argument('-f', '--force', help='Force.', action='store_true')
    # parser.add_argument('-e', '--exclude', help='Exclude.', type=str, default='', nargs='+')
    args = parser.parse_args()

    # Set up logging
    _LOG_FORMAT = ' > [%(levelname)s:%(filename)s] - %(message)s'
    if args.verbose == 0:
        logging.basicConfig(level=logging.ERROR, format=_LOG_FORMAT)
    elif args.verbose == 1:
        logging.basicConfig(level=logging.WARNING, format=_LOG_FORMAT)
    elif args.verbose == 2:
        logging.basicConfig(level=logging.INFO, format=_LOG_FORMAT)
    else:
        logging.basicConfig(level=logging.DEBUG, format=_LOG_FORMAT)

    # Load the config file
    with open(args.config, 'r') as stream:
        try:
            config = yaml.load(stream, Loader=yaml.FullLoader)
        except yaml.YAMLError as exc:
            logging.error(exc)
            sys.exit(1)

    # Load the operations
    try:
        if args.operations == "default_operations":
            logging.info("Loading default operations")
            operations_name = config["general"]['default_operations']
        else:
            operations_name = config[args.operation]
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
    directory_handler = DirectoryHandler(args.folder)

    for file in directory_handler.get_files():
        logging.debug("Processing {}".format(file))
        file_handler = Handler(file)
        rich.inspect(file_handler)