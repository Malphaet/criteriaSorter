#  Test file for fileops.py
import logging
from criteriaSorter.modules import fileops
import pathlib
import os
import pytest
import io
import yaml


class SUPERNONE:
    pass


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
_TEST_ARTIST_FILE_PATH = [
    (_BASE_PATH / "TestArtist  -    Testpicture.jpg", "TestArtist", "Testpicture", 'Artists/{obj.artist}/{obj.name}'),
    (_BASE_PATH / "Testpicture       by  TestArtist.jpg", "TestArtist", "Testpicture", 'Artists/{obj.artist}/{obj.name}'),
    (_BASE_PATH / "Testpicture  by    \t     TestArtist.jpg", "TestArtist", "Testpicture", 'Artists/{obj.artist}/{obj.name}'),
    (_BASE_PATH / "Testpicture  by  TestArtist.jpg", "TestArtist", "Testpicture", 'Artists/{obj.artist}/{obj.name}'),
    (_BASE_PATH / "Testpicture  made with TestArtist.jpg", None, "Testpicture  made with TestArtist", SUPERNONE),
]

_TEST_MOVE_FILE_PATH = [
    (_BASE_PATH / "TestFile.txt", True, "", "TestFile.txt"),
    (_BASE_PATH / "TestFile.txt", False, "", "TestFile.txt"),
]

_FALSE_CONFIG = """
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
"""


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

    # @staticmethod
    # def stat(path):
    #     if pathlib.Path(path) == _BASE_PATH / 'a':
    #         return MockOS.getsize(path)
    #     else:
    #         return MockOS.getsize(path)
    class stat:
        @staticmethod
        def S_ISDIR(path):
            if pathlib.Path(path) == _BASE_PATH / 'a':
                return True
            else:
                return False

        @staticmethod
        def S_ISREG(path):
            if pathlib.Path(path) != _BASE_PATH / 'a':
                return True
            else:
                return False

        @staticmethod
        def S_ISLNK(path):
            return False

        @staticmethod
        def S_ISFIFO(path):
            return False

        @staticmethod
        def S_ISSOCK(path):
            return False

        @staticmethod
        def S_ISBLK(path):
            return False

        @staticmethod
        def S_ISCHR(path):
            return False

        @staticmethod
        def S_ISDOOR(path):
            return False

        @staticmethod
        def S_ISPORT(path):
            return False

        @staticmethod
        def __call__(path):
            if pathlib.Path(path) == _BASE_PATH / 'a':
                return MockOS.getsize(path)
            else:
                return MockOS.getsize(path)

    @staticmethod
    def rename(src, dst):
        if src != dst:
            return True
        return False

    @staticmethod
    def remove(path):
        if "__nonexistent__" in str(path):
            return False
        return True

    @staticmethod
    def dirname(path):
        return pathlib.Path(path).parent

    @staticmethod
    def exists(path):
        if "__nonexistent__" in str(path):
            return False
        return True

    @staticmethod
    def mkdir(path):
        if "__nonexistent__" in str(path):
            return True
        else:
            return False


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
    monkeypatch.setattr(os.path, 'join', MockOS.join)
    monkeypatch.setattr(os.path, 'dirname', MockOS.dirname)
    monkeypatch.setattr(os, 'rename', MockOS.rename)
    monkeypatch.setattr(os.path, 'exists', MockOS.exists)


@pytest.fixture
def a_handler(monkeypatch):
    monkeypatch.setattr(os.path, 'getsize', MockOS.getsize)
    monkeypatch.setattr(os.path, 'isfile', MockOS.isfile)
    monkeypatch.setattr(os.path, 'stat', MockOS.stat)
    monkeypatch.setattr(os.path, 'dirname', MockOS.dirname)
    monkeypatch.setattr(os, 'rename', MockOS.rename)
    monkeypatch.setattr(os.path, 'exists', MockOS.exists)
    monkeypatch.setattr(os, 'mkdir', MockOS.mkdir)
    monkeypatch.setattr(os, 'makedirs', MockOS.mkdir)


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
    assert handler.fills_all_conditions(["is_document", "is_picture"]) is False
    assert handler.fills_all_conditions(["is_bigger_than,10",
                                         "is_bigger_than_mb,0",
                                         "is_smaller_than,100000000",
                                         "is_smaller_than_mb,1000"]) is True


@pytest.mark.parametrize("path, artist, picture, return_pathlike", _TEST_ARTIST_FILE_PATH)
def test_ArtistHandler(caplog, a_handler, path, artist, picture, return_pathlike):
    handler = fileops.ArtistHandler(str(path))
    assert handler.get_artist() == artist
    assert handler.get_file_name_without_artist() == picture
    if artist:
        assert handler.has_artist()
        assert handler.get_file_name_with_artist() == artist + " - " + picture
    else:
        assert not handler.has_artist()
        assert handler.get_file_name_with_artist() == path.name.split(".")[0]

    YAML_FALSE_CONFIG = yaml.load(io.StringIO(_FALSE_CONFIG), Loader=yaml.FullLoader)
    list_conds = [YAML_FALSE_CONFIG[cond] for cond in YAML_FALSE_CONFIG]

    with caplog.at_level(logging.WARNING):
        assert handler.sort(list_conds, default=SUPERNONE) == return_pathlike
        assert handler.future_name == return_pathlike
        if return_pathlike is SUPERNONE:
            assert "default" in caplog.text
            assert handler.future_name is return_pathlike
        else:
            assert "default" not in caplog.text


@pytest.mark.parametrize("path, dry_run, destination, return_pathlike", _TEST_MOVE_FILE_PATH)
def test_FileHandler_move(f_handler, path, dry_run, destination, return_pathlike):
    # Test the move method
    handler = fileops.FileHandler(str(_BASE_PATH / "a"))
    handler.future_name = "{obj.base_name}/{obj.type} - {obj.base_name}.{obj.extension}"
    handler.move(str(_BASE_PATH / "b"), dry_run=dry_run)
    # assert pathlib.Path(handler.get_file_path()) == _BASE_PATH / "b"


def test_ArtistHandler_exception(caplog, a_handler):
    handler = fileops.ArtistHandler(str(_BASE_PATH / "a"), regex=["(?<=\\()[^)*(?=\\)"])
    caplog.set_level(logging.ERROR)
    with caplog.at_level(logging.ERROR):
        handler.guess_artist_and_file_name()
        assert "An error occured while processing regex on" in caplog.text

    YAML_BAD_CONFIG = yaml.load(io.StringIO("""test: no"""), Loader=yaml.FullLoader)
    list_conds = [YAML_BAD_CONFIG[cond] for cond in YAML_BAD_CONFIG]
    with caplog.at_level(logging.ERROR):
        handler.sort(list_conds, default=SUPERNONE)
        assert "No conditions found in condition" in caplog.text
        assert handler.future_name is SUPERNONE


def test_ArtistHandler_exception_2(caplog, a_handler):
    handler = fileops.ArtistHandler(str(_BASE_PATH / "a"), regex=["(?<=\\()[^)*(?=\\)"])
    handler.future_name = None
    with caplog.at_level(logging.DEBUG):
        assert handler.move(str(_BASE_PATH / "b"), dry_run=False) is None
        assert "No future_name found" in caplog.text


def test_ArtistHandler_exception_3(caplog, a_handler):
    handler = fileops.ArtistHandler(str(_BASE_PATH / "a"))
    handler.future_name = "{obj.base_name}/{obj.type} - {obj.base_name}{obj.extension}"
    with caplog.at_level(logging.INFO):
        assert handler.move("__nonexistent__", dry_run=False)
        assert "Creating directory" in caplog.text
