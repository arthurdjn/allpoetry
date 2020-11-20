# File: scrape.py
# Creation: Thursday November 19th 2020
# First Author: Marcus Hughes
# Second Author: Arthur Dujardin
# Contact: arthur.dujardin@ensg.eu
#          arthurd@ifi.uio.no
# --------
# Copyright (c) 2020 Arthur Dujardin
# All rights reserved. See LICENSE.md for more details.


from dateutil.parser import parse as parse_date
from bs4 import BeautifulSoup


import re


UNWANTED_PARTS = [
    ".............",
    "-------------",
    "............."
]


def process_lines(lines):
    """Process the lines of a ``Poem``, and make sure all poems are in the same format.
    For example, this function will remove special characters, unnecessary white spaces and unwanted words.

    Args:
        lines (list): List of strings which correspond to the lines of the poem.

    Returns:
        list
    """
    new_lines = []
    for line in lines:
        add_line = True
        for word in UNWANTED_PARTS:
            if word in line:
                add_line = False
        if add_line:
            line = re.sub('[^A-Za-z0-9|?|!|.|,|;|:|(|)|"|\'|—]+', " ", line)
            line = line.replace(" s ", "'s ")
            line = line.replace(" t ", "'t ")
            new_lines.append(" ".join(line.split()))
    new_lines = re.sub(r"\n\s*\n\s*\n", "\n\n", "\n".join(new_lines)).split("\n")
    if new_lines[0] == "":
        new_lines.pop(0)
    if new_lines[0] == "":
        new_lines.pop(0)
    if new_lines[-1] == "":
        new_lines.pop(-1)
    if new_lines[-1] == "":
        new_lines.pop(-1)
    return new_lines


def process_name(name):
    """Process a name (author's name, poem's title, etc.).

    Args:
        name (str): name to process.

    Returns:
        str
    """
    name = name.replace("-", " ").replace("_", " ")
    return " ".join(name.split())


def element2string(element):
    """Convert a ``bs4.Element`` containing text data to a string.

    Args:
        element (bs4.Element): HTML element to convert to string.

    Returns:
        str
    """
    text = ""
    for elem in element.recursiveChildGenerator():
        if isinstance(elem, str):
            text += elem.strip()
        elif elem.name == "br":
            text += "\n"
    return text


def get_nth_poem_links(sess, author, page=1):
    """Load the links for the n-th page of the author's poems.

    Args:
        sess (requests.Session): Session used to connect to the server.
        author (str): Name of the author to scrape poems.
        page (int, optional): Page of the website. Defaults to 1.

    Returns:
        dict: Couple (title, url).
    """
    links_url = f"https://allpoetry.com/{author}?links=1&page={page}"
    session = sess.get(links_url)
    links_soup = BeautifulSoup(session.text, "html.parser")
    links = {}
    # NOTE: Home pages are different from users / real poets. (ex Sylvia Plath).
    # For user-base pages:
    if len(links_soup.select(".t_links")[0].select(".clearfix")) > 0:
        for entry in links_soup.select(".t_links")[0].select(".clearfix")[0].find_all("div", {"class": "itm"}):
            entry = entry.select("a")[0]
            title = entry.text
            url = "https://allpoetry.com" + entry["href"]
            links[title] = url
    # For poet-base pages:
    elif len(links_soup.select(".items_group")[0].select("h1.title")) > 0:
        for entry in links_soup.select(".items_group")[0].select("h1.title"):
            entry = entry.select("a")[0]
            title = entry.text
            url = "https://allpoetry.com" + entry["href"]
            links[title] = url
    return links


def get_poems_links(sess, author, top_k=None):
    """Retrieve names of all poems written by user.

    Args:
        author (str): Name of user (from url) to search.
        at_least (int, optional): Approximate number of most recent poems titles to return, may slightly exceed this number.

    Returns:
        dictionary of couples (poem's title, url)
    """
    links = {}
    poems_found = True
    page = 1
    while poems_found:
        # Go to next page, and search for poems
        new_links = get_nth_poem_links(sess, author, page=page)
        if new_links:
            for title, url in new_links.items():
                links[title] = url
                # Break if the maximum poems are reached
                if top_k and len(links) >= top_k:
                    return links
        else:
            poems_found = False
        page += 1
    return links


def _parse_view_string(view_string):
    """Given a string indicating number of views for a poem, e.g. ``"321 views"`` or ``"541.7k views"``
    parse and return an integer type.

    Args:
        view_string (str): string indicating number of views, output of span with ``id=views``.

    Returns:
        int
    """
    count = None
    try:
        count = int(view_string)
    except ValueError:
        if "k" in view_string:
            try:
                count = int(float(view_string.replace("k", "")) * 1000)
            except ValueError:
                pass
    return count


def get_poem_from_url(sess, poem_url):
    """Retrieve the poem and parse metadata from an url.

    Args:
        poem_url (str): string for location of poem

    Returns:
        Poem
    """
    # get page contents
    poem_html = sess.get(poem_url)
    poem_soup = BeautifulSoup(poem_html.text, "html.parser")

    poem_data = {}
    # 1. Poem URL
    poem_data["url"] = poem_url
    # 2. Poem title
    poem_data["title"] = poem_soup.select(".title")[0].text
    # 3. Poem author
    poem_data["author"] = poem_soup.select(".bio")[0].select(".u")[0].get("href")[1:]
    # 4. Poem lines
    lines = ""
    for div_content in poem_soup.select(".poem_body")[0].findChildren("div", recursive=False):
        if "hidden" in div_content.get("class"):
            continue
        elif "copyright" in div_content.get("class"):
            continue
        else:
            lines += element2string(div_content)
    poem_data["lines"] = lines.split("\n")
    # 5. Poem metadata
    poem_data["meta"] = poem_soup.find_all("div", {"class": "copyright"})[0].text
    # 6. Poem views
    view_string = poem_soup.find("span", {"id": "views"}).text.split("views")[0].strip()
    poem_data["views"] = _parse_view_string(view_string)
    # 7. Poem views
    try:
        date = parse_date(poem_soup.select(".author_copyright")[0].select(".timeago")[0].get("title"))
    except IndexError:
        date = None
    finally:
        poem_data["date"] = date
    # 7. Poem likes
    try:
        likes = int(poem_soup.select(".cmt_wrap")[0].select(".num")[0].text)
    except IndexError:
        likes = None
    finally:
        poem_data["likes"] = likes
    # 9. Poem tags
    try:
        tags = [a.text.strip() for a in poem_soup.select(".cats_dot")[0].select("a")]
    except IndexError:
        tags = None
    finally:
        poem_data["tags"] = tags

    return poem_data


def get_nth_famous_authors(sess, page=1):
    """Load the links for the n-th page of the famous authors.

    Args:
        sess (requests.Session): Session used to connect to the server.
        page (int, optional): Page of the website. Defaults to 1.

    Returns:
        dict: Couple (author, url).
    """
    links_url = f"https://allpoetry.com/famous-poets?page={page}"
    session = sess.get(links_url)
    links_soup = BeautifulSoup(session.text, "html.parser")
    links = {}
    for entry in links_soup.select(".items.users")[0].find_all("div", {"class": "itm"}):
        entry = entry.select("a")[0]
        author = entry.text
        url = "https://allpoetry.com" + entry["href"]
        links[author] = url
    return links


def get_famous_authors_links(sess, top_k=None):
    """Retrieve names of all poems written by user.

    Args:
        author (str): Name of user (from url) to search.
        at_least (int, optional): Approximate number of most recent poems titles to return, may slightly exceed this number.

    Returns:
        dictionary of couples (poem's title, url)
    """
    links = {}
    poems_found = True
    page = 1
    while poems_found:
        # Go to next page, and search for poems
        new_links = get_nth_famous_authors(sess, page=page)
        if new_links:
            for author, url in new_links.items():
                links[author] = url
                # Break if the maximum poems are reached
                if top_k and len(links) >= top_k:
                    return links
        else:
            poems_found = False
        page += 1
    return links


def get_author_from_url(sess, author_url):
    author_html = sess.get(author_url)
    author_soup = BeautifulSoup(author_html.text, "html.parser")
    name = " ".join(author_soup.select(".media-body h1.notop")[0].text.split())
    info = ""
    # For users
    if len(author_soup.select(".sub_bio .clearfix")) > 0:
        info = element2string(author_soup.select(".sub_bio .clearfix")[0])
    # For famous poets
    elif len(author_soup.select(".media .preview")) > 0:
        info = element2string(author_soup.select(".media .preview")[0])
    info = "\n".join(process_lines(info.split("\n")))
    return {"name": name, "url": author_url, "info": info}
