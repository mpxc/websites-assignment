# Python websites to JSON parser

Welcome to your new assignment project ;-)

I am sure there are much shorter/better ways to implement most of the functionality found in this repo, but I wanted to play with BeautifulSoup and Python in general - so beware all the cruft inside (Comments instead of Docstrings, formatting, etc).

## Usage

Adding here only for completeness:

```
$ docker build -t "websites" .
$ cat websites.txt | docker run --rm -i websites
```

## Technical overview

There are a few variables that impact how the script is running, these could have been implemented as runtime arguments.
Here is the list:

- HTTP_CONNECTION_TIMEOUT
    - Set to "30" so it doesn't hang forever on closed ports.

- ENABLE_CUSTOM_HTML_HEADERS
    - Disabled, but gives much better results when enabled ;-)

There are at least a few modules I could have used instead, but I really wanted to roll my own functions.
Here is the list:

- set_global_session()
    - Initializes the multiprocessing pool

- extract_logo()
    - Extracts logo from HTML "img" tag

- clean_phone()
    - Cleans unwanted characters from phone numbers

- extract_phones()
    - Calls `extract_phone_from_tag()` and `extract_phone_from_html()` depending on where the phone number was found - anchor tags, tags by class name and other div/p tags with numbers in them.

- fetch_all_websites()
    -  The one called from __main__ with variable filled from stdin. Heavy lifting is done by `fetch_website()`.

