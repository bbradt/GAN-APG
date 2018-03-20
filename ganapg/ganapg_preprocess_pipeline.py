import ganapg_preprocess_tokens as gtok
import ganapg_vocabulary as gvoc
import ganapg_preprocess_ast as gast
import ganapg_config as cfg

class Pipeline():

    default_steps = ['obfuscate',
                     'symbols',
                     'posneg',
                     'vocabgen',
                     'vocabhash'
                     ]

    default_data_dir = '/home/bbradt/AGAN/data/codeflaws/'

    def __init__(self, method='cf_tokens_seqgan'):
        self.m = getattr(cfg, method)

    def run(self):
        #  Run with default parameters for codeflaws with seqgan
        for step in self.steps:
            if step is 'obfuscate':
                print('Obfuscating cfiles')
                gtok.obfuscate_cfiles(data_dir=self.data_dir,
                                      recurse=1, save_dir='./obfuscated_c/',
                                      save=True)
            elif step is 'symbols':
                print('Converting symbols to tokens')
                gtok.convert_cfiles_symbols(data_dir='./cf_obfs/',
                                            save_dir='./cf_nosym/',
                                            save=True)
            elif step is 'posneg':
                print('Creating positive/negative splits')
                gtok.codeflaws_posneg(data_dir='./cf_nosym/',
                                      save_dir='./cf_posneg/',
                                      save=True)
            elif step is 'vocabgen':
                print('Generating vocabulary')
                gvoc.generate_vocab_to_file(data_dir='./cf_posneg/',
                                            save_dir='./cf_vocab/',
                                            save=True)
            elif step is 'vocabhash':
                print('Hashing codeflaws files')
                gvoc.hash_files(data_dir='./cf_posneg/',
                                vocabfile='./cf_vocab/vocab.txt',
                                save_dir='./cf_hashed/')
            elif step is 'astseq':
                print('Generating AST sequences')
                gast.cfiles_to_nodesequences(data_dir=self.method['data_dir'],
                                    save_dir=self.method['save_dirs'][step],
                                    save=self.method['save'])
                
if __name__ == '__main__':
    PP = PreprocPipeline()
    PP.cf_run()
