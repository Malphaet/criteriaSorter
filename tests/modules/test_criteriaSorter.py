# Test file for the criteriaSorter module
import io
import os
import logging
import importlib
import pytest
from criteriaSorter.modules import criteriaSorter


_ARGS_LIST = [
    # ("--config=config.yaml"),
    # ("--config=noconf.yaml"),
    # ("--cancel-file=cancel.txt"),
    # ("--cancel-file=nocancel.txt"),
    ("sort . -o testf/"),
    ('-vvvv sort . -o testf/'),
    ('-v sort . -o testf/ -c sort_junk_files'),
]

_EXIT_ARGS_LIST = [
    ("-h", "help"),
    ("--help", "help"),
    ("--version", "criteriaSorter "),
    ('list', "sort_junk"),
    # ('help', "help"),
]

_JUNK_FILE_LIST = """junk
path/to/file4 : path/to/destination4
also/junk"""

_JUNK_RESULT = """[MOVED] path/to/destination4 to path/to/file4"""

_GOOD_FILE_LIST = """
path/to/file1 : path/to/destination1
path/to/file2/. : path/to/destination2
path/to/file3/ : path/to/destination3/.
"""

_GOOD_RESULT = """[MOVED] path/to/destination1 to path/to/file1
[MOVED] path/to/destination2 to path/to/file2/.
[MOVED] path/to/destination3/. to path/to/file3/
"""


@pytest.mark.parametrize("args, outp", _EXIT_ARGS_LIST)
def test_parse_args_exit(args, outp, capsys):
    args = args.split(" ")
    try:
        criteriaSorter.parse_args(args)
    except SystemExit:
        assert outp in capsys.readouterr().out


@pytest.mark.parametrize("args", _ARGS_LIST)
def test_parse_args(args, capsys):
    args = args.split(" ")
    criteriaSorter.parse_args(args)


@pytest.mark.parametrize("vlevel,login,logout", [
                                    ("--silent", logging.ERROR, logging.INFO),
                                    ("", logging.ERROR, logging.WARNING),
                                    ("-v", logging.WARNING, logging.INFO),
                                    ("-vv", logging.INFO, logging.DEBUG),
                                    ("-vvv", logging.DEBUG, logging.NOTSET),
                                    ("--silent -v", logging.CRITICAL, logging.ERROR),
                                    ])
def test_config_log(vlevel, login, logout, caplog):
    if vlevel != "":
        vlevel += " "
    arg = (vlevel+"sort . -o .").split(" ")
    args = criteriaSorter.parse_args(arg)
    criteriaSorter.config_log(args)
    with caplog.at_level(login):
        logging.log(login, "testcap")
        assert "testcap" in caplog.text
        assert caplog.records[0].levelno == login
        if logout:
            logging.log(logout, "testnocap")
            assert "testnocap" not in caplog.text
    logging.shutdown()
    importlib.reload(logging)


def test_action_sort():
    pass


def move(path, dest):
    print("[MOVED] "+str(path.strip())+" to "+str(dest.strip()))
    return True


class falseArg:
    def __init__(self, path):
        self.cancel_file = path
    cancel_file = "nocancel.txt"


@pytest.mark.parametrize("list_of_cancels, result_expected", [
    (io.StringIO(_GOOD_FILE_LIST), _GOOD_RESULT), (io.StringIO(_JUNK_FILE_LIST), _JUNK_RESULT)
])
def test_action_cancel(monkeypatch, list_of_cancels, result_expected, capsys):
    monkeypatch.setattr(os, "rename", move)
    monkeypatch.setattr(os, "remove", move)
    monkeypatch.setattr(os, "rmdir", move)
    monkeypatch.setattr(os.path, "join", lambda a: a)

    with open("cancelfile.txt", "w") as f:
        f.write(list_of_cancels.read())
    criteriaSorter.action_cancel(falseArg("cancelfile.txt"))
    assert result_expected in capsys.readouterr().out


@pytest.mark.parametrize("verbose", [0, 1, 2, 3, 4])
def test_action_list(verbose, capsys):
    args = ["-"+"v"*verbose]+["list"] if verbose else ["list"]
    args = criteriaSorter.parse_args(args)
    criteriaSorter.action_list(args)
    if verbose == 0:
        assert "sort_junk" in capsys.readouterr().out
    else:
        assert "condition" in capsys.readouterr().out


# @pytest.mark.parametrize("args", [["--config=noconf.yaml","list"]])
# def test_action_list_error(args, caplog, monkeypatch):
#
#     with open("noconf.yaml", "w") as f:
#         f.write("Bad config =:/\n+3")
#
#     args = criteriaSorter.parse_args(args)
#     with pytest.raises(SystemExit):
#         with caplog.at_level(logging.ERROR):
#             criteriaSorter.action_list(args)
