
# -*- coding: utf-8 -*-
import os
import re

DATA_DIR = 'Days_With_Recipients'
USE_DB = False
if USE_DB:
    import psycopg2cffi as psycopg2
    from psycopg2cffi.extensions import QuotedString

out = open('ubuntu.sql', 'w')
id = 1

lone = re.compile(
    ur'''(?x)            # verbose expression (allows comments)
    (                    # begin group
    [\ud800-\udbff]      #   match leading surrogate
    (?![\udc00-\udfff])  #   but only if not followed by trailing surrogate
    )                    # end group
    |                    #  OR
    (                    # begin group
    (?<![\ud800-\udbff]) #   if not preceded by leading surrogate
    [\udc00-\udfff]      #   match trailing surrogate
    )                    # end group
    ''')




def qs(s):
    return QuotedString(s.encode('utf-8')).getquoted()


def commit(con, date, time, sender, recipient, message):
    global id
    YYYY = int(date[0:4])
    MM = int(date[5:7])
    DD = int(date[8:])
    hh = int(time[0:2])
    mm = int(time[3:])
    if USE_DB:
        dt = psycopg2.Timestamp(YYYY, MM, DD, hh, mm, 00)
        cur = con.cursor()
        sql = "INSERT INTO messages (timestamp, sender, recipient, message) VALUES (%s, %s, %s, %s)" % (
        dt, qs(sender), qs(recipient) if recipient else "''", qs(message))
        con.cursor().execute(sql)
    else:
        dt = "%d-%d-%d %d:%d:00" % (YYYY, MM, DD, hh, mm)
        s = "%d\t%s\t%s\t%s\t%s\t" % (id, dt, sender, recipient if recipient else '', message)
        s = s.replace('\\', '\\\\') + "\\N\n"
       # s = lone.sub(ur'\ufffd', s).encode('utf8')
        out.write(s)
        id += 1


def main():
    con = psycopg2.connect(database='ubuntu') if USE_DB else None
    fnames = os.listdir(DATA_DIR)
    nicks = set()
    #    fnames = ['2004-09-27.tsv', '2004-09-17.tsv', '2007-10-17.tsv', '2012-01-18.tsv']
    for fname in fnames:
        if not str(fname).startswith('.'):
            with open(DATA_DIR+'/'+fname) as f:
                print fname
                lines = f.readlines()
                for line in lines:
                    raw_line = line.split('\t')
                    date = raw_line[0].split('T')[0]
                    time = raw_line[0].split('T')[1][:5]
                    commit(con, date, time, raw_line[1], raw_line[2], raw_line[3].rstrip())
                    nicks.add(raw_line[1])
    with open('nicks.txt', 'w') as f:
        for nick in nicks:
            f.write(str(nick)+'\n')

    if USE_DB:
        con.commit()


if __name__ == '__main__':
    main()
