import json
import re
import requests
import os
import shutil
from cachecontrol import CacheControl
from cachecontrol.caches.file_cache import FileCache


DBG_CACHED_DOWNLOAD = False  # for tests only. True = cache downloaded files. Used for test case performance improvement

__STORED_SESSION = None
CACHE_DIR = os.path.expanduser('~/.thread_files/cache')


def get_stored_session():
    global __STORED_SESSION
    create_directory_tree(CACHE_DIR)

    if __STORED_SESSION is None:
        __STORED_SESSION = CacheControl(requests.Session(), cache=FileCache(CACHE_DIR))
    return __STORED_SESSION


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


def download_file(url, directory='.', filename=None, overwrite=False, silent=False):
    directory = os.path.abspath(os.path.expanduser(directory))

    save_as = filename
    if filename is None:
        save_as = os.path.basename(url)
    save_path = os.path.join(directory, save_as)

    if os.path.exists(save_path) and not overwrite:
        raise FileExistsError('Overwrite is disabled, and {} already exists!'.format(save_path))

    if not os.path.exists(directory):
        os.makedirs(directory, exist_ok=True)

    if DBG_CACHED_DOWNLOAD:
        r = get_stored_session().get(url, stream=True)
    else:
        # On release: Do not cache file downloads since they waste HDD space
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


class IgnoreFilter:
    def __init__(self, filter_list, is_regex=False):
        self.filter_list = None
        if not is_regex:
            self.filter_list = filter_list
        else:
            self.filter_list = IgnoreFilter.convert_filter_list_to_regex_list(filter_list)
        self.source_path = None
        self.is_regex_list = is_regex

    def filter(self, items):
        """Returns a generator of a list of items that have been filtered with the filter list"""
        if not self.is_regex_list:
            return IgnoreFilter.filter_with_ignore_list(items, self.filter_list)
        return IgnoreFilter.filter_with_regexp_list(items, self.filter_list)

    # @staticmethod
    # def filter_with_ignore_list(urls, ignore_list):
    #     ignore_list = tuple((os.path.basename(filename) for filename in ignore_list))
    #     filtered = list(link for link in urls if os.path.basename(link) not in ignore_list)
    #     return filtered
    @staticmethod
    def filter_with_ignore_list(urls, ignore_list):
        """Returns a generator of a list of items that are not ignored using ignore_list"""
        def ignore_list_gen():
            return (os.path.basename(filename) for filename in ignore_list)
        return (link for link in urls if os.path.basename(link) not in ignore_list_gen())

    @staticmethod
    def load_filter(list_path):
        ignore_list = []
        list_path = os.path.expanduser(list_path)

        with open(list_path) as fh:
            for line in fh:
                ignore_list += [line.strip()]

        new_instance = IgnoreFilter(ignore_list, is_regex=True)
        new_instance.source_path = list_path
        return new_instance

    def save(self, save_path=None):
        if save_path is None:
            if self.source_path is None:
                raise ValueError('self.source_path ({}) is not available!'.format(self.source_path))
            save_path = self.source_path

        create_directory_tree(os.path.dirname(save_path))
        with open(save_path, 'w') as fh:
            patterns = None
            if self.is_regex_list:
                patterns = (p.pattern for p in self.filter_list)
            else:
                patterns = self.filter_list

            for pattern in patterns:
                fh.write(pattern + '\n')
            fh.write(pattern + '\n')

    @staticmethod
    def convert_filter_list_to_regex_list(ignore_list):
        """Converts an ignore list into a list of regexp engines"""
        new_list = []
        for item in ignore_list:
            new_list = [re.compile(item)]
        return new_list

    # @staticmethod
    # def filter_with_regexp_list(items, regexp_list):
    #     filtered = list()
    #     # filtered = set()
    #
    #     for item in items:
    #         add_item = True
    #         for regexp in regexp_list:
    #             res = regexp.search(item)
    #             if res is not None:
    #                 add_item = False
    #                 break
    #         if add_item:
    #             filtered += [item]
    #
    #     return filtered

    @staticmethod
    def filter_with_regexp_list(items, regexp_list):
        # filtered = list()
        for item in items:
            add_item = True
            for regexp in regexp_list:
                res = regexp.search(item)
                if res is not None:
                    add_item = False
                    break
            if add_item:
                yield item


def json_from_path(path):
    # json_obj = None
    with open(path, encoding='utf-8') as f:
        json_obj = json.load(f)
    return json_obj