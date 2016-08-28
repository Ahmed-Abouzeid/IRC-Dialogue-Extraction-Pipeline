"""checks if any dialogue file has only one or more than two users """

import os
from progress.bar import Bar

DIA_PATH = '/Users/ahmed/desktop/ubuntu_results/dialogues/'
FILE_LIST = []
FOLDERS = os.listdir(DIA_PATH)
bar_ = Bar('Counting Number of Users In Each Dialogue. Processing {} Folder(s)'
           .format(len(FOLDERS)), max=len(FOLDERS))

for folder_ in FOLDERS:
    if not folder_.startswith('.'):
        files = os.listdir(DIA_PATH + folder_)
        for file_ in files:
            if not file_.startswith('.'):

                users_list = []
                with open(DIA_PATH + folder_ + '/' + file_) as opener:
                    lines = opener.readlines()
                    for line in lines:
                        sender = line.split('\t')[1]
                        recipient = line.split('\t')[2]
                        if sender not in users_list and sender != '':
                            users_list.append(sender)
                        if recipient not in users_list and recipient != '':
                            users_list.append(recipient)
                if len(users_list) != 2:
                    FILE_LIST.append(folder_ + '/' + file_ + 'Num of Users -------->'
                                     + str(len(users_list)))
    bar_.next()
bar_.finish()


print '\n-----------------------------------------------------\n'
print 'Number Of Dialogue(s) With More or Less Than Two Users Is: {}'.format(len(FILE_LIST))
print '\n-----------------------------------------------------\n'

for file_ in FILE_LIST:
    print file_
