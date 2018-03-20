#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
C-Processing Scripts

requires:
    Python 3.5
    gcc

Created on Sun Nov 12 20:59:37 2017

@author: bbradt
"""


import os
import subprocess
import re
from sklearn.model_selection import train_test_split
from ganapg_util import json_to_dict, pad_string


def obfuscate_cfile(c_file, out_path, gcc_path='/usr/bin/gcc'):
    if os.path.exists(gcc_path):
        try:
            # Use GCC to remove comments, if gcc is available
            gcc_cmd = ('%s -fpreprocessed -dD -E %s'
                       % (gcc_path, c_file))
            c_text = subprocess.check_output(gcc_cmd, shell=True)
        except subprocess.CalledProcessError:
            with open(c_file, "r") as file:
                c_text = file.read()
    else:
        # Otherwise, only load the file without processing comments
        with open(c_file, "r") as file:
            c_text = file.read()

    # Remove all include statements
    c_text = re.sub('#include.*>', ' ', str(c_text), flags=re.DOTALL)

    # Place all code on one line
    c_text = str(c_text).strip().replace('\n', '').replace('\t', '')
    c_text = c_text.replace('\\n', '').replace('\\t', '')
    return c_text


def obfuscate_cfiles(data_dir='.', extension='.obfs', save=False,
                     gcc_path='/usr/bin/gcc',  save_dir=None, recurse=0):
    """
        Recursively obfuscate c files in a directory by placing all code on
        one line, removing include statements, and removing comments.
        This simplifies data assembly and processing by allowing one instance
        (one c-file) on one line in the training and testing sets.
    """
    walk = os.walk(data_dir)
    c_texts = []
    for root, dirnames, filenames in walk:
        for filename in filenames:
            if os.path.splitext(filename)[1] == '.c':
                in_path = os.path.join(root, filename)
                if save_dir:
                    if not os.path.exists(save_dir):
                        os.mkdir(save_dir)
                    out_path = os.path.join(save_dir, filename)
                else:
                    out_path = in_path
                # Replace the file extension to avoid duplication in data
                out_path = out_path.replace('.c', extension)

                c_text = obfuscate_cfile(in_path, out_path=out_path,
                                         gcc_path=gcc_path)

                # Write to file
                if save:
                    with open(out_path, 'w') as f:
                        f.write(c_text)
                c_texts.append(c_text)
    return c_texts


def traintest_split(data_dir='.', in_extension='.obfs',
                    save_dir=None,
                    save=True, trainfile='train', testfile='target', recurse=0,
                    testsize=0.1):
    """
        Implements the sklearn train_test_split function in a recursive fashion

    """
    walk = os.walk(data_dir)
    all_data = []
    for root, dirnames, filenames in walk:
        if recurse:
            # Until the recursion level is 0, go through all child dirs
            for dirname in dirnames:
                all_data += traintest_split(data_dir=dirname,
                                            in_extension=in_extension,
                                            recurse=recurse - 1)
        for filename in filenames:
            if os.path.splitext(filename)[1] == in_extension:
                in_path = os.path.join(root, filename)
                with open(in_path, 'r') as file:
                    text = file.read()
                    all_data.append(text)

    train, test = train_test_split(all_data, shuffle=True, testsize=testsize)
    if save_dir:
        if not os.path.exists(save_dir):
            os.mkdir(save_dir)
        trainfile = os.path.join(save_dir, trainfile)
        testfile = os.path.join(save_dir, testfile)

    if save:
        with open(trainfile, 'w') as file:
            for instance in train:
                file.write(instance+'\n')
        with open(testfile, 'w') as file:
            for instance in test:
                file.write(instance+'\n')
    return train, test, all_data


def codeflaws_posneg(header='', data_dir='.', extension='.obfs', save=True,
                            posfile='pos', negfile='neg', recurse=0,
                            save_dir=None):
    """
        This preprocessing function uses the codeflaws directory naming scheme
        to split files into separate data sets of positive and negative
        samples.

        We assume no recursion is required, i.e. data_dir points directly to
        the codeflaws directory.

        From the CodeFlaws github:
        "Each subject folder is named using the following convention:
        <contestid>-<problem>-bug-<buggy-submisionid>-<accepted-submissionid>

        Each folder contains:
        Buggy submission with name
                <contestid>-<problem>-<buggy-submisionid>.c
        Accepted submission with name
                <contestid>-<problem>-<accepted-submisionid>.c "
    """
    walk = os.walk(data_dir)
    posdata = []
    negdata = []
    for root, dirnames, filenames in walk:
        for dirname in dirnames:
            contestid, problem, _, negid, posid = dirname.split('-')
            pos_filename = '-'.join([contestid, problem, posid]) + extension
            neg_filename = '-'.join([contestid, problem, negid]) + extension
            
            pospath = os.path.join(root, dirname, pos_filename)
            negpath = os.path.join(root, dirname, neg_filename)
            if os.path.exists(pospath):
                with open(pospath, 'r') as file:
                    c_text = file.read()
                    posdata.append(c_text)
            if os.path.exists(negpath):
                with open(negpath, 'r') as file:
                    c_text = file.read()
                    negdata.append(c_text)

    # Write files
    if save_dir:
        if not os.path.exists(save_dir):
            os.mkdir(save_dir)
        posfile = os.path.join(save_dir, posfile)
        negfile = os.path.join(save_dir, negfile)
    if save:
        with open(posfile, 'w') as file:
            for instance in posdata:
                file.write(instance + '\n')
        with open(negfile, 'w') as file:
            for instance in negdata:
                file.write(instance + '\n')
    return posdata, negdata


def convert_cfiles_symbols(data_dir='.', out_extension='.nosym', save=False,
                           save_dir=None, in_extension='',
                           symbol_json_filename="C_SYMBOL_MAP.json",
                           recurse=0):
    walk = os.walk(data_dir)
    c_texts = []
    symbol_dict = json_to_dict(symbol_json_filename)
    for root, dirnames, filenames in walk:
        for filename in filenames:
            if os.path.splitext(filename)[1] == in_extension:
                in_path = os.path.join(root, filename)
                if save_dir:
                    if not os.path.exists(save_dir):
                        os.mkdir(save_dir)
                    out_path = os.path.join(save_dir, filename)
                else:
                    out_path = in_path
                if len(in_extension) > 0:
                    out_path = out_path.replace(in_extension,
                                                out_extension)
                else:
                    out_path += out_extension
                nosym = convert_cfile_symbols(in_path,
                                              symbol_dict=symbol_dict)
                c_texts.append(nosym)
                if save:
                    with open(out_path, 'w') as file:
                        file.write(str(nosym))
        return c_texts


def convert_cfile_symbols(in_filename, symbol_dict=None,
                          symbol_json_filename="C_SYMBOL_MAP.json"):
    """
        This function converts all C operators into unique tokens which allows
        them to be viewed as tokens by the parser.
    """
    if not symbol_dict or type(symbol_dict) is not dict:
        symbol_dict = json_to_dict(symbol_json_filename)

    with open(in_filename, "r") as file:
        c_text = str(file.read())

    """
    Replace the longest symbols first to avoid collision. Pad the replacement
    strings to prevent token collision.

    Using solution from
    https://stackoverflow.com/questions/11753809/sort-dictionary-by-key-length
    """
    for punc in sorted(symbol_dict, key=len, reverse=True):
        c_text = c_text.replace(punc, pad_string(symbol_dict[punc], 1))
    c_text = c_text.replace("\n", " \n ")  # Pad the beginning and end of lines
    c_text = pad_string(c_text, 1)  # Pad the beginning and end of file
    return c_text


def convert_symbols_to_cfile(in_filename, out_filename,
                             symbol_json_filename="C_SYMBOL_MAP.json"):
    """
    """
    symbol_dict = json_to_dict(symbol_json_filename)

    # flush the output file
    with open(out_filename, "w") as out_file:
        out_file.write("")

    with open(in_filename, "r") as in_file:
        for line in in_file:
            for k, v in symbol_dict.items():
                line = line.replace(v.strip(), k)
            with open(out_filename, "a") as out_file:
                out_file.write(line+'\n')
