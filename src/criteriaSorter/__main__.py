from criteriaSorter.modules import criteriaSorter
import sys


# pragma: nocover  # The main call can't be covered because it will only execute through the CLI
if __name__ == "__main__":
    if len(sys.argv) > 1:
        criteriaSorter.main(sys.argv[1:])
    else:
        criteriaSorter.main(("-h",))
    sys.exit(0)
