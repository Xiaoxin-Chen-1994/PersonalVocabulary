# Use the code below to install or upgrade tkwebview2
import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
# install("tkwebview2")
# install("requests_html")

import csv
import tkinter as tk
from tkinter import messagebox
import random, pandas, math
from datetime import date, datetime
import fnmatch
from tkwebview2.tkwebview2 import WebView2
from requests_html import HTMLSession

def ClearExplanations():
    Explanation.delete("1.0", tk.END)
    Examples.delete("1.0", tk.END)
    IllustrationURL.delete("1.0", tk.END)
    
    VocabularyDisplay.rowconfigure(2, weight=10) # Set the weight of a row
    VocabularyDisplay.rowconfigure(3, weight=10) # Set the weight of a row

    # Hide the illustration image grid
    IllustrationFrame.columnconfigure(1, weight=0)
    IllustrationImage.grid_forget()
    IllustrationImage.load_url("https://www.blank.org/")

def ClearAllBoxes():
    # Clear all boxes to prepare for the next word
    WordItem.delete(0, tk.END)
    Pronunciation.delete(0, tk.END)
    ClearExplanations()
    SearchBox.delete(0, tk.END)
    SearchFeedback.config(text="")
    ListBoxForSearchInHistory.grid_forget()

def RandomPickCommandLevel(dfobject):
    # Create a list to assign different weights to various levels of command
    CommandLevels = list()
    for i in range(LowestLevel, HighestLevel+1): # Levels 1-9, 1 very familiar, 9 unfamiliar
        CommandLevels += [i] * i * dfobject[dfobject[TitleLevel]==i].count()[0]

    # Pick a command level
    Repick = True
    while Repick:
        # Exit the loop when there is at least one word found at this level
        CurrentLevel = random.choice(CommandLevels)
        if dfobject[dfobject[TitleLevel]==CurrentLevel].count()[0] != 0: 
            Repick = False

    # Randomly pick a word from the random level
    CurrentWord = dfobject[dfobject[TitleLevel]==CurrentLevel].sample()

    # Get the row index of that word
    CurrentRow = CurrentWord.index[0]
    return CurrentRow

def DisplayExamples(dfobject, CurrentRow, Redact):
    # Highlight the word in examples with a given format or redact the word
    Word = dfobject.at[CurrentRow, "Item"].split(", ")# Read all words from "Item" in case there is more than one word
    ExampleTexts = dfobject.at[CurrentRow, "Examples"].replace("\r", "").split(" ") # Split examples texts by space
    Examples.tag_configure("highlight", foreground="red") # Configure a text format
    # Print one word at a time
    # Quit the loop when all ExampleTexts have been printed
    while len(ExampleTexts) > 0: 
        HightlightLength = 0 # Number of words that match with a given keyword
        for keyword in Word:
            MatchLength = 0
            keyword = keyword.strip(" ").strip("…").strip("...")
            kwsplit = keyword.split(" ") # Split this keyword into separate words
            if len(ExampleTexts) >= len(kwsplit): # Only compare words when ExampleTexts list has sufficient elements
                for i in range(0, len(kwsplit)):
                    kws = kwsplit[i].split("/") # Split this word if there are multiple options such as on/upon
                    for kw in kws:
                        if kw in ("be", "sb", "sth"):
                            kw = "*" # If the word is be or sb/sth, it can match any word
                        else:
                            kw = kw.strip("(").strip(")").rstrip("-").rstrip("e").rstrip("y").lower()+"*"

                        if fnmatch.filter([ExampleTexts[i].lower().strip("\n")], kw):
                            # if the current word matches the text in Examples
                            MatchLength += 1
                            # Mark the length of matching words in HightlightLength only when all words in this keyword match
                            if MatchLength == len(kwsplit) and MatchLength > HightlightLength:
                                if "sb" in kwsplit[-1] or "sth" in kwsplit[-1]: 
                                    MatchLength -= 1 # If the keyword ends with sb or sth, do not hightlight the last word
                                HightlightLength = MatchLength 
        
        if HightlightLength: # Highlight matching words
            for i in range(0, HightlightLength):
                if Redact:
                    Examples.insert(tk.END, "____")
                    ExampleTexts.pop(0)
                else:
                    Examples.insert(tk.END, ExampleTexts.pop(0), "highlight")
                Examples.insert(tk.END, " ")
        else: # Use plain text for all other non-matching words
            Examples.insert(tk.END, ExampleTexts.pop(0))
            Examples.insert(tk.END, " ")

def DisplayWord(dfobject, CurrentRow, DisplayType):
    # Display the below message when reaching a milestone
    global StartRun
    if StartRun:    
        StartRun = False
    elif WordCount % 10 == 1 and WordCount != 1:
        Milestone = random.choice(["Great job", "Wonderful", "Excellent", "Fantastic", "Amazing"]) + "! You have learned and reviewed " + str(WordCount-1) + " words today! "
        Examples.insert(tk.INSERT, Milestone)
        VocabularyDisplay.update() # Update the text box before tk 

        # Display the message for a given amount of time
        VocabularyDisplay.after(2000) # the number of miliseconds that the script pauses for
        Examples.delete("1.0", tk.END)

    # Display the chosen word
    if DisplayType == 1:
        WordItem.insert(0, dfobject.at[CurrentRow, "Item"])
        Pronunciation.insert(0, dfobject.at[CurrentRow, "Pronunciation"])
    elif DisplayType == 2:
        DisplayExamples(dfobject, CurrentRow, Redact=True)

    # Reset show/hide button text to Show
    try: 
        ShowOrHide['text'] = 'Show'
    except NameError:
        pass

def NextItem(dfobject):
    # Randomly pick a word and display this word
    CurrentRow = RandomPickCommandLevel(dfobject)
    ClearAllBoxes()

    if dfobject.at[CurrentRow, "Examples"].startswith(("Examples", "24 Greek letters")):
        DisplayType = 1
    else:
        DisplayType = random.choice((1,2))
    DisplayWord(dfobject, CurrentRow, DisplayType)

    return CurrentRow

def SearchDictionaries(word):
    if ShowSecondDictionary:
        # Display both dictionaries
        OnlineDict.load_url(Dicts[0]["SearchURL"] + word)
        OnlineDict2.load_url(Dicts[1]["SearchURL"] + word)
    else:
        # Display the first dictionary
        OnlineDict.load_url(Dicts[0]["SearchURL"] + word)
        # If the word was not found, as indicated by the title of the website
        if "Did you spell it correctly" in HTMLSession().get(Dicts[0]["SearchURL"] + word).html.find('title', first=True).text:
            OnlineDict.load_url(Dicts[1]["SearchURL"] + word) # Display the second dictionary instead

def ShowAllBoxes(dfobject, CurrentRow):
    # Calculate the approximate numbers of rows required and set weights of Explanation and Examples proportionally
    LengthRow1 = math.ceil(len(dfobject.at[CurrentRow, "Explanation"])/widthB) + dfobject.at[CurrentRow, "Explanation"].count("\n")
    LengthRow2 = math.ceil(len(dfobject.at[CurrentRow, "Examples"])/widthB) + dfobject.at[CurrentRow, "Examples"].count("\n")
    ratio = LengthRow1 / (LengthRow1 + LengthRow2)
    VocabularyDisplay.rowconfigure(2, weight=max(min(round(20*ratio),15),1)) # Set the weight of a row
    VocabularyDisplay.rowconfigure(3, weight=max(min(20-round(20*ratio),15),1)) # Set the weight of a row

    WordItem.insert(0, dfobject.at[CurrentRow, "Item"])
    Pronunciation.insert(0, dfobject.at[CurrentRow, "Pronunciation"])

    Explanation.tag_configure("PoS", font = (fontB + " italic"), foreground="blue") # Configure a text format
    Explanation.tag_configure("italicgrey", font = (fontB + " italic"), foreground="#AEAEAE") # Configure a text format
    Explanation.tag_configure("highlight", foreground="blue") # Configure a text format

    PoS = ('abbr.', 'adj.', 'adv.', 'conj.', 'n.', 'prep.', 'pron.', 'v.') # Part of speech
    Prepositions = ('about', 'against', 'among', 'around', 'at', 'away', 'between', 'down', 'for)', 'for/', 'from', 'in)', 'in/', 'into', 'of)', 'of/', 'off', 'on', 'out', 'to', 'with')
    Prepositions = tuple(["(" + p for p in Prepositions])

    TextFormat = None
    ExplanationTexts = dfobject.at[CurrentRow, "Explanation"].replace("\r", "").split(" ")
    for i, EachWord in enumerate(ExplanationTexts):
        if EachWord.strip("\n") in PoS: # Part of speech
            TextFormat = "PoS"
        if EachWord.startswith(("(anat", "(appro", "(astro", "(bio", "(botany", "(busi", "(chem", "(computing", "(disapp", "(finan", "(formal", "(gene", "(geo", "(gramm", "(humour", "(informal", "(law", "(litera", "(math", "(med", "(mus", "(philo", "(phy", "(psy", "(plural", "(rather", "(specialist", "(sometimes", "(statis", "(usually", "[")) or EachWord=="(in": 
            TextFormat = "italicgrey"
        if EachWord.startswith(Prepositions) or EachWord.startswith(("(also", "(oneself", "(sb", "(sth", "(that", "(be")) or EachWord.startswith("("+dfobject.at[CurrentRow, "Item"].split(", ")[0].split(" ")[0]) or EachWord == "(for":
            TextFormat = "highlight"
        if EachWord == "[":
            TextFormat = None

        if TextFormat:
            Explanation.insert(tk.END, EachWord, TextFormat)
        else:
            Explanation.insert(tk.END, EachWord)
        Explanation.insert(tk.END, " ")

        if EachWord.strip("\n") in PoS: # Part of speech
            TextFormat = None
        if EachWord.endswith(("]", ")")): 
            TextFormat = None

    IllustrationURL.insert(tk.INSERT, dfobject.at[CurrentRow, "Illustration"])

    if dfobject.at[CurrentRow, "Illustration"] != DefaultIllustrationText:
        try: # Display the illstration image when there is a valid URL
            IllustrationImage.load_url(dfobject.at[CurrentRow, "Illustration"])
            IllustrationImage.grid(row=0, column=1, sticky="NSEW") # Expand the widget to fill the space
            IllustrationFrame.columnconfigure(1, weight=9)
        except:
            pass
    
    # Display online dictionaries
    SearchDictionaries(dfobject.at[CurrentRow, "Item"].split(", ")[0].split("/")[0].replace("'", "-").replace(" ", "-"))

    # Display examples
    DisplayExamples(dfobject, CurrentRow, Redact=False)

def UpdateDataFrame(dfobject, CurrentRow):
    # Get strings from input boxes and save them to the data frame
    dfobject.at[CurrentRow, "Item"] = WordItem.get().strip(" ")
    dfobject.at[CurrentRow, "Pronunciation"] = Pronunciation.get().strip(" ")
    dfobject.at[CurrentRow, "Explanation"] = Explanation.get("1.0", tk.END).replace("\r", "").strip("\n").strip(" ")
    dfobject.at[CurrentRow, "Examples"] = Examples.get("1.0", tk.END).replace("\r", "").strip("\n").strip(" ")
    IllustrationURLText = IllustrationURL.get("1.0", tk.END).strip("\n").strip(" ")
    if IllustrationURLText == "":
        IllustrationURLText = "Illustration"
    dfobject.at[CurrentRow, "Illustration"] = IllustrationURLText

    if dfobject.at[CurrentRow, TitleLevel] not in range(LowestLevel,HighestLevel+1):
        dfobject.at[CurrentRow, TitleLevel] = HighestLevel

def SaveToFile(csvfile, dfobject):
    # Sort the data frame based on condtion sequence and save it to a csv file
    dfobject = dfobject.sort_values(by=['Item'], ascending=True)
    dfobject.to_csv(csvfile, index=False, encoding='utf-8-sig')

def CheckDateAndUpdateCommandLevels(csvfile, dfobject):
    LastUpdateDate = datetime.date(datetime.strptime(dfobject.columns.values[6], "LastUpdateDate %d/%m/%Y"))
    TodayDate = date.today()

    if  (TodayDate - LastUpdateDate).days >= 30: 
        TotalNumberOfRows = OriginalDF.count()[0]
        for eachrow in range(0, TotalNumberOfRows):
            if dfobject.at[eachrow, TitleLevel] < HighestLevel:
                dfobject.at[eachrow, TitleLevel] += (TodayDate - LastUpdateDate).days // 30

    if LastUpdateDate != TodayDate:
        print(dfobject.columns.values[6])
        dfobject.columns.values[6] = datetime.strftime(TodayDate, "LastUpdateDate %d/%m/%Y")
        dfobject.columns.values[7] = "Words reviewed on the day: 0"
    
    SaveToFile(csvfile, dfobject)

# Update the Entry widget with the selected item in list
def update(data):
    # Clear the Combobox
    ListBoxForSearchInHistory.delete(0, tk.END)
    # Add values to the combobox
    for value in data:
        ListBoxForSearchInHistory.insert(tk.END, value)

def check(e):
    v= SearchBox.get()
    if v=='':
        # Hide this SearchInHistory listbox
        ListBoxForSearchInHistory.grid_forget()
    else:
        # Show this SearchInHistory listbox as the user starts typing
        ListBoxForSearchInHistory.grid(row=1, column=0)
        # Search the input word in any columns and assemble results in a new data frame
        SearchDF = OriginalDF[OriginalDF.apply(lambda r: r.str.contains(v, case=False).any(), axis=1)]

        data=[]
        for item in SearchDF["Item"]:
            data.append(item)

        update(data)

def LoadTextInSearchBoxAndSearch(TextToLoad):
    SearchBox.delete(0, tk.END)
    SearchBox.insert(tk.INSERT, TextToLoad)
    SearchButton()

def CopySelectedText(event):
    LoadTextInSearchBoxAndSearch(ListBoxForSearchInHistory.get(ListBoxForSearchInHistory.curselection()))

# At the start of this script
StartRun = True

# Read data from a file and put them in a pandas DataFrame 
VocabularyFile = "Vocabulary.csv"
OriginalDF = pandas.read_csv(VocabularyFile, sep = ',')

# Define familiarity levels
LowestLevel = 1 # Most familiar
HighestLevel = 9 # Least familiar
TitleLevel = "Level"

CheckDateAndUpdateCommandLevels(VocabularyFile, OriginalDF)

# Create a tkinter window
tkWindow = tk.Tk()
tkWindow.title("Vocabulary")

fontA = "Arial 20"
fontB = "Arial 16"
widthA = 40
widthB = round(40*20/16)

screen_height = tkWindow.winfo_screenheight()

# Initialize WordCount. Add 1 before the first word displays.
WordCount = int(OriginalDF.columns.values[7].split(": ")[1]) + 1

# Prepare online dictionary info
Dicts = list()
Dicts.append({
    "SiteName"  : "Oxford Learner's Dictionaries", 
    "Website"   : 'https://www.oxfordlearnersdictionaries.com', 
    "SearchURL" : 'https://www.oxfordlearnersdictionaries.com/definition/english/', 
})
Dicts.append({
    "SiteName"  : "Dictionary.com", 
    "Website"   : 'https://www.dictionary.com/', 
    "SearchURL" : 'https://www.dictionary.com/browse/', 
})

# Append YouGlish.com abd Google.com at the end of the Dicts list
NumberOfDictsToShowAtBottom = 2
Dicts.append({
    "SiteName"  : "YouGlish.com", 
    "Website"   : 'https://youglish.com/', 
    "SearchURL" : 'https://youglish.com/pronounce/', 
})
Dicts.append({
    "SiteName"  : "Google.com", 
    "Website"   : 'https://www.google.com/', 
    "SearchURL" : 'https://www.google.com/search?q=', 
})

DefaultIllustrationText = "https://www.google.com/search?q=?&tbm=isch"

# Left frame: show online dictionaries
DictionaryFrame = tk.Frame(tkWindow)
DictionaryFrame.grid(row=0, column=0)

ShowSecondDictionary = False
ShowDictSwitchButtons = True

# First online dictionary
if ShowSecondDictionary:
    OnlineDict = WebView2(DictionaryFrame, 500, round(screen_height*0.7/2))
    ShowDictSwitchButtons = False # Override the above definition
else: 
    OnlineDict = WebView2(DictionaryFrame, 500, round(screen_height*0.7))
OnlineDict.grid(row=1)
OnlineDict.load_url(Dicts[0]["Website"])

if ShowSecondDictionary:
    # Split between two dictionaries
    tk.Label(DictionaryFrame).grid(row=2)

    # Second online dictionary
    OnlineDict2 = WebView2(DictionaryFrame, 500, round(screen_height*0.7/2))
    OnlineDict2.grid(row=3)
    OnlineDict2.load_url(Dicts[0]["Website"])

# Split between left and right frames
tk.Label(tkWindow).grid(row=0, column=1)

# Right frame: show key words
VocabularyDisplay = tk.Frame(tkWindow)
VocabularyDisplay.grid(row=0, column=2, sticky="NS") # Expand the widget to fill the space

# Prepare rows in the right frame
WordItem = tk.Entry(VocabularyDisplay, font=fontA, width=widthA, foreground='red')
WordItem.grid(row=0)

PronunciationFrame = tk.Frame(VocabularyDisplay)
PronunciationFrame.grid(row=1, sticky="EW") # Expand the widget to fill the space

Explanation = tk.Text(VocabularyDisplay, font=fontB, width=widthB, height=1, wrap=tk.WORD)
Explanation.grid(row=2, sticky="NS") # Expand the widget to fill the space

Examples = tk.Text(VocabularyDisplay, font=fontB, width=widthB, height=1, wrap=tk.WORD)
Examples.grid(row=3, sticky="NS") # Expand the widget to fill the space

IllustrationFrame = tk.Frame(VocabularyDisplay)
IllustrationFrame.grid(row=4, sticky="EW") # Expand the widget to fill the space

ButtonFrame = tk.Frame(VocabularyDisplay)
ButtonFrame.grid(row=5, sticky="EW") # Expand the widget to fill the space

SearchFrame = tk.Frame(VocabularyDisplay)
SearchFrame.grid(row=6, sticky="EW") # Expand the widget to fill the space

# Configure those frame rows
PronunciationFrame.columnconfigure(0, weight=1) # Set the weight of a column
PronunciationFrame.columnconfigure(1, weight=5) # Set the weight of a column
PronunciationFrame.columnconfigure(2, weight=1) # Set the weight of a column

Pronunciation = tk.Entry(PronunciationFrame, font=fontB)
Pronunciation.grid(row=0, column=1, sticky="EW") # Expand the widget to fill the space

VocabularyDisplay.rowconfigure(2, weight=10) # Set the weight of a row
VocabularyDisplay.rowconfigure(3, weight=10) # Set the weight of a row

IllustrationFrame.columnconfigure(0, weight=1)
IllustrationURL = tk.Text(IllustrationFrame, font=fontB, width=1, height=1, wrap=tk.WORD)
IllustrationURL.grid(column=0, sticky="NSEW") # Expand the widget to fill the space

IllustrationImage = WebView2(IllustrationFrame, 350, round(screen_height*0.7/2))

ButtonFrame.columnconfigure(0, weight=1) # Set the weight of a column
ButtonFrame.columnconfigure(1, weight=1) # Set the weight of a column
ButtonFrame.columnconfigure(2, weight=1) # Set the weight of a column

SearchFrame.columnconfigure(0, weight=1) # Set the weight of a column
SearchFrame.columnconfigure(1, weight=1) # Set the weight of a column
SearchFrame.columnconfigure(2, weight=1) # Set the weight of a column

SearchBox = tk.Entry(SearchFrame, font=fontB)
SearchBox.grid(row=0, column=0, padx=10, sticky="EW") # Expand the widget to fill the space
SearchBox.bind('<KeyRelease>', check)
SearchFeedback = tk.Label(SearchFrame, font=fontB)
SearchFeedback.grid(row=0, column=2)

# Create a Listbox widget to display the list of items
ListBoxForSearchInHistory = tk.Listbox(SearchFrame, height=5)
ListBoxForSearchInHistory.bind('<<ListboxSelect>>', CopySelectedText)

# Pick a word and display it in the input boxes
WordRow = NextItem(OriginalDF)

def SwitchToDict(DictIndex):
    CurrentSearchWord = OnlineDict.get_url().split("=")[-1].split("/")[-1].split("_")[0]
    if CurrentSearchWord == "" or "misspelling" in CurrentSearchWord:
        OnlineDict.load_url(Dicts[DictIndex]["Website"])
        # print(Dicts[DictIndex]["Website"])
    else:
        OnlineDict.load_url(Dicts[DictIndex]["SearchURL"] + CurrentSearchWord.replace("--", "-"))
        # print(Dicts[DictIndex]["SearchURL"] + CurrentSearchWord)

def ShowButton():
    global WordRow
    # If it's a Show button, unhide explanations and switch the button text to Hide
    if ShowOrHide.cget('text')=='Show':
        ClearAllBoxes()
        ShowAllBoxes(OriginalDF, WordRow)
        ShowOrHide['text'] = 'Hide'
    # If it's a Hide button, hide explanations and switch the button text to Show
    elif ShowOrHide.cget('text')=='Hide':
        ClearExplanations()
        ShowOrHide['text'] = 'Show'

def SearchButton():
    global WordRow
    SearchWord = SearchBox.get()
    # If there is no input in the search box, look for a selected word in Examples and Explanation
    if SearchWord == "":
        try:
            SearchWord = Examples.selection_get().strip(" ").rstrip("s").rstrip("d").rstrip("ing")
        except tk.TclError:
            pass
    if SearchWord == "":
        try:
            SearchWord = Explanation.selection_get().strip(" ").rstrip("s").rstrip("d").rstrip("ing")
        except tk.TclError:
            pass
    # If there is a word to search
    if SearchWord != "":
        WordFound = True
        # First look for this word in Item
        SearchResult = OriginalDF[OriginalDF['Item'].str.match(SearchWord, case=False, na=False)]
        if len(SearchResult) < 1:
            # If an exact match doesn't exist, look for a word that contains it in Item
            SearchResult = OriginalDF[OriginalDF['Item'].str.contains(SearchWord, case=False, na=False)]
            if len(SearchResult) < 1: 
                SearchDictionaries(SearchWord)
                # If the word doesn't exist, look for this word in Explanation
                SearchResult = OriginalDF[OriginalDF['Explanation'].str.contains(SearchWord, case=False, na=False)]
                if len(SearchResult) < 1: 
                    # If the word doesn't appear in Explanation, look for this word in Examples
                    SearchResult = OriginalDF[OriginalDF['Examples'].str.contains(SearchWord, case=False, na=False)]
                    if len(SearchResult) < 1:# do nothing if there is no match
                        SearchFeedback["text"] = "No match found."
                        WordFound = False
                        ListBoxForSearchInHistory.grid_forget()
        
        if WordFound:
            # Display the first match
            WordRow = SearchResult.index[0]
            ClearAllBoxes()
            DisplayWord(OriginalDF, WordRow, DisplayType=1)

def NewItemButton():
    global WordRow
    # Reset all boxes to prepare for input of a new word
    ClearAllBoxes()
    WordItem.insert(0, "Item")
    Pronunciation.insert(0, "Pronunciation")
    Explanation.insert(tk.INSERT, "Explanation")
    IllustrationURL.insert(tk.INSERT, DefaultIllustrationText)
    Examples.insert(tk.INSERT, "Examples")
    WordRow = OriginalDF.count()[0]

def FamiliarButton():
    global WordRow, WordCount
    # Save the new command level to file
    WordLevel = OriginalDF.at[WordRow, TitleLevel]
    OriginalDF.at[WordRow, TitleLevel] = max(WordLevel - 1, LowestLevel) # CommandLevel should never be smaller than the lowest level defined
    OriginalDF.columns.values[7] = "Words reviewed on the day: " + str(WordCount)
    SaveToFile(VocabularyFile, OriginalDF)
    WordCount += 1
    WordRow = NextItem(OriginalDF)

def InProgressButton():
    global WordRow, WordCount
    # Save the new command level to file
    WordLevel = OriginalDF.at[WordRow, TitleLevel]
    OriginalDF.at[WordRow, TitleLevel] = min(WordLevel + 1, HighestLevel) # CommandLevel should never be larger than the highest level defined
    OriginalDF.columns.values[7] = "Words reviewed on the day: " + str(WordCount)
    SaveToFile(VocabularyFile, OriginalDF)
    WordCount += 1
    WordRow = NextItem(OriginalDF)

def SaveItemToRow(row):
    global WordRow, WordCount
    try:
        dialog.destroy()  # Close the popup window
    except:
        pass
    
    WordRow = row
    
    # Save the word to file
    UpdateDataFrame(OriginalDF, WordRow)
    OriginalDF.columns.values[7] = "Words reviewed on the day: " + str(WordCount)
    SaveToFile(VocabularyFile, OriginalDF)
    WordCount += 1
    WordRow = NextItem(OriginalDF)

def SaveItemButton():
    global dialog
    
    try:
        if OriginalDF.at[WordRow, "Item"] != WordItem.get():
            # Create the toplevel window to confirm when the keyword is being changed
            dialog = tk.Toplevel()
            dialog.title("Confirmation overwriting")

            # Add a label with the confirmation message
            message_label = tk.Label(dialog, text="The keyword is being changed. Please confirm overwriting!", font=fontB)
            message_label.pack(padx=20, pady=20)
            
            # Add a "Cancel" button
            cancel_button = tk.Button(dialog, text="Oops! Please save as a new item.", command=lambda: SaveItemToRow(OriginalDF.count()[0]), bg="#FF8383", font=fontB)
            cancel_button.pack(side=tk.LEFT, padx=10, pady=10)

            # Add a "Save" button
            save_button = tk.Button(dialog, text="Yes, please overwrite.", command=lambda: SaveItemToRow(WordRow), bg="yellow", font=fontB)
            save_button.pack(side=tk.LEFT, padx=10, pady=10)
        else:
            # Proceed and save when the keyword is not changed
            SaveItemToRow(WordRow)
    
    except KeyError:
        # Proceed and save when a new keyword is being created
        SaveItemToRow(WordRow)

if ShowDictSwitchButtons:
    # Prepare a frame to host switch buttons
    SwitchDictButtonFrame = tk.Frame(DictionaryFrame)
    SwitchDictButtonFrame.grid(row=0, sticky="EW") # Expand the widget to fill the space
    # Create buttons to switch dictionaries
    for DictIndex in range(0, len(Dicts)-NumberOfDictsToShowAtBottom):
        SwitchDictButtonFrame.columnconfigure(DictIndex, weight=1) # Set the weight of a column
        tk.Button(SwitchDictButtonFrame, text=Dicts[DictIndex]["SiteName"], command=lambda m=DictIndex:SwitchToDict(m), font=fontB).grid(row=0, column=DictIndex, sticky="EW") # Expand the widget to fill the space
        # Note that with the lambda function, the buttons are able to identify which dict to search in

# Show YouGlish button at the bottom
BottomDictsButtonFrame = tk.Frame(DictionaryFrame)
BottomDictsButtonFrame.grid(row=3, sticky="EW") # Expand the widget to fill the space
for DictIndex in range(len(Dicts)-NumberOfDictsToShowAtBottom, len(Dicts)):
    tk.Button(BottomDictsButtonFrame, text=Dicts[DictIndex]["SiteName"], command=lambda m=(DictIndex):SwitchToDict(m), font=fontB).grid(row=0, column=DictIndex-(len(Dicts)-NumberOfDictsToShowAtBottom), sticky="EW") # Expand the widget to fill the space

# Create a Show button
ShowOrHide = tk.Button(PronunciationFrame, text='Show', command=ShowButton, font=fontB)
ShowOrHide.grid(row=0, column=0)

# Create a New Item button
tk.Button(PronunciationFrame, text='New', command=NewItemButton, font=fontB).grid(row=0, column=2)

# Create a Search button
tk.Button(SearchFrame, text='Search', command=SearchButton, font=fontB).grid(row=0, column=1)

# Create a Familiar button
tk.Button(ButtonFrame, text="I'm familiar", command=FamiliarButton, font=fontB).grid(row=0, column=0)

# Create a In Progress button
tk.Button(ButtonFrame, text='Need more practice', command=InProgressButton, font=fontB).grid(row=0, column=1)

# Create a Save Item button
tk.Button(ButtonFrame, text='Save', command=SaveItemButton, font=fontB).grid(row=0, column=2)

VocabularyDisplay.mainloop()

quit()
