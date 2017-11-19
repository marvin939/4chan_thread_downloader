# 4CHAN THREAD FILES DOWNLOADER
This is my 4chan images/videos downloader in Python.

## Features
* Download threads
* Synchronise downloaded threads
* Synchronise recently downloaded threads

## System Requirements:
* Linux (old version works on Windows 10, not sure with new one)
* Python 3.5.2

## Installation
* Clone this repo
* Go into the folder (`thread_files`)
* Run `pip install .`

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

### Modify settings
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