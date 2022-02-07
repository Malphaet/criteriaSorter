# All operation related to file and directory
import logging
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

    def get_files(self):
        for file in self.get_file_list():
            fullname = os.path.join(self.dir_path, file)
            if os.path.isfile(fullname):
                yield fullname

    def get_directories(self):
        for file in self.get_file_list():
            if os.path.isdir(os.path.join(self.dir_path, file)):
                yield file

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
        self.dir_path = os.path.dirname(file_path)
        self.name = self.file_name
        self.base_name, self.extension = os.path.splitext(self.file_name)
        self.type = self.guess_file_type()
        self.future_name = None  # Do a no operation

    def get_file_path(self):
        return self.file_path

    def get_file_name(self):
        return self.file_name

    def get_extension(self):
        return os.path.splitext(self.file_name)[1]

    def guess_file_type(self):
        try:
            return TYPE_BY_EXTENTION[self.extension[1:]]
        except KeyError:
            return None

    def is_image(self):
        return self.guess_file_type() == 'image'

    def is_picture(self):
        return self.is_image()

    def is_video(self):
        return self.guess_file_type() == 'video'

    def is_music(self):
        return self.guess_file_type() == 'music'

    def is_audio(self):
        return self.is_music()

    def is_document(self):
        return self.guess_file_type() == 'document'

    def fills_all_conditions(self, list_functions):
        for function in list_functions:
            if not self.__getattribute__(function)():
                return False
        return True

    def sort(self, list_of_condition_dicts, default=None):
        for condition in list_of_condition_dicts:
            if self.fills_all_conditions(condition['conditions'].split('\n')[:-1]):
                self.future_name = condition['destination']
                return self.future_name
        logging.warning("The file {} doesn't meet any criteria, reverting to default".format(self.file_name))
        self.future_name = default
        return default

    def move(self, destination=".", dry_run=False):
        if dry_run:
            dry_run_message = ' > [dry] '
        else:
            dry_run_message = ''

        if self.future_name is None:
            logging.debug('No future_name found for file: ' + self.file_name)  # This is a no-op
            return
        destination = os.path.join(destination, self.future_name.format(obj=self))
        destination_dir = os.path.dirname(destination)
        if not os.path.exists(destination_dir):
            logging.info(dry_run_message+'Creating directory: ' + destination_dir)
            if not dry_run:
                os.makedirs(destination_dir)

        logging.info(dry_run_message+'Moving file: ' + self.name + ' to: ' + destination)
        if not dry_run:
            os.rename(self.file_path, destination)
        return self.file_path, destination


class ArtistHandler(FileHandler):
    def __init__(self, file_path):
        super().__init__(file_path)
        self.artist, self.file_name = self.guess_artist_and_file_name()

    def guess_artist_and_file_name(self):
        """Try to guess artist from file name"""
        regex = [
            r"(?P<file_name>.+) by (?P<artist>.+)$",
            r"(?P<artist>[^-]+)-(?P<file_name>.+)$",
            # r"(?P<artist>.+)_(?P<file_name>.+)$",
        ]
        try:
            for r in regex:
                m = re.match(r, self.file_name)
                if m:
                    return m.group("artist").rstrip(" "), m.group("file_name").lstrip(" ")
            return None, self.file_name
        except re.error as e:
            logging.error("An error occured while processing regex on " + self.file_name)
            logging.error(e)
            logging.info("", exc_info=True)
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
