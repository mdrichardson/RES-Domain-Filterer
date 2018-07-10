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
print ("Selected: " + root.filename)