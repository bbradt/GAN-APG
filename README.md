# GAN-APG

## Generative Adversarial Networks for Automatic Patch Generation

## author: Brad Baker

Running 'make' will untar all of the files in the directory
Note that the data.tar.gz file contains a lot of files, since it now tracks some of the preprocessing
stages to avoid unnecessary reprocessing 
and will take a while to uncompress.

cd ganapg to enter the working directory for the project. 

Most of the models should work both in python 2 or 3, but it's typically more
reliable to run them in python 2.

This module requires the following python modules:
	numpy
	sklearn
	scipy
	pycparser
	progressbar
	tensorflow <= 1.2.1
	
You can run the default model (SeqGan with Token preprocessing) by running
	python2 ganapg_pipeline.py


Currently, you can switch between the different models on the command line:	
	# For example with token-based preprocessing
	python ganapg_pipeline.py cf_tokens_seqgan
	python ganapg_pipeline.py cf_tokens_seq2seq

You can also run the AST preprocessing models:
	python ganapg_pipeline.py cf_ast_seqgan
	python ganapg_pipeline.py cf_ast_seq2seq

Each model will generate files in cf_<MODEL_NAME>_<OPERATION> directories. 
Some of these directories have already been included, and you can choose to just
skip over the preprocessing if you do not want to regenerate them and run the model itself.

The models output to different directories currently:
	seqgan outputs predicitons and model checkpoints to ../SeqGAN/save
	seq2seq outputs predictions and model checkpoints ./<MODEL_NAME>_{model, predictions}


To run the suite of classifiers on the AST-based data, you can cd to the clfsuite directory
and run
	python ClassSuite.py

you will need to reconfigure the main call in the script to rerun on the tokenized data set. 

To regenerate the figure included in the paper, run
	python clfsuite_plot.py

you will need the seaborn, matplotlib, and pandas libraries to run the plotting script.

[embed]https://github.com/bbradt/GAN-APG/blob/master/seqgan-apg-sequential.pdf[/embed]
