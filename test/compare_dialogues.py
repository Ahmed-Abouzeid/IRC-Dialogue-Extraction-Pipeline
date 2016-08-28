"""this module can be used to compare two generated dialogues from the same irc data to validate
 two different processing algorithms on these data"""

import os
import sqlite3
from progress.bar import Bar

__author__ = 'Ahmed'

CONN = sqlite3.connect(":memory:")
CURSOR = CONN.cursor()

CURSOR.execute('create table Dialogue_aInfo '
               '(file_name text ,sender_usr text, recipient_usr text)')
CURSOR.execute('CREATE INDEX dia_a_sender_index ON Dialogue_aInfo '
               '(sender_usr)')
CURSOR.execute('CREATE INDEX dia_a_recipient_index ON Dialogue_aInfo '
               '(recipient_usr)')
CURSOR.execute('create table Dialogue_bInfo (file_name text ,sender_usr text,'
               ' recipient_usr text)')
CURSOR.execute('CREATE INDEX dia_b_sender_index ON Dialogue_bInfo (sender_usr)')
CURSOR.execute('CREATE INDEX dia_b_recipient_index ON Dialogue_bInfo (recipient_usr)')

DIA_A_PATH = '/users/ahmed/desktop/mcgill_dialogues'
DIA_B_PATH = '/users/ahmed/desktop/dialogues'


def load_dialogue_info():
    """loads dialogues file names with pair of users into data-base"""
    counter = 0
    print 'Loading Dialogues_A Files Info Into Database . . .'
    folders = os.listdir(DIA_A_PATH)
    bar_ = Bar('Processing {} Folder(s).'.format(len(folders)), max=len(folders))
    for folder_ in folders:
        if not folder_.startswith('.'):
            files = os.listdir(DIA_A_PATH.rstrip('/') + '/' + folder_)
            for file_ in files:
                users = []
                if not file_.startswith('.'):
                    with open(DIA_A_PATH.rstrip('/') + '/' + folder_ + '/' + file_) as opener:
                        lines = opener.readlines()
                        for line in lines:
                            sender = line.split('\t')[1]
                            recipient = line.split('\t')[2]
                            if sender not in users and sender != '':
                                users.append(sender)
                            if recipient not in users and recipient != '':
                                users.append(recipient)
                        if len(users) == 2:
                            CURSOR.execute('insert into Dialogue_aInfo Values'
                                           ' ("{}", "{}", "{}")'
                                           .format(folder_ + '/' + file_,
                                                   max(users[0], users[1]),
                                                   min(users[0], users[1])))
                            counter += 1
        bar_.next()
    bar_.finish()
    print '{} Dialogues_A Were Loaded.'.format(counter)
    files_count(DIA_A_PATH)
    if os.path.exists('./dialogue_a.txt'):
        os.remove('./dialogue_a.txt')
        print 'Old Data Removed.'
    write_dialogue_users('dialogue_a.txt', 'Dialogue_aInfo')

    counter = 0
    print 'Loading Dialogues_B Files Info Into Database . . .'
    folders = os.listdir(DIA_B_PATH)
    bar_ = Bar('Processing {} Folder(s).'.format(len(folders)), max=len(folders))
    for folder_ in folders:
        if not folder_.startswith('.'):
            files = os.listdir(DIA_B_PATH.rstrip('/') + '/' + folder_)
            for file_ in files:
                users = []
                if not file_.startswith('.'):
                    with open(DIA_B_PATH.rstrip('/') + '/' + folder_ + '/' + file_) as opener:
                        lines = opener.readlines()
                        for line in lines:
                            sender = line.split('\t')[1]
                            recipient = line.split('\t')[2]
                            if sender not in users:
                                users.append(sender)
                            if recipient != '':
                                if recipient not in users:
                                    users.append(recipient)
                            if len(users) == 2:
                                CURSOR.execute('insert into Dialogue_bInfo Values'
                                               ' ("{}", "{}", "{}")'
                                               .format(folder_ + '/' + file_,
                                                       max(users[0], users[1]),
                                                       min(users[0], users[1])))
                                counter += 1
                                break
        bar_.next()
    bar_.finish()
    print '{} Of Dialogue_B Were Loaded.'.format(counter)
    files_count(DIA_B_PATH)
    if os.path.exists('./dialogue_b.txt'):
        os.remove('./dialogue_b.txt')
        print 'Old Data Removed.'

    write_dialogue_users('dialogue_b.txt', 'Dialogue_bInfo')


def write_dialogue_users(filename, dbname):
    """writes dialogue info like file name and the involved pair of users"""
    counter = 0
    CURSOR.execute('select * from {}'.format(dbname))
    users = CURSOR.fetchall()
    bar_ = Bar('Writing {} Record(s) To File'.format(len(users)), max=len(users))
    for i in users:
        dia_file_name = i[0]
        dia_user1 = i[1]
        dia_user2 = i[2]
        with open(filename, 'a') as opener:
            opener.write('\t'.join([dia_file_name, dia_user1, dia_user2])+'\n')
            counter += 1
            bar_.next()
    bar_.finish()
    print '{} Dialogue(s) Info Were Written To File {}.'.format(counter, filename)


def files_count(path):
    """counts dialogues files number to compare with the loaded dialogues number"""
    files_counter = 0
    print 'Checking Correctness Of Loaded Dialogues Count, Counting Physical Files On {}'\
        .format(path)
    for _, _, files_ in os.walk(path):
        for file_ in files_:
            if not file_.startswith('.'):
                files_counter += 1

    if files_counter == 0:
        print '\nNo Files Were Found To Process.'
        exit()
    print '{} Files Found.'.format(files_counter)


def check_diff():
    """check differences between loaded dialogues, reports the missing from one to one and the
     additional in one and not in the other one and reports the matches also"""
    mis_counter = 0
    ad_counter = 0
    match_counter = 0
    if os.path.exists('./missing.txt'):
        os.remove('./missing.txt')
        print 'Old missing.txt Removed.'
    if os.path.exists('./additional.txt'):
        os.remove('./additional.txt')
        print 'Old additional.txt Removed.'
    if os.path.exists('./matches.txt'):
        os.remove('./matches.txt')
        print 'Old matches.txt Removed.'
    print 'Now Checking Differences Between The Two Dialogues And Reporting Mismatches/Matches' \
          ' Info (Might Take Time!) . . .\n'
    print 'Checking Matches . . .\n'

    CURSOR.execute('select mc.file_name, mc.sender_usr, mc.recipient_usr ,mi.file_name,'
                   ' mi.sender_usr, mi.recipient_usr from Dialogue_aInfo as mc inner join'
                   ' Dialogue_bInfo as mi on mc.sender_usr = mi.sender_usr and mc.recipient_usr'
                   ' = mi.recipient_usr')
    matches_result = CURSOR.fetchall()
    print 'Writing Dialogues That Exist in Both Dialogues_A/Dialogues_B (Matching Dialogues)' \
          ' To matches.txt...'

    with open('matches.txt', 'a') as opener:
        for m in matches_result:
            dia_a_file_name = m[0]
            dia_a_user1 = m[1]
            dia_a_user2 = m[2]
            dia_b_file_name = m[3]
            dia_b_user1 = m[4]
            dia_b_user2 = m[5]

            opener.write('\t'.join([dia_a_file_name, dia_a_user1, dia_a_user2, dia_b_file_name,
                                    dia_b_user1, dia_b_user2.strip('\n')]) + '\n')
            match_counter += 1
    print 'Done. please Check matches.txt\n'

    print 'Checking Missing Dialogues In Dialogues_B. . .\n'

    CURSOR.execute('select mi.file_name,mc.file_name,mc.sender_usr, mc.recipient_usr from'
                   ' Dialogue_aInfo as mc left outer join Dialogue_bInfo as mi on'
                   ' mc.sender_usr = mi.sender_usr and mc.recipient_usr = mi.recipient_usr')
    missing_result = CURSOR.fetchall()
    print 'Writing Dialogues That Exist in Dialogues_A And Not In Dialogues_B (Missing Dialogues)' \
          ' To missing.txt...'

    with open('missing.txt', 'a') as opener:
        for missed in missing_result:
            dia_b_file_name = missed[0]
            dia_a_user1 = missed[2]
            dia_a_user2 = missed[3]
            dia_a_file_name = missed[1]
            if dia_b_file_name is None:
                opener.write('\t'.join([dia_a_file_name, dia_a_user1, dia_a_user2.strip('\n')])
                             + '\n')
                mis_counter += 1

    print 'Done. please Check missing.txt\n'
    print 'Checking Additional Dialogues In Dialogues_B and Missing In Dialogues_A . . .\n'

    CURSOR.execute('select mc.file_name,mi.file_name,mi.sender_usr, mi.recipient_usr from'
                   ' Dialogue_bInfo as mi left outer join Dialogue_aInfo as mc on'
                   ' mc.sender_usr = mi.sender_usr and mc.recipient_usr = mi.recipient_usr')
    additional_result = CURSOR.fetchall()

    print 'Writing Dialogues That Exist in Dialogues_B And Not In Dialogues_A ' \
          '(Additional Dialogues) To additional.txt...'

    with open('additional.txt', 'a') as opener:
        for additional in additional_result:
            dia_a_file_name = additional[0]
            dia_b_user1 = additional[2]
            dia_b_user2 = additional[3]
            dia_b_file_name = additional[1]
            if dia_a_file_name is None:
                opener.write('\t'.join([dia_b_file_name, dia_b_user1, dia_b_user2.strip('\n')])
                             + '\n')
                ad_counter += 1
    print 'Done. please Check additional.txt'

    print '\n-------------------------------------------------------------------------------' \
          '-----------------'
    print 'Number Of Total Matches Is: {}'.format(match_counter)
    print 'Number Of Total Mismatches Is: '+str(mis_counter+ad_counter)
    print 'Number Of Dialogues That Exist in Dialogues_A And Not In Dialogues_B' \
          ' (Missing Dialogues) Is {}'.format(mis_counter)
    print 'Number Of Dialogues That Exist in Dialogues_B And Not In Dialogues_A' \
          ' (Additional Dialogues) Is {}'.format(ad_counter)
    print '-------------------------------------------------------------------------------' \
          '-----------------\n'


load_dialogue_info()
check_diff()
