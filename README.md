# IRC Processing Software Is A Tool For Gathering And Processing IRC Channels Conversations For Creating One/One Dialogues Files That Can Be Used As Training Data-Set For Deep Neural Networks Used In Dialogue Systems#


### The IRC Processing Software Can Be Used By Running Three Python Scripts (Located In /irc_process) In The Following Order: ###
 
- crawler.py (downloads irc logs)
 
- rawirc.py (clean/transform/recognize recipients in logs)
 
- dialogue.py (extract one-one dialogues for each pair of users in logs)

### Run setup.py To Be Able To Use The Above Scripts From Other Modules ###

### For Testing Purposes, Below Are Unit-Test & Verification Modules Located In /test ###

- compare_dialogues.py (compares two extracted dialogues from the same irc logs but from different algorithms maybe, and report the matched records and the mismatches)

- count_users_in_dialogues.py (report if there is any dialogue with only one user or more than two users talking, that should be considered as an error)

- test_rawirc.py (tests major functions in rawer.py using mock data included in the repository)

- test_dialogue.py (tests major functions in dialogue.py using mock data included in the repository)
### How To Use The Processing Scripts? ###
Go To /irc_process Then Run The Below:
####crawler.py On Ubuntu IRC####
```python
python crawler.py -crawl yes -urls_file 'files_as_arguments/urls_ubuntu.txt' -file_spider yes -target_format txt -ignored_links_file 'files_as_arguments/ignore.txt' -time_out 60 -work_path '/output_path -max_recursion_depth 3 -white_list_path 'files_as_arguments/white_list.txt'
```
####crawler.py On Lisp IRC####
```python
python crawler.py -crawl yes -urls_file 'files_as_arguments/urls_lisp.txt' -file_spider yes -target_format txt -ignored_links_file 'files_as_arguments/ignore.txt' -time_out 60 -work_path '/output_path' -max_recursion_depth 1
```
####crawler.py On Perl6 IRC####
```python
python crawler.py -crawl yes -urls_file 'files_as_arguments/urls_perl.txt' -ignored_links_file 'files_as_arguments/ignore.txt' -time_out 60 -work_path '/output_path' -max_recursion_depth 1 -allow_clean_url yes
```
####crawler.py On Koha IRC####
```python
python crawler.py -crawl yes -urls_file 'files_as_arguments/urls_koha.txt' -ignored_links_file 'files_as_arguments/ignore.txt' -time_out 60 -work_path '/output_path' -max_recursion_depth 1 -allow_clean_url yes
```
####rawirc.py On ubuntu IRC####
```python
python rawirc.py -raw_data_path '/path_to/crawled_data' -time_regexp '\[\d\d:\d\d\]' -date_regexp '\d\d\d\d\d\d\d\d' -old_date_format %Y%m%d -clean_work_path '/output_path' -user_sys_annotation '<,>' -time_sys_annotation '[,]' -raw_msg_separator ' ' -use_enchant yes
```
####rawirc.py On Lisp IRC####
```python
python rawirc.py -raw_data_path '/path_to/crawled_data' -time_regexp '\[\d\d:\d\d\]' -date_regexp '\d\d\d\d\d\d\d\d' -old_date_format %Y%m%d -clean_work_path '/output_path' -old_date_format %Y.%m.%d -user_sys_annotation '<,>'  -raw_msg_separator ' ' -use_enchant yes -process_file_reg_exp '(lisp-)(\d\d\d\d-\d\d)' -process_file_date_format %Y-%m -force_remove_sysmsg yes -rtrim_time 3
```
####rawirc.py On Koha IRC####
```python
python rawirc.py -raw_data_path '/path_to/crawled_data' -time_regexp '^(\s*\d\d\:\d\d)$' -date_regexp '\d\d\d\d-\d\d-\d\d' -old_date_format %Y-%m-%d -clean_work_path '/output_path' -time_user_lines 1 -use_enchant yes
```
####rawirc.py On Perl6 IRC####
```python
python rawirc.py -raw_data_path '/path_to/crawled_data' -time_regexp '^(\s*\d\d\:\d\d)$' -date_regexp '\d\d\d\d-\d\d-\d\d' -old_date_format %Y-%m-%d -clean_work_path '/output_path' -use_enchant yes
```