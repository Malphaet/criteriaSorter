import yaml
import argparse
import logging
import rich


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='A simple scrip to sort files according to a plethora of criteria.')
    parser.add_argument('-f', '--folder', help='The folder to sort.', required=True)
    parser.add_argument('-o', '--output', help='The output folder.', required=True)
    parser.add_argument('-c', '--operation', help='The specific batch of operations to draw from.', default='default')
    parser.add_argument('--dry-run', help='Dry run.', action='store_true')
    parser.add_argument('--verbose', help='Verbose.', action='store_true')
    parser.add_argument('--debug', help='Debug.', action='store_true')
    parser.add_argument('--version', action='version', version='%(prog)s 1.0')
    parser.add_argument('--help', action='help', help='Show this help message and exit.')
    parser.add_argument('--config', help='The config file.', default='config.yaml')
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.INFO)
    elif args.debug:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.WARNING)

    # Load the config file
    with open(args.config, 'r') as stream:
        try:
            config = yaml.load(stream)
        except yaml.YAMLError as exc:
            logging.error(exc)

    # Load the operations ? what is this?
    with open(config['operations'][args.operation], 'r') as stream:
        try:
            operations = yaml.load(stream)
        except yaml.YAMLError as exc:
            logging.error(exc)

    rich.inspect(operations)
    rich.inspect(config)
    rich.inspect(args)
    rich.inspect(config['operations'][args.operation])
    rich.inspect(config['operations'][args.operation]['operations'])