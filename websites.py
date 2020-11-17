#!/usr/bin/env python

import json
import multiprocessing
import re
import requests
import sys
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from urllib.parse import urlsplit

session = None

# If unset, defaults to never
HTTP_CONNECTION_TIMEOUT = 30

# Setting "True" here will send custom headers
# Websites sometimes don't like scripts
ENABLE_CUSTOM_HTML_HEADERS = False

CUSTOM_HTML_HEADERS = {
    # The "fake-useragent" module is an option as well
    "User-Agent":
        "Mozilla/5.0 (X11; Linux x86_64; rv:82.0) Gecko/20100101 Firefox/82.0",
    "Accept": "text/html;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en,*;q=0.5",
    "Referer": "",  # Referer gets updated
    "DNT": "1",
    "Connection": "keep-alive",
    "Upgrade-Insecure-Requests": "1"
}


def set_global_session():
    global session
    if not session:
        session = requests.Session()


def extract_logo(input):
    logo = None  # Change to "" for an empty string in JSON output
    class_tag = input.find(class_=re.compile(r"logo", re.I))

    if (class_tag) and (class_tag.has_attr("src")):
        logo = class_tag["src"]

    elif (class_tag) and (class_tag.find("img", src=True)):
        logo = class_tag.find("img")["src"]

    return logo


def clean_phone(input):
    # This is only called from extract_phone_* functions.
    # Ideally, these four should be rewritten or imported from "phonenumbers"
    clean_bad_chars = re.sub(r"[^+()\d]", " ", input)
    clean_extra_space = re.sub(r"\s+", " ", clean_bad_chars).strip()
    # ITU E.123 and E.164 approximation
    if (8 <= len(clean_extra_space) <= 22):
        return clean_extra_space


def extract_phone_from_tag(input):
    search = re.search("([+()\d\s/-]{8,22})", input)
    if (search):
        return clean_phone(search.group(1))


def extract_phone_from_html(input):
    search = re.search("[>]([+()\d\s/-]{8,22})", input)
    if (search):
        return clean_phone(search.group(1))


def extract_phones(input):
    phones = []
    # Best case: "tel" anchor tag
    regex = re.compile(r"^(tel|http[s]?):([/]+)?[+()\d\s/-]+$")
    href_tags = input.find_all("a", href=regex)
    for tag in href_tags:
        phone = extract_phone_from_tag(tag["href"])
        if (phone) and (phone not in phones):
            phones.append(phone)

    if (len(phones) == 0):
        # Fallback: named class and its descendants
        regex = re.compile(r"(call|phone|mobile|fax|number)", re.I)
        class_tags = input.find_all(class_=regex)
        for tags in class_tags:
            for tag in tags.find_all(True):
                phone = extract_phone_from_html(str(tag))
                if (phone) and (phone not in phones):
                    phones.append(phone)

    if (len(phones) == 0):
        # Another fallback: "p" and "div" tags
        html_tags = input.find_all(["p", "div"])
        for tag in html_tags:
            phone = extract_phone_from_html(str(tag))
            # 3rd time is the charm, it begs for another function
            if (phone) and (phone not in phones):
                phones.append(phone)

    return phones


def fetch_website(website):
    if ENABLE_CUSTOM_HTML_HEADERS:
        headers = CUSTOM_HTML_HEADERS
        split_url = urlsplit(website)
        headers["Referer"] = "{0.scheme}://{0.netloc}/".format(split_url)
    else:
        headers = {}

    try:
        with session.get(website,
                         timeout=HTTP_CONNECTION_TIMEOUT,
                         headers=headers) as response:
            name = multiprocessing.current_process().name

    except requests.exceptions.RequestException as e:
        print ("DeadPage:", website, "Exception:", e, file=sys.stderr)
        return

    if response.status_code != 200:
        print ("DeadPage:", website, file=sys.stderr)
        return

    html = BeautifulSoup(response.text, "html.parser")
    logo = extract_logo(html)
    if (logo):
        logo = urljoin(response.url, logo)
    phones = extract_phones(html)
    print (json.dumps({"logo": logo, "phones": phones, "website": website}))


def fetch_all_websites(websites):
    with multiprocessing.Pool(initializer=set_global_session) as pool:
        pool.map(fetch_website, websites)


if __name__ == "__main__":
    websites = []
    for line in sys.stdin:
        if line.strip() != "":
            websites.append(line.strip())
    fetch_all_websites(websites)
