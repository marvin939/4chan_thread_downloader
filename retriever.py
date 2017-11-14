import glob
import pickle
from bs4 import BeautifulSoup
import requests
import re
import os
import utilities


class BatchDownloader:
    THREAD_SAVE_NAME = 'thread.html'
    THREAD_DETAILS_FILENAME = 'thread_details.pkl'  # pickle
    IGNORE_LIST_FILENAME = 'ignore_list.txt'
    MEDIA_FILE_EXTENSIONS = ('.png', '.webm', '.jpg')

    def __init__(self, links_retriever, destination_folder='.'):
        self.files_to_download = None
        self.links_retriever = None
        if isinstance(links_retriever, LinksRetriever):
            self.links_retriever = links_retriever
            self.files_to_download = links_retriever.get_all_file_links()
        else:
            '''check if it is iterable'''
            try:
                self.files_to_download = (link for link in links_retriever)
            except:
                raise TypeError('links argument must be iterable!')
        self.destination_folder = os.path.expanduser(destination_folder)
        self.ifilter = None

    # def read_response(self):
    #     if self.links_retriever.response is None:
    #         return

    def start_download(self):
        pass

    def has_response(self):
        return (self.links_retriever and self.links_retriever.response) or not self.links_retriever.thread_is_dead()

    def save_html(self):
        if not self.has_response():
            return
        utilities.create_directory_tree(self.destination_folder)
        with open(os.path.join(self.destination_folder, self.THREAD_SAVE_NAME),'w') as fh:
            fh.write(self.links_retriever.response.text)

    def pickle_details(self, details=None):
        if details is None:
            details = self.construct_details_dict()
            assert details is not None
        details_dict = details

        utilities.create_directory_tree(self.destination_folder)
        pickle_destination = os.path.join(self.destination_folder, self.THREAD_DETAILS_FILENAME)
        with open(pickle_destination, 'wb') as fh:
            pickle.dump(details_dict, fh)

    def load_details_into_dict(self):
        pickle_source = os.path.join(self.destination_folder, self.THREAD_DETAILS_FILENAME)
        if not os.path.exists(pickle_source):
            return None
        with open(pickle_source, 'rb') as fh:
            return pickle.load(fh)

    def construct_details_dict(self):
        if not self.has_response():
            return
        details_dict = dict()
        details_dict['last-modified'] = self.links_retriever.response.headers['last-modified']
        details_dict['url'] = self.links_retriever.response.url
        #details_dict['thread_alive'] = True
        details_dict['thread_alive'] = (not self.links_retriever.from_hdd and self.links_retriever.response is not None)
        return details_dict

    def get_links_not_downloaded(self):
        return tuple(self.links_not_downloaded())

    def links_not_downloaded(self):
        """Returns a generator for a list of files that have not been downloaded"""
        links = set(self.files_to_download)
        not_downloaded = (link for link in links if
                          os.path.join(self.destination_folder, os.path.basename(link)) not in self.files_downloaded())
        return not_downloaded

    def get_files_downloaded(self):
        return tuple(self.files_downloaded())

    def files_downloaded(self):
        """Returns a generator that contains a list of files that have been downloaded"""
        return (file for file in glob.glob(self.destination_folder + '*') if
                os.path.splitext(file)[1] in self.MEDIA_FILE_EXTENSIONS)

    def get_links(self, filtered=True):
        not_downloaded = tuple(self.get_links_not_downloaded())
        if self.ifilter is None or filtered is False:
            return not_downloaded
        return self.ifilter.filter(not_downloaded)


class LinksRetriever():
    """Retrieves media links from a thread URL"""
    PATTERN_TITLE = r"\/(?P<board>\w+)\/ - (?P<title>\w+(\s+\w+)*)"
    RE_TITLE = re.compile(PATTERN_TITLE)
    PATTERN_FILENAME = r"(?P<filename>\d+\.\w+)$"  # will be set later
    RE_LINK_FILENAME = re.compile(PATTERN_FILENAME)
    PATTERN_FOURCHAN_URL = r'(https?:\/\/)?boards.4chan.org\/(?P<board>\w+)\/thread\/(?P<thread_id>\d+)'
    RE_FOURCHAN_URL = re.compile(PATTERN_FOURCHAN_URL)
    PATTERN_MEDIA_URL = r'i\.4cdn\.org\/\w+\/\w+\.\w+'
    RE_MEDIA_URL = re.compile(PATTERN_MEDIA_URL)

    def __init__(self, url):
        self.thread_url = url
        self.from_hdd = False
        self.soup = None
        self.response = None
        if isinstance(url, str):
            if self.RE_FOURCHAN_URL.search(url) is None:
                # Then the file is on the HDD
                with open(url, 'r', encoding='utf-8') as fh:
                    self.soup = BeautifulSoup(fh, 'lxml')
                self.from_hdd = True
            else:
                self.response = requests.get(url)
                self.soup = BeautifulSoup(self.response.text, 'lxml')
        elif isinstance(url, requests.models.Response):
            # Response object
            self.soup = BeautifulSoup(url.text, 'lxml')
            self.response = url

        self.thread_title = None
        self.__thread_id = None
        self.thread_board_name = None

        self.files_links = []

    def get_title(self):
        if self.thread_title is not None:
            return self.thread_title

        title_text = self.soup.title.get_text()
        title = ""
        if title_text is not None:
            matches = self.RE_TITLE.search(title_text)
            if matches is not None:
                title = matches.group("title")
                self.thread_title = title
        return title

    @property
    def title(self):
        return self.get_title()

    def retrieve_board_name(self):
        if self.thread_board_name is not None:
            return self.thread_board_name

        board = ""
        if self.thread_url is not None:
            board_match = self.RE_FOURCHAN_URL.search(self.thread_url)
            if board_match is not None:
                board = board_match.group("board")
                self.thread_board_name = board
        return board

    @property
    def board_name(self):
        return self.retrieve_thread_id()

    def retrieve_thread_id(self):
        if self.__thread_id is not None:
            return self.__thread_id

        tid = ""
        if self.thread_url is not None:
            matches = self.RE_FOURCHAN_URL.search(self.thread_url)

            if matches is not None:
                tid = matches.group("thread_id")
                self.self.__thread_id = tid
        return tid

    @property
    def thread_id(self):
        return self.retrieve_thread_id()

    @thread_id.setter
    def thread_id(self, new_val):
        self.__thread_id = new_val

    def __post_has_media_file(self, tag):
        if tag.name == "a" and tag.has_attr("class"):
            for classVal in tag["class"]:
                if classVal == "fileThumb":
                    return True
        return False

    def __get_media_url(self, link):
        m = self.RE_MEDIA_URL.search(link)
        res = m.group()
        if res is not None:
            return res if res.startswith('https://') else 'https://' + res
        return None

    def get_all_file_links(self):
        if len(self.files_links) > 0:
            return self.files_links

        self.files_links = []
        for media in self.soup.find_all(self.__post_has_media_file):
            self.files_links.append(self.__get_media_url(media["href"]))

        return self.files_links

    def thread_is_dead(self):
        """
        Returns True if response's status_code is not 200, but 404
        """
        if self.from_hdd:
            return True
        if self.response.status_code is not requests.codes.ok:
            return True
        return False
