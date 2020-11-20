# File: poem.py
# Creation: Thursday November 19th 2020
# First Author: Marcus Hughes
# Second Author: Arthur Dujardin
# Contact: arthur.dujardin@ensg.eu
#          arthurd@ifi.uio.no
# --------
# Copyright (c) 2020 Arthur Dujardin
# All rights reserved. See LICENSE.md for more details.


from .functional import process_lines, process_name


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
        self.lines = process_lines(lines)
        self.author = process_name(author)
        self.meta = meta
        self.url = url
        self.likes = likes
        self.views = views
        self.date = date
        self.tags = tags or []

    @property
    def text(self):
        return "\n".join(self.lines)

    def __len__(self):
        return len((" ".join(self.lines)).split(" "))

    def __str__(self):
        rep = self.title or ""
        rep += "\n" + "¯" * len(rep) + "\n\n"
        rep += "“" + self.text + "”\n\n"
        rep += "— " + self.author + "\n"
        rep += f"  Likes: {self.likes:,}"
        rep += f", Views: {self.views:,}"
        if self.tags != []:
            rep += f", Tags: {', '.join(self.tags)}"
        return rep

    def __repr__(self):
        return f"<Poem: {self.title}, from {self.author}>"
    