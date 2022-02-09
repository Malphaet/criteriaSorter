# Test file for the criteriaSorter module
import io
import os
import logging
import importlib
import pytest
from criteriaSorter.modules import criteriaSorter
import tempfile


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


def cldl(*l_file):
    for f in l_file:
        f.close()
        os.remove(f.name)


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
    cancel_file = tempfile.NamedTemporaryFile(mode="w+", suffix=".txt", delete=False)
    monkeypatch.setattr(os, "rename", move)
    # monkeypatch.setattr(os, "remove", move)
    monkeypatch.setattr(os, "rmdir", move)
    monkeypatch.setattr(os.path, "join", lambda a: a)

    with open(cancel_file.name, "w") as f:
        f.write(list_of_cancels.read())
    criteriaSorter.action_cancel(falseArg(cancel_file.name))
    assert result_expected in capsys.readouterr().out

    cldl(cancel_file)

@pytest.mark.parametrize("verbose", [0, 1, 2, 3, 4])
def test_action_list(verbose, capsys):
    args = ["-"+"v"*verbose]+["list"] if verbose else ["list"]
    args = criteriaSorter.parse_args(args)
    criteriaSorter.action_list(args)
    if verbose == 0:
        assert "sort_junk" in capsys.readouterr().out
    else:
        assert "condition" in capsys.readouterr().out


@pytest.mark.parametrize("args, error", [
    [["--config=noconf.yaml", "list"], "No operations found"],
    [["--config=unexisting_conf", "list"], "Config unexisting_conf file not found"],
])
def test_action_list_error(args, error,  caplog, monkeypatch):
    no_conf = tempfile.NamedTemporaryFile(mode="w+t", delete=False)
    with open(no_conf.name, "w") as f:
        f.write("Bad config =:/\n+3")

    args = criteriaSorter.parse_args(args)
    with pytest.raises(SystemExit):
        with caplog.at_level(logging.ERROR):
            criteriaSorter.action_list(args)
            assert error in caplog.text
    cldl(no_conf)

def test_load_config():
    good_conf = tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False)
    with open(good_conf.name, "w") as f:
        f.write("""test:
    - path: path/to/file1
                """)

    assert criteriaSorter.load_config(good_conf.name) == {"test": [{"path": "path/to/file1"}]}
    cldl(good_conf)


def test_load_config_error():
    bad_conf = tempfile.NamedTemporaryFile(suffix=".yaml", delete=False)
    good_conf = tempfile.NamedTemporaryFile(suffix=".yaml", delete=False)

    with open(bad_conf.name, "w") as f:
        f.write("""test:
    - path: path/to/file1
      condition:
        - path: path/to/file1
                """)

    with open(good_conf.name, "w") as f:
        f.write("""operations:
  sort_junk_folder:
    operation_order: |
      operation1
      operation2
      operation3
      operation4
    operation1:
      conditions : |
        has_artist
        is_image
      destination : Artists/{obj.artist}/{obj.name}
    operation2:
      conditions : |
        is_video
      destination : vids/{obj.name}
    operation3:
      conditions : |
        is_audio
      destination : audios/{obj.name}
    operation4:
      conditions : |
        is_document
      destination : others/{obj.name}
""")

    with pytest.raises(SystemExit):
        conf = criteriaSorter.load_config(bad_conf.name)
        criteriaSorter.load_operations("default_operation", conf)

    cldl(good_conf, bad_conf)