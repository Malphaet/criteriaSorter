# All operation related to file and directory

import os
import re

EXTENTION_BY_TYPE = {
    'image': ["jpg", "jpeg", "png", "gif", "bmp", "tiff", "tif"],
    'video': ["mp4", "avi", "mkv", "mov", "flv", "wmv", "mpg", "mpeg", "m4v", "3gp", "3g2"],
    'music': ["mp3", "wav", "wma", "ogg", "flac", "aac", "m4a"],
    'document': ["doc", "docx", "xls", "xlsx", "ppt", "pptx", "pdf", "txt", "rtf", "odt", "ods", "odp", "odg", "odf", "odc", "odb", "csv", "tsv", "html", "htm", "css", "js", "json", "xml", "yml", "yaml", "java", "py", "c", "cpp", "h", "hpp", "hxx", "h++", "cs", "php", "sql", "log", "md", "markdown", "rst", "tex", "latex", "bib", "bibtex"]
}

TYPE_BY_EXTENTION = {}
for i, j in EXTENTION_BY_TYPE.items():
    for k in j:
        TYPE_BY_EXTENTION[k] = i


class DirectoryHandler:
    def __init__(self, dir_path):
        self.dir_path = dir_path

    def get_dir_path(self):
        return self.dir_path

    def get_dir_name(self):
        return os.path.basename(self.dir_path)

    def get_dir_size(self):
        return os.path.getsize(self.dir_path)

    def get_dir_size_in_mb(self):
        return self.get_dir_size() / (1024 * 1024)

    def get_dir_size_in_gb(self):
        return self.get_dir_size() / (1024 * 1024 * 1024)

    def get_file_list(self):
        return os.listdir(self.dir_path)

    def get_file_list_with_size(self):
        file_list = self.get_file_list()
        file_list_with_size = []
        for file in file_list:
            file_path = os.path.join(self.dir_path, file)
            file_list_with_size.append((file, os.path.getsize(file_path)))
        return file_list_with_size


class FileHandler:
    def __init__(self, file_path):
        self.file_path = file_path
        self.file_name = os.path.basename(file_path)
        self.name, self.extension = os.path.splitext(self.file_name)

    def get_file_path(self):
        return self.file_path

    def get_file_name(self):
        return self.file_name

    def get_extension(self):
        return os.path.splitext(self.file_name)[1]

    def guess_file_type(self):
        return TYPE_BY_EXTENTION.get(self.get_extension())

    def is_image(self):
        return self.guess_file_type() == 'image'

    def is_video(self):
        return self.guess_file_type() == 'video'

    def is_music(self):
        return self.guess_file_type() == 'music'

    def is_document(self):
        return self.guess_file_type() == 'document'



class ArtistHandler(FileHandler):
    def __init__(self, file_path):
        super().__init__(file_path)
        self.artist, self.file_name = self.guess_artist_and_file_name()

    def guess_artist_and_file_name(self):
        """Try to guess artist from file name"""
        regex = [
            r"?(?P<artist>[^-]+)-(?P<file_name>.+)$",
            r"?(?P<file_name>.+) by (?P<artist>.+)$",
            r"?(?P<artist>.+)_(?P<file_name>.+)$",
        ]
        for r in regex:
            m = re.match(r, self.file_name)
            if m:
                return m.group("artist"), m.group("file_name")
        return None, self.file_name

    def get_artist(self):
        return self.artist

    def has_artist(self):
        return self.artist is not None

    def get_file_name_without_artist(self):
        return self.file_name

    def get_file_name_with_artist(self):
        if self.has_artist():
            return "{} - {}".format(self.artist, self.file_name)
        return self.file_name

