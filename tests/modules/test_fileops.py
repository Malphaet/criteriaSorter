#  Test file for fileops.py

from criteriaSorter.modules import fileops
import pathlib
import os


_BASE_PATH = pathlib.Path("/Test/Path")

class MockOS:
    @staticmethod
    def getsize(path):
        if pathlib.Path(path) == _BASE_PATH / 'a':
            return 2*(1024 * 1024)
        else:
            return 1024 * 1024

    @staticmethod
    def listdir(path):
        if pathlib.Path(path) == _BASE_PATH / 'a':
            return ['b', 'c']
        else:
            return ['a', 'b', 'c']

    @staticmethod
    def path_exists(path):
        if path in [_BASE_PATH / i for i in ['a', 'b', 'c', 'a/b', 'a/c', 'a\\b', 'a\\c']]:
            return True
        return True

    @staticmethod
    def isdir(path):
        if pathlib.Path(path) == _BASE_PATH / 'a':
            return True
        else:
            return False

    @staticmethod
    def isfile(path):
        if pathlib.Path(path) != _BASE_PATH / 'a':
            return True
        else:
            return False

    @staticmethod
    def join(path, *args):
        return pathlib.Path(path).joinpath(*args)

    @staticmethod
    def stat(path):
        if pathlib.Path(path) == _BASE_PATH / 'a':
            return MockOS.getsize(path)
        else:
            return MockOS.getsize(path)


def test_DirectoryHandler(monkeypatch):
    # Regular invocation
    handler = fileops.DirectoryHandler(".")

    # Test regular calls, doen't test the return value
    handler.get_dir_path()
    handler.get_dir_name()
    handler.get_dir_size()
    handler.get_dir_size_in_mb()
    handler.get_dir_size_in_gb()
    assert [f for f in handler.get_files()]
    assert [f for f in handler.get_directories()]
    handler.get_full_list_with_size()

    # Using a mock function to test return value
    handler = fileops.DirectoryHandler("/Test/Path")
    monkeypatch.setattr(os, 'listdir', MockOS.listdir)
    monkeypatch.setattr(os.path, 'isdir', MockOS.isdir)
    monkeypatch.setattr(os.path, 'isfile', MockOS.isfile)
    monkeypatch.setattr(os.path, 'getsize', MockOS.getsize)
    monkeypatch.setattr(os.path, 'join', MockOS.join)
    monkeypatch.setattr(os, 'stat', MockOS.stat)

    # Test return values
    assert pathlib.Path(handler.get_dir_path()) == _BASE_PATH
    assert handler.get_dir_name() == "Path"
    assert handler.get_dir_size() == (1024 * 1024) * 1
    assert handler.get_dir_size_in_mb() == 1
    assert handler.get_dir_size_in_gb() == 1 / 1024
    assert handler.get_full_list() == ["a", "b", "c"]
    assert handler.get_full_list_with_size() == [("a", (1024 * 1024) * 2), ("b", (1024 * 1024) * 1), ("c", (1024 * 1024) * 1)]
    assert handler.get_file_list() == [_BASE_PATH / "b", _BASE_PATH / "c"]
    assert handler.get_directory_list() == ["a"]

# def test_FileHandler():
#     handler = fileops.FileHandler(".")
#
#
# def test_ArticleHandler():
#     handler = fileops.ArtistHandler(".")
