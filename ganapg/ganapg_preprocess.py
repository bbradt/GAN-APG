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


def obfuscate_cfiles(data_dir='.', extension='.obfs',
                     gcc_path='/usr/bin/gcc',  save_dir=None, recurse=0):
    """
        Recursively obfuscate c files in a directory by placing all code on
        one line, removing include statements, and removing comments.
        This simplifies data assembly and processing by allowing one instance
        (one c-file) on one line in the training and testing sets.
    """
    walk = os.walk(data_dir)
    for root, dirnames, filenames in walk:
        if recurse:
            # Until the recursion level is 0, go through all child dirs
            for dirname in dirnames:
                obfuscate_cfiles(data_dir=dirname, extension=extension,
                                 gcc_path=gcc_path, save_dir=save_dir,
                                 recurse=recurse - 1)
        for filename in filenames:
            if os.path.splitext(filename)[1] is '.c':
                in_path = os.path.join(root, filename)
                if save_dir:
                    out_path = os.path.join(save_dir, filename)
                else:
                    out_path = in_path

                # Replace the file extension to avoid duplication in data
                out_path = out_path.replace('.c', extension)

                if os.path.exists(gcc_path):
                    # Use GCC to remove comments, if gcc is available
                    gcc_cmd = ('%s -fpreprocessed -dD -E %s'
                               % (gcc_path, out_path))
                    c_text = subprocess.check_output(gcc_cmd, shell=True)
                else:
                    # Otherwise, only load the file without processing comments
                    with open(in_path, "rb") as file:
                        c_text = file.read().decode('utf-8')

                # Remove all include statements
                c_text = re.sub('#include.*>', ' ', c_text, flags=re.DOTALL)

                # Place all code on one line
                c_text = re.sub('\t\n\\t\\n', '', c_text.strip())

                # Write to file
                with open(out_path, 'w') as f:
                    f.write(c_text)


def traintest_split(data_dir='.', extension='.obfs',
                           trainfile='train', testfile='target', recurse=0,
                           testsize=0.1):
    walk = os.walk(data_dir)
    all_data = []
    for root, dirnames, filenames in walk:
        if recurse:
            # Until the recursion level is 0, go through all child dirs
            for dirname in dirnames:
                all_data += ganapg_traintest_split(data_dir=dirname,
                                                   extension=extension,
                                                   recurse=recurse - 1)
        for filename in filenames:
            if os.path.splitext(filename)[1] is extension:
                in_path = os.path.join(root, filename)
                with open(in_path, 'rb') as file:
                    text = file.read().decode('utf-8')
                    all_data.append(text)

    # if we are still recursing, push alldata up the stack
    if recurse:
        return all_data

    train, test = train_test_split(all_data, shuffle=True, testsize=testsize)
    # Write to files, splitting instances by newlines
    with open(trainfile, 'wb') as file:
        for instance in train:
            file.write(instance+'\n')
    with open(testfile, 'wb') as file:
        for instance in test:
            file.write(instance+'\n')
    return train, test, all_data


def codeflaws_posneg(header='', data_dir='.', extension='.obfs',
                            posfile='pos', negfile='neg', recurse=0):
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
            pospath = os.path.join(root, pos_filename)
            negpath = os.path.join(root, neg_filename)

            with open(pospath, 'rb') as file:
                c_text = file.read().decode('utf-8')
                posdata.append(c_text)
            with open(negpath, 'rb') as file:
                c_text = file.read()
                negdata.append(c_text)

    # Write files
    with open(posfile, 'wb') as file:
        for instance in posdata:
            file.write(instance + '\n')
    with open(negfile, 'w') as file:
        for instance in negdata:
            file.write(instance + '\n')


def convert_cfile_to_symbols(datadir,infile,outfile,
                         punc_map="PUNC_MAP.json"):
    """
        This function converts all C operators into unique tokens which allows
        them to be viewed as tokens by the parser.
    """
    
    with open(punc_map,"r") as jsfile:
        pm = json.load(jsfile)
    with open(infile, "r") as f:
        fr = f.read()
    for punc in sorted(pm, key=len, reverse=True):
         fr = fr.replace(punc," " + pm[punc] + " ")
    fr = fr.replace('\n', ' \n ')
    fr = " " + fr + " "
    with open(outfile, "w") as f:
        f.write(fr)
    return fr


def convert_symbols_words(infile,outfile,punc_map="PUNC_MAP.json"):
    with open(punc_map,"r") as jsfile:
        pm = json.load(jsfile)
    with open(outfile, "w") as wf:
        with open(infile, "r") as f:
            for line in f:
                for k, v in pm.items():
                    line = line.replace(v.strip(), k)
                wf.write(line+'\n')






def vocab_to_hash(vocabfile='c_ext.vocab'):
    hash_dict = {}
    hash_index = 0
    with open(vocabfile, "r") as file:
        for line in file:
            line = line.strip().replace('\n','')
            hash_dict[line] = hash_index
            hash_index += 1
    #print(hash_dict)
    return hash_dict


def file_to_hash(infilename,vocab,outfilename=''):
    if outfilename == '':
        outfilename = infilename + '.hash'
    with open(outfilename, 'w') as outfile:
        outfile.write('')
    with open(infilename, 'r') as infile:
        for line in infile:
            found = {' '+str(k).strip()+' ': ' '+str(v)+' ' for k,v in vocab.items() if ' '+str(k).strip()+' ' in line}
            outline = ''
            for token in line.split():
                token = found[' '+token.strip()+' ']
                outline += token
            outline = outline.replace('\n','')
            with open(outfilename, 'a') as outfile:
                outfile.write(' '.join(outline.split()) + '\n')


def hash_to_file(infilename,vocab,outfilename=''):
    if outfilename == '':
        outfilename = infilename.replace('.hash','.unhash')
    inv_vocab = {v:k for k,v in vocab.items()}
    with open(infilename, 'r') as infile:
        for line in infile:
            print([[k,str(k) in line] for k,v in inv_vocab.items()])
            found = {str(k): v for k,v in inv_vocab.items() if str(k) in line}
            outline = ''
            print(found)
            print(line)
            for token in line.split():
                token = found[token.strip()]
                outline += token
            outline = outline.replace('\n','')
            with open(outfilename, 'a') as outfile:
                outfile.write(' '.join(outline.split()) + '\n')