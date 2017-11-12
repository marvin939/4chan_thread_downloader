from pathlib import Path
import re
from time import time
from timeit import timeit

media_links = ["http://i.4cdn.org/g/1497326411255.jpg",
               "http://i.4cdn.org/g/1497330384263.png",
               "http://i.4cdn.org/g/1497331121191.png",
               "http://i.4cdn.org/g/1497331662633.png",
               "http://i.4cdn.org/g/1497332117573.jpg",
               "http://i.4cdn.org/g/1497333014551.png",
               "http://i.4cdn.org/g/1497336694160.jpg",
               "http://i.4cdn.org/g/1497337390076.jpg",
               "http://i.4cdn.org/g/1497337391884.png",
               "http://i.4cdn.org/g/1497338639533.jpg",
               "http://i.4cdn.org/g/1497338914430.jpg",
               "http://i.4cdn.org/g/1497339159378.jpg",
               "http://i.4cdn.org/g/149733915937833322.jpg",
               "http://i.4cdn.org/g/149733915937811111.jpg",
               "http://i.4cdn.org/g/149733915937855555.jpg",]
board_name = "g"

compare_folder = "downloaded1"
existing_files = []

# PATTERN_FILENAME = r"http:\/\/i\.4cdn\.org\/" + board_name + "\/(?P<filename>\d+\.(png|jpg|gif|webm))"
PATTERN_FILENAME = r"(?P<filename>\d+\.\w+)$"
RE_LINK_FILENAME = re.compile(PATTERN_FILENAME)


# media_links will include the new stuff, compare_folder has the old stuff
# so do subtractive comparison, where media_links items are subtracted

def main():
    media_links.sort()
    print("\n".join(media_links))

    p = Path(compare_folder)
    for path in p.iterdir():
        if not path.is_dir():
            existing_files.append(str(path))
    existing_files.sort()
    print("\n".join(existing_files))

    difference = subtract_links_paths(media_links, existing_files)
    print("Differences:")
    print("\n".join(difference))

def subtract_links_paths(links, existing):
    media_links = list(links)
    existing_files = list(existing)

    for i in range(len(media_links) - 1, -1, -1):
        link_ref = media_links[i]
        media_fn = get_filename(link_ref)
        for o in range(len(existing_files) - 1, -1, -1):
            existing_ref = existing_files[o]
            existing_fn = get_filename(existing_files[o])
            if media_fn == existing_fn:
                media_links.remove(link_ref)
                existing_files.remove(existing_ref)
                break

    return media_links

def get_filename(link):
    m = RE_LINK_FILENAME.search(link)
    return m.group("filename")

if __name__ == "__main__":
    main()
