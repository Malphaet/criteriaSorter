#  Test file for fileops.py
from criteriaSorter.modules import fileops


def _mock_get_file_list(dir_path):
    # Mock function for testing
    return ["file1", "file2", "file3"]


def _mock_get_file_list_with_size(dir_path):
    # Mock function for testing
    return [("file1", 1), ("file2", 2), ("file3", 3)]


def test_DirectoryHandler():
    # Regular invocation
    handler = fileops.DirectoryHandler(".")

    # Test regular calls, doen't test the return value
    handler.get_dir_path()
    handler.get_dir_name()
    handler.get_dir_size()
    handler.get_dir_size_in_mb()
    handler.get_dir_size_in_gb()
    [f for f in handler.get_files()]
    [f for f in handler.get_directories()]
    handler.get_file_list_with_size()

    # Using a mock function to test return value
    handler = fileops.DirectoryHandler("/Test/Path")
    handler.get_file_list=_mock_get_file_list
    handler.get_file_list_with_size=_mock_get_file_list_with_size

    # Test return values
    assert handler.get_dir_path() == "/Test/Path"
    assert handler.get_dir_name() == "Path"
    assert handler.get_dir_size() == 6
    assert handler.get_dir_size_in_mb() == 0.06
    assert handler.get_dir_size_in_gb() == 0.00006
    assert handler.get_files() == ["file1", "file2", "file3"]



# def test_FileHandler():
#     handler = fileops.FileHandler(".")
#
#
# def test_ArticleHandler():
#     handler = fileops.ArtistHandler(".")
