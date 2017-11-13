import requests
import os
import shutil


def retrieve_url_as_string(url):
    r = requests.get(url)
    return r.text


__accessibleUrls = {}


def url_is_accessible(url):
    global __accessibleUrls
    if url in __accessibleUrls.keys():
        return __accessibleUrls[url]

    try:
        if requests.get(url).status_code == requests.codes.ok:
            __accessibleUrls[url] = True
            return True
    except:
        __accessibleUrls[url] = False
        return False


def download_file(url, directory='.', filename=None):
    directory = os.path.abspath(os.path.expanduser(directory))

    save_as = filename
    if filename is None:
        save_as = os.path.basename(url)
    save_path = os.path.join(directory, save_as)

    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

    r = requests.get(url, stream=True)
    with open(save_path, 'wb') as f:
        shutil.copyfileobj(r.raw, f)

    return save_path


def create_directory_tree(directory):
    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)


def delete_directory_tree(directory):
    if not os.path.exists(directory):
        return

    shutil.rmtree(directory)