#  Test file for fileops.py
from criteriaSorter.modules import fileops


def test_DirectoryHandler():
    handler = fileops.DirectoryHandler(".")


def test_FileHandler():
    handler = fileops.FileHandler(".")


def test_ArticleHandler():
    handler = fileops.ArtistHandler(".")
