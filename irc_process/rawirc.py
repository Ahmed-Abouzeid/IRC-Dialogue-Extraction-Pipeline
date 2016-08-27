"""The RawIRC Module Is The Second Main Component In The IRC Post-Processing Software
It Works On Cleaning & Recognizing Recipients In Utterances"""
from __future__ import division
import os
import shutil
import re
import argparse
import datetime
import time
import logging
import enchant
from progress.bar import Bar
__author__ = 'Ahmed Abouzeid'

DICT = enchant.Dict("en_US")
logging.basicConfig(filename='RawIRC.log', filemode='w', level=logging.INFO)

###################################################################################################
# The RawIRC Class is dedicated for Cleaning, structuring and Recognizing Recipients in a raw IRC #
# logs                                                                                            #
#                                                                                                 #
# The RawIRC Class initiate a RawIRC instance by giving the below parameters values:              #
#                                                                                                 #
#  1- raw_data_path: this is the path of the crawled data that needs to be cleaned and recipient  #
#  will be recognized from each cleaned line later                                                #
#                                                                                                 #
#  2- time_regexp: the time pattern in the raw IRC logs crawled, so the software will be able to  #
#  recognize the time in a message in order to create the time field.                             #
#                                                                                                 #
#  3- old_date_format: the original date format in the crawled data file names, that is to change #
#  the date format of the messages to another date format                                         #
#                                                                                                 #
#  4- date_regexp : the pattern of the date format in the messages in order to be able to extract #
#  and recognize the date field.                                                                  #
#                                                                                                 #
#  5- clean_work_path: the path of the cleaned IRC logs which are tsv files that will be created  #
#                                                                                                 #
#  6- raw_msg_field_separator: the separator between raw IRC messages, so, if a crawled raw IRC   #
#  messages fields are only separated by a space or a tab or any other characters, the software   #
#  will be able to recognize each date and sender and message more easily. default is '' means not#
#  defined                                                                                        #
#                                                                                                 #
#  7- delete_cleaned_data: if set to yes, the generated cleaned tsv files will be deleted just    #
#  after processed to avoid consuming lot of memory resources                                     #
#                                                                                                 #
#  8- user_sys_annotations: if there is annotations surrounding the user names in the raw messages#
#  so, the software ignores it when extracting the users name or the sender field values. By      #
#  default set to '' which means no annotations                                                   #
#                                                                                                 #
#  9- time_sys_annotations: if there is any annotations surrounding the time field, so the        #
#  software ignore it when extracting the time field values. default is '' which means no annotat-#
#  ions                                                                                           #
#                                                                                                 #
#  10- recipient_only: for only run the create recipient algorithm                                #
#                                                                                                 #
#  11- clean_only: for only run the cleaning of the raw data without recognizing the recipients   #
#                                                                                                 #
#  12- concatenate: when you want to concatenate messages without a recipient to their relevant   #
#  message as sometimes a new IRC message is not a new msg as it can be rest of a previous msg    #
#                                                                                                 #
#  13- rtrim_time: when unwanted time fractions existed in the crawled IRC, like seconds          #
#   ltrim_time: when unwanted time additional strings existed in the crawled IRC from left side   #
#                                                                                                 #
#  14- time_user_lines: when in perl6 like structure data, when time is separated from user name  #
#   by number of empty lines, then you pass that argument with the number of empty lines          #
#                                                                                                 #
#  15- force_remove_sysmsg: when you need to explicitly tell component to remove certain message  #
#  while cleaning, these are some sys messages from IRC server and not needed, prepare a file and #
#  put the fixed part of such msg so the component will ignore any line contains these words      #
#                                                                                                 #
#  16- change_time_regexp: when a change in time format is needed to match further post-processing#
#                                                                                                 #
#  17- process_file_reg_exp: when crawled files not having same file name and date format in these#
#  names, we pass the reg_exp for target file name date format to change it to the required ones  #
#                                                                                                 #
#  18- process_file_date_format: when crawled files not having same file name and date format in  #
#  these  names, we pass the date format to be able to replace it with the rest of file names date#
#  formats                                                                                        #
#                                                                                                 #
#  19- sys_msg_path: path to sys msg sample file                                                  #
#                                                                                                 #
#  20- common_english_path: path to common english text file that is alternative to pyenchant usag#
###################################################################################################


class RawIRC(object):
    """Defines a RawIRC Object That Cleans & Recognizes Recipients In a Given IRC Raw Data"""
    def __init__(self, raw_data_path, time_regexp, old_date_format, date_regexp, clean_work_path,
                 raw_msg_field_separator='', delete_cleaned_data='no',
                 user_sys_annotations='', time_sys_annotations='', clean_only='no',
                 recipient_only='no', concatenate='no', rtrim_time=0, ltrim_time=0,
                 time_user_lines=0, force_remove_sysmsg='no', use_enchant='no',
                 process_file_reg_exp='', process_file_date_format='', sys_msg_path='',
                 common_english_path=''):

        self.__concatenate = concatenate
        self.__process_file_reg_exp = process_file_reg_exp
        self.__process_file_date_format = process_file_date_format
        self.__time_user_lines = int(time_user_lines)
        self.__raw_data_path = raw_data_path
        self.__date_regexp = date_regexp
        self.__delete_cleaned_data = delete_cleaned_data
        self.__time_regexp = time_regexp
        self.__raw_msg_field_separator = raw_msg_field_separator
        self.__clean_work_path = clean_work_path
        self.__clean_full_path = os.path.join(self.__clean_work_path.rstrip('/')+'/', 'Clean')
        self.__user_sys_annotations = user_sys_annotations
        self.__time_sys_annotations = time_sys_annotations
        self.__old_date_format = old_date_format
        self.__clean_days_path = os.path.join(self.__clean_full_path.rstrip('/')+'/', 'Days')
        self.__clean_days_recipients_path = os.path.join(self.__clean_full_path.rstrip('/')+'/',
                                                         'Days_With_Recipients')
        self.__clean_days_concatenation_path = os.path.join(self.__clean_full_path.rstrip('/')+'/',
                                                            'Days_With_Concatenation')
        self.__common_english_path = common_english_path
        self.__sys_msg_path = sys_msg_path
        self.__clean_only = clean_only
        self.__recipient_only = recipient_only
        self.__rtrim_time = int(rtrim_time)
        self.__ltrim_time = int(ltrim_time)
        self.__force_remove_sysmsg = force_remove_sysmsg
        self.__use_enchant = use_enchant
        self.__recipient_reg_exp = re.compile(r'^@?(.*?)([:,\.])?\s(.*)')

    def clean(self):
        """This function is to clean the crawled data and remove system messages and junk lines
        , recipients are not recognized yet in this function """
        clean_start_time = time.time()
        sys_msg = self.__run_configuration()
        if os.path.exists(self.__clean_days_path):
            shutil.rmtree(self.__clean_days_path)
        date_pattern = re.compile(self.__date_regexp)
        time_pattern = re.compile(self.__time_regexp)
        file_counter = RawIRC.__files_count(self.__raw_data_path)
        print '\nStarted Cleaning Raw Data...'
        logging.info('Started Cleaning Raw Data')
        bar_ = Bar('Cleaning {} File(s) of Raw Data'.format(file_counter), max=file_counter)
        for sub_dir, _, files in os.walk(self.__raw_data_path):
            for file_name in sorted(files):
                if not file_name.startswith('.'):
                    date_match = re.search(date_pattern, file_name)
                    with open(sub_dir+'/'+file_name, 'r') as file_:
                        lines = file_.readlines()
                        try:
                            if self.__date_regexp != '':
                                # when giving a separator value. that happens
                                #  when crawled data are much more structured
                                #  like the Ubuntu IRC
                                if self.__raw_msg_field_separator != '':
                                    self.__simple_clean(lines, time_pattern, date_match,
                                                        sys_msg)
                                # when the crawled data are missy like the Perl IRC,
                                #  when we need to find out where is the date or time
                                #  and the sender and the associated message
                                else:
                                    self.__complicated_clean(lines, time_pattern, date_match,
                                                             sys_msg)
                            else:
                                print '\nARGUMENT date_regexp VALUE IS NOT GIVEN AS EXPECTED!'
                                logging.error('date_regexp Argument Value is Not Given As Expected')
                        except BaseException as excep:
                            print '\nPROBLEM OCCURRED WHILE CLEANING FILE "{}"'\
                                .format(file_name)
                            print ' -POSSIBLE REASON: {}'.format(excep.message)
                            logging.error('Problem Occurred While Cleaning File %s,'
                                          ' Possible Reasons: %s', file_name, excep.message)

                            exit()
                    bar_.next()
        bar_.finish()

        assert os.path.exists(self.__clean_days_path), 'SOMETHING WENT WRONG,' \
                                                       ' NO DATA HAVE BEEN CLEANED.'
        print '\n--------------------------------------------------------------------------------'
        print 'Cleaning Raw Data Has Finished. Please Check the Results on the Path: "{}"'\
            .format(self.__clean_days_path)
        print 'Time Elapsed Was Approximately {} Minute(s)'\
            .format(int((time.time() - clean_start_time)/60))
        print '--------------------------------------------------------------------------------\n'

        logging.info('Cleaning Raw Data Has Finished')

    def create_recipient(self):
        """this function goes line by line on the cleaned tsv generated file and search
         for a user name mentioned as the first word in the raw message"""
        start_time = time.time()
        utterances_count = 0
        utter_w_recipient_count = 0
        if os.path.exists(self.__clean_days_recipients_path):
            shutil.rmtree(self.__clean_days_recipients_path)
        if self.__use_enchant != 'yes':
            common_words = RawIRC.__load_common_english(self.__common_english_path)
        else:
            common_words = set()
        users = RawIRC.make_user_list(self.__clean_days_path)
        print 'Started createRecipient Algorithm....'
        logging.info('Started createRecipient Algorithm')
        try:
            files_counter = RawIRC.__files_count(self.__clean_days_path)
            bar_ = Bar('Recognizing Utterance Recipient in {} File(s)'
                       .format(files_counter), max=files_counter)
            files = os.listdir(self.__clean_days_path)
            index_ = len(files) - 1
            while index_ >= 0:
                if not files[index_].startswith('.'):
                    with open(self.__clean_days_path+'/'+files[index_], 'r') as file_:
                        lines = file_.readlines()
                        utterances_count += len(lines)
                        for line in lines:
                            line = line.split('\t')
                            user_name = line[1]
                            recipient_match = self.__recipient_reg_exp.match(line[2])
                            match_results = RawIRC.__match_recipient(recipient_match)

                            line_to_write = RawIRC.__check_candidate_recipient(self.__use_enchant,
                                                                               match_results[0],
                                                                               users, user_name,
                                                                               match_results[1],
                                                                               line,
                                                                               common_words)
                            if line_to_write.split('\t')[2] != '':
                                utter_w_recipient_count += 1

                            RawIRC.__file_writer(self.__clean_days_recipients_path,
                                                 str(files[index_]),
                                                 str(line_to_write).strip('\n')+'\n')

                index_ -= 1
                bar_.next()
            bar_.finish()
            if self.__delete_cleaned_data == 'yes':
                if os.path.exists(self.__clean_days_path):
                    shutil.rmtree(self.__clean_days_path)
                    print '\nCleaned Without Recipient Data have been Removed' \
                          ' According the Parameter: (delete_cleaned_data = True).\n'

        except BaseException as excep:
            print '\nPROBLEM OCCURRED WHILE PROCESSING UTTERANCES IN createRecipient FUNCTION.' \
                  ' IN FILE {}'\
                .format(files[index_])
            print ' -Reason: {}'.format(excep.message)
            logging.error('Problem Occurred While Processing Utterances in createRecipient'
                          ' Function. File: %s, Reason: %s', files[index_], excep.message)
            exit(excep.message)

        logging.info('Creating Recipients Has Finished')

        if self.__concatenate == 'yes':
            conc_utterances_count = \
                RawIRC.__concatenate_utterance(self.__clean_days_concatenation_path,
                                               self.__clean_days_recipients_path,
                                               self.__delete_cleaned_data)

            RawIRC.__report_work_concatenate(self.__clean_days_concatenation_path,
                                             start_time, conc_utterances_count,
                                             utter_w_recipient_count)
            RawIRC.__validate_cleaned_data(self.__clean_days_concatenation_path)

        else:
            RawIRC.__report_work(self.__clean_days_recipients_path, start_time,
                                 utterances_count, utter_w_recipient_count)
            RawIRC.__validate_cleaned_data(self.__clean_days_recipients_path)

    @staticmethod
    def make_user_list(clean_days_path):
        """this function is to create a users list from previous day to compare against
        when searching for recipients in a cleaned raw line"""
        user_list = set()
        assert os.path.exists(clean_days_path), 'THE GIVEN ARGUMENT VALUES' \
                                                ' DECLARED THE RUNNING OF' \
                                                ' createRecipient ALGORITHM.' \
                                                ' HOWEVER, NO CLEANED FILES' \
                                                ' WERE FOUND TO APPLY THE ALGORITHM ON.'

        files = os.listdir(clean_days_path)
        assert not ((len(files) == 1 and files[0].startswith('.')) or len(files) < 1),\
            'THE GIVEN ARGUMENT VALUES DECLARED THE RUNNING OF createRecipient' \
            ' ALGORITHM HOWEVER, NO CLEANED FILES WERE FOUND TO APPLY THE ALGORITHM ON.'

        file_counter = RawIRC.__files_count(clean_days_path)

        bar_ = Bar('Creating Users List From All IRC Logs History. Processing {} File(s)'
                   .format(file_counter), max=file_counter)
        logging.info('Started Creating Users List')

        try:
            for file_ in files:
                if not file_.startswith('.'):
                    with open(clean_days_path+'/'+file_, 'r') as opener:
                        lines = opener.readlines()
                        for line in lines:
                            if line != '\n':
                                line = line.split('\t')
                                user_name = line[1].strip()
                                user_list.add(user_name)

                    bar_.next()
            bar_.finish()
        except BaseException as excep:
            print '\nPROBLEM OCCURRED WHILE PROCESSING LINE IN makeUserList FUNCTION.' \
                  ' PROBLEMATIC LINE IS "{}":'\
                .format(line)
            print 'CHECK THE FILE: {}'.format(file_)
            print ' -REASON: {}'.format(excep.message)
            logging.error('Problem Occurred While Processing Line the makeUserList Function.'
                          ' Problematic Line is %s, File Is %s, Reason Maybe: %s'
                          , line, file_, excep.message)
            exit(excep.message)

        logging.info('Creating Users List Has Finished')
        return user_list

    @staticmethod
    def __concatenate_utterance(result_path, with_recipients_path, delete_cleaned_data):
        """in case users keep talking during the same time and send several messages
         we concatenate these messages to their original message"""
        conc_utterances_count = 0
        if os.path.exists(result_path):
            shutil.rmtree(result_path)

        files_counter = RawIRC.__files_count(with_recipients_path)
        print 'Started concatenateRelevantUtterances Algorithm....'
        logging.info('Started concatenateRelevantUtterances Algorithm')
        try:
            bar_ = Bar('Concatenating Relevant Utterances in {} File(s)'
                       .format(files_counter),
                       max=files_counter)
            files = os.listdir(with_recipients_path)
            for file_ in files:
                if not file_.startswith('.'):
                    with open(with_recipients_path + '/' + file_, 'r') as opener:
                        lines = opener.readlines()
                        counter = \
                            RawIRC.__check_relevant_utterance(lines, file_,
                                                              result_path)
                        conc_utterances_count += counter
                bar_.next()
            bar_.finish()

            if delete_cleaned_data == 'yes':
                if os.path.exists(with_recipients_path):
                    shutil.rmtree(with_recipients_path)
                    print '\nCleaned Data Before Concatenation have been Removed According' \
                          ' to the Parameter: (delete_cleaned_data = True).\n'
        except BaseException as excep:
            print "\nPROBLEM OCCURRED WHILE CONCATENATING RELEVANT UTTERANCES IN FILE {}" \
                .format(file_)
            print ' -Reason: {}'.format(excep.message)
            logging.error('Problem Occurred While Concatenating Relevant Utterances in'
                          ' File %s, Possible Reasons: %s', file_, excep.message)
            exit(excep.message)
        logging.info('Concatenation Has Finished')

        return conc_utterances_count

    def __run_configuration(self):
        """runs some optional given settings like if to load a sys message file to ignore
         such messages or to apply some pre-processing on the crawled file names before cleaning"""
        sys_msg = []
        if self.__force_remove_sysmsg == 'yes':
            sys_msg = RawIRC.__load_sys_msg(self.__sys_msg_path)
        if self.__process_file_reg_exp != '' and self.__process_file_date_format != '':
            logging.info('Started Pre-Processing Of Crawled File Names As Requested')
            for sub_dir, _, files in os.walk(self.__raw_data_path):
                for file_name in files:
                    if not file_name.startswith('.'):
                        match = re.search(self.__process_file_reg_exp, file_name)
                        if match:
                            new_file_name = \
                                RawIRC.__change_date_format(match.group(2),
                                                            self.__process_file_date_format,
                                                            self.__old_date_format)
                            os.rename(sub_dir + '/' + file_name, sub_dir + '/' + new_file_name)
        return sys_msg

    @staticmethod
    def __check_sys_msg(line, sys_msg):
        """checks if the current given line is a system message, if so: ignore it"""
        for msg in sys_msg:
            if re.search(msg, line):
                return True
        return False

    @staticmethod
    def __match_sender(line, user_sys_ann, msg_separator, time_reg_exp):
        """matches the sender in a raw line according to the given settings like the
         sender surrounding annotations and time regular expression it comes after"""
        if user_sys_ann != '':
            user_ann_x = user_sys_ann.split(',')[0]
            user_ann_y = user_sys_ann.split(',')[1]
            user_name_pattern = re.compile('(' + time_reg_exp + r'\s?' + user_ann_x
                                           + ')' + '(.*)' + '(' + user_ann_y + r'\s?)')
            user_match = re.search(user_name_pattern, line)
            if user_match:
                user_name = user_match.group(2).split('>')[0]
            else:
                user_name = ''
        else:
            user_name = line.split(msg_separator)[1]

        return user_name

    def __simple_clean(self, lines, time_pattern, date_match, sys_msg):
        """this function is invoked by the main clean function in case the crawled data
         were simple lines Ubuntu IRC, so they do not require complicated pattern
          to follow to be cleaned"""
        for line in lines:
            if RawIRC.__check_sys_msg(line, sys_msg):
                continue
            time_match = re.search(time_pattern, line)
            user_name = RawIRC.__match_sender(line, self.__user_sys_annotations,
                                              self.__raw_msg_field_separator,
                                              self.__time_regexp)
            if date_match:
                date_string = RawIRC.__change_date_format(date_match.group(0),
                                                          self.__old_date_format,
                                                          '%Y-%m-%d')
                prev_date = date_string
                if time_match:
                    if user_name != '':
                        if self.__time_sys_annotations != '':
                            annotations = self.__time_sys_annotations.split(',')
                            time_ = time_match.group(0).lstrip(annotations[0]) \
                                .rstrip(annotations[1])
                        else:
                            time_ = time_match.group(0)

                        if self.__rtrim_time != 0:
                            time_ = time_[:-self.__rtrim_time]
                        if self.__ltrim_time != 0:
                            time_ = str(time_).replace(time_[:self.__ltrim_time], '')

                        converted_line = (date_string + 'T' + time_ + ':00.000Z',
                                          user_name,
                                          line.replace(time_match.group(0), '')
                                          .replace(self.__user_sys_annotations.split(',')[0]
                                                   + user_name
                                                   + self.__user_sys_annotations.split(',')[1], '')
                                          .lstrip(self.__raw_msg_field_separator)
                                          .lstrip())

                        RawIRC.__file_writer(self.__clean_days_path,
                                             str(prev_date) + '.tsv',
                                             str('{}\t{}\t{}'.format(converted_line[0],
                                                                     converted_line[1],
                                                                     converted_line[2])))

            else:
                print '\nTHE GIVEN date_regexp ARGUMENT VALUE NOT' \
                      ' A CORRECT MATCH FOR THE CRAWLED FILE'
                logging.error('The Given date_regexp Parameter Value Not a Correct Match'
                              ' for the Crawled File')
                exit()

    def __complicated_clean(self, lines, time_pattern, date_match, sys_msg):
        """this function will be invoked by the main clean function in case the crawled data were
         more complicated and need more cleaning following up a certain pattern like Perl6, it
         will be cleaned by iterating through the file and find certain pattern to
          get nickname, time, msg."""
        nick_name_created = False
        date_time_created = False
        date_time = ''
        prev_date = ''
        nick_name = ''
        for line in lines:
            if RawIRC.__check_sys_msg(line, sys_msg):
                continue
            time_match = re.search(time_pattern, line)
            if nick_name_created:
                msg = line.strip()
                date_time_created = False
                nick_name_created = False
                full_msg = '\t'.join([date_time.strip('\n'),
                                      nick_name.strip('\n'), msg.strip('\n')])
                if nick_name.strip('\n') != '':
                    RawIRC.__file_writer(self.__clean_days_path,
                                         str(prev_date) + '.tsv',
                                         str(full_msg) + '\n')

            if date_match:
                date_string = RawIRC.__change_date_format(date_match.group(0),
                                                          self.__old_date_format, '%Y-%m-%d')
                prev_date = date_string

                if time_match:
                    line_skipped = 0
                    time_ = RawIRC.__get_time(self.__time_sys_annotations, time_match,
                                              self.__rtrim_time, self.__ltrim_time)

                    date_time = date_string + 'T' + time_.strip() + ':00.000Z'
                    date_time_created = True
                else:
                    if date_time_created:
                        if line.strip('\n').strip() != '':
                            if line_skipped <= self.__time_user_lines:
                                nick_name = line.strip()
                                nick_name_created = True

                        else:
                            line_skipped += 1
            else:
                print '\nTHE GIVEN date_regexp ARGUMENT VALUE NOT' \
                      ' A CORRECT MATCH FOR THE CRAWLED FILE'
                logging.error('The Given date_regexp Parameter Value Not a Correct Match'
                              ' for the Crawled File')
                exit()

    @staticmethod
    def __get_time(time_sys_ann, time_match, rtrim_time, ltrim_time):
        """get the matched time field after apply certain transformation on it"""
        if time_sys_ann != '':
            annotations = time_sys_ann.split(',')
            time_ = time_match.group(0).lstrip(annotations[0]) \
                .rstrip(annotations[1])
        else:
            time_ = time_match.group(0)

        if rtrim_time != 0:
            time_ = time_[:-rtrim_time]
        if ltrim_time != 0:
            time_ = str(time_).replace(time_[:ltrim_time], '')

        return time_

    @staticmethod
    def __check_relevant_utterance(lines_p, file_p, path_p):
        """this function will be invoked by the main concatenate_utterance function,
        in order to loop through each crawled file lines and find relevant utterances
         that belongs to each other"""
        origline = ''
        utterance = ''
        day_conc_utterances_count = 0
        for line in lines_p:
            line = line.split("\t")
            if (line[2] != "" and line != lines_p[len(lines_p) - 1].split("\t")) \
                    or line == lines_p[0].split("\t"):
                if utterance != "":
                    RawIRC.__file_writer(path_p, file_p,
                                         "\t".join([origline[0], origline[1],
                                                    origline[2],
                                                    utterance.strip("\n") + "\n"]))
                    day_conc_utterances_count += 1

                    origline = line
                    utterance = origline[3].strip("\n")
                    continue
                else:
                    origline = line
                    utterance = origline[3].strip("\n")
                    continue
            if (line[1] == origline[1]) and (line[2] == "" or line[2] == origline[2]):
                utterance += ", " + line[3].strip("\n")
            else:
                RawIRC.__file_writer(path_p, file_p,
                                     "\t".join([origline[0], origline[1],
                                                origline[2],
                                                utterance.strip("\n") + "\n"]))
                day_conc_utterances_count += 1

                origline = line
                utterance = origline[3].strip("\n")

            if line == lines_p[len(lines_p) - 1].split("\t"):
                RawIRC.__file_writer(path_p, file_p, "\t"
                                     .join([origline[0],
                                            origline[1], origline[2],
                                            utterance.strip("\n") + "\n"]))
                day_conc_utterances_count += 1

        return day_conc_utterances_count

    @staticmethod
    def __load_common_english(path_):
        """this function loads common english words from a file that will be
         passed as an argument"""
        common_words = set()
        logging.info('Started Loading Common English File')
        assert os.path.exists(path_), 'COMMON ENGLISH FILE NOT FOUND'
        with open(path_) as file_:
            for word in file_.readlines():
                common_words.add(str(word).strip().lower())

        logging.info('Loading Common English Words Has Finished')
        return common_words

    @staticmethod
    def __load_sys_msg(path_):
        """this function loads the sys message is defined in a file as a given parameter
         to the component to so these sys messages will be ignored during processing"""
        logging.info('Started Loading Sys Messages')
        assert os.path.exists(path_), 'SYS MSG SAMPLE FILE NOT FOUND.'
        sys_msg = []
        with open(path_) as file_:
            for line in file_.readlines():
                sys_msg.append(str(line).strip())

        logging.info('Loading Sys Messages Has Finished')
        return sys_msg

    @staticmethod
    def __match_recipient(recipient_match):
        """checks if the regular expression for the recipient is matched so returns the string,
         otherwise, returns empty string"""
        if recipient_match is not None:
            possible_recipient = recipient_match.group(1)
            symbol = recipient_match.group(2)
        else:
            possible_recipient = ''
            symbol = None
        return [possible_recipient, symbol]

    @staticmethod
    def __check_candidate_recipient(use_enchant_p, possible_recipient_p, users_p, user_name_p,
                                    symbol_p, line_p, common_words_p):
        """this function checks a candidate recipient as the first word in the utterance
         or the word that matches the recipient regular expression (recipient_reg_exp),
          if all conditions met, so the utterance first word will be recognized as a recipient"""

        # if the candidate recipient found in the extracted users from the makeUserList function
        if possible_recipient_p in users_p and possible_recipient_p != user_name_p:
            if use_enchant_p == 'yes':

                if not DICT.check(possible_recipient_p.strip('\n')) or symbol_p is not None:
                    msg = line_p[2][len(possible_recipient_p):] \
                        .lstrip(' ').lstrip(':').lstrip(',').lstrip(' ')
                    line_to_write = '\t'.join([line_p[0], user_name_p, possible_recipient_p, msg])

                # if the user name of the recipient is an English word or recipient regular
                #  expression not matched so we ignore it and write empty string to
                #  the recipient filed in the tsv file
                else:
                    if line_p[2].split(' ')[0].endswith(':') or line_p[2].split(' ')[0]\
                            .endswith(','):
                        msg = line_p[2][len(possible_recipient_p):] \
                            .lstrip(' ').lstrip(':').lstrip(',').lstrip(' ')
                    else:
                        msg = line_p[2]
                    line_to_write = '\t'.join([line_p[0], user_name_p, '', msg])
            else:
                if not possible_recipient_p.lower() in common_words_p or symbol_p is not None:

                    msg = line_p[2][len(possible_recipient_p):].lstrip(' ') \
                        .lstrip(':').lstrip(',').lstrip(' ')
                    line_to_write = '\t'.join([line_p[0], user_name_p, possible_recipient_p, msg])

                # if the user name of the recipient is an English word, we ignore it and
                #  write empty string to the recipient filed in the tsv file
                else:
                    if line_p[2].split(' ')[0].endswith(':') or line_p[2].split(' ')[0]\
                            .endswith(','):
                        msg = line_p[2][len(possible_recipient_p):].lstrip(' ') \
                            .lstrip(':').lstrip(',').lstrip(' ')
                    else:
                        msg = line_p[2]
                    line_to_write = '\t'.join([line_p[0], user_name_p, '', msg])

        else:
            msg = line_p[2]
            line_to_write = '\t'.join([line_p[0], user_name_p, '', msg])

        return line_to_write

    @staticmethod
    def __report_work(work_path, work_start_time, utterances_count, utter_w_recipients_count):
        """function to report some statistics for no concatenated results"""
        if not os.path.exists(work_path):
            print '\nNOTHING TO REPORT!\n'
        else:
            logging.info('Getting Results Report')
            print '\n----------------------------------------------------------------------------'
            print 'Recognizing Utterance Recipient Has Finished.' \
                  ' Please Check the Results on the Path: "{}"'\
                .format(work_path.rstrip('/'))
            print 'Time Elapsed Was Approximately {} Minute(s)'\
                .format(int((time.time() - work_start_time)/60))
            print '----------------------------------------------------------------------------'
            print '\n-------------------------------'
            print 'IRC Post-Processing Data Statistics:'
            print '-------------------------------'
            print ' -Number of Utterance(s) is {}'.format(utterances_count)
            if utterances_count > 0:
                print ' -Number of Utterance(s) With a Recipient is {}. With a Percentage of {}%'\
                    .format(utter_w_recipients_count,
                            round(utter_w_recipients_count/utterances_count*100, 4))
            print '\n--------------------------------------------------------------------------'

    @staticmethod
    def __report_work_concatenate(work_path, work_start_time, conc_utterances_count,
                                  utter_w_recipients_count):
        """function to report some statistics for concatenated results"""
        if not os.path.exists(work_path):
            print '\nNOTHING TO REPORT!\n'
        else:
            logging.info('Getting Results Report')
            print '\n----------------------------------------------------------------------------'
            print 'Recognizing Utterance Recipient Has Finished.' \
                  ' Please Check the Results on the Path: "{}"'\
                .format(work_path.rstrip('/'))
            print 'Time Elapsed Was Approximately {} Minute(s)'\
                .format(int((time.time() - work_start_time)/60))
            print '----------------------------------------------------------------------------'
            print '\n----------------------------------'
            print 'RawIRC Component Output Statistics:'
            print '----------------------------------\n'
            print ' -Number of Utterance(s) is {}'.format(conc_utterances_count)
            if conc_utterances_count > 0:
                print ' -Number of Utterance(s) With a Recipient is {}. With a Percentage of {}%'\
                    .format(utter_w_recipients_count,
                            round(utter_w_recipients_count/conc_utterances_count*100, 4))
            print '\n--------------------------------------------------------------------------'

    @staticmethod
    def __files_count(path):
        """function to count how many files in a directory,
         useful for quantifying the required work"""
        print 'Gathering Information Required for Post-Processing...'
        counter = 0
        for _, _, files in os.walk(path):
            for file_ in files:
                if not file_.startswith('.'):
                    counter += 1
        return counter

    @staticmethod
    def __change_date_format(date_string, old_format, new_format):
        """function to change the crawled data old date format to a new date format"""
        try:
            new_format = datetime.datetime.strptime(date_string, old_format).strftime(new_format)
            return new_format
        except BaseException as excep:
            print '\nPROBLEM OCCURRED IN changeDateFormat FUNCTION'
            print ' -REASON: {}'.format(excep.message)
            logging.error('Problem Occurred in changeDateFormat Function,'
                          ' Reason: %s', excep.message)
            exit(excep.message)

    @staticmethod
    def __file_writer(path, file_name, context):
        """function that writes a processed line to a file"""
        if not os.path.exists(path):
            os.makedirs(path)
        with open(path+'/'+file_name, 'a') as opener:
            opener.write(context)

    @staticmethod
    def __validate_cleaned_data(path):
        """function that checks if the output is well structured"""
        print '\nValidating Component Output...'
        logging.info('Validating Component Output')
        problematic_files = set()
        errors = set()
        files = os.listdir(path)
        for file_ in files:
            if not file_.startswith('.'):
                with open(path+'/'+file_, 'r') as opener:
                    lines = opener.readlines()
                    for line in lines:
                        line = line.split('\t')
                        if len(line) != 4:
                            problematic_files.add(path+'/'+file_)
                            errors.add('bad file structure,'
                                       ' each file must have not less or more than 4 fields!')

                        if len(line[0]) == 0 or len(line[1]) == 0 or len(line[3]) == 0:
                            problematic_files.add(path+'/'+file_)
                            errors.add('Unexpected Empty String at one of the Fields')

        if len(problematic_files) > 0:
            print 'COMPONENT OUTPUT HAS SOME BAD RESULTS'
            logging.error('Component Output Has Some Bad Results In %s', problematic_files)
            print ' - PROBLEM OCCURRED IN THE BELOW OUTPUT FILE(S)'
            for file_ in problematic_files:
                print file_
            print '- REASON(S):'
            for err in errors:
                print err
            exit()
        else:
            print 'SUCCESS: Component Output Is OK!\n'
            logging.info('SUCCESS: Component Output Is OK!')

# running from command line related part
if __name__ == '__main__':
    PARSER = argparse.ArgumentParser()
    PARSER.add_argument('-raw_data_path', help='mandatory parameter to specify the path'
                                               ' of the crawled data to be processed,'
                                               ' the default is the local folder path',
                        type=str, const='./', default='./', nargs='?')

    PARSER.add_argument('-clean_work_path', help="specify the path for the output data,"
                                                 " the default is the local folder", nargs='?',
                        const='./', type=str, default='./')

    PARSER.add_argument('-sys_msg_path', help="specify the path for the sys msg text file"
                                              " sample that will be used to ignore sys"
                                              " messages", nargs='?',
                        const='', type=str, default='')

    PARSER.add_argument('-common_english_path', help="specify the path for the common english"
                                                     " text file that will be used in"
                                                     " recognizing recipients instead of"
                                                     " pyenchant messages", nargs='?',
                        const='', type=str, default='')

    PARSER.add_argument('-time_regexp', help="""the time pattern in the raw IRC logs
     crawled, so the software will be able to recognize the time in a message in order
      to create the time field. default value is empty string""",
                        type=str, const='', default='', nargs='?')

    PARSER.add_argument('-date_regexp', help="""the date pattern in the raw IRC logs files
     to be cleaned, so the software should be able to recognize the date in the files
      to concatenate that date with the time field, default value is empty string """,
                        nargs='?', const='', type=str, default='')

    PARSER.add_argument('-time_user_lines', help="""indicates how many empty lines
     between the message time and sender in an IRC log, these lines to be ignored and
      are important to know how to match the sender name, by default the value is 0""",
                        type=int, nargs='?', const=0, default=0)

    PARSER.add_argument('-raw_msg_separator', help="""specify if the raw lines in the
     crawled IRCs are separated by a space  or not default value is an empty string and
      for IRCs lines separated by a space you should give a value ' '""",
                        type=str, nargs='?', const='', default='')

    PARSER.add_argument('-user_sys_annotation', help="""specify if there is
     annotations surrounding the user names in the raw messages so, the software
      ignores it when extracting the sender name field values. By default set
       to '' which means no annotations""", nargs='?', const='', type=str, default='')

    PARSER.add_argument('-time_sys_annotation', help="""specify if there is annotations
     surrounding the time in the raw messages so, the software ignores it when extracting
      the time field values. By default set to '' which means no annotations"""
                        , type=str, nargs='?', const='', default='')

    PARSER.add_argument('-old_date_format', help="""specify the old date format
     found in crawled files to convert it to a new date format, the default
      value is empty string""", nargs='?', const='', type=str, default='')

    PARSER.add_argument('-delete_cleaned_data', help="""(yes)indicates if the cleaned
     data created should be deleted after creating the final output which is
      the recognized recipients, the default value is no""",
                        type=str, nargs='?', const='no', default='no')

    PARSER.add_argument('-clean_only', help='(yes)indicates if only cleaning task'
                                            ' should be executed, default value is no',
                        nargs='?', const='no', type=str, default='no')

    PARSER.add_argument('-recipient_only', help='(yes)indicates if only create recipient task'
                                                ' should be executed, default value is no',
                        nargs='?', const='no', type=str, default='no')

    PARSER.add_argument('-concatenate', help="""(yes) indicates if a concatenation
     algorithm will be executed when creating recipients, default value is no""",
                        type=str, const='no', default='no', nargs='?')

    PARSER.add_argument('-rtrim_time', help="""specify how many characters to be trimmed
     from time field from the right side, default value is 0""",
                        type=int, const=0, default=0, nargs='?')

    PARSER.add_argument('-ltrim_time', help="""specify how many characters to be trimmed
     from time field from the left side, default value is 0""", type=int,
                        const=0, default=0, nargs='?')

    PARSER.add_argument('-use_enchant', help="""(yes) indicates if pyenchant module
     will be used as the English dictionary to check if a user is a common English
      word or not, default value is no""", type=str, const='no', default='no', nargs='?')

    PARSER.add_argument('-force_remove_sysmsg', help="""(yes) indicates if the clean
     algorithm should ignore certain lines pattern recognized by a passed file as another
      argument, default value is no""", type=str, const='no', default='no', nargs='?')

    PARSER.add_argument('-process_file_date_format', help="""specify the date format of
     the input crawled files in case these files are not having the same date format in
      their names as the rest of the crawled files, this parameter helps to guide in the
       process of renaming these files with different date formats, default value
        is empty string""", type=str, const='', default='', nargs='?')

    PARSER.add_argument('-process_file_reg_exp', help="""specify the date regular expression
     of the input crawled files in case these files are not having the same date format in
     their names as the rest of the crawled files, this parameter helps to guide in the
      process of renaming these files with different date formats, default value is
       empty string""", type=str, const='', default='', nargs='?')

    ARGM = PARSER.parse_args()
    RAW_IRC = RawIRC(raw_data_path=ARGM.raw_data_path, clean_work_path=ARGM.clean_work_path,
                     time_regexp=ARGM.time_regexp,
                     raw_msg_field_separator=ARGM.raw_msg_separator,
                     date_regexp=ARGM.date_regexp,
                     user_sys_annotations=ARGM.user_sys_annotation,
                     delete_cleaned_data=ARGM.delete_cleaned_data,
                     time_sys_annotations=ARGM.time_sys_annotation,
                     old_date_format=ARGM.old_date_format,
                     recipient_only=ARGM.recipient_only, clean_only=ARGM.clean_only,
                     concatenate=ARGM.concatenate, rtrim_time=ARGM.rtrim_time,
                     ltrim_time=ARGM.ltrim_time, time_user_lines=ARGM.time_user_lines,
                     force_remove_sysmsg=ARGM.force_remove_sysmsg,
                     use_enchant=ARGM.use_enchant,
                     process_file_date_format=ARGM.process_file_date_format,
                     process_file_reg_exp=ARGM.process_file_reg_exp,
                     sys_msg_path=ARGM.sys_msg_path,
                     common_english_path=ARGM.common_english_path)

    if ARGM.clean_only.lower() == 'yes':
        assert ARGM.recipient_only.lower() == 'no', 'Cannot Specify Recipient_Only=yes' \
                                                    ' While Specifying Clean_Only=yes.' \
                                                    ' Please Specify Only One Of These Options' \
                                                    ' or Leave Them To Default Values.'
        RAW_IRC.clean()

    elif ARGM.recipient_only.lower() == 'yes':
        assert ARGM.clean_only.lower() == 'no', 'Cannot Specify Clean_Only=yes' \
                                                    ' While Specifying Recipient_Only=yes.' \
                                                ' Please Specify Only One Of These Options or' \
                                                ' Leave Them To Default Values.'
        RAW_IRC.create_recipient()

    else:
        RAW_IRC.clean()
        RAW_IRC.create_recipient()
