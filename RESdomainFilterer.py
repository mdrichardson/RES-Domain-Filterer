import requests
from tkinter import filedialog
from tkinter import *
import webbrowser


# Welcome and tell user to back up their current RES settings
print("\n\n")
print("RES DOMAIN FILTERER - Scrapes domains from selected pages of MediaBiasFactCheck.com and adds them to Reddit Enhancement Suite's Domain Filters")
print("=" * 100)
print("You first need to back up your current RES settings.")
print("Press ENTER to open your RES settings page.")
input()
webbrowser.open("https://old.reddit.com/r/all/#res:settings/backupAndRestore")
print("Backup your settings as a File. Save the file to your hard drive.\n\n")

# Get user's current .resbackup file
print("Press ENTER to select the RES backup file you just saved. It\'s probably in your Downloads folder.")
input()
root = Tk()
root.filename =  filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes = (("RES Backup File","*.resbackup"),("all files","*.*")))
print ("Selected: " + root.filename + "\n\n")

# Get user's filter criteria
filterDict = {
    1: {
        "source:": "https://mediabiasfactcheck.com/left/",
        "title": "Left Bias"
    },
    2: {
        "source:": "https://mediabiasfactcheck.com/leftcenter/",
        "title": "Left-Center Bias"
    },
    3: {
        "source:": "https://mediabiasfactcheck.com/center/",
        "title": "Least Biased"
    },
    4: {
        "source:": "https://mediabiasfactcheck.com/right-center/",
        "title": "Right-Center Bias"
    },
    5: {
        "source:": "https://mediabiasfactcheck.com/right/",
        "title": "Right Bias"
    },
    6: {
        "source:": "https://mediabiasfactcheck.com/pro-science/",
        "title": "Pro-Science"
    },
    7: {
        "source:": "https://mediabiasfactcheck.com/conspiracy/",
        "title": "Conspiracy-Pseudocience"
    },
    8: {
        "source:": "https://mediabiasfactcheck.com/fake-news/",
        "title": "Questionable Sources"
    },
    9: {
        "source:": "https://mediabiasfactcheck.com/satire/",
        "title": "Satire"
    },
}
print("Filter options:")
for num, details in filterDict.items():
    print("  {}. {}".format(num, details["title"]))
print("\nEnter the filters you\'d like to create. For multiple filters, enter them without spaces or commas.")
print("For example, if you wanted to filter Left Bias, Right Bias, and Quesionable Sources, you'd use \"158\"\n")
filterSelection = input("Enter your desired filters: ")
print("\nYou selected:")
for selected in filterSelection:
    print("  {}. {}".format(selected, filterDict[int(selected)]["title"]))

