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
### How To Use The Scripts? ###

####crawler.py On Ubuntu IRC####
```python
python crawler.py -urls_file ./urls_ubuntu.txt -file_spider yes -target_format txt -ignored_links_file path_to/ignore.txt -time_out 60 -work_path /output_path max_recursion_depth 3 white_list_path path_to/white_list.txt
```
####crawler.py On Lisp IRC####
```python
python crawler.py -urls_file path_to/urls_lisp.txt -file_spider yes -target_format txt -ignored_links_file path_to/ignore.txt -time_out 60 -work_path /output_path max_recursion_depth 2
```
####crawler.py On Perl6 IRC####
```python
python crawler.py -urls_file path_to/urls_perl6.txt -ignored_links_file path_to/ignore.txt -time_out 60 -work_path /output_path max_recursion_depth 1 -allow_clean_url yes
```
####crawler.py On Koha IRC####
```python
python crawler.py -urls_file path_to/urls_koha.txt -ignored_links_file path_to/ignore.txt -time_out 60 -work_path /output_path max_recursion_depth 1 -allow_clean_url yes
```