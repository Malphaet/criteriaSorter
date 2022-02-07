#  Test file for fileops.py

from criteriaSorter.modules import fileops
import pathlib
import os
import pytest


_BASE_PATH = pathlib.Path("/Test/Path")
_LIST_BASE_FILE_PATH = [
    (_BASE_PATH / "TestFile.txt", "document", "is_document"),
    (_BASE_PATH / "TestFile.pdf", "document", "is_document"),
    (_BASE_PATH / "TestFile.doc", "document", "is_document"),
    (_BASE_PATH / "TestFile.jpg", "image", "is_image"),
    (_BASE_PATH / "TestFile.png", "image", "is_picture"),
    (_BASE_PATH / "TestFile.mp3", "music", "is_music"),
    (_BASE_PATH / "TestFile.aiff", "music", "is_audio"),
    (_BASE_PATH / "TestFile.mp4", "video", "is_video"),
    (_BASE_PATH / "TestFile.mpg", "video", "is_video"),
    (_BASE_PATH / "TestFile.unknown_type", None, "is_unknown"),
]


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


@pytest.fixture
def handler(monkeypatch):
    # Using a mock function to test return value
    handler = fileops.DirectoryHandler("/Test/Path")
    monkeypatch.setattr(os, 'listdir', MockOS.listdir)
    monkeypatch.setattr(os.path, 'isdir', MockOS.isdir)
    monkeypatch.setattr(os.path, 'isfile', MockOS.isfile)
    monkeypatch.setattr(os.path, 'getsize', MockOS.getsize)
    monkeypatch.setattr(os.path, 'join', MockOS.join)
    monkeypatch.setattr(os, 'stat', MockOS.stat)
    return handler


@pytest.fixture
def f_handler(monkeypatch):
    # Regular invocation
    monkeypatch.setattr(os.path, 'getsize', MockOS.getsize)
    monkeypatch.setattr(os.path, 'isfile', MockOS.isfile)
    monkeypatch.setattr(os.path, 'stat', MockOS.stat)


def test_DirectoryHandler(handler):
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


@pytest.mark.parametrize("path, expected, method", _LIST_BASE_FILE_PATH)
def test_FileHandler(f_handler, path, expected, method):
    # Test return values

    handler = fileops.FileHandler(str(path))

    assert pathlib.Path(handler.get_file_path()) == path
    assert handler.get_file_name() == path.name
    assert handler.get_file_size() == (1024 * 1024) * 1
    assert handler.get_file_size_in_mb() == 1
    assert handler.get_file_size_in_gb() == 1 / 1024
    assert handler.guess_file_type() == expected
    assert handler.get_extension() == path.suffix
    assert handler.__getattribute__(method)() is True
    assert handler.fills_all_conditions(
        [method, method]
    )
    assert handler.fills_all_conditions(["is_document","is_picture"]) is False
    assert handler.fills_all_conditions(["is_bigger_than,10","is_bigger_than_mb,0","is_smaller_than,100000000","is_smaller_than_mb,1000"]) is True

# def test_FileHandler_exception(f_handler):
#     handler = fileops.FileHandler(str(path))
#     assert f_handler.guess_file_type() is None

# def test_ArticleHandler():
#     handler = fileops.ArtistHandler(".")
