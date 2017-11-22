# THREAD FILES
This is my 4chan images/videos downloader made using Python.

## Features
* Download threads
* Synchronise downloaded threads
* Synchronise recently downloaded threads
* Multi-threaded downloading
* Cached HTTP responses
* Ignore list

## System Requirements:
* Linux (old version works on Windows 10, not sure with new one)
* Python 3.5.2

## Installation
* Clone/download this repo and extract anywhere
* Go into the folder (`thread_files`)
* Run `pip install . --upgrade --user` (note the period!)

## Usage:
Once you have installed it, the command is `4tdl`. To view help, run `4tdl -h`

### Downloading
`4tdl download <url> -d <dir>`
Where `<url>` is the URL of the thread, and `<dir>` is the download destination of the specified URL.
The directory parameter is optional, and will download the thread to ~/Downloads/4threads/ if left none.
You can change the default behaviour by modifying `~/.4tdl_settings.json`

### Synchronise directory
`4tdl syncdir <dir>`
This command is when you want to update the contents of a previously downloaded directory.

### Synchronise recent
`4tdl sync-recent`
Synchronises all recently acquired threads.

### Modifying settings
Modifying settings can be done with:
`4tdl setting <option> <newval>`
`<option>` can be any of the following, corresponds to the value type next to the command:
* `default_download_directory` (string) DEFAULT = ~/Downloads/4threads/
* `max_recent_threads` (number; eg. 1, 2, 3, etc.) DEFAULT = 20

Example:
`4tdl setting max_recent_threads 100`

### Viewing setting values
`4tdl setting <option>`
Prints the value of the option.

### Creating ignore lists
If you want to exclude downloading of a certain url/file on an already downloaded thread, just add its file name into a text file in the thread folder called `ignore_list.txt`. You may delete the excluded file if you want.

For instance, you have the thread's folder at `/home/<username>/Downloads/<thread_folder>`. Save a text file 'ignore_list.txt' on this directory and include the filename in there.

I usually just open a terminal in the directory and run the command `echo '1234567890.png' >> ignore_list.txt'`.

Regular expressions work too; for instance, ignore all png files: `echo png$ >> ignore_list.txt`

## Future plans/Next steps
- [x] [Response caching](https://cachecontrol.readthedocs.io/en/latest/storage.html)
- [ ] I plan on implementing a JSON version of the LinksRetriever class with [4chan's JSON API](https://github.com/4chan/4chan-API).
- [ ] Use factory class/method for choosing between HTML/JSON LinksRetriever (I'm still new to Python)