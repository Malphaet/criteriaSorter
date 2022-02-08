# Test file for the criteriaSorter module
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
        vlevel = vlevel + " "
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
