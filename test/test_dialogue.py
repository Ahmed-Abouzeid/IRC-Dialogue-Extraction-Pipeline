"""this module is responsible for implementing the unit tests for major
 functions in Dialogue.py module"""
import cPickle
import unittest
from unittest import TestCase
from irc_process.dialogue import Dialogue

# initialize the dialogue instance as a required step for some units
DIALOGUE = Dialogue(clean_work_path='./days_with_recipients',
                    dialogue_work_path='./',
                    gap_time_frame=3,
                    time_frame=3,
                    min_turns=3, bots_path='./bots_ubuntu.txt')

# the below are all mocks needed to run the unit test, they are parameters
#  that will be passed as mock data for test

MATCH_UTTER_MOCKS = ['./utterances.pkl', '2007-01-01', 12063]
WRITE_DIA_MOCK = './segmenteg_users.pkl'
PROCESS_HOLES_MOCK = './process_holes_parameters.pkl'

IS_MATCH_MOCKS = [[(12061, '2007-01-01', '2007-01-01T12:01:00.000Z', 'mnoir', 'sharp15',
                   'possible problem in the conf file - it sounds like to me\n'),
                  (12048, '2007-01-01', '2007-01-01T12:00:00.000Z', 'sharp15', 'mnoir',
                   "either way. i can't find error messages from either sshd or proftpd."
                   "  both init scripts print Starting service   [fail] \n"), set([]), True],
                  [(12061, '2007-01-01', '2007-01-01T12:01:00.000Z', 'mnoir', 'sharp15',
                   'possible problem in the conf file - it sounds like to me\n'),
                  (12052, '2007-01-01', '2007-01-01T12:00:00.000Z', 'MuffY', '', 'PONG!\n')
                      , set([]), False],
                  [(12060, '2007-01-01', '2007-01-01T12:01:00.000Z', 'jasin', 'lintux',
                    'To fix screen resolution or other X problems:'
                    ' http://help.ubuntu.com/community/FixVideoResolutionHowto\n'),
                   (12059, '2007-01-01', '2007-01-01T12:01:00.000Z', 'mwe', '', 'yeah ;)\n'),
                   set([12061, 12048]), False]]

UPDATE_USR_ADDR_REC_MOCKS = [{'jasin': set(['lintux']), 'mnoir': set(['sharp15']),
                              'mwe': set(['']), 'MuffY': set(['pong'])},
                             (12056, '2007-01-01', '2007-01-01T12:01:00.000Z', 'adam_', 'ok',
                              "I'll get to that, but in the meantime, maybe you could help me"
                              " out with my onboard card then.....?\n"),
                             (12061, '2007-01-01', '2007-01-01T12:01:00.000Z', 'mnoir',
                              'sharp15', 'possible problem in the conf file - it sounds'
                                         ' like to me\n'),
                             {'jasin': set(['lintux']), 'mnoir': set(['sharp15']), 'mwe': set(['']),
                              'MuffY': set(['pong']), 'adam_': set(['ok'])}]


IS_TIME_CHANGED_MOCKS = [('2007-01-01T12:07:00.000Z', '2007-01-01T12:04:00.000Z', False),
                         ('2007-01-01T12:01:00.000Z', '2007-01-01T11:58:00.000Z', False),
                         ('2007-01-01T00:01:00.000Z', '2007-01-01T23:59:00.000Z', False),
                         ('2007-01-01T12:08:00.000Z', '2007-01-01T12:04:00.000Z', True)]


class TestDialogue(TestCase):
    """class that defines the unit test functions"""
    def test___process_holes(self):
        """tests the process_holes function given a mock arguments, note that this unit test
         is affecting the result of write_segmented_dialogues unit test as it creates database
          records that will be manipulated later by the write_segmented_dialogues"""
        process_holes_parameters = cPickle.load(open(PROCESS_HOLES_MOCK, 'rb'))
        day_index_p = process_holes_parameters[0]
        indices_p = process_holes_parameters[1]
        non_addr_msg_p = process_holes_parameters[2]
        users_addr_rec_p = process_holes_parameters[3]
        correct_post_condition = 1
        self.assertEqual(Dialogue.process_holes(day_index_p, indices_p, non_addr_msg_p,
                                                users_addr_rec_p), correct_post_condition)

    def test___match_utterances(self):
        """tests the match_utterances function in dialogue.py"""
        day_index = MATCH_UTTER_MOCKS[1]
        max_seg_index = MATCH_UTTER_MOCKS[2]
        day_utterances = MATCH_UTTER_MOCKS[0]
        utterances = cPickle.load(open(day_utterances, 'rb'))
        correct_post_condition = [7747, 1626]

        self.assertEqual(DIALOGUE.match_utterances(utterances, day_index, max_seg_index),
                         correct_post_condition)

    def test___write_seg_dialogues(self):
        """tests the number of segmented dialogues after evaluating them, note that it is depending
         on the other unit test results (process_holes) as it creates the database records that
          will be manipulated by that unit test"""
        segmented_users = cPickle.load(open(WRITE_DIA_MOCK, 'rb'))
        correct_post_condition = 7283
        self.assertEqual(DIALOGUE.write_segmented_dialogues(segmented_users),
                         correct_post_condition)

    def test___is_match(self):
        """tests the is_match function in dialogue.py"""
        for element in IS_MATCH_MOCKS:
            first_response = element[0]
            initial_question = element[1]
            found_indices = element[2]
            correct_post_condition = element[3]
            self.assertEqual(Dialogue.is_match(first_response, initial_question,
                                               found_indices), correct_post_condition)

    def test___update_usr_addr_rec(self):
        """tests the update_usr_addr_rec function in dialogue.py"""
        users_addr_recipients = UPDATE_USR_ADDR_REC_MOCKS[0]
        initial_question = UPDATE_USR_ADDR_REC_MOCKS[1]
        first_response = UPDATE_USR_ADDR_REC_MOCKS[2]
        correct_post_condition = UPDATE_USR_ADDR_REC_MOCKS[3]
        self.assertEqual(Dialogue.update_usr_addr_rec(users_addr_recipients, initial_question,
                                                      first_response),
                         correct_post_condition)

    def test___is_time_changed(self):
        """tests the is_time_changed function in dialogue.py"""
        for element in IS_TIME_CHANGED_MOCKS:
            initial_date = element[0]
            new_date = element[1]
            correct_post_condition = element[2]
            self.assertEqual(Dialogue.is_time_changed(initial_date, new_date, 3),
                             correct_post_condition)

if __name__ == '__main__':
    unittest.main()
