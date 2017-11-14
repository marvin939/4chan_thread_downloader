from retriever import *


def createTestEnvironment(dirname, num_files_to_download):
    utilities.create_directory_tree(dirname)

    # Create pickle
    downloader = BatchDownloader(LinksRetriever('test_thread.html'), dirname)
    downloader.pickle_details()

    # Create filter
    ifilter = utilities.IgnoreFilter(['\w+\.png'], is_regex=True)
    ifilter.save(os.path.join(dirname, downloader.IGNORE_LIST_FILENAME))

    # Download the first/top 3 images from the thread
    for url in downloader.links()[:num_files_to_download]:
        utilities.download_file(url, dirname)