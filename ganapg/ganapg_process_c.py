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
from ganapg_util import py3


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


def ganapg_traintest_split(data_dir='.', extension='.obfs',
                           trainfile='train', testfile='target', recurse=0):
    walk = os.walk(data_dir)
    alldata = []
    for root, dirnames, filenames in walk:
        if recurse:
            # Until the recursion level is 0, go through all child dirs
            for dirname in dirnames:
                obfuscate_cfiles(data_dir=dirname, extension=extension,
                                 trainfile='train', testfile='target',
                                 recurse=recurse - 1)
        for filename in filenames:
            if os.path.splitext(filename)[1] is extension:
                in_path = os.path.join(root, filename)
                with open(in_path, 'rb') as file:
                    text = file.read().decode('utf-8')
                    alldata.append(text)
    train, test = train_test_split(alldata, shuffle=True)
    with open(trainfile,'w') as file:
        for instance in train:
            file.write(instance+'\n')
    with open(testfile,'w') as file:
        for instance in test:
            file.write(instance+'\n')


def codeflaws_posneg(header='', dd='/home/bbradt/AGAN/data/codeflaws',
                        post='.obfs.c', posfile='pos.c',negfile='neg.c'):
    walk = os.walk(dd)
    posdata = []
    negdata = []
    for root, dirs, files in walk:
        for sdir in dirs:
            swalk = os.walk(os.path.join(dd, sdir))
            for sroot, sdirs, sfiles in swalk:
                contestid,problem,_,negid,posid = sdir.split('-')
                posid = '-'.join([contestid,problem,posid])
                negid = '-'.join([contestid,problem,negid])
                pospath = os.path.join(sroot+'/',posid+post)
                negpath = os.path.join(sroot+'/',negid+post)

                with open(pospath,'r') as f:
                    fr = f.read()
                    posdata.append(fr)
                with open(negpath,'r') as f:
                    fr = f.read()
                    negdata.append(fr)
    with open(posfile,'w') as file:
        for instance in posdata:
            file.write(instance+'\n')
    with open(negfile,'w') as file:
        for instance in negdata:
            file.write(instance+'\n')