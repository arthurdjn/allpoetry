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


def get_nth_links(sess, author, page=1):
    """Load the links for the n-th page of the author's poems.

    Args:
        sess (requests.Session): Session used to connect to the server.
        author (str): Name of the author to scrape poems.
        page (int, optional): Page of the website. Defaults to 1.

    Returns:
        dict: Couple (title, url).
    """
    links_url = f"https://allpoetry.com/{author}?links=1&page={page}"
    links = sess.get(links_url)
    links_soup = BeautifulSoup(links.text, "html.parser")
    links = dict()
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


def get_poem_links(sess, author, top_k=None):
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
        new_links = get_nth_links(sess, author, page=page)
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
