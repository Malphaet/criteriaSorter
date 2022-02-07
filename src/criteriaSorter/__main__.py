from criteriaSorter.modules import criteriaSorter
import sys


# pragma: nocover  # The main call can't be covered because it will only execute through the CLI
if __name__ == "__main__":
    criteriaSorter.main(sys.argv)
    sys.exit(0)