from bs4 import BeautifulSoup
import requests
from tkinter import filedialog
from tkinter import *
import webbrowser
import json


# Welcome and tell user to back up their current RES settings
print("\n\n")
print("RES DOMAIN FILTERER - Scrapes domains from selected pages of MediaBiasFactCheck.com and adds them to Reddit Enhancement Suite's Domain Filters")
print("=" * 100)
print("You first need to back up your current RES settings.")
print("Press ENTER to open your RES settings page. Or type 's' to skip")
choice = input()
if choice != "s":
    webbrowser.open("https://old.reddit.com/r/all/#res:settings/backupAndRestore")
    print("Backup your settings as a File. Save the file to your hard drive.\n\n")

# Get user's current .resbackup file
print("Press ENTER to select the RES backup file you just saved. It\'s probably in your Downloads folder.")
input()
root = Tk()
root.filename =  filedialog.askopenfilename(initialdir = "/",title = "Select file",filetypes=(("RES Backup File","*.resbackup"),("all files","*.*")))
print ("Selected: " + root.filename + "\n\n")

# Load User's RES settings
current_domain_names = {}
with open(root.filename, 'r', encoding='utf-8') as json_data:
    settings = json.load(json_data)
    current_domains = settings["data"]["RESoptions.filteReddit"]["domains"]["value"]
    for c_d in current_domains:
        current_domain_names[c_d[0]] = True

# Get user's filter criteria
filter_dict = {
    1: {
        "source": "https://mediabiasfactcheck.com/left/",
        "title": "Left Bias"
    },
    2: {
        "source": "https://mediabiasfactcheck.com/leftcenter/",
        "title": "Left-Center Bias"
    },
    3: {
        "source": "https://mediabiasfactcheck.com/center/",
        "title": "Least Biased"
    },
    4: {
        "source": "https://mediabiasfactcheck.com/right-center/",
        "title": "Right-Center Bias"
    },
    5: {
        "source": "https://mediabiasfactcheck.com/right/",
        "title": "Right Bias"
    },
    6: {
        "source": "https://mediabiasfactcheck.com/pro-science/",
        "title": "Pro-Science"
    },
    7: {
        "source": "https://mediabiasfactcheck.com/conspiracy/",
        "title": "Conspiracy-Pseudocience"
    },
    8: {
        "source": "https://mediabiasfactcheck.com/fake-news/",
        "title": "Questionable Sources"
    },
    9: {
        "source": "https://mediabiasfactcheck.com/satire/",
        "title": "Satire"
    },
}
print("Filter options:")
for num, details in filter_dict.items():
    print("  {}. {}".format(num, details["title"]))
print("\nEnter the filters you\'d like to create. For multiple filters, enter them without spaces or commas.")
print("For example, if you wanted to filter out Left Bias, Right Bias, and Quesionable Sources, you'd use \"158\"\n")
filter_selection = input("Enter your desired filters: ")
print("\nYou selected:")
selected_urls = []
for selected in filter_selection:
    print("  {}. {}".format(selected, filter_dict[int(selected)]["title"]))
    selected_urls.append(filter_dict[int(selected)]["source"])

# Scrape filter selections for URLs to filter
print("\nGetting list of domains...")
header = {'User-agent' : 'Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5'}
domains_to_search = []
for url in selected_urls:
    page = requests.get(url, headers=header).text
    soup = BeautifulSoup(page, 'html.parser')
    table = soup.find(id='mbfc-table')
    if not table:
        print(f"Error finding table for {url}")
        break
    rows = table.findAll('tr')
    for row in rows:
            try:
                internal_link = row.find('a')['href']
                site = internal_link.split("/")[-2]
                dotcom = f"{site}.com"
                dotnet = f"{site}.net"
                dotorg = f"{site}.org"
                if not current_domain_names.get(dotcom, False) and not current_domain_names.get(dotnet, False) and not current_domain_names.get(dotorg, False):
                    domains_to_search.append(internal_link)
            except:
                continue

# From mediabiasfactcheck links, get domain's actual URL
print("Getting URLs for those domains. This might take a few minutes...")
added = 0
domains_to_add = []
domains_to_add_dict = {}
domain_errors = []
for link in domains_to_search:
    if "mediabiasfactcheck" in link:
        try:
            page = requests.get(link, headers=header).text
        except:
            continue
        soup = BeautifulSoup(page, 'html.parser')
        all_p = soup.findAll(text=re.compile('Source:'))
        parent = None
        # Most links are listed under "Source:"
        for p in all_p:
            if "Source:" in p:
                parent = p.parent
                break
        # Otherwise, they seem to be listed under "Notes:"
        if not parent:
            for p in all_p:
                if "Notes:" in p.getText():
                    parent = p
        if not parent:
            print("\rError getting actual URL for {}".format(link))
            domain_errors.append(link)
            continue
        try:
            source = parent.find("a")['href'].replace("http://", "").replace("https://","").replace("www.","").replace("/","")
        except TypeError:
            domain_errors.append(link)
    else:
        source = link.replace("http://", "").replace("https://","").replace("www.","").replace("/","")
    if not domains_to_add_dict[source]:
        domains_to_add.append(source)
        domains_to_add_dict[source] = True
    added += 1
    print("\rAdding: {0:<75} [Domain {1:>4}/{2:<4}]".format(source, added, len(domains_to_search)), end="", flush=True)
print("\n")

# Load User's RES settings
with open(root.filename, 'r', encoding='utf-8') as json_data:
    settings = json.load(json_data)
    current_domains = settings["data"]["RESoptions.filteReddit"]["domains"]["value"]
    current_domain_names = {}
    for c_d in current_domains:
        current_domain_names[c_d[0]] = True
    # Add new domains
    for domain in domains_to_add:
        if not current_domain_names[domain]:
            current_domains.append([domain, 'everywhere', ''])
    # Sort domains
    current_domains.sort()
    # Save it
    print("Domain filters are ready to be saved. Press ENTER when ready.")
    input()
    new_settings = filedialog.asksaveasfile(mode='w', defaultextension=".resbackup", filetypes=(("RES Backup", "*.resbackup"),("All Files", "*.*") ))
    new_settings.write(json.dumps(settings))
    new_settings.close()

# Help user upload new settings
print("SUCCESS!\n")
print("Now, you need to use RES's Restore function to upload your new settings")
print("Press ENTER to open the Restore Settings page. Restore your settings using the new file we just created.")
print("If you backup your RES settings to a cloud service, you may want to manually force a backup so RES doesn't nag you about it.")
input()
webbrowser.open("https://old.reddit.com/r/all/#res:settings/backupAndRestore")
print("COMPLETE")
print("Please note, the following domains failed to be filtered:")
for error in domain_errors:
    print(error)

