# IRC Processing Software Is A Tool For Gathering And Processing IRC Channels Conversations For Creating One/One Dialogues Files That Can Be Used As Training Data-Set For Deep Neural Networks Used In Dialogue Systems#


### The IRC Processing Software Can Be Used By Running Three Python Scripts (Located In /irc_process) In The Following Order: ###
 
- crawler.py (downloads irc logs)
 
- rawirc.py (clean/transform/recognize recipients in logs)
 
- dialogue.py (extract one-one dialogues for each pair of users in logs)

The three components are interfacing with each others via their generated outputs, the trawler will download files that can be passed as an argument to the rawirc.py then these files will be cleaned and passed as another argument to dialogue.py which will apply the dialogue extraction algorithms and generate the dialogues data-set 

### Dependecies ###

- pypy

- penchant

- nltk

- sqlalchemy

### Run setup.py To Be Able To Use And Reference The Above Scripts As A Package Modules ###

### For Testing Purposes, Below Are Unit-Test & Verification Modules Located In /test ###

- compare_dialogues.py (compares two extracted dialogues from the same irc logs but from different algorithms maybe, and report the matched records and the mismatches)

- count_users_in_dialogues.py (report if there is any dialogue with only one user or more than two users talking, that should be considered as an error)

- test_rawirc.py (tests major functions in rawer.py using mock data included in the repository)

- test_dialogue.py (tests major functions in dialogue.py using mock data included in the repository)
### The Software Has Been Tested And Designed To Work On Two Common IRC Logging Site Templates (Ubuntu like & Perl6 like) ###
### How To Use The Processing Scripts? ###
Go To /irc_process Then Run The Below:
####crawler.py On Ubuntu IRC - https://irclogs.ubuntu.com####
```python
python crawler.py -crawl yes -urls_file 'files_as_arguments/urls_ubuntu.txt' -file_spider yes -target_format txt -ignored_links_file 'files_as_arguments/ignore.txt' -time_out 60 -work_path '/output_path' -max_recursion_depth 3 -white_list_path 'files_as_arguments/white_list.txt'
```
####crawler.py On Lisp IRC - http://ccl.clozure.com/irc-logs/lisp/####
```python
python crawler.py -crawl yes -urls_file 'files_as_arguments/urls_lisp.txt' -file_spider yes -target_format txt -ignored_links_file 'files_as_arguments/ignore.txt' -time_out 60 -work_path '/output_path' -max_recursion_depth 1
```
####crawler.py On Perl6 IRC - https://irclog.perlgeek.de/perl6/####
```python
python crawler.py -crawl yes -urls_file 'files_as_arguments/urls_perl.txt' -ignored_links_file 'files_as_arguments/ignore.txt' -time_out 60 -work_path '/output_path' -max_recursion_depth 1 -allow_clean_url 'yes'
```
####crawler.py On Koha IRC - http://irc.koha-community.org/koha/####
```python
python crawler.py -crawl yes -urls_file 'files_as_arguments/urls_koha.txt' -ignored_links_file 'files_as_arguments/ignore.txt' -time_out 60 -work_path '/output_path' -max_recursion_depth 1 -allow_clean_url 'yes'
```
####crawler.py On ScummVM IRC - http://logs.scummvm.org####
```python
python crawler.py -crawl yes -urls_file 'files_as_arguments/urls_scummvm.txt' -time_out 60 -work_path '/output_path' -one_bite yes -ignored_links_file 'files_as_arguments/ignore.txt'
```
####rawirc.py On ubuntu IRC####
```python
pypy rawirc.py -raw_data_path '/path_to/crawled_data' -time_regexp '\[\d\d:\d\d\]' -date_regexp '\d\d\d\d\d\d\d\d' -old_date_format %Y%m%d -clean_work_path '/output_path' -user_sys_annotation '<,>' -time_sys_annotation '[,]' -raw_msg_separator ' ' -use_enchant 'yes'
```
####rawirc.py On Lisp IRC####
```python
pypy RawIRC.py -raw_data_path '/path_to/crawled_data' -time_regexp '\d\d:\d\d:\d\d' -date_regexp '\d\d\d\d.\d\d.\d\d' -old_date_format %Y.%m.%d -clean_work_path '/output_path' -user_sys_annotation '<,>'  -raw_msg_separator ' ' -use_enchant 'yes' -process_file_reg_exp '(lisp-)(\d\d\d\d-\d\d)' -process_file_date_format %Y-%m -force_remove_sysmsg 'yes' -rtrim_time 3 -sys_msg_path 'files_as_arguments/sysmsg.txt'
```
####rawirc.py On Koha IRC####
```python
pypy rawirc.py -raw_data_path '/path_to/crawled_data' -time_regexp '^(\s*\d\d\:\d\d)$' -date_regexp '\d\d\d\d-\d\d-\d\d' -old_date_format %Y-%m-%d -clean_work_path '/output_path' -time_user_lines 1 -use_enchant 'yes'
```
####rawirc.py On Perl6 IRC####
```python
pypy rawirc.py -raw_data_path '/path_to/crawled_data' -time_regexp '^(\s*\d\d\:\d\d)$' -date_regexp '\d\d\d\d-\d\d-\d\d' -old_date_format %Y-%m-%d -clean_work_path '/output_path' -use_enchant 'yes'
```
####rawirc.py On ScummVM IRC####
```python
pypy rawirc.py -raw_data_path '/path_to/crawled_data' -time_regexp '\[\d\d:\d\d\]' -date_regexp '\d\d\w\w\w\d\d\d\d' -old_date_format %d%b%Y -clean_work_path '/output_path' -user_sys_annotation '<,>' -time_sys_annotation '[,]' -raw_msg_separator ' ' -use_enchant 'yes' -lowercase 'yes'
```
####dialogue.py On Any IRC Cleaned Output From rawer.py####
```python
pypy dialogue.py -clean_work_path '/path_to/clean/days_with_recipients' -dialogue_work_path '/output_path' -gap_time_frame 3 -min_turns 3 -time_frame 3 -bots_path 'files_as_arguments/bots_[irc_name].txt'
```
####dialogue.py For Only Statistical Report On Already Extracted Dialogues####
```python
pypy dialogue.py -only_stats yes -extracted_dialogues_path 'path_to/dialogues'
```
### How To Use The Test Scripts? ###
The Test Scripts Require Some Mock Data Located in /test Directory, The Paths To These Data Already Configured In The Script, Do Not Change The Hierarchy Of The Mock Data Unless You Will Change It In The Scripts As Well.
 
To Use, Go To /test Then Run The Below:
####test_dialogue.py####
```python
pypy test_dialogue.py
```
####test_rawirc.py####
```python
pypy test_rawirc.py
```
####compare_dialogues.py####
```python
pypy compare_dialogues.py
```
####count_users_in_dialogues.py####
```python
pypy count_users_in_dialogues.py
```