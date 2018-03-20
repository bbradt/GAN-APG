#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Nov 13 01:06:24 2017
Config file for GANAPG file
@author: bbradt
"""

CODEFLAWS_DIR = '../data/codeflaws/'
SEQGAN_DIR = '../SeqGAN'
SEQ2SEQ_DIR = '../seq2seq'
MARKOV_DIR = ''
DEEPFIX_DIR = ''
BASE_VOCAB = './vocab/c_base_vocab.txt'
ALL_STEPS = ['astseq',
             'obfuscate',
             'symbols',
             'posneg',
             'vocabgen',
             'vocabhash',
             'seqgan',
             'seq2seq',
             'deepfix',
             'seqtok',
             'markov']


name = 'cf_tokens_seqgan'
cf_tokens_seqgan = {'name': name,
                    'steps': ['obfuscate',
                              'posneg',
                              'symbols',
                              'vocabgen',
                              'vocabhash',
                              'seqgan'],
                    'data_dir': CODEFLAWS_DIR,
                    'save': True,
                    'save_dir': {k: './%s_%s/' % (name, k) for k in ALL_STEPS},
                    'vocab': './%s_vocabgen/vocab.txt' % name,
                    'config': None,
                    'run': '%s/sequence_gan.py' % SEQGAN_DIR,
                    'eval': None,
                    'pos': 'pos.hash',
                    'neg': 'neg.hash'
                    }

name = 'cf_tokens_seq2seq'
cf_tokens_seq2seq = {'name': name,
                     'steps': ['obfuscate',
                               'posneg',
                               'symbols',
                               'vocabgen',
                               'seq2seq'],
                     'data_dir': CODEFLAWS_DIR,
                     'save': True,
                     'save_dir':
                         {k: './%s_%s/' % (name, k) for k in ALL_STEPS},
                     'iters': 2000,
                     'vocab': './%s_vocabgen/vocab.txt' % name,
                     'config': 'ganapg_export_seq2seq.sh',
                     'run': 'ganapg_run_seq2seq.sh',
                     'eval': 'ganapg_predict_seq2seq.sh',
                     'pos': 'pos.nosym',
                     'neg': 'neg.nosym'
                     }

name = 'cf_tokens_markov'
cf_tokens_markov = {'name': name,
                    'steps': ['obfuscate',
                              'posneg',
                              'symbols',
                              'vocabgen',
                              'markov'],
                    'data_dir': CODEFLAWS_DIR,
                    'save': True,
                    'save_dir': {k: './%s_%s/' % (name, k) for k in ALL_STEPS},
                    'vocab': './%s_vocabgen/vocab.txt' % name,
                    'pos': 'pos.nosym',
                    'neg': 'neg.nosym'
                    }

name = 'cf_tokens_deepfix'
cf_tokens_deepfix = {'name': name,
                     'steps': ['obfuscate',
                               'posneg',
                               'symbols',
                               'vocabgen',
                               'vocabhash',
                               'deepfix'],
                     'data_dir': CODEFLAWS_DIR,
                     'save': True,
                     'save_dir':
                         {k: './%s_%s/' % (name, k) for k in ALL_STEPS},
                     'vocab': './%s_vocabgen/vocab.txt' % name
                     }

name = 'cf_ast_seqgan'
cf_ast_seqgan = {'name': name,
                 'steps': ['astseq',
                           'seqtok',
                           'posneg',
                           'vocabgen',
                           'vocabhash',
                           'seqgan'],
                 'data_dir': CODEFLAWS_DIR,
                 'save': True,
                 'save_dir': {k: './%s_%s/' % (name, k) for k in ALL_STEPS},
                 'vocab': './%s_vocabgen/vocab.txt' % name,
                 'config': None,
                 'run': '%s/sequence_gan.py' % SEQGAN_DIR,
                 'eval': None,
                 'pos': 'pos.hash',
                 'neg': 'neg.hash'
                 }

name = 'cf_ast_seq2seq'
cf_ast_seq2seq = {'name': name,
                  'steps': ['astseq',
                            'seqtok',
                            'posneg',
                            #'vocabgen',
                            #'vocabhash',
                            'seq2seq'],
                  'data_dir': CODEFLAWS_DIR,
                  'save': True,
                  'save_dir': {k: './%s_%s/' % (name, k) for k in ALL_STEPS},
                  'iters': 2000,
                  'vocab': './%s_vocabgen/vocab.txt' % name,
                  'run': 'ganapg_run_seq2seq.sh',
                  'eval': 'ganapg_predict_seq2seq.sh',
                  'pos': 'pos',
                  'neg': 'neg'
                  }

name = 'cf_ast_markov'
cf_ast_markov = {'name': name,
                 'steps': ['astseq',
                          # 'seqtok',
                           'posneg',
                           'markov'],
                 'data_dir': CODEFLAWS_DIR,
                 'save': True,
                 'save_dir': {k: './%s_%s/' % (name, k) for k in ALL_STEPS},
                 'vocab': './%s_vocabgen/vocab.txt' % name
                 }

name = 'cf_ast_deepfix'
cf_ast_deepfix = {'name': name,
                  'steps': ['astseq',
                            'vocabgen',
                            'vocabhash',
                            'deepfix'],
                  'data_dir': CODEFLAWS_DIR,
                  'save': True,
                  'save_dir': {k: './%s_%s/' % (name, k) for k in ALL_STEPS},
                  'vocab': './%s_vocabgen/vocab.txt' % name
                  }

name = 'ganapg_config'
