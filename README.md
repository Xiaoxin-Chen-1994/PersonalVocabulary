# Personal Vocabulary

This Python script was created for my personal usage, and I'm sharing it online in case anyone's interested in using it. The reason I built this script was to have a personalized dictionary, especially to learn and review academic words that I encounter in papers. 

Compared to online software for expanding vocabulary, the benefit of a personal dictionary is that it's more relevant to myself. I can add only the words that I want to learn, and I can make any notes I want to it. 

In this repository, I've uploaded both the script and an example of the .csv personal dictionary file. 

## Acknowledgement
First of all, I'd like to acknowledge that this script opens--or at least attempts to open--webpages from various sources including [Oxford Learner's Dictionaries](https://www.oxfordlearnersdictionaries.com), [Dictionary.com](https://www.dictionary.com/), [YouGlish.com](https://youglish.com/) and [Google.com](https://www.google.com/). These are sites that I like and find helpful to myself. 

This script imports various modules, especially [tkinter](https://docs.python.org/3/library/tkinter.html), [tkwebview2](https://pypi.org/project/tkwebview2/). There is however a potential dependency issue, where tkwebview2 may fail. Unfortunately I do not have a good solution to it if that happens. The only recommendation I have is, once the webpages are able to load, do **_not_** upgrade modules unless absolutely necessary. 

The idea of this personal dictionary was inspired by an academic writing course that I took in the first year of my PhD study. 

## The interface
Below is a screenshot of the interface. 

The left side envelops different options for sources of online dictionaries. 

The right side loads my/your personal dictionary. 

![image](https://github.com/Xiaoxin-Chen-1994/PersonalVocabulary/assets/49115976/4ae90a9b-65f0-49df-b98b-760fce4df377)

## There are six main buttons. 
### Show/Hide
When a new word/phrase loads, it is hidden by default. You need to either recall its usage (left), or guess the word by its usage in examples (right). 

![image](https://github.com/Xiaoxin-Chen-1994/PersonalVocabulary/assets/49115976/921bd2ce-0caf-45ec-bb43-655c8db02c65)

By clicking Show/Hide, you're able to see or hide the full explanations and examples of this word/phrase. By clicking Show, the webpage from an online dictionary will also load on the left side. 

### New
You can define a new word/phrase using this button. 

### I'm familiar vs Need more practice
There is a level of unfamiliarity associated with each word/phrase. This level ranges from 1 (most familiar) to 9 least familiar.  
These two buttons reduces or increases this level of unfamiliarity. This information, along with the word/phrase itself, its pronunciation, explanations, examples and illustrations, is stored in a .csv file as your personal dictionary. 
When a word/phrase loads up, it is chosen randomly from this .csv file, weighted by its level of unfamiliarity. The more unfamiliar you are with a word/phrase, the more likely it will be selected to pop up. 

### Save
This button saves new words/phrases that you create and any changes you make to an existing word/phrase.

### Search
By typing in the search box, the script tries to find all its appearance -- as the keyword, or in explanations and examples. 

You can either click on a word that shows up in the search list -- this will load the word from your personal dictionary,  
or click the Search button -- this will both load the word from an online dictionary, and load the word from your personal dictionary (if the search word exists).  
![image](https://github.com/Xiaoxin-Chen-1994/PersonalVocabulary/assets/49115976/dbed405b-113a-46d4-af7c-56e12f9dbfa3)
