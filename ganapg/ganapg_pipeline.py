import ganapg_preprocess_tokens as gtok
import ganapg_vocabulary as gvoc
from ganapg_util import query_yes_no, py3
import ganapg_preprocess_ast as gast
import ganapg_config as cfg
if py3():
    from ganapg_pymarkov import Ganapg_Markov
import subprocess as sp
import os
import sys


class Pipeline():
    """
        The Pipeline class controls experiment flow based on the steps outlined
        in ganapg_config.py. The entire experimental process including
        preprocessing, model training, and evaluation is broken into a
        number of steps defined in the config file.

        The results of each run are saved locally, also according to definition
        in the config file, and can be saved locally.

        Currently finished:
            SeqGan with Token and AST Preprocessing
            Seq2Seq with Token and AST Preprocessing
            Markov model with Token and AST Preprocessing

        Currenlty TODO:
            Comprehensive cross-evaluation of diselffferent models
            Deepfix model with Token and AST Preprocessing
            Integration of all models into python (currently the pipeline
                                                   relies on external calls)

    """

    def __init__(self, method='cf_ast_seqgan', skip=[]):
        print('Running model %s' % method)
        self.meth = getattr(cfg, method)
        self.data_dir = self.meth['data_dir']
        self.meth['steps'] = [s for s in self.meth['steps'] if s not in skip]
        self.extension = None
    def run(self):
        for step in self.meth['steps']:
            save_dir = self.meth['save_dir'][step]
            save = self.meth['save']
            if step is 'obfuscate':
                print('Obfuscating cfiles')
                self.extension = '.obfs'
                if not query_yes_no("Are you sure you want to re-obfuscate?"
                                    " It will take a few seconds longer than"
                                    " the other steps."):
                    continue
                gtok.obfuscate_cfiles(data_dir=self.data_dir,
                                      recurse=1, save_dir=None,
                                      save=save)
                # self.data_dir = save_dir if save_dir else '.'
            elif step is 'symbols':
                print('Converting symbols to tokens')
                self.extension = '.nosym'
                if os.path.exists(save_dir):
                    if not query_yes_no("Looks like this data has already been"
                                        " generated. Rebuild?"):
                        self.data_dir = save_dir if save_dir else '.'
                        continue
                gtok.convert_cfiles_symbols(data_dir=self.data_dir,
                                            save_dir=save_dir,
                                            save=save)
                self.data_dir = save_dir if save_dir else '.'
            elif step is 'posneg':
                print('Creating positive/negative splits')
                if not query_yes_no("Looks like this data has already been "
                                    "generated. Rebuild?"):
                    self.data_dir = save_dir if save_dir else '.'
                    continue
                gtok.codeflaws_posneg(data_dir=self.data_dir,
                                      save_dir=save_dir,
                                      extension=self.extension,
                                      save=save)
                self.data_dir = save_dir if save_dir else '.'
            elif step is 'vocabgen':
                print('Generating vocabulary')
                gvoc.generate_vocab_to_file(data_dir=self.data_dir,
                                            vocab_filename=cfg.BASE_VOCAB,
                                            out_filename=self.meth['vocab'])
            elif step is 'vocabhash':
                self.extension = '.hash'
                print('Hashing codeflaws files')
                if not query_yes_no("Looks like this data has already been "
                                    "generated. Rebuild?"):
                    self.data_dir = save_dir if save_dir else '.'
                    continue
                vocabfile = self.meth['vocab']
                gvoc.hash_files(data_dir=self.data_dir,
                                vocabfile=vocabfile,
                                save_dir=save_dir,
                                save=save)
                self.data_dir = save_dir if save_dir else '.'
            elif step is 'astseq':
                print('Generating AST sequences')
                if not query_yes_no("Looks like this data has already been "
                                    "generated. Rebuild?"):
                    continue
                gast.cfiles_to_nodesequences(data_dir=self.data_dir,
                                             save_dir=None,
                                             save=save, recurse=0)
            elif step is 'seqtok':
                self.extension = '.seq.hash'
                print('Generating AST tokens')
                if not query_yes_no("Looks like this data has already been "
                                    "generated. Rebuild?"):
                    continue
                _, v = gast.nodesequences_to_tokens(data_dir=self.data_dir,
                                                    save_dir=None,
                                                    save=save)
                print('Redumping AST vocabulary')
                gvoc.list_to_vocabfile(v.get_feature_names(),
                                       self.meth['vocab'])
            elif step is 'seq2seq':
                self._config_seq2seq()
                self._run_seq2seq()
                self._eval_seq2seq()
            elif step is 'seqgan':
                self._config_seqgan()
                self._run_seqgan()
                self._eval_seqgan()
            elif step is 'markov':
                self._config_markov()
                self._run_markov()
                self._eval_markov()
            elif step is 'deepfix':
                self._config_deepfix()
                self._run_deepfix()
                self._eval_deepfix()
    """
        The following functions make external calls to the libraries which
        run particular models. This follows the recommended protocol for each
        of the libraries. TODO: Reconfigure the libraries so that calls can
        be made entirely within python, without calling subprocesses.
    """

    def _config_seqgan(self):
        # Currently nothing to configure externally
        return

    def _run_seqgan(self):
        cmd = ('python2 %s --pos %s --neg %s' % (self.meth['run'],
                                            self.data_dir+self.meth['pos'],
                                            self.data_dir+self.meth['neg']))
        print("In config seqgan calling:\n\t%s" % cmd)
        o = sp.check_output([cmd], shell=True)
        # print(o)
        return

    def _eval_seqgan(self):
        # Currently nothing to evaluate externally
        return

    def _config_seq2seq(self):
        """
            This function is currently a hacky workaround to implement the
            seq2seq library as was initially done with the shell files prior
            to building the python module.
            It does, however, work.

            TODO: Instead of adding environment variables, just call the 
            python script directly with command line arguments corresponding
            to these arguments.
        """
        print(self.meth['neg'], self.meth['pos'])
        os.environ['DATA_PATH'] = '../ganapg/'+self.data_dir
        os.environ['VOCAB_NAME'] = self.meth['vocab']
        os.environ['TRAIN_NAME'] = self.meth['neg']
        os.environ['TARGET_NAME'] = self.meth['pos']
        os.environ['MODEL_NAME'] = self.meth['name']
        os.environ['TRAIN_STEPS'] = str(self.meth['iters'])
        model_dir = '../ganapg/%s/' % (
                                                self.meth['name']+'_model')
        pred_dir = '../ganapg/%s/' % (
                                              self.meth['name']+'_predictions')
        os.environ['VOCAB_SOURCE'] = '../ganapg/%s' % self.meth['vocab']
        os.environ['VOCAB_TARGET'] = '../ganapg/%s' % self.meth['vocab']
        os.environ['TRAIN_SOURCES'] = '../ganapg/%s/%s' % (self.data_dir,
                                                   self.meth['neg'])
        os.environ['TRAIN_TARGETS'] = '../ganapg/%s/%s' % (self.data_dir,
                                                   self.meth['pos'])
        os.environ['DEV_SOURCES'] = '../ganapg/'+'%s_posneg/neg' % self.meth['name']
        os.environ['DEV_TARGETS'] = '../ganapg/'+'%s_posneg/pos' % self.meth['name']
        os.environ['DEV_TARGETS_REF'] = '../ganapg/'+'%s_posneg/pos' % self.meth['name']
        os.environ['MODEL_DIR'] = model_dir
        os.environ['PRED_DIR'] = pred_dir
        if not os.path.exists(model_dir):
            os.mkdir(model_dir)
        if not os.path.exists(pred_dir):
            os.mkdir(pred_dir)
        return

    def _run_seq2seq(self):
        cmd = './%s' % (self.meth['run'])
        print("In run seq2seq calling:\n\t%s" % cmd)
        o = sp.check_output([cmd], shell=True)
        # print(e)

    def _eval_seq2seq(self):
        cmd = './%s' % (self.meth['eval'])
        print("In run seq2seq calling:\n\t%s" % cmd)
        o = sp.check_output([cmd], shell=True)
        # print(o)

    def _config_markov(self):
        self.markov = Ganapg_Markov(data_dir=self.data_dir,
                                    in_filename=self.meth['pos'],
                                    save_dir=self.meth['save_dir'],
                                    save=self.meth['save'])
        return

    def _run_markov(self):
        self.markov.build()
        return

    def _eval_markov(self):
        with open(os.path.join(self.data_dir, self.meth['neg'])) as file:
            prediction = self.markov.predict(file.read(), 100)
        self.prediction = prediction
        print(self.prediction)
        return

    def _config_deepfix(self):
        # Currently nothing to configure externally
        print("The deepfix library is broken and not yet implemented")
        return

    def _run_deepfix(self):
        # Currently nothing to run externally
        print("The deepfix library is broken and not yet implemented")
        return

    def _eval_deepfix(self):
        # Currently nothing to evaluate externally
        print("The deepfix library is broken and not yet implemented")
        return


if __name__ == '__main__':
    if len(sys.argv) > 1:
        PL = Pipeline(skip=[], method=sys.argv[1])
    else:
        PL = Pipeline(skip=[])
    PL.run()
