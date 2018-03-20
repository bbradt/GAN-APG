#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 12 21:11:41 2017

@author: bbradt
"""
import sys
import json
import os


""" Python Versioning for Convenience """


def pyversion():
    """ return python version """
    if sys.version_info[0] < 3:
        return 2
    return 3


def py3():
    """ return True if user is using major python version 3"""
    return pyversion() == 3


def py2():
    """ return True if user is using major python version 2"""
    return pyversion() == 2


def json_to_dict(filename):
    """ Simplify json loading """
    with open(filename, "rb") as json_file:
        object = json.load(json_file)
    return(object)


def pad_string(string, pad_len):
    """
        Pad a string with whitespace.
        This solution is a modified version of the solution posted here:
            https://stackoverflow.com/questions/
                    5676646/how-can-i-fill-out-a-python-string-with-spaces
    """
    string = ('{0: <%d}' % pad_len).format(string)  # left padding
    string = ('{0: >%d}' % pad_len).format(string)  # right padding
    return string


def walklevel(some_dir, level=1):
    """
        Modified walk function with restricted recursion
        https://stackoverflow.com/questions/229186/
                os-walk-without-digging-into-directories-below
    """
    some_dir = some_dir.rstrip(os.path.sep)
    assert os.path.isdir(some_dir)
    num_sep = some_dir.count(os.path.sep)
    for root, dirs, files in os.walk(some_dir):
        yield root, dirs, files
        num_sep_this = root.count(os.path.sep)
        if num_sep + level <= num_sep_this:
            del dirs[:]


def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        if py2():
            choice = raw_input().lower()
        else:
            choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")
