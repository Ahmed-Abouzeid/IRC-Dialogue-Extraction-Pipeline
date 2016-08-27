# IRC Processing Software Is A Tool For Gathering And Processing IRC Channels Conversations For Creating One/One Dialogues Files That Can Be Used As Training Data-Set For Deep Neural Networks Used In Dialogue Systems#


### The IRC Processing Software Can Be Used By Running Three Python Scripts (Can Be Found Under "irc_process" Folder) In The Following Order: ###
 
-crawler.py (downloads irc logs)
 
-rawirc.py (clean/transform/recognize recipients in logs)
 
-dialogue.py (extract one-one dialogues for each pair of users in logs)

### Run setup.py To Be Able To Use The Above Scripts From Other Modules ###

### For Testing Purposes, Below Are Unit-Test & Verification Modules Can Be Found Under "test" Folder ###

- compare_dialogues.py (compares two extracted dialogues from the same irc logs but from different algorithms maybe, and report the matched records and the mismatches)

- count_users_in_dialogues.py (report if there is any dialogue with only one user or more than two users talking, that should be considered as an error)

- test_rawirc (tests major functions in rawer.py using mock data included in the repository)

- test_dialogue (tests major functions in dialogue.py using mock data included in the repository)
### How To Use The Scripts ###

* Summary of set up
* Configuration
* Dependencies
* Database configuration
* How to run tests
* Deployment instructions

### Contribution guidelines ###

* Writing tests
* Code review
* Other guidelines

### Who do I talk to? ###

* Repo owner or admin
* Other community or team contact