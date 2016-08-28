"""this module responsible for the pre-processing required to extract dialogues
 before classifying and creating dialogues data-set for training"""
from __future__ import division
import os
import shutil
import sys
import logging
import argparse
import time
import re
import enchant
import nltk.tokenize
from nltk import FreqDist
from stemming.porter2 import stem
from progress.bar import Bar
from irc_process.ircdb import save_segmented_message, save_segmented_user, get_db_statistics,\
    get_msg_segmented_indices, get_segmented_message, get_senders, get_timing_indices,\
    get_users_pairs, get_usr_segmented_indices, get_utterances, save_dialogue_turns,\
    save_utterance

reload(sys)
sys.setdefaultencoding('utf-8')
DICT = enchant.Dict("en_US")
logging.basicConfig(filename='Dialogue.log', filemode='w', level=logging.INFO)

__author__ = 'Ahmed Abouzeid'
#################################################################################################
#                                                                                               #
# The Dialogue Class is dedicated for the extraction of on on one dialogues and segmentation of #
# all these dialogues between a pair of users during the whole period of the IRC chats          #
#                                                                                               #
# The Dialogue Class initiate a Dialogue instance by giving the below parameters values:        #
#                                                                                               #
# 1- clean_work_path: this is the path of the cleaned and structured .tsv data                  #
#                                                                                               #
# 2- dialogue_work_path: the path that the generated segmented one on one dialogues between pair#
# of users will be written to chunk files. Each file contains only a dialogue between two users #
# recognize the time in a message in order to create the time field.                            #
#                                                                                               #
# 3- delete_with_recipient_file: set to yes when we want to delete input structured .tsv files  #
# after loading the lines from it prior to segmentation and dialogue extraction                 #
#                                                                                               #
# 4- time_frame: how many minutes in between the dialogue extraction algorithm will search for  #
# dialogue between two users. The default is 3 minutes                                          #
#                                                                                               #
# 5- with_stats: to print Dialogues statistical information after generating them               #
#                                                                                               #
# 6- only_stats: in case you want to run the statistical information later when there is already#
# extracted dialogues, so you can just call script for statistics without do the Post-Processing#
# again                                                                                         #
#                                                                                               #
# 7- min_turns : specify the minimum number of turns in a dialogue to accept it and write it to #
# a file                                                                                        #
#                                                                                               #
# 8- bots_path : parameter takes a value of a file path that contains in each line all IRC bots #
# that might be involved in the dialogues and we should ignore these dialogues as our target is #
# Human-Human conversation                                                                      #
#                                                                                               #
# 9- gap_time_frame : parameter takes a value specifies the amount of time in minutes for which #
# the hole filling algorithm should try to find non-addressed messages(gaps) and include them   #
# in case there were no other users talking with involved current users during that amount of   #
# time                                                                                          #
#################################################################################################


class Dialogue(object):
    """defines the dialogue class and its objects that process the IRC utterances
     with different algorithms"""
    def __init__(self, clean_work_path='./', dialogue_work_path='./',
                 delete_with_recipient_file='no', time_frame=3,
                 with_stats='no', only_stats='no', min_turns=3,
                 bots_path='', gap_time_frame=3):
        """initialise the dialogue instance"""
        self.__clean_work_path = clean_work_path
        self.__dialogue_work_path = dialogue_work_path
        self.__dialogue_full_path = os.path.join(self.__dialogue_work_path.rstrip('/') + '/',
                                                 'Dialogues')
        self.__gap_time_frame = gap_time_frame
        self.__delete_with_recipient_file = delete_with_recipient_file
        self.__time_frame = time_frame
        self.__turns_per_weak_dialogue = set()
        self.__with_stats = with_stats
        self.__only_stats = only_stats
        self.__min_turns = min_turns
        self.__bots_path = bots_path

    def match_utterances(self, day_utterances, day_index, max_seg_index):
        """match Raw IRC utterances so each response is matched with its initial question in
         a given time frame (in minutes). The method takes a list of all utterances in a day
          log irc file and another two arguments as indices to track and identify
           each utterance in the Data-base"""
        index = len(day_utterances) - 1
        last_sender = ''
        last_recipient = ''
        last_index = -1
        found_indices = set()
        non_addressed_msg = set()
        users_addressed_recipients = {}
        initial_res_date_time = day_utterances[index][2]
        day_segmentation_indices = []
        filled_holes = 0
        while index >= 0:
            current_recipient = day_utterances[index][4].strip()
            if index == 0 and current_recipient == '':
                non_addressed_msg.add(day_utterances[index])
            if Dialogue.is_time_changed(initial_res_date_time, day_utterances[index][2],
                                        self.__gap_time_frame) or index == 0:
                filled_holes_count = self.process_holes(day_index, day_segmentation_indices,
                                                        non_addressed_msg,
                                                        users_addressed_recipients)
                filled_holes += filled_holes_count
                non_addressed_msg = set()
                users_addressed_recipients = {}
                day_segmentation_indices = []
                initial_res_date_time = day_utterances[index][2]

            if current_recipient != '':
                candidate_first_response = day_utterances[index]
                response_index = index
                inner_index = index - 1
                candidate_response = True
                index -= 1
            # if the message was not with a recipient, do not loop over the some minutes
            #  time frame to find a matching initial question
            else:
                non_addressed_msg.add(day_utterances[index])
                index -= 1
                continue
            # if a candidate response found(message with a recipient), then looping over some
            #  minutes time frame messages to find a matching initial question asked
            #  by that recipient
            if candidate_response:
                response_sender = candidate_first_response[3]
                response_recipient = candidate_first_response[4]
                user1_name = str.decode(max(response_recipient, response_sender), 'utf-8')
                user2_name = str.decode(min(response_recipient, response_sender), 'utf-8')
                response_date_time = candidate_first_response[2]
                while inner_index >= 0:
                    try:
                        candidate_initial_question = day_utterances[inner_index]
                        response_time_index = day_utterances[response_index][0]
                        question_time_index = day_utterances[inner_index][0]
                        question_date_time = candidate_initial_question[2]

                        # as long as the previous messages are in the same some minutes time
                        #  frame to the candidate first response
                        if not Dialogue.is_time_changed(response_date_time, question_date_time,
                                                        self.__time_frame):
                            users_addressed_recipients = Dialogue.update_usr_addr_rec(
                                users_addressed_recipients, candidate_initial_question,
                                candidate_first_response)

                            if Dialogue.is_match(candidate_first_response,
                                                 candidate_initial_question, found_indices):
                                if (response_sender == last_sender or response_sender == last_recipient)\
                                        and (response_recipient == last_recipient or
                                             response_recipient == last_sender):

                                    index_to_insert = last_index
                                else:
                                    index_to_insert = max_seg_index
                                    last_index = index_to_insert
                                    day_segmentation_indices.append(max_seg_index)
                                    last_recipient = response_recipient
                                    last_sender = response_sender
                                    max_seg_index -= 1

                                Dialogue.__add_to_dialogues(candidate_first_response, day_index,
                                                            index_to_insert,
                                                            candidate_initial_question)
                                save_segmented_user(index_to_insert, user1_name, user2_name)
                                found_indices.add(response_time_index)
                                found_indices.add(question_time_index)
                                break
                            inner_index -= 1
                        # if some minutes time frame ended, add any candidate responses left
                        #  without initial questions
                        else:
                            if response_time_index not in found_indices:
                                if (response_sender == last_sender or response_sender == last_recipient)\
                                        and (response_recipient == last_recipient
                                             or response_recipient == last_sender):
                                    index_to_insert = last_index
                                else:
                                    index_to_insert = max_seg_index
                                    save_segmented_user(index_to_insert, user1_name,
                                                        user2_name)

                                    last_index = index_to_insert
                                    last_recipient = response_recipient
                                    last_sender = response_sender
                                    max_seg_index -= 1

                                Dialogue.__add_to_dialogues(candidate_first_response, day_index,
                                                            index_to_insert)
                            break
                    except BaseException as excep:
                        print '\nERROR: PROBLEM OCCURRED IN match_utterances METHOD WHILE' \
                              ' MATCHING AN INITIAL QUESTION WITH A FIRST RESPONSE.'
                        print ' -PROBLEMATIC DIALOGUE DATE IS {}'.format(day_index)
                        print ' -REASON: {}'.format(excep.message)
                        logging.error('problem Occurred In match_utterances Method')
                        exit()
        return [max_seg_index, filled_holes]

    def extract_dialogues(self):
        """loads each IRC log single day utterances and pass it to match_utterances method
         to apply dialogue extraction algorithm and hole-filling algorithm"""
        logging.info('Dialogue Extraction Algorithm Started')
        start_time = time.time()
        day_utterances = []
        first_call = True
        filled_holes = 0
        max_seg_index = self.__segmentation_index_setup(self.__clean_work_path)
        print '\nStarting Dialogue Extraction Algorithm...'
        item_index = 0
        files_count = Dialogue.__files_count(self.__clean_work_path)
        bar_ = Bar('Extracting One-One Dialogue From {} Day(s)'.format(files_count),
                   max=files_count)
        for root_dir, _, files in os.walk(self.__clean_work_path):
            try:
                for file_ in sorted(files):
                    if not file_.startswith('.'):
                        with open(str(root_dir) + '/' + file_) as reader_:
                            lines = reader_.readlines()
                            for line_ in lines:
                                line_ = str(line_).split('\t')
                                if len(line_) == 4:
                                    day_index = line_[0].split('T')[0]
                                    date_time = line_[0]
                                    sender = line_[1].replace('"', '')
                                    recipient = line_[2].replace('"', '')
                                    utterance = line_[3].replace('"', '')

                                    day_utterances.append((item_index, day_index, date_time, sender,
                                                           recipient, utterance))
                                    item_index += 1

                        if first_call:
                            processing_states = self.match_utterances(
                                day_utterances, str.decode(str(file_).strip('.tsv'), 'utf-8'),
                                max_seg_index)
                            latest_holes_count = processing_states[1]
                            filled_holes += latest_holes_count
                            first_call = False
                        else:
                            max_seg_index = processing_states[0]
                            processing_states = self.match_utterances(
                                day_utterances, str.decode(str(file_).strip('.tsv'), 'utf-8'),
                                max_seg_index)
                            latest_holes_count = processing_states[1]
                            filled_holes += latest_holes_count

                        day_utterances = []
                        bar_.next()
            except BaseException as excep:
                print '\nERROR: PROBLEM OCCURRED IN EXTRACTED DIALOGUES METHOD.'
                print ' -MOST PROBABLY THE PROBLEM IS IS FILE: "{}"'.format(file_)
                print ' -REASON: {}'.format(excep.message)
                logging.error('problem Occurred In dialogue_extraction Method')
                exit()
        bar_.finish()
        logging.info('Dialogue Extraction Algorithm Finished')
        pairs = get_users_pairs()
        dialogues_utterances_count = self.write_segmented_dialogues(pairs)
        Dialogue.verify_cleaned_data(self.__dialogue_full_path)
        Dialogue.verify_segmentation(self.__dialogue_full_path)
        Dialogue.__report_work(self.__dialogue_full_path, start_time,
                               filled_holes, dialogues_utterances_count)

        if self.__with_stats == 'yes':
            self.calculate_statistics(self.__dialogue_full_path)

    def write_segmented_dialogues(self, segmented_users_p):
        """handles the writing of segmented dialogues and creates
         chunks folders and files"""
        logging.info('Writing Segmented Dialogues Started')
        segmentation_ids = []
        dialogues = []
        final_dialogues_utterances = 0
        bots = Dialogue.__load_bots(self.__bots_path)
        segmented_dialogue_counter = len(segmented_users_p)
        if os.path.exists(self.__dialogue_full_path):
            print 'Old Dialogues Have Been Found. System Is Deleting Old Dialogues Files...'
            shutil.rmtree(self.__dialogue_full_path)
        bar_ = Bar('Segmenting {} Relevant Dialogue(s) and Writing To File(s).'
                   .format(segmented_dialogue_counter),
                   max=segmented_dialogue_counter)
        folder_name = 3
        file_name = 0
        try:
            for users_pair in segmented_users_p:
                segmentation_indices = get_usr_segmented_indices(users_pair)
                for index_ in segmentation_indices:
                    segmentation_ids.append(index_[0])

                dialogues = get_segmented_message(segmentation_ids)

                if len(dialogues) < 1:
                    print '\nNo Dialogues To write! Dialogue Extraction Algorithm Gave' \
                          ' Zero Dialogues'
                    exit()

                is_dialogue = Dialogue.is_dialogue(dialogues, bots)

                for dialogue_ in dialogues:

                    if is_dialogue:

                        date_time = dialogue_[0]
                        sender = dialogue_[1]
                        recipient = dialogue_[2]
                        utterance = dialogue_[3]

                        path = os.path.join(self.__dialogue_full_path, str(folder_name))
                        Dialogue.__file_writer(path, str(file_name) + '.tsv', '\t'
                                               .join([date_time, sender, recipient, utterance]))
                        final_dialogues_utterances += 1

                segmentation_ids = []
                file_name += 1
                if file_name == 1000:
                    folder_name += 1
                    file_name = 0
                bar_.next()
            bar_.finish()

        except BaseException as excep:
            print '\nERROR: PROBLEM OCCURRED DURING WRITING DIALOGUES TO FILES.'
            print ' -LAST DETECTED PAIR OF USERS BEFORE THE ISSUE: {}'.format(users_pair)
            print ' -PROBLEMATIC DIALOGUE MOST PROBABLY IN "{}"'.format(dialogues)
            print ' -REASON: {}'.format(excep.message)
            logging.error('problem Occurred In write_segmented_dialogues Method')

        logging.info('Writing Segmented Dialogues Started')
        if self.__min_turns != 0:
            final_dialogues_utterances = Dialogue.__skip_dialogues(self.__dialogue_full_path,
                                                                   self.__min_turns)

        if self.__delete_with_recipient_file == 'yes':
            if os.path.exists(self.__clean_work_path):
                shutil.rmtree(self.__clean_work_path)
                print '\nSystem Is Committed To Remove Old Raw Data According the Parameter:' \
                      ' (delete_with_recipient_file = True). Data Removed.'
        return final_dialogues_utterances

    @staticmethod
    def is_match(candidate_first_response, candidate_initial_question, found_indices):
        """check when there is matching between a response and its related initial question"""
        response_time_index = candidate_first_response[0]
        response_sender = candidate_first_response[3]
        response_recipient = candidate_first_response[4]
        question_sender = candidate_initial_question[3]
        question_recipient = candidate_initial_question[4]

        return (response_recipient == question_sender and
                (question_recipient == '' or question_recipient == response_sender)
                and response_time_index not in found_indices)

    @staticmethod
    def __add_to_dialogues(candidate_first_response, day_index, seg_index,
                           candidate_initial_question=''):
        """this method adds a matched initial question with first response as a dialogue
         and also in case of only first response found, it adds it to be concatenated
          with relative dialogue """
        response_time_index = candidate_first_response[0]
        response_date_time = str.decode(candidate_first_response[2], 'utf-8')
        response_sender = str.decode(candidate_first_response[3], 'utf-8')
        response_recipient = str.decode(candidate_first_response[4], 'utf-8')
        response_utterance = str.decode(candidate_first_response[5], 'utf-8')

        save_segmented_message(seg_index, response_time_index, day_index,
                               response_date_time, response_sender,
                               response_recipient, response_utterance)

        if candidate_initial_question != '':
            question_time_index = candidate_initial_question[0]
            question_date_time = str.decode(candidate_initial_question[2], 'utf-8')
            question_sender = str.decode(candidate_initial_question[3], 'utf-8')
            question_recipient = str.decode(candidate_initial_question[4], 'utf-8')
            question_utterance = str.decode(candidate_initial_question[5], 'utf-8')

            save_segmented_message(seg_index, question_time_index, day_index,
                                   question_date_time, question_sender,
                                   question_recipient, question_utterance)

    @staticmethod
    def __load_bots(bots_path):
        """loads IRC channel bots names from a given txt file"""
        bots = set()
        if bots_path != '':
            with open(bots_path, 'r') as opener:
                lines = opener.readlines()
                for line in lines:
                    bots.add(line.strip())
        return bots

    @staticmethod
    def update_usr_addr_rec(users_addressed_recipients, candidate_initial_question,
                            candidate_first_response):
        """updates the state of dictionary that holds who is responding to whom,
         that dictionary will be passed to process_holes method in order to
          decide if a message is a hole and can be filled or not"""
        question_sender = candidate_initial_question[3]
        question_recipient = candidate_initial_question[4]
        response_sender = candidate_first_response[3]
        response_recipient = candidate_first_response[4]
        senders = users_addressed_recipients.keys()
        if question_sender not in senders:
            users_addressed_recipients.update(
                {question_sender: set([question_recipient])})
        else:
            users_addressed_recipients[question_sender].add(question_recipient)
        if response_sender not in senders:
            users_addressed_recipients.update(
                {response_sender: set([response_recipient])})
        else:
            users_addressed_recipients[response_sender].add(response_recipient)
        return users_addressed_recipients

    @staticmethod
    def is_dialogue(dialogues, bots):
        """checks if a segmented dialogue is a valid dialogue or not according
         to if it has chat bots messages or only one user is talking"""
        prev_sender = ""
        for dialogue_ in dialogues:
            sender = dialogue_[1]
            if prev_sender != sender and prev_sender != "":
                return sender not in bots and prev_sender not in bots
            prev_sender = sender

    @staticmethod
    def __load_dialogues(segmented_dialogues_counter, dialogue_full_path):
        """Loading Dialogue(s) Information Into Database so the statistical information
         called by the calculate_statistics function will be easily and fast fetched"""
        bar_ = Bar('Loading {} Dialogue(s) Information Into Database'
                   .format(segmented_dialogues_counter),
                   max=segmented_dialogues_counter)

        assert os.path.exists(dialogue_full_path), 'NO DIALOGUES FOUND TO GET STATISTICS' \
                                                   ' FOR! MAKE SURE YOU HAVE EXTRACTED' \
                                                   ' THE DIALOGUES FIRST!'
        folders = os.listdir(dialogue_full_path)
        for folder_ in folders:
            if not folder_.startswith('.'):
                files = os.listdir(dialogue_full_path + '/' + folder_)
                for file_ in files:
                    if not file_.startswith('.'):
                        with open(dialogue_full_path + '/' + folder_ + '/' + file_, 'r')\
                                as opener:
                            lines = opener.readlines()
                            for line in lines:
                                utterance = str.decode(line.split('\t')[3], 'utf-8')
                                file_id = str.decode(folder_ + '/' + file_, 'utf-8')
                                save_utterance(file_id, utterance)
                        bar_.next()
        bar_.finish()

    @staticmethod
    def calculate_statistics(dialogue_full_path):
        """get statistical information from extracted dialogues"""
        logging.info('Calculating Statistics Method Called')
        print 'Fetching Required Python NLTK Data\n'
        nltk.download('stopwords')
        segmented_dialogues_counter = Dialogue.__files_count(dialogue_full_path)
        print 'Extracted Dialogues Statistics Were Requested, That Might Take Some Time.'
        start_time = time.time()
        folders = os.listdir(dialogue_full_path)
        Dialogue.__load_dialogues(segmented_dialogues_counter, dialogue_full_path)
        stopwords = nltk.corpus.stopwords.words('english')
        colloquial_counter = 0
        nstop_words_counter = 0
        words_counter = 0
        all_utterances = []
        bar_ = Bar('Calculating Statistics Over All {} Dialogue(s)'
                   .format(segmented_dialogues_counter),
                   max=segmented_dialogues_counter)
        for folder_ in folders:
            if not folder_.startswith('.'):
                files = os.listdir(dialogue_full_path + '/' + folder_)
                for file_ in files:
                    if not file_.startswith('.'):
                        turns = 0
                        utterances_text = get_utterances(str.decode(folder_ + '/' + file_, 'utf-8'))
                        for text_ in utterances_text:
                            turns += 1
                            all_utterances.append(text_[0])
                            utterance_words = 0
                            if text_[0] != '':
                                for word_ in re.split("[, \-!?;.]", text_[0]):
                                    word_ = word_.strip().strip('.').strip(',').strip("'")\
                                        .strip(':').strip(';').strip('_').strip('-').strip()\
                                        .strip('!').strip('?')

                                    if len(word_) > 0:
                                        if not stem(word_.lower()) in stopwords:
                                            nstop_words_counter += 1
                                            utterance_words += 1
                                        words_counter += 1
                                        if not DICT.check(word_):
                                            colloquial_counter += 1
                        bar_.next()
                        save_dialogue_turns(str.decode(dialogue_full_path + '/' + folder_ + '/'
                                                       + file_, 'utf-8'), turns)
        bar_.finish()

        get_db_statistics()
        db_stats = get_db_statistics()
        Dialogue.__write_statistics(start_time, segmented_dialogues_counter, all_utterances,
                                    nstop_words_counter, words_counter, colloquial_counter,
                                    db_stats)
        logging.info('Calculating Statistics Finished')

    @staticmethod
    def __write_statistics(start_time, segmented_dialogues_counter, all_utterances,
                           nstop_words_counter, words_counter, colloquial_counter,
                           db_stats):
        """write statistical figures"""
        min_turn_value = db_stats[0]
        max_turn_value = db_stats[1]
        min_turn_dialogue = db_stats[2]
        max_turn_dialogues = db_stats[3]
        sum_turn_value = db_stats[4]
        print '\nCalculating Dialogues Turns Averages Over All Dialogues . . .'

        print '\nComputation Has Finished. Time Elapsed Was Approximately {} Minute(s)'.format(
            int((time.time() - start_time) / 60))
        print '\n-----------------------------------------------------------------------------'
        print 'Final Statistics Before Creating Dialogues Data-set For Supervised-Learning'
        print '-----------------------------------------------------------------------------\n'
        print ' - Num Of One-One Dialogue(s): {}'.format(segmented_dialogues_counter)
        print ' - Num Of Utterances: {}'.format(len(all_utterances))
        print ' - Num Of Words (Excluding Stop-Words): {}'.format(nstop_words_counter)

        print ' - Avg Num Of Words (Excluding Stop-Words) Per utterance: {}'.format(
            round((nstop_words_counter / len(all_utterances)), 4))

        print ' - Avg Num Of Turns In Dialogues: {}'. \
            format(round((sum_turn_value / segmented_dialogues_counter), 4))

        print ' - Maximum Num Of Turns In Dialogues Is {}, With a Percentage {}%' \
              ' Occurrence in All Dialogues.' \
            .format(max_turn_value,
                    round((len(max_turn_dialogues) / segmented_dialogues_counter) * 100, 4))
        print ' - Dialogue(s) That have The Max Turns:'
        for file_ in max_turn_dialogues:
            file_path = file_[0]
            print '    -' + file_path

        print ' - Minimum Num Of Turns In Dialogues Is {}, With a Percentage {}%' \
              ' Occurrence in All Dialogues'. \
            format(min_turn_value,
                   round((len(min_turn_dialogue) / segmented_dialogues_counter) * 100, 4))

        print ' - Percentage of Colloquial Text Over All IRC Words: {}%'. \
            format(round((colloquial_counter / words_counter) * 100, 4))

        print '\n Now Computing Top 100 Words Frequency . . . (Might Take Time!)\n'
        top_words = Dialogue.__filter_top_words(FreqDist(re.split("[, \-!?;.]", ' '
                                                                  .join(all_utterances)))
                                                .most_common())
        print ' - Most Frequent 100 Words (Excluding Stop-Words) Occurred On That IRC' \
              ' Users Utterances: {}\n' \
            .format(Dialogue.__filter_top_words(top_words)[:100])

    @staticmethod
    def process_holes(day_index_p, indices_p, non_addressed_msg_p,
                      users_addressed_recipients_p):
        """this method is where to apply the hole-filling algorithm, first, it loop through
         all non-addressed utterances gathered from the match_utterance method, then it fills
          gaps which are the utterances without an explicitly mentioned recipient, it tries
           to guess who was the recipient by checking if only two persons were talking in a
            given time frame so any un-addressed utterance sent by one of them,
             will be considered as addressing the other"""
        holes = set()
        as_sender_chat_count = 0  # counts how many users this user is talking to when
        #  he/she is sender

        # to be used to guide the algorithm for which relative conversations indices
        # it should include a found hole
        seg_indices = get_msg_segmented_indices(day_index_p, indices_p)
        as_recipient_chat_count = 0  # counts how many users this user is talking to when
        #  he/she is recipient
        filled_holes = 0
        for seg_index in seg_indices:
            if len(non_addressed_msg_p) != 0:
                for outer_sender in users_addressed_recipients_p:
                    for recipient in users_addressed_recipients_p[outer_sender]:
                        if recipient != '':
                            as_sender_chat_count += 1
                    for inner_sender in users_addressed_recipients_p:
                        for recipient_ in users_addressed_recipients_p[inner_sender]:
                            if recipient_ == inner_sender:
                                as_recipient_chat_count += 1
                    if as_sender_chat_count <= 1 and as_recipient_chat_count <= 1:
                        filled_holes_counts = Dialogue.fill_hole(non_addressed_msg_p,
                                                                 day_index_p, seg_index,
                                                                 outer_sender, holes)
                        filled_holes += filled_holes_counts
                    as_sender_chat_count = 0

        return filled_holes

    @staticmethod
    def fill_hole(non_addressed_msg_p, day_index_p, seg_index_p, user_name_p, holes_p):
        """this method invoked by the process_holes function, this method responsible
         for the real filling and insertion to database of these non-addressed utterances
          when the conditions met to apply the filling and it matches which non-address
           utterance is to be added to which dialogue"""
        # get senders list of a certain day and certain conversation segmentation id
        senders = get_senders(day_index_p, seg_index_p)
        filled_holes_count = 0
        segmentation_index = seg_index_p[0]
        # match a passed user name to insert a hole utterance to its related segmentation id
        for msg in non_addressed_msg_p:

            msg_time_index = msg[0]
            msg_date_time = str.decode(msg[2], 'utf-8')
            msg_sender = str.decode(msg[3], 'utf-8')
            msg_utterance = str.decode(msg[5], 'utf-8')

            for sender in senders:
                sender = sender[0]
                if sender == msg_sender:
                    if msg_sender == user_name_p:
                        if msg_time_index not in holes_p:
                            holes_p.add(msg_time_index)

                            # check if the hole is not added before
                            timing_indices = get_timing_indices(day_index_p, msg_time_index,
                                                                seg_index_p)
                            if len(timing_indices) == 0:
                                save_segmented_message(segmentation_index, msg_time_index,
                                                       day_index_p, msg_date_time,
                                                       msg_sender, '', msg_utterance)
                                filled_holes_count += 1
        return filled_holes_count

    @staticmethod
    def __report_work(dialogue_full_path, start_time, filled_holes, dialogues_utterances_count):
        """report segmentation results"""
        print '\n------------------------------------------------------------------------------'
        print 'Dialogues Have Been Segmented For Each Pair of Users. Please Check the Results' \
              ' on the Path: "{}"'.format(dialogue_full_path)
        print 'Time Elapsed Was Approximately {} Minute(s)'\
            .format(int((time.time() - start_time) / 60))
        print '------------------------------------------------------------------------------'

        print '\n----------------------------------------------------------------------'
        if filled_holes == 0:
            print 'No Filled Holes Applied In The Processed Dialogue(s)'

        else:
            print 'Percentage of Holes Utterances Found and Filled In All ' \
                  'Extracted Utterances: {}%'.format\
            (round((filled_holes/dialogues_utterances_count) * 100, 4))
        print '----------------------------------------------------------------------\n'

    @staticmethod
    def verify_segmentation(dialogue_full_path):
        """validate generated segmented dialogue files, each file must have only two users"""
        logging.info('Verifying Segmentation results')
        print '\nValidating dialogueExtraction Algorithm Output...'
        assert os.path.exists(dialogue_full_path), 'NO DIALOGUES FOUND TO VALIDATE!' \
                                                   ' MAKE SURE YOU HAVE EXTRACTED THE' \
                                                   ' DIALOGUES FIRST!'
        folders = os.listdir(dialogue_full_path)
        segmented_dialogues_counter = 0
        problematic_files = set()
        for folder_ in folders:
            if not folder_.startswith('.'):
                files = os.listdir(dialogue_full_path + '/' + folder_)
                for file_ in files:
                    user_list = set()
                    if not file_.startswith('.'):
                        segmented_dialogues_counter += 1
                        with open(dialogue_full_path + '/' + folder_ + '/' + file_, 'r')\
                                as reader:
                            lines = reader.readlines()
                            for line in lines:
                                user = line.split('\t')[1]
                                if user not in user_list:
                                    user_list.add(user)
                        if len(user_list) > 2:
                            problematic_files.\
                                add(dialogue_full_path + '/' + folder_ + '/' + file_)

        assert segmented_dialogues_counter > 0, 'NO DIALOGUES FOUND TO VALIDATE!' \
                                                ' MAKE SURE YOU HAVE EXTRACTED' \
                                                ' THE DIALOGUES FIRST!'

        if len(problematic_files) > 0:
            print 'PROBLEM: SEGMENTED DIALOGUE(S) HAVE MORE THAN TWO USERS!'
            print ' - THE PROBLEM OCCURRED IN THE BELOW DIALOGUE FILE(S)'
            for file_ in problematic_files:
                print file_
            logging.error('Verifying Segmented Dialogues Failed')
            exit()
        else:
            print 'SUCCESS: {} Segmented Dialogue(s) Are OK!\n'\
                .format(segmented_dialogues_counter)

        return segmented_dialogues_counter

    @staticmethod
    def verify_cleaned_data(dialogue_full_path):
        """validate output structure, each line in each file must have
         4 fields and some fields should not be empty"""
        logging.info('Verifying Files Output')
        print '\nValidating Component Output...'
        problematic_files = set()
        errors = set()
        path_to_check = dialogue_full_path
        counter = 0
        assert os.path.exists(path_to_check), 'NO DIALOGUES FOUND TO VALIDATE! MAKE SURE' \
                                              ' YOU HAVE EXTRACTED THE DIALOGUES FIRST!'
        folders = os.listdir(path_to_check)
        for folder_ in folders:
            if not folder_.startswith('.'):
                files = os.listdir(path_to_check + '/' + folder_)
                for file_ in files:
                    processed_lines = set()
                    if not file_.startswith('.'):
                        counter += 1
                        with open(path_to_check + '/' + folder_ + '/' + file_, 'r') as opener:
                            lines = opener.readlines()
                            for line in lines:
                                if line in processed_lines:
                                    problematic_files.add(path_to_check + '/' + file_)
                                    errors.add('Duplicated Lines!')

                                processed_lines.add(line)
                                line = line.split('\t')
                                if len(line) != 4:
                                    problematic_files.add(path_to_check + '/' + file_)
                                    errors.add(
                                        'Bad File Structure, Each File Must Have not less'
                                        ' or more than 4 fields!')

                                data_time = line[0]
                                sender = line[1]
                                utterance = line[3]
                                if len(data_time) == 0 or len(sender) == 0 or len(utterance) == 0:
                                    problematic_files.add(path_to_check + '/' + file_)
                                    errors.add('Unexpected Empty String at one of the Fields')

        assert counter > 0, 'NO DIALOGUES FOUND TO VALIDATE! MAKE SURE YOU HAVE' \
                            ' EXTRACTED THE DIALOGUES FIRST!'
        if len(problematic_files) > 0:
            print 'PROBLEM: COMPONENT OUTPUT HAS SOME BAD RESULTS'
            print ' - THE PROBLEM OCCURRED IN THE BELOW OUTPUT FILE(S)'
            for file_ in problematic_files:
                print file_
            print '- REASON(S):'
            for error_ in errors:
                print error_
            logging.error('Verifying Files Output Failed')
            exit()
        else:
            print 'SUCCESS: {} Component Outputs Are OK!'.format(counter)

    @staticmethod
    def __filter_top_words(freq_dist_list):
        """loop through all the most frequent words retrieved from the calculate statistics
         method and ignore some of these words if they were in stop words or too
         small in length and only get 100 words form the list"""
        new_list = []
        counter = 0
        stopwords_ = nltk.corpus.stopwords.words('english')

        for word_, freq_ in freq_dist_list:

            word_ = word_.strip().strip('.').strip(',').strip("'").strip(':').strip(';')\
                .strip('_').strip('-').strip().strip('!').strip('?')

            if not len(word_) <= 2 and not stem(word_.lower()) in stopwords_:
                new_list.append((word_, freq_))
                counter += 1

            if counter == 100:
                break
        return new_list

    @staticmethod
    def __skip_dialogues(path_p, min_turns):
        """evaluating number of turns in generated dialogues, if less than a certain number,
         then these dialogues will be removed"""
        logging.info('Skipping Dialogues Method Called')
        turns_per_weak_dialogue = set()
        final_dialogues_utterances = 0
        print '\nEvaluating Number Of Turns In Dialogues. Removing Weak Dialogues According' \
              ' To parameter (min_turns)'
        files_count = Dialogue.__files_count(path_p)
        path_to_check = path_p
        if not os.path.exists(path_to_check):
            print 'NO DIALOGUES FOUND TO PROCESS! MAKE SURE' \
                  ' YOU HAVE EXTRACTED THE DIALOGUES FIRST!'
            exit()
        bar_ = Bar('Detecting Dialogue(s) With Turns Less Than {}. Processing {} File(s)'
                   .format(min_turns, files_count), max=files_count)

        folders = os.listdir(path_to_check)

        for folder_ in folders:
            if not folder_.startswith('.'):
                files = os.listdir(path_to_check + '/' + folder_)
                for file_ in files:
                    if not file_.startswith('.'):
                        with open(path_to_check + '/' + folder_ + '/' + file_, 'r')\
                                as opener:
                            lines = opener.readlines()
                            turns = len(lines)

                        if turns < min_turns:
                            turns_per_weak_dialogue\
                                .add(path_to_check + '/' + folder_ + '/' + file_)
                        else:
                            final_dialogues_utterances += turns
                        bar_.next()
        bar_.finish()
        if len(turns_per_weak_dialogue) < 1:
            print 'No Weak Dialogues Found!'
        else:
            bar_ = Bar('Removing {} Detected Weak Dialogue(s)'
                       .format(len(turns_per_weak_dialogue)),
                       max=len(turns_per_weak_dialogue))
            for weak_dia in turns_per_weak_dialogue:
                os.remove(weak_dia)
                bar_.next()
            bar_.finish()
        return final_dialogues_utterances

    @staticmethod
    def is_time_changed(initial_date, new_date, time_frame):
        """logical function to compare and validate two messages times to check if these
             two dates were in some minutes time frame or not"""
        initial_time = str(initial_date).split('T')[1].replace(':00.000Z', '')  # like 03:45
        new_time = str(new_date).split('T')[1].replace(':00.000Z', '')

        initial_hour = int(initial_time.split(':')[0])  # like 03
        new_hour = int(new_time.split(':')[0])

        initial_minute = int(initial_time.split(':')[1])  # like 45
        new_minute = int(new_time.split(':')[1])

        # if time difference like : 03:45 & 03:43
        if (initial_hour == new_hour) and abs(initial_minute - new_minute) <= time_frame:
            return False
        # if time difference like : 3:00 & 02:59 or 00:00 & 23:59
        elif ((initial_hour - new_hour == 1) or (initial_hour == 00 and new_hour == 23)) \
                and (60 - new_minute + initial_minute) <= time_frame:
            return False
        else:
            return True

    @staticmethod
    def __files_count(path):
        """to count how many files in a directory,
         useful for quantifying the required work"""
        files_count = 0
        print '\nGathering Information Required Before Processing...'
        for _, _, files in os.walk(path):
            for file_ in files:
                if not file_.startswith('.'):
                    files_count += 1

        if files_count < 1:
            print 'NO FILES WERE FOUND TO PROCESS.'

        return files_count

    @staticmethod
    def __segmentation_index_setup(path):
        """to count how many utterances in all raw data about to be processed,
         useful to measure the max segmentation index used in a loop through all utterances"""
        files_count = Dialogue.__files_count(path)
        max_seg_index = 0
        bar_ = Bar('Counting All Utterances To Measure Maximum Segmentation Index.'
                   ' Processing {} File(s)'.format(files_count),
                   max=files_count)
        for _, _, files in os.walk(path):
            for file_ in files:
                if not file_.startswith('.'):
                    with open(path + '/' + file_, 'r') as reader:
                        lines = reader.readlines()
                        max_seg_index += len(lines)
                        bar_.next()
        bar_.finish()
        return max_seg_index

    @staticmethod
    def __file_writer(path, file_name, context):
        """appending a dialogue message between two users to their
         associate dialogue file"""
        if os.path.exists(path):
            with open(path + '/' + file_name, 'a') as file_:
                file_.write(context)
        else:
            os.makedirs(path)
            with open(path + '/' + file_name, 'a') as file_:
                file_.write(context)

if __name__ == '__main__':

    PARSER = argparse.ArgumentParser()
    PARSER.add_argument('-clean_work_path', help='specify the path of data to extract dialogues'
                                                 ' from. by default set to local folder',
                        nargs='?', const='./', type=str, default='./')

    PARSER.add_argument('-dialogue_work_path', help="""specify the path of the output dialogues,
     by default set to local folder.""", nargs='?', const='./', type=str, default='./')

    PARSER.add_argument('-delete_with_recipient_file', help='(yes) indicates if the raw data'
                                                            ' before extraction should be'
                                                            ' deleted after dialogues extraction'
                                                            ', the default is no',
                        type=str, nargs='?', const='no', default='no')

    PARSER.add_argument('-with_stats', help="""(yes)indicates if statistical report will be
     executed after the dialogues extraction, default is no""", nargs='?', const='no',
                        type=str, default='no')

    PARSER.add_argument('-time_frame', help="""specify the conversation time frame (in minutes)
    the dialogue extraction algorithm will use as a heuristic, default is 3 """,
                        type=int, nargs='?', const=3, default=3)

    PARSER.add_argument('-gap_time_frame', help='specify the time frame of conversation the'
                                                ' hole-filling algorithm will use as a'
                                                ' heuristic, default is 3',
                        type=int, nargs='?', const=3, default=3)

    PARSER.add_argument('-only_stats', help='(yes)indicates if only statistical report weill be'
                                            ' called supposing that there is already extracted'
                                            ' dialogues, default is no', nargs='?',
                        const='no', type=str, default='no')

    PARSER.add_argument('-min_turns', help='by default = 3 and it specify the minimum number of'
                                           ' turns in extracted dialogues to be accepted,'
                                           ' if turns were less than that number,'
                                           ' they will be deleted later '
                        , type=int, nargs='?', const=3, default=3)

    PARSER.add_argument('-bots_path', help='to configure the path from where to load IRC channel'
                                           ' bots names to ignore their messages since they'
                                           ' are not humans',
                        nargs='?', const='', type=str, default='')

    PARSER.add_argument('-extracted_dialogues_path', help='specifies the path of already '
                                                          'extracted dialogues to'
                                                          ' run statistics for',
                        nargs='?', const='', type=str, default='')

    ARGM = PARSER.parse_args()

    DIALOGUE = Dialogue(clean_work_path=ARGM.clean_work_path,
                        dialogue_work_path=ARGM.dialogue_work_path,
                        gap_time_frame=ARGM.gap_time_frame,
                        delete_with_recipient_file=ARGM.delete_with_recipient_file,
                        time_frame=ARGM.time_frame,
                        with_stats=ARGM.with_stats, only_stats=ARGM.only_stats,
                        min_turns=ARGM.min_turns, bots_path=ARGM.bots_path)

    if ARGM.only_stats == 'yes':
        if ARGM.extracted_dialogues_path != '':
            Dialogue.calculate_statistics(ARGM.extracted_dialogues_path)
        else:
            print 'YOU MUST GIVE A PATH OF ALREADY EXTRACTED DIALOGUES'
    else:
        DIALOGUE.extract_dialogues()
