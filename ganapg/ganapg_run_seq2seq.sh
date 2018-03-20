#!/bin/bash

: <<'END'
This script runs the seq2seq framework using exported environment variables.
Currently it just uses the medium configuration and default training parameters.
TODO : Choose configuration from command line/ from python pipeline
END
cd ../seq2seq

python2 -m bin.train \
  --config_paths="
      ./example_configs/nmt_small.yml,
      ./example_configs/train_seq2seq.yml" \
  --model_params "
      vocab_source: $VOCAB_SOURCE
      vocab_target: $VOCAB_TARGET" \
  --input_pipeline_train "
    class: ParallelTextInputPipeline
    params:
      source_files:
        - $TRAIN_SOURCES
      target_files:
        - $TRAIN_TARGETS" \
  --input_pipeline_dev "
    class: ParallelTextInputPipeline
    params:
       source_files:
        - $DEV_SOURCES
       target_files:
        - $DEV_TARGETS" \
  --batch_size 32 \
  --train_steps $TRAIN_STEPS \
  --output_dir $MODEL_DIR
