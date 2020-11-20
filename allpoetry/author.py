# File: author.py
# Creation: Friday November 20th 2020
# First Author: Marcus Hughes
# Second Author: Arthur Dujardin
# Contact: arthur.dujardin@ensg.eu
#          arthurd@ifi.uio.no
# --------
# Copyright (c) 2020 Arthur Dujardin
# All rights reserved. See LICENSE.md for more details.


from .functional import process_name


class Author:
    def __init__(self, name, url=None, info=None):
        self.name = process_name(name)
        self.url = url
        self.info = info

    def __repr__(self):
        return f"<Author: {self.name}>"
