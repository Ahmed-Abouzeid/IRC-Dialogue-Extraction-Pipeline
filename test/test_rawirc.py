"""This module responsible for handling the major RawIRC functions to be test for
 correctness based on some trusted post_conditions"""
import difflib
import os
import cPickle
from irc_process.rawirc import RawIRC
# test clean function related settings

UBUNTU_POST_CON_CLN = './ubuntu_correct_cln'
UBUNTU_TST_CLN = './ubuntu_test'
UBUNTU_MOCK = './ubuntu_mocks'
KOHA_POST_CON_CLN = './koha_correct_cln'
KOHA_TST_CLN = './koha_test'
KOHA_MOCK = './koha_mocks'
PERL_POST_CON_CLN = './perl_correct_cln'
PERL_TST_CLN = './perl_test'
PERL_MOCK = './perl_mocks'
LISP_POST_CON_CLN = './lisp_correct_cln'
LISP_TST_CLN = './lisp_test'
LISP_MOCK = './lisp_mocks'
SYS_MSG_FILE = './sysmsg.txt'

# test createRecipient function related settings

UBUNTU_POST_CON_RCP = './ubuntu_correct_rcp'
UBUNTU_TST_RCP = './ubuntu_test'
KOHA_POST_CON_RCP = './koha_correct_rcp'
KOHA_TST_RCP = './koha_test'
PERL_POST_CON_RCP = './perl_correct_rcp'
PERL_TST_RCP = './perl_test'
LISP_POST_CON_RCP = './lisp_correct_rcp'
LISP_TST_RCP = './lisp_test'

# test concatenation function related settings

UBUNTU_POST_CON_CON = './ubuntu_correct_con'
UBUNTU_TST_CON = './ubuntu_test'
KOHA_POST_CON_CON = './koha_correct_con'
KOHA_TST_CON = './koha_test'
PERL_POST_CON_CON = './perl_correct_con'
PERL_TST_CON = './perl_test'
LISP_POST_CON_CON = './lisp_correct_con'
LISP_TST_CON = './lisp_test'

# test make_user_list function related settings
UBU_USERS = cPickle.load(open('./ubuntu_list.pkl', 'rb'))
KOH_USERS = cPickle.load(open('./koha_list.pkl', 'rb'))
PER_USERS = cPickle.load(open('./perl_list.pkl', 'rb'))
LIS_USERS = cPickle.load(open('./lisp_list.pkl', 'rb'))

IRCS = [('Ubuntu', UBUNTU_POST_CON_CLN, UBUNTU_TST_CLN, UBUNTU_POST_CON_RCP,
         UBUNTU_TST_RCP, UBUNTU_POST_CON_CON, UBUNTU_TST_CON, UBU_USERS),
        ('Koha', KOHA_POST_CON_CLN, KOHA_TST_CLN, KOHA_POST_CON_RCP,
         KOHA_TST_RCP, KOHA_POST_CON_CON, KOHA_TST_CON, KOH_USERS),
        ('Perl', PERL_POST_CON_CLN, PERL_TST_CLN, PERL_POST_CON_RCP,
         PERL_TST_RCP, PERL_POST_CON_CON, PERL_TST_CON, PER_USERS),
        ('Lisp', LISP_POST_CON_CLN, LISP_TST_CLN, LISP_POST_CON_RCP,
         LISP_TST_RCP, LISP_POST_CON_CON, LISP_TST_CON, LIS_USERS)]


def get_ubuntu_test_data():
    """run rawirc on lisp arguments"""
    raw_irc = RawIRC(raw_data_path=UBUNTU_MOCK, clean_work_path=UBUNTU_TST_CLN,
                     time_regexp=r'\[\d\d:\d\d\]',
                     raw_msg_field_separator=' ',
                     date_regexp=r'\d\d\d\d\d\d\d\d',
                     user_sys_annotations='<,>',
                     time_sys_annotations='[,]',
                     old_date_format='%Y%m%d',
                     concatenate='yes',
                     use_enchant='yes')
    raw_irc.clean()
    raw_irc.create_recipient()


def get_perl_test_data():
    """run rawirc on lisp arguments"""
    raw_irc = RawIRC(raw_data_path=PERL_MOCK, clean_work_path=PERL_TST_CLN,
                     time_regexp=r'^(\s*\d\d\:\d\d)$',
                     date_regexp=r'\d\d\d\d-\d\d-\d\d',
                     old_date_format='%Y-%m-%d',
                     concatenate='yes',
                     use_enchant='yes')
    raw_irc.clean()
    raw_irc.create_recipient()


def get_koha_test_data():
    """run rawirc on lisp arguments"""
    raw_irc = RawIRC(raw_data_path=KOHA_MOCK, clean_work_path=KOHA_TST_CLN,
                     time_regexp=r'^(\s*\d\d\:\d\d)$',
                     date_regexp=r'\d\d\d\d-\d\d-\d\d',
                     old_date_format='%Y-%m-%d',
                     concatenate='yes',
                     use_enchant='yes',
                     time_user_lines=1)
    raw_irc.clean()
    raw_irc.create_recipient()


def get_lisp_test_data():
    """run rawirc on lisp arguments"""
    raw_irc = RawIRC(raw_data_path=LISP_MOCK, clean_work_path=LISP_TST_CLN,
                     time_regexp=r'\d\d:\d\d:\d\d',
                     raw_msg_field_separator=' ',
                     date_regexp=r'\d\d\d\d.\d\d.\d\d',
                     user_sys_annotations='<,>',
                     old_date_format='%Y.%m.%d',
                     concatenate='yes',
                     use_enchant='yes',
                     process_file_reg_exp=r'(lisp-)(\d\d\d\d-\d\d)',
                     process_file_date_format='%Y-%m',
                     force_remove_sysmsg='yes', rtrim_time=3, sys_msg_path=SYS_MSG_FILE)
    raw_irc.clean()
    raw_irc.create_recipient()


def test_clean():
    """test function for the clean function output"""
    for irc in IRCS:
        success = 0
        test_data_path = irc[2] + '/Clean/Days/'
        post_con_path = irc[1] + '/'
        irc_name = irc[0]
        for tst_file in os.listdir(test_data_path):
            if not tst_file.startswith('.'):
                post_con_counter = 0
                for post_con_file in os.listdir(irc[1]):
                    if not post_con_file.startswith('.'):
                        post_con_counter += 1
                        if tst_file == post_con_file:
                            correct_contents = open(post_con_path + post_con_file, 'r')
                            test_contents = open(test_data_path + tst_file, 'r')
                            if difflib.SequenceMatcher(None, correct_contents.read(),
                                                       test_contents.read())\
                                    .real_quick_ratio() == 1:
                                success += 1
                            else:
                                success -= 1

        assert success == post_con_counter and success != 0, 'FAILURE: Clean Function Test' \
                                                             ' Failed For {} IRC'.format(irc_name)
        print 'SUCCESS: Clean Function Test Passed For {} IRC'.format(irc_name)


def test_create_recipient():
    """test function for the create_recipient function output"""
    for irc in IRCS:
        success = 0
        test_data_path = irc[4] + '/Clean/Days_With_Recipients/'
        post_con_path = irc[3] + '/'
        irc_name = irc[0]
        for tst_file in os.listdir(test_data_path):
            if not tst_file.startswith('.'):
                post_con_counter = 0
                for post_con_file in os.listdir(irc[3]):
                    if not post_con_file.startswith('.'):
                        post_con_counter += 1
                        if tst_file == post_con_file:
                            correct_contents = open(post_con_path + post_con_file, 'r')
                            test_contents = open(test_data_path
                                                 + tst_file, 'r')
                            if difflib.SequenceMatcher(None, correct_contents.read(),
                                                       test_contents.read()) \
                                    .real_quick_ratio() == 1:
                                success += 1
                            else:
                                success -= 1
        assert success == post_con_counter and success != 0, 'FAILURE: createRecipient' \
                                                             ' Function Test Failed' \
                                                             ' For {} IRC'.format(irc_name)
        print 'SUCCESS: createRecipient Function Test Passed For {} IRC'.format(irc_name)


def test_concatenate():
    """test function for the concatenate function output"""
    for irc in IRCS:
        success = 0
        test_data_path = irc[6] + '/Clean/Days_With_Concatenation/'
        post_con_path = irc[5] + '/'
        irc_name = irc[0]
        for tst_file in os.listdir(irc[6] + '/Clean/Days_With_Concatenation/'):
            if not tst_file.startswith('.'):
                post_con_counter = 0
                for post_con_file in os.listdir(irc[5]):
                    if not post_con_file.startswith('.'):
                        post_con_counter += 1
                        if tst_file == post_con_file:
                            correct_contents = open(post_con_path + post_con_file, 'r')
                            test_contents = open(test_data_path
                                                 + tst_file, 'r')
                            if difflib.SequenceMatcher(None, correct_contents.read(),
                                                       test_contents.read()) \
                                    .real_quick_ratio() == 1:
                                success += 1
                            else:
                                success -= 1
        assert success == post_con_counter and success != 0, 'FAILURE: concatenate ' \
                                                             'Function Test Failed' \
                                                             ' For {} IRC'.format(irc_name)
        print 'SUCCESS: concatenate Function Test Passed For {} IRC'.format(irc_name)


def test_make_user_list():
    """test function for the make_user_list function output"""
    for irc in IRCS:
        test_data_path = irc[2]+'/Clean/Days'
        post_con_path = irc[7]
        irc_name = irc[0]
        assert difflib.SequenceMatcher(None, RawIRC.make_user_list(test_data_path),
                                       post_con_path)\
                   .real_quick_ratio() == 1, 'FAILURE: make users Function Test Failed' \
                                             ' For {} IRC'.format(irc_name)
        print 'SUCCESS: make users Function Test Passed For {} IRC'.format(irc_name)


if __name__ == '__main__':
    print '\nGetting Data To Be Tested, Running RawIRC On All IRCs'
    get_ubuntu_test_data()
    get_koha_test_data()
    get_lisp_test_data()
    get_perl_test_data()
    print '\n\n*************************************TEST STARTED****************************' \
          '*****************\n\n'
    test_clean()
    print '\n****************************Clean Function Succeeded For All IRCs*****************' \
          '************\n'
    test_make_user_list()
    print '\n***********************Make User List Function Succeeded For All IRCs**************' \
          '***********\n'
    test_create_recipient()
    print '\n**********************Create Recipient Function Succeeded For All IRCs*************' \
          '***********\n'
    test_concatenate()
    print '\n************************Concatenate Function Succeeded For All IRCS****************' \
          '***********\n'
    print '\n\n**************************TEST FINISHED SUCCESSFULLY FOR ALL IRCS***********' \
          '******************\n\n'
