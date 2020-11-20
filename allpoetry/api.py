# File: api.py
# Creation: Thursday November 19th 2020
# First Author: Marcus Hughes
# Second Author: Arthur Dujardin
# Contact: arthur.dujardin@ensg.eu
#          arthurd@ifi.uio.no
# --------
# Copyright (c) 2020 Arthur Dujardin
# All rights reserved. See LICENSE.md for more details.


import requests
import lxml.html
from bs4 import BeautifulSoup
from tqdm import tqdm

# allpoetry package
from .poem import Poem
from .author import Author
from .functional import *


class AllPoetry:
    r"""
    API to access poems on ``allpoetry.com``

    * :attr:`session` (requests.Session): Session used to connect on ``allpoetry`` servers.

    .. note::
        You must login if wanting more than the 15th page of poems.

    """

    LOGIN_URL = "https://allpoetry.com/login"

    def __init__(self, username=None, password=None):
        self.session = requests.session()  # a continuous session is used for security authentication
        if username and password:
            self.login(username, password)

    def login(self, username, password):
        login_page = self.session.get(self.LOGIN_URL)
        login_html = lxml.html.fromstring(login_page.text)
        # find authentication token and other form data
        hidden_inputs = login_html.xpath(r"//form//input[@type='hidden']")
        indices = [0, 1]  # these are the two attributes we need: authenticity token and utf8
        form = {hidden_inputs[i].attrib["name"]: hidden_inputs[i].attrib["value"] for i in indices}
        form["user[name]"] = username
        form["user[password]"] = password
        form["referer"] = self.LOGIN_URL
        response = self.session.post(self.LOGIN_URL, data=form)
        errors = BeautifulSoup(response.text, "html.parser").select(".error")
        if errors:
            raise RuntimeError("Error logging in: {}".format("&&".join([e.text for e in errors])))

    def get_poem_links(self, author_name, top_k=None):
        return get_poems_links(self.session, author_name, top_k=top_k)

    def get_poem_from_url(self, poem_url):
        poem_data = get_poem_from_url(self.session, poem_url)
        return Poem(**poem_data)

    def get_poems(self, author_name, top_k=None):
        poems = []
        links = self.get_poem_links(author_name, top_k=top_k)
        length_str = len(str(len(links)))
        trange = tqdm(links.values(), desc=f"Poem", position=0, leave=True)
        for i, link in enumerate(trange):
            # Update the progress bar
            trange.set_description(f"Poem {i+1:>{length_str}}/{len(links)}")
            trange.refresh()
            try:
                poem = self.get_poem_from_url(link)
                trange.set_postfix({"title": poem.title[:12] + "..." if len(poem.title[:15]) == 15 else poem.title[:15]})
                poems.append(poem)
            except IndexError:
                pass
        return poems

    def get_author_from_url(self, author_url):
        author_data = get_author_from_url(self.session, author_url)
        return Author(**author_data)

    def get_author(self, author_name):
        author_data = get_author_from_url(self.session, f"https://allpoetry.com/{author_name}")
        return Author(**author_data)

    def get_famous_authors_links(self, top_k=None):
        return get_famous_authors_links(self.session, top_k=top_k)

    def get_famous_authors(self, top_k=None):
        authors = []
        links = self.get_famous_authors_links(top_k=top_k)
        length_str = len(str(len(links)))
        trange = tqdm(links.values(), desc=f"Author", position=0, leave=True)
        for i, link in enumerate(trange):
            # Update the progress bar
            trange.set_description(f"Author {i+1:>{length_str}}/{len(links)}")
            trange.refresh()
            try:
                author = self.get_author_from_url(link)
                trange.set_postfix({"name": author.name[:12] + "..." if len(author.name[:15]) == 15 else author.name[:15]})
                authors.append(author)
            except IndexError:
                pass
        return authors

    def __repr__(self):
        return "<AllPoetry API>"
