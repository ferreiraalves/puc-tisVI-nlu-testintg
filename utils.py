import os
import config

remove_this = {
    'utlLink',
    '\\'
}

def sanitize_string(string):
    aux = string
    for i in remove_this:
        aux = aux.replace(i, '')
    return aux


def get_files_in_folder(path):
    files = []
    # r=root, d=directories, f = files
    for r, d, f in os.walk(path):
        for i in range(config.n_test):
            files.append(os.path.join(r, f[i]))

    return files