#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This file contains functions for parsing c files as AST objects. This
preprocessing step is distinguished from other preprocessing steps because it
is not required for most models.

Created on Sun Nov 12 22:58:12 2017

@author: bbradt
"""

import json
import os
from pycparser.plyparser import ParseError
from pycparser import c_generator, parse_file
from ganapg_pycp import pycp_from_dict, pycp_to_dict
from sklearn.feature_extraction import DictVectorizer
import progressbar


def ast_to_nodesequence(ast, t0=0, child_prefix='_children_%s'):
    """
        This function takes a recursive, depth-first strategy
        to flatten an Absract Syntax Tree.
        Starting at given root, follow a path to the deepest, left-most
        unvisited child node. Each node encountered along the path, then
        receives a sequence index (analogous to a timepoint) t_i.
        This is loosely based off the strategy taken in this paper:
        but does not currently implement the translation into "program actions"
        beforehand.

        Each parent node then implicitely points to each child by adding keys
        appended by the child prefix.
        Example:
             pp = {'_node_type': 'root',
          'body': [{'_node_type': '_child0', '_child_field': 1},
                   {'_node_type': '_child1', '_chield_field2': 2},
                   {'_node_type': '_child2',
                    'init': [{'_node_type': '__child_0'}],
                    'dir': {'_node_type': '__child_0'}
                    }
                   ],
          '_root_field': 0
          }

        The first element of the reesulting sequence will be:
            {'_node_type': 'root',
             '_children_body': [1, 2, 3],
             '_root_field':0
            }
    """
    t = t0
    seq = []
    ast['t_i'] = t
    unwrapped_subtree = {}  # the root node's unwrapped subtree
    if isinstance(ast, dict):
        for k, v in ast.items():
            child_key = child_prefix % (k)
            if isinstance(v, dict):
                """
                    if the child is a single dictionary, just place it into
                    a dictionary so that we reduce the number of object
                    type cases
                """
                v = [v]

            if isinstance(v, list) and len(v) > 0:
                """
                    If the child object is a list, that list could contain
                    non-node objects, or it might contain a set of child
                    nodes.

                    If the child object in the lsit is a dictionary,
                    it indicates we've hit another node along the path
                    to the deepest child.
                    We increment the current point in the sequence, and then
                    recurse into that child's subtree, keeping track of how
                    deep that child goes to make sure the resulting sequence
                    is correctly ordered.
                """
                for child in v:
                    if isinstance(child, dict):
                        t += 1
                        child_seq, child_t = ast_to_nodesequence(child, t0=t)
                        seq += child_seq
                        if child_key not in unwrapped_subtree.keys():
                            unwrapped_subtree[child_key] = []
                        unwrapped_subtree[child_key].append(t)
                        t = child_t
                        continue
                    if k not in unwrapped_subtree.keys():
                        unwrapped_subtree[k] = []
                    unwrapped_subtree[k].append(child)
                continue
            unwrapped_subtree[k] = v
        seq.append(unwrapped_subtree)

        # make sure the resulting sequence is correctly sorted
        seq = sorted(seq, key=lambda k: k['t_i'])
    return seq, t


def grab_children_from_sequence(seq, t_i):
    """
        Given a sequence of nodes and a sequence of coordinates
        return the corresponding children. This allows us to access a
        root node's children given the indices which that node has stored
        during the ast_to_nodelist.
    """
    return [seq[t] for t in t_i]


def nodesequence_to_ast(seq, child_prefix='_children_',
                        full_seq=None, nodes_hit=[]):
    """
        Given a sequence of nodes converted by ast_to_nodesequence,
        convert that sequence back to an Abstract Syntax Tree.

        full_seq is the full node sequence of the entire tree, which has
        to be pased to each recursion to make sure that the correct
        children are grabbed.

        nodes_hit is a list of nodes already visited, to prevent duplication
    """
    if full_seq is None:  # this should be the case at the root node
        full_seq = seq
    for node in seq:
        ast = {}
        if node['t_i'] in nodes_hit:
            continue
        for name, field in node.items():
            if name is 't_i':
                continue
            if child_prefix in name:  # we've found edges to children
                children = grab_children_from_sequence(full_seq, field)
                cname = name.replace(child_prefix, '')
                ast[cname] = nodesequence_to_ast(children, fullseq=full_seq,
                                                 nodes_hit=nodes_hit)
                nodes_hit += field
                continue
            ast[name] = field
            nodes_hit.extend(node['t_i'])
    return ast


def nodesequence_to_ctext(seq):
    """
        Implements pycparser's CGenerator class in combination with the above
        conversion functions to convert a sequence of nodes back to c code.
    """
    generator = c_generator.CGenerator()
    ast_dict = nodesequence_to_ast(seq)
    ast = pycp_from_dict(ast_dict)
    c_text = generator.visit(ast)
    return c_text


def nodesequence_to_tokens(seq, v=None):
    """
        Uses the sklearn DictVectorizer to convert AST sequences to
        sequences of tokens (hashes for the features in the dictionaries)
    """
    tokens = []
    if not v:
        v = DictVectorizer(sparse=False)
    for node in seq:
        uw_node = {}
        for key, val in node.items():
            if type(val) is list:
                for i, e in enumerate(val):
                    uw_node["%s%d" % (str(key), i)] = e
            else:
                uw_node[key] = val
        node_transform = v.fit_transform(uw_node)
        tokens.append(list(node_transform))
    return tokens, v


def nodesequences_to_tokens(header='', data_dir='.', save=True,
                            save_dir=None, delimiter=' ',
                            in_ext=".json",
                            out_ext=".hash",
                            recurse=0, v=None):
    """
        Recursively parses a subdirectory, converting sequences to token hashes
    """
    if not v:
        v = DictVectorizer(sparse=False)
    all_tokens = []
    walk = os.walk(data_dir)
    i = 0
    with progressbar.ProgressBar(max_value=8000) as bar:
        for root, dirnames, filenames in walk:
            for j, filename in enumerate(filenames):
                bar.update(i)
                if os.path.splitext(filename)[1] == in_ext:
                    i += 1
                    in_path = os.path.join(root, filename)
                    if save_dir is None:
                        out_path = in_path
                    else:
                        if not os.path.exists(save_dir):
                            os.mkdir(save_dir)
                        out_path = os.path.join(save_dir, filename)
                    out_path = out_path.replace(in_ext, out_ext)
                    with open(in_path, "r") as json_file:
                        seq = json.load(json_file)
                    tokens, v = nodesequence_to_tokens(seq, v=v)
                    if save:
                        with open(out_path, 'w') as file:  # flush with header
                            file.write(header)
                        with open(out_path, 'a') as file:
                            flattokens = [str(item)
                                          for sublist in tokens
                                          for subsublist in sublist
                                          for item in subsublist]
                            file.write(delimiter.join(flattokens) + '\n')
                    all_tokens.append(tokens)
    return all_tokens, v


def cfile_to_nodesequence(c_filename):
    """
        Implements pycparser's parse_file and dictionary conversion
        in combination with the custom conversion functions
        in order to convert c code into a sequence of nodes.
    """
    try:
        ast = parse_file(c_filename, use_cpp=True,
                         cpp_path='gcc',
                         cpp_args=['-E', r'-Iutils/fake_libc_include'])
        ast_dict = pycp_to_dict(ast)
        seq, t_n = ast_to_nodesequence(ast_dict)
        return seq, t_n
    except ParseError:
        return None, False


def cfiles_to_nodesequences(header='', data_dir='.', save=True,
                            save_dir=None, delimiter=',',
                            out_ext=".seq.json", recurse=0, maxfiles=8000):
    """
        Given a directory, parse through all of the c files and convert them
        into sequences. Optionally write these sequences to json files.
    """
    cwd = os.getcwd()

    seqs = []
    walk = os.walk(data_dir)
    i = 0
    with progressbar.ProgressBar(max_value=maxfiles) as bar:
        for root, dirnames, filenames in walk:
            for filename in filenames:
                os.chdir('../pycparser/')
                if os.path.splitext(filename)[1] == '.c':
                    in_path = os.path.join(root, filename)
                    if save_dir is None:
                        out_path = in_path
                    else:
                        out_path = os.path.join(save_dir, filename)
                    out_path = out_path.replace('.c', out_ext)
                    seq, t_n = cfile_to_nodesequence(in_path)
                    i += 1
                    if seq is None:
                        continue
                    if save:
                        os.chdir(cwd)
                        # allow json saving of dictionary
                        with open(out_path, 'w') as file:
                            json.dump(seq, file)
                    os.chdir(cwd)
                    seqs.append(seq)
                    bar.update(i)
                os.chdir(cwd)

    return seqs
