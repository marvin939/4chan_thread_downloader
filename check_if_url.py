import re

# Check if 4chan URL:
# URL = 'http://boards.4chan.org/g/thread/60892882'
URL = 'http://boards.4chan.org/g/thread/60887612'
PATTERN_4CHAN_URL = 'https?:\/\/boards.4chan.org\/(?P<board>\w+)\/thread\/(?P<thread_id>\d+)'
FOURCHAN_URL_RE = re.compile(PATTERN_4CHAN_URL)

def main():
    match = FOURCHAN_URL_RE.match(URL)
    if match is not None:
        print(match.groups())

        if match.group("board") == "g":
            print("The board is G")
        else:
            print("Board name:", match.group("board"))
            
        if match.group("thread_id") == "60892882":
            print("Thread ID is", match.group("thread_id"))
    

if __name__ == "__main__":
    main()
