#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 13 04:14:26 2017

@author: bbradt
"""
import os


from python_markov.markov.chain.markov_perf import markov_perf as markov


class Ganapg_Markov():
    """
        Implement the python-markov library
        which is a simple model, but which is not
    """
    def __init__(self, data_dir='.', in_filename='pos',
                 save_dir=None, save=True):
        file_contents = []
        with open(os.path.join(data_dir, in_filename), "r") as in_file:
            for line in in_file:
                file_contents += line.split()
        self.data = file_contents

    def build(self):
        self.chain = markov(self.data)

    def predict(self, text, N, m=2):
        prediction = ''
        text=text.replace('\n', '')
        text_slice = text.split()[-m:]
        print(text_slice)
        for i in range(N):
            try:
                next_prediction = self.chain[tuple(text_slice)]
                prediction += next_prediction + ' '
                text_slice = text_slice[1:]
                text_slice.append(next_prediction)
            except KeyError:
                text_slice = text_slice[1:]
                continue
        return(prediction)
