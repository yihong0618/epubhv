"""
Follow these steps to change epub books to vertical or horizontal.

"""
import os
import zipfile
import bs4


def _list_all_epub_in_dir(path):
    files = []                                                                                                                                                                                                                      
    for root, _, filenames in os.walk(path):                                                                                                                                                                                   
        for filename in filenames:                                                                                                                                                                                                  
            files.append(os.path.join(root, filename))         
    return files

class EPUBHV:
    def __init__(self, file_name):
        if os.path.isdir(file_name):
            self.files_list = _list_all_epub_in_dir(file_name)
        elif os.path.isfile(file_name):
            self.files_list = [file_name]
        else:
            raise Exception(f"{file_name}, is not a file or dir")

    def load_one_file(self, epub_file):
        # make a temp dir to ignore the same temp name
        if not os.path.exists("epub_temp_dir"):
            os.mkdir("epub_temp_dir")
        pass

    def extract_one_epub_to_dir(self, epub_file):
        assert epub_file.endswith(".epub"), f"{epub_file} Must be epub file"
        book_path = os.path.join(".epub_temp_dir", "animal_farm")
        if not os.path.exists(".epub_temp_dir"):
            os.mkdir(".epub_temp_dir")
        with zipfile.ZipFile(epub_file) as f:
            f.extractall(book_path)

    def change_epub_to_vertical(self, epub_file):
        pass

    def change_epub_to_horizontal(self, epub_file):
        pass