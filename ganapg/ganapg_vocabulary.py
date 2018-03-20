#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This file deals with vocabulary generation, and with other functions related
to vocabulary and vectorization of string files. These are kept separate
from other preprocessing steps, because they are not required for all input
methods (e.g. seq2seq does not require vectorziation, but SeqGAN does)


@author: Brad Baker
"""


import os
import re
from ganapg_util import pad_string as pad


def list_to_vocabfile(vocab_list, filename):
    if not os.path.exists(os.path.dirname(filename)):
        os.makedirs(os.path.dirname(filename))
    with open(filename, "w") as file:
        for word in vocab_list:
            file.write(word.strip() + '\n')


def vocabfile_to_list(filename):
    with open(filename, 'r') as file:
        return [word for word in file]


def vocabfile_to_hashdict(vocabfile):
    """
        A basic vocabulary hashing strategy just uses the line indices
        of each vocabulary word to generate sequential hashes. Thus,
        unique hashes are provided for each word in the vocabulary, and the
        hash is trivially reversable for easy re-translation.
    """
    hash_dict = {}
    hash_index = 0
    with open(vocabfile, "rb") as file:
        for line in file:
            line = line.decode('utf-8')
            line = line.strip().replace('\n', '')  # to prevent bad encoding
            hash_dict[line] = hash_index
            hash_index += 1
    return hash_dict


def hash_files(data_dir='.', vocab_hashdict=None, vocabfile=None, save=True,
               out_filenames=None, save_dir=None):
    for _, _, filenames in os.walk(data_dir):
        for i, filename in enumerate(filenames):
            out_filename = None
            if out_filenames and i < len(out_filenames):
                out_filename = out_filenames[i]
            hash_file(filename, data_dir=data_dir,
                      vocab_hashdict=vocab_hashdict,
                      save=save, vocabfile=vocabfile,
                      out_filename=out_filename,
                      save_dir=save_dir)


def hash_file(in_filename, data_dir='.', vocab_hashdict=None, save=True,
              vocabfile=None, out_filename=None, save_dir=None,
              out_extension='.hash'):
    """
        Use a given hashdict, or load a dict to hash a particular file
        token-wise, and line-by-line.
    """
    in_filepath = os.path.join(data_dir, in_filename)
    if not out_filename:
        #  if no filename was entered, just modify the in_filename
        in_extension = os.path.splitext(in_filename)[1]
        if save_dir:
            if not os.path.exists(save_dir):
                os.mkdir(save_dir)
            out_filename = os.path.join(save_dir, in_filename)
        else:
            out_filename = in_filepath
        out_filename = out_filename.replace(in_extension, out_extension)
        print(out_filename)

    if not vocab_hashdict or type(vocab_hashdict) is not dict:
        if not vocabfile:
            raise Exception("""ganapg_vocabulary: hash_file:
                                    you must enter a vocabulary or a file
                                    containing a vocabulary""")
        vocab_hashdict = vocabfile_to_hashdict(vocabfile)
    if save:
        with open(out_filename, 'wb') as out_file:
            # Flush the output
            out_file.write(b'')
    out_txt = ''
    with open(in_filepath, 'r') as in_file:
        for in_line in in_file:
            """
                The keys of the vocab_dict should be strings (but we cast just
                to be sure), some of which occur in the input line. Thus,
                we can use pythonic list comprehension to get token-wise
                hashed string, with each hashed string separated by spaces.
            """
            out_line = " ".join([str(v) for k, v in vocab_hashdict.items()
                                if str(k).strip() in in_line.split()])
            out_line = out_line.replace('\n', '')  # to prevent double newlines
            if save:
                with open(out_filename, 'a') as out_file:
                    out_file.write(' '.join(out_line.split()) + '\n')
            out_txt += ' '.join(out_line.split()) + '\n'
    return out_txt


def unhash_file(in_filename, vocab_hashdict=None,
                vocab_filename=None, out_filename=None):
    """
        Invert the hashing process from the hash_file function. We can
        exploit the design of the hash_file to do this without rewriting.
    """
    if not out_filename:
        #  if no filename was entered, just modify the in_filename
        in_extension = os.path.split(in_filename)[1]
        if len(in_extension) > 0:
            out_filename = in_filename.replace(in_extension, '.unhash')
        else:
            out_filename += '.unhash'

    if not vocab_hashdict or type(vocab_hashdict) is not dict:
        if not vocab_filename:
            raise Exception("""ganapg_vocabulary: hash_file:
                                    you must enter a vocabulary hashdict
                                    or a file containing a vocabulary""")
        vocab_hashdict = vocabfile_to_hashdict(vocab_filename)

    # We can just pass the inverse hash to the above function to invert
    inverse_hash = {v: k for k, v in vocab_hashdict.items()}
    hash_file(in_filename, vocab_hashdict=inverse_hash,
              out_filename=out_filename)


def generate_vocab(data_dir, in_filenames=None, in_extension=None,
                   vocab_list=None, vocab_filename=None):
    if not vocab_list or type(vocab_list) is not list:
        if not vocab_filename:
            vocab_list = []
        else:
            vocab_list = vocabfile_to_list(vocab_filename)
    if type(in_filenames) is not list:
        if type(in_filenames) is str:
            in_filenames = [in_filenames]
        else:
            for _, _, filenames in os.walk(data_dir):
                in_filenames = filenames
                if in_extension:
                    in_filenames = [f for f in filenames
                                    if os.path.split(f)[1] is in_extension]

    for in_filename in in_filenames:
        with open(os.path.join(data_dir, in_filename)) as train:
            vocab_list += [word for line in train for word in line.split()]

    # Remove whitespace, tabs, and newlines from tokens
    vocab_list = [re.sub('\n\t', '', word.strip()) for word in vocab_list]

    # Only return unique tokens
    return set(vocab_list)


def generate_vocab_to_file(data_dir, in_filenames=None, vocab_list=None,
                           in_extension=None, save_dir=None,
                           vocab_filename=None, out_filename=None):
    if not out_filename:
        out_filename = "vocab.txt"
    if save_dir:
        if not os.path.exists(save_dir):
                os.mkdir(save_dir)
        out_filename = os.path.join(save_dir, out_filename)
    if not os.path.exists(os.path.dirname(out_filename)):
        os.makedirs(os.path.dirname(out_filename))
    vocab_list = generate_vocab(data_dir, in_filenames=in_filenames,
                                vocab_list=vocab_list,
                                vocab_filename=vocab_filename)

    with open(out_filename, "w") as file:
        for word in vocab_list:
            file.write(word + '\n')
