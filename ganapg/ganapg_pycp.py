#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Nov 12 23:08:13 2017

@author: bbradt
"""

import re
from pycparser import c_ast
from pycparser.plyparser import Coord
# from pycparser.plyparser import ParseError

""" These PYCPARSER functions were ripped from pycparser.examples.to_json
For some reason, importing them from the module itself created strange errors.
So they have been included here with slight renaming to avoid collision"""
pycp_RE_CHILD_ARRAY = re.compile(r'(.*)\[(.*)\]')
pycp_RE_INTERNAL_ATTR = re.compile('__.*__')


class pycp_CJsonError(Exception):
    pass


def pycp_memodict(fn):
    """
        !!FROM PYCPARSER!!
        Fast memoization decorator for a function taking a single argument
    """
    class memodict(dict):
        def __missing__(self, key):
            ret = self[key] = fn(key)
            return ret
    return memodict().__getitem__


@pycp_memodict
def pycp_child_attrs_of(klass):
    """
    !!FROM PYCPARSER!!
    Given a Node class, get a set of child attrs.
    Memoized to avoid highly repetitive string manipulation

    """
    non_child_attrs = set(klass.attr_names)
    all_attrs = set([i for i in klass.__slots__
                     if not pycp_RE_INTERNAL_ATTR.match(i)])
    return all_attrs - non_child_attrs


def pycp_to_dict(node):
    """
        !!FROM PYCPARSER!!
        Recursively convert an ast into dict representation.
    """
    klass = node.__class__

    result = {}

    # Metadata
    result['_nodetype'] = klass.__name__

    # Local node attributes
    for attr in klass.attr_names:
        result[attr] = getattr(node, attr)

    # Coord object
    if node.coord:
        result['coord'] = str(node.coord)
    else:
        result['coord'] = None

    # Child attributes
    for child_name, child in node.children():
        # Child strings are either simple (e.g. 'value')
        # or arrays (e.g. 'block_items[1]')
        match = pycp_RE_CHILD_ARRAY.match(child_name)
        if match:
            array_name, array_index = match.groups()
            array_index = int(array_index)
            # arrays come in order, so we verify and append.
            result[array_name] = result.get(array_name, [])
            if array_index != len(result[array_name]):
                raise pycp_CJsonError(
                        'Internal ast error. Array {} out of order. '
                        'Expected index {}, got {}'.format(
                                array_name, len(result[array_name]),
                                array_index))
            result[array_name].append(pycp_to_dict(child))
        else:
            result[child_name] = pycp_to_dict(child)

    # Any child attributes that were missing need "None" values in the json.
    for child_attr in pycp_child_attrs_of(klass):
        if child_attr not in result:
            result[child_attr] = None

    return result


def pycp_parse_coord(coord_str):
    """
    !!! FROM PYCPARSER !!!
    Parse coord string (file:line[:column]) into Coord object.
    """
    if coord_str is None:
        return None

    vals = coord_str.split(':')
    vals.extend([None] * 3)
    filename, line, column = vals[:3]
    return Coord(filename, line, column)


def pycp_convert_to_obj(value):
    """
    !!! FROM PYCPARSER !!!
    Convert an object in the dict representation into an object.
    Note: Mutually recursive with from_dict.

    """
    value_type = type(value)
    if value_type == dict:
        return pycp_from_dict(value)
    elif value_type == list:
        return [pycp_convert_to_obj(item) for item in value]
    else:
        # String
        return value


def pycp_from_dict(node_dict):
    """ Recursively build an ast from dict representation """
    class_name = node_dict.pop('_nodetype')

    klass = getattr(c_ast, class_name)

    # Create a new dict containing the key-value pairs which we can pass
    # to node constructors.
    objs = {}
    for key, value in node_dict.items():
        if key == 'coord':
            objs[key] = pycp_parse_coord(value)
        else:
            objs[key] = pycp_convert_to_obj(value)

    # Use keyword parameters, which works thanks to beautifully consistent
    # ast Node initializers.
    return klass(**objs)