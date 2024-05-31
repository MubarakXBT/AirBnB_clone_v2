#!/usr/bin/python3
"""
fabric api
"""
from fabric.api import local
from time import strftime
from datetime import date


def do_pack():
    """
    pack file into tgz archive
    """
    filename = strftime("%Y%m%d%H%M%S")

    try:
        local("mkdir -p versions")
        local ("tar -czvf versions/web_static_{}.tgz web_static/"
               .format(filename))

        return "versions/web_static_{}.tgz".format(filename)
    except Exception as e:
        return None
