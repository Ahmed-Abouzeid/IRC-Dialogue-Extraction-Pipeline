#Test Data#


###test_rawirc.py###
 
 - [irc]_correct_cln : the post conditions that should be met when running the clean function in the module, generated files will be compared with these files
 
 - [irc]_correct_rcp : the post conditions that should be met when running the createRecipient function in the module, generated files will be compared with these files
 
 - [irc]_correct_con : the post conditions that should be met when running the concatenation function in the module, generated files will be compared with these files
 
 - [irc]_mocks : the required data the will be given as an argument to rawirc.py as a mock crawled files, the mock files expected to produce the same as [irc]_correct output and if not, the test fails
 
 - [irc]_test : the output generated from the rawirc.py after using the mock data, that output should be the same as [irc]_correct
 
 - [irc]_list.pkl : contains the post condition that should be met after running the makeUser function, the pickled files are just a binarised list of users to compare with and report failure in case of the new generated user list from that function were not identical with it	
###test_dialogue.py###
 
 - process_holes_parameters.pkl : the parameters that will be passed to the process_holes in dialogue.py as a mock data.
 
 - segmented_users.pkl : the parameters that will be passed to the write_seg_dialogues in dialogue.py as a mock data.
 
 - utterances.pkl : the utterances that will be passed as one of the arguments to the match_utterance function in dialogue.py as part of its mock data.
 
 - rest of mocks are hand-crafted in the script itself since they are simple mocks.
 
###compare_dialogue.py### 

you just need two already existed dialogues and to set their paths in the script then all will be handled by the script.

###count_users_in_dialogues.py###

you will need to set a path for an extracted dialogues folder to count users over the underlying files.


###Note : The Paths To The Above Mocks & Test Data Are Hand-Crafted In The Scripts And Follow The Same Hierarchy In The Repository, So It Is Recommended Not To Change The Paths In The Scripts###