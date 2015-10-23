# RueLaLa-App
Program to apply for internship at RueLaLa

TODO: Write installation instructions

Current Status: code works just fine in the IDE, can't run it from the command line at all. Therefore, can't package it up.

Notes for RueLaLa Talent Team:
- I don't use Twitter, personally. I'm fully confident that this code works and it shouldn't blow up given any strange inputs, however apart from basic knowledge of what Twitter is, I don't have much.

- If I had to do this again, I realize that there is some code that can be factored out. For example, the similarities between searching for a tweet from a person and to a person make those functions such that they should really be one function with a boolean or integer flag set to indicate whether it is a TO or a FROM request

- I also realize that there are some security flaws with this program, notably hardcoding my consumer_key and consumer_secret. I know I could do this with a config file, but to be honest it's getting late and I still have homework to do.
 
- I'm not fully sure how to write unit tests for this... Since the entire functionality of the program requires it to authenticate and interact with Twitter, it seems that automated tests without user input would be difficult to write as they wouldn't be able to authenticate. I understand the importance of testing, and I'd be eager to learn the correct way to test a script such as this one where user interaction is vital to the program. I've tested it with different, strange inputs for a while and I'm confident that there aren't any inputs left that would cause an unhandled exception.
