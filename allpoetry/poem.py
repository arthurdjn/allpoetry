# File: poem.py
# Creation: Thursday November 19th 2020
# First Author: Marcus Hughes
# Second Author: Arthur Dujardin
# Contact: arthur.dujardin@ensg.eu
#          arthurd@ifi.uio.no
# --------
# Copyright (c) 2020 Arthur Dujardin
# All rights reserved. See LICENSE.md for more details.


import re


UNWANTED_PARTS = [
    ".............",
    "-------------",
    "............."
]


def process(lines):
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


class Poem:
    r"""
    Defines a poem from ``allpoetry.com`` with its associated metadata.

    * :attr:`title` (str): Poem's title.

    * :attr:`author` (str): Poem's author.

    * :attr:`body` (list): Poem's lines. Break lines should be taken into account.

    * :attr:`meta` (str): Poem's meta data (i.e. copyrights etc.).

    * :attr:`url` (str): Poem's url page.

    * :attr:`date` (str): Date when the poem was published.

    * :attr:`likes` (int): Number of likes.

    * :attr:`views` (int): Number of views.

    * :attr:`tags` (list): list of tags assigned to the poem.

    """

    def __init__(self, title=None, lines=None, author=None, meta=None, url=None, 
                 date=None, likes=None, views=None, tags=None):
        self.title = title
        self.lines = process(lines)
        self.author = author
        self.meta = meta
        self.url = url
        self.likes = likes
        self.views = views
        self.date = date
        self.tags = tags or []

    @property
    def text(self):
        return "\n".join(self.lines)

    def __str__(self):
        rep = self.title or ""
        rep += "\n" + "¯" * len(rep) + "\n\n"
        rep += "“" + "\n".join(self.lines) + "”\n\n"
        rep += "— " + " ".join(" ".join(self.author.split("-")).split("_")) + "\n"
        rep += f"  Likes: {self.likes:,}"
        rep += f", Views: {self.views:,}"
        if self.tags != []:
            rep += f", Tags: {', '.join(self.tags)}"
        return rep

    def __len__(self):
        return len((" ".join(self.lines)).split(" "))
