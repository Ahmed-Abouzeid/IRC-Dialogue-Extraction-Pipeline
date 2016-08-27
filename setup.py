from setuptools import setup

setup(name='IRC-Processing', packages=['irc_process'], version='0.1',
      description='The Software is a framework to automate the work\n'
                  'required for creating very large corpora for Data\n'
                  'Driven Dialogue Systems. The tasks that can be done\n'
                  'by the software are as below:\n 1.Downloading IRC Logs'
                  'from different logging sites\n 2.Cleaning and transforming'
                  'the crawled data prior to further pre-processing\n'
                  ' 3.Apply certain algorithms required to extract one on one\n'
                  ' dialogues from all the historical logs \n\nThe output of Dialogue.Py'
                  ' is compatible with the\nLabeled Data-set creation software published'
                  ' by McGill University\non https://github.com/ryan-lowe/Ubuntu-Dialogue-Generationv2',
      author='Ahmed Abouzeid', author_email='ahmedabouzeid.cs@gmail.com', license='MIT', install_requires=
      ['progress', 'sqlalchemy', 'nltk', 'stemming'])
