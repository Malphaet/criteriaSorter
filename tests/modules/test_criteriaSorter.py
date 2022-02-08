# Test file for the criteriaSorter module
import pytest
from criteriaSorter.modules import criteriaSorter


_ARGS_LIST = [
    # ("--config=config.yaml"),
    # ("--config=noconf.yaml"),
    # ("--cancel-file=cancel.txt"),
    # ("--cancel-file=nocancel.txt"),
    ("sort . -o testf/"),
    ('sort -vvvv . -o testf/'),
    # ('sort -vvvv . -o testf/ -c sort_junk_files'),
]

_EXIT_ARGS_LIST = [
    ("-h", "help"),
    ("--help", "help"),
    ("--version", "version"),
    # ('list', "sort"),
    # ('help'),
]


@pytest.mark.parametrize("args, outp", _EXIT_ARGS_LIST)
def test_parse_args_exit(args, outp, capsys):
    args = args.split(" ")
    with pytest.raises(SystemExit):
        criteriaSorter.parse_args(args)
        assert outp in capsys.readouterr().out


# @pytest.mark.parametrize("args", _ARGS_LIST)
# def test_parse_args(args,capsys):
#     args = args.split(" ")
#     criteriaSorter.parse_args(args)


def test_action_sort():
    pass
