import sys
from pathlib import Path
import re
import shutil

sort_path = sys.argv[1]
home = Path.home()

EXTENSIONS = {
    'images': ['jpg', 'png', 'bmp', 'ai', 'psd', 'ico', 'jpeg', 'ps', 'svg', 'tif', 'tiff'],
    'documents': ['pdf', 'txt', 'doc', 'docx', 'rtf', 'tex', 'wpd', 'odt', 'xlsx', 'pptx'],
    'audio': ['mp3', 'wav', 'ogg', 'flac', 'aif', 'mid', 'midi', 'mpa', 'wma', 'wpl', 'cda', 'amr'],
    'video': ['mp4', 'mov', 'avi', 'mkv', 'wmv', '3gp', '3g2', 'mpg', 'mpeg', 'm4v', 'h264', 'flv', 'rm', 'swf', 'vob'],
    'archives': ['zip', 'rar', '7z', 'z', 'gz', 'rpm', 'arj', 'pkg', 'deb', 'tar'],
    'other': []
}

CYRILLIC_SYMBOLS = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюяєіїґ'
TRANSLATION = ("a", "b", "v", "g", "d", "e", "e", "j", "z", "i", "j", "k", "l", "m", "n", "o", "p", "r", "s", "t", "u",
               "f", "h", "ts", "ch", "sh", "sch", "", "y", "", "e", "yu", "u", "ja", "je", "ji", "g")

TRANS = {}
for c, l in zip(CYRILLIC_SYMBOLS, TRANSLATION):
    TRANS[ord(c)] = l
    TRANS[ord(c.upper())] = l.upper()

def normalize(name: str) -> str:
    first_part = name.split('.')[0]
    extension = name.split('.')[1]
    t_name = first_part.translate(TRANS)
    t_name = re.sub(r'\W', '_', t_name)
    final_name = f'{t_name}.{extension}'
    return final_name

def create_folders(folder_path, folder_names):
    for folder in folder_names:
        path_absolute = Path(home, folder_path, folder)
        path_absolute.mkdir(exist_ok=True, parents=True)

create_folders(sort_path, EXTENSIONS)

def sort_files(folder_path, extensions):
    pathes = list(Path(folder_path).rglob( '*.*' ))
    extensions_list = list(extensions.items())
    for path in pathes:
        extension = path.suffix[1:]
        name = path.name
        if not name.startswith('.'):
            for i in range(len(extensions_list)):
                if extension in extensions_list[i][1]:
                    path.rename(Path(home, folder_path, extensions_list[i][0], normalize(name)))
                    break
        if not name.startswith('.') and path.exists():
            path.rename(Path(home, folder_path, extensions_list[-1][0], normalize(name)))

sort_files(sort_path, EXTENSIONS)

def remove_empty_folders(folder_path):
    subfolder_paths = list(Path(folder_path).iterdir())
    for path in subfolder_paths:
        if path.is_dir():
            is_empty = not any(Path(path).iterdir())
            if is_empty:
                path.rmdir()

remove_empty_folders(sort_path)

def handle_archive():
    archives = Path(sort_path, 'archives')
    pathes = list(archives.iterdir())
    for path in pathes:
        folder_name = path.name.split('.')[0]
        folder_for_archive = Path(archives, folder_name)
        folder_for_archive.mkdir(exist_ok=True, parents=True)
        shutil.unpack_archive(str(path), str(folder_for_archive))
    for path in pathes:
        path.unlink()

if Path(sort_path, 'archives').exists():
    handle_archive()

def make_files_list():
    FOLDERS_DICT = {}
    for path in list(Path(sort_path).iterdir()):
        if not path.name.startswith('.'):
            FILES_LIST = []
            EXTENSIONS_LIST = []
            for file in list(path.iterdir()):
                FILES_LIST.append(file.name)
                extension = file.suffix
                ext_exists = extension in EXTENSIONS_LIST
                if not ext_exists:
                    EXTENSIONS_LIST.append(file.suffix)
            FOLDERS_DICT[path.stem] = FILES_LIST
            FOLDERS_DICT[f'{path.stem}-extensions'] = EXTENSIONS_LIST
    print('Files and extensions:', FOLDERS_DICT)

make_files_list()
