import tkinter as tk
import tkinter.filedialog
import webbrowser
import json
import argparse
import re
import time
from typing import TypedDict, List, Dict, Any
from bs4 import BeautifulSoup
import requests


class Args(TypedDict):
    skip_settings: bool
    res_backup_file: str
    filter_selection: str


AVAILABLE_FILTERS = {
    1: {"source": "https://mediabiasfactcheck.com/left/", "title": "Left  Bias"},
    2: {
        "source": "https://mediabiasfactcheck.com/leftcenter/",
        "title": "Left-Center Bias",
    },
    3: {"source": "https://mediabiasfactcheck.com/center/", "title": "Least Biased"},
    4: {
        "source": "https://mediabiasfactcheck.com/right-center/",
        "title": "Right-Center Bias",
    },
    5: {"source": "https://mediabiasfactcheck.com/right/", "title": "Right Bias"},
    6: {
        "source": "https://mediabiasfactcheck.com/pro-science/",
        "title": "Pro-Science",
    },
    7: {
        "source": "https://mediabiasfactcheck.com/conspiracy/",
        "title": "Conspiracy-Pseudocience",
    },
    8: {
        "source": "https://mediabiasfactcheck.com/fake-news/",
        "title": "Questionable Sources",
    },
    9: {"source": "https://mediabiasfactcheck.com/satire/", "title": "Satire"},
}

SITE_MAP_PATH = "site_map.json"

HEADER = {
    "User-agent": "Mozilla/5.0 (Windows; U; Windows NT 5.1; de; rv:1.9.1.5) Gecko/20091102 Firefox/3.5.5"
}


def parse_args() -> Args:
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", action="store_true", help="Skip RES Settings Backup Step")
    parser.add_argument("-b", help="Path to RES Backup File")
    parser.add_argument("-f", help="Numbered Biases to Filter Out")

    args = parser.parse_args()

    return {
        "skip_settings": args.s,
        "res_backup_file": args.b,
        "filter_selection": args.f,
    }


def print_welcome() -> None:
    print("\n\n")
    print(
        "RES DOMAIN FILTERER - Scrapes domains from selected pages of MediaBiasFactCheck.com and adds them to Reddit Enhancement Suite's Domain Filters"
    )
    print("=" * 100)


def backup_RES_settings(args: Args) -> None:
    if not args["skip_settings"]:
        print("You first need to back up your current RES settings.")
        print("Press ENTER to open your RES settings page. Or type 's' to skip")
        choice = input()
        if choice != "s":
            webbrowser.open(
                "https://old.reddit.com/r/all/#res:settings/backupAndRestore"
            )
            print(
                "Backup your settings as a File. Save the file to your hard drive.\n\n"
            )


def get_currently_filtered_domains(args: Args) -> Dict[str, Any]:
    if not args["res_backup_file"]:
        # Get user's current .resbackup file
        print(
            "Press ENTER to select the RES backup file you just saved. It's probably in your Downloads folder."
        )
        input()
        root = tk.Tk()
        root.filename = tkinter.filedialog.askopenfilename(
            initialdir="/",
            title="Select file",
            filetypes=(("RES Backup File", "*.resbackup"), ("all files", "*.*")),
        )
        args["res_backup_file"] = root.filename
        print("Selected: " + args["res_backup_file"] + "\n\n")

    # Load User's RES settings
    currently_filtered_domains_map = {}
    with open(args["res_backup_file"], "r", encoding="utf-8") as json_data:
        settings = json.load(json_data)
        currently_filtered_domains_res = settings["data"]["RESoptions.filteReddit"][
            "domains"
        ]["value"]
        for c_d in currently_filtered_domains_res:
            currently_filtered_domains_map[c_d[0]] = True
        json_data.close()
    return currently_filtered_domains_map


def get_filters(args: Args) -> List[str]:
    print("Filter options:")
    for num, details in AVAILABLE_FILTERS.items():
        print(f"  {num}. {details['title']}")
    if not args["filter_selection"]:
        print(
            "\nEnter the filters you'd like to create. For multiple filters, enter them without spaces or commas."
        )
        print(
            'For example, if you wanted to filter out Left Bias, Right Bias, and Quesionable Sources, you\'d use "158"\n'
        )
        args["filter_selection"] = input("Enter your desired filters: ")
    print("\nYou selected to filter out:")
    urls_to_filter = []
    for selected in args["filter_selection"]:
        print(f"  {selected}. {AVAILABLE_FILTERS[int(selected)]['title']}")
        urls_to_filter.append(AVAILABLE_FILTERS[int(selected)]["source"])
    return urls_to_filter


def get_site_map() -> Dict[str, str]:
    site_map = {}
    try:
        site_map = json.load(open(SITE_MAP_PATH, encoding="utf8"))
        print("Loaded site map")
    except json.JSONDecodeError:
        pass
    return site_map


def get_domains_to_search_for(
    urls_to_filter: List[str],
    currently_filtered_domains_map: Dict[str, bool],
    site_map: Dict[str, str],
) -> List[str]:
    print("\nGetting list of domains...")
    domains_to_search_for = []
    for url in urls_to_filter:
        page = requests.get(url, headers=HEADER).text
        soup = BeautifulSoup(page, "html.parser")
        table = soup.find(id="mbfc-table")
        if not table:
            print(f"Error finding table for {url}")
            break
        rows = table.findAll("tr")
        for row in rows:
            try:
                internal_link = row.find("a")["href"]
                site = internal_link.split("/")[-2]
                dotcom = f"{site}.com"
                dotnet = f"{site}.net"
                dotorg = f"{site}.org"
                if (
                    not currently_filtered_domains_map.get(dotcom)
                    and not currently_filtered_domains_map.get(dotnet)
                    and not currently_filtered_domains_map.get(dotorg)
                    and not site_map.get(internal_link)
                ):
                    domains_to_search_for.append(internal_link)
            # Row has no links
            except TypeError:
                continue
    return domains_to_search_for


def parse_url(url_str: str) -> str:
    return (
        url_str.replace("http://", "")
        .replace("https://", "")
        .replace("www.", "")
        .split("/")[0]
    )


def get_domains_to_add_and_errors(
    domains_to_search_for: List[str], site_map: Dict[str, str]
) -> List[str]:
    print("Getting URLs for those domains. This might take a while...")
    added = 0
    domains_to_add = []
    domains_to_add_dict = {}
    domain_errors = []
    pauses = 1
    for link in domains_to_search_for:
        source = site_map.get(link)
        sources = []
        if source:
            domains_to_add.append(link)
            domains_to_add_dict[link] = True
            continue
        if "mediabiasfactcheck" in link:
            result = requests.get(link, headers=HEADER)
            if result.status_code == 429:
                sleep = 60 * pauses
                print(f"Hit 429 error. Pausing for {sleep} seconds")
                time.sleep(sleep)
                pauses += 1
                domains_to_search_for.append(link)
                break
            elif result.status_code != 200:
                print(
                    f"Error getting actual URL for {link}. Status {result.status_code}"
                )
                domain_errors.append(link)
                continue
            page = result.text
            soup = BeautifulSoup(page, "html.parser")
            source_texts = soup.findAll(text=re.compile("Source"))
            parent = None
            # Most links are listed under "Source:"
            for source_text in source_texts:
                # Some pages have a primary source and then a list of others
                if "Related Network Sources:" in source_text:
                    sources = source_text.parent.find_next_sibling().text.split("\n")
                # Link placement is extremely inconsistent
                elif "Source:" in source_text or "Sources:" in source_text:
                    if (
                        source_text.parent.name == "strong"
                        or source_text.parent.name == "span"
                        or source_text.parent.name == "em"
                    ):
                        parent = source_text.parent.parent
                    else:
                        parent = source_text.parent
                    continue
                # Check table at the top
                if not parent and "Source URL:" in source_text:
                    parent = source_text.parent.parent.find_next_sibling()
            # Otherwise, we can probably find it in the Analysis section
            if not parent:
                analysis = soup.find(text=re.compile("Analysis"))
                while analysis.name != "h4" and analysis.name != "p":
                    analysis = analysis.parent
                parent = analysis.find_next_sibling()
            if not parent:
                print(f"\rError getting actual URL for {link}")
                domain_errors.append(link)
                continue
            try:
                source = parse_url(parent.find("a")["href"])
            except TypeError:
                if "(dot)" in parent.text or " dot " in parent.text:
                    source = (
                        parent.text.replace("Source:", "")
                        .replace(" dot ", ".")
                        .replace(" ", "")
                        .replace("(dot)", ".")
                    )
                if (
                    ".com" in parent.text
                    or ".net" in parent.text
                    or ".org" in parent.text
                ):
                    source = parent.text.split("\xa0")[1]
                else:
                    domain_errors.append(link)
        else:
            source = parse_url(link)
        sources.append(source)
        for s in sources:
            if not domains_to_add_dict.get(s):
                domains_to_add.append(s)
                domains_to_add_dict[s] = True
                site_map[link] = s
                json.dump(site_map, open(SITE_MAP_PATH, "w", encoding="utf8"))
                added += 1
                print(
                    f"\rAdding: {s:<75} [Domain {added:>4}/{len(domains_to_search_for):<4}]",
                    end="",
                    flush=True,
                )
    print("\n")
    return domains_to_add, domain_errors


def save_RES_settings(domains_to_add: List[str], args: Args) -> None:
    with open(args["res_backup_file"], "r", encoding="utf-8") as json_data:
        settings = json.load(json_data)
        current_domains = settings["data"]["RESoptions.filteReddit"]["domains"]["value"]
        current_domain_names = {}
        for c_d in current_domains:
            current_domain_names[c_d[0]] = True
        # Add new domains
        for domain in domains_to_add:
            if not current_domain_names.get(domain):
                current_domains.append([domain, "everywhere", ""])
        # Sort domains
        current_domains.sort()
        # Save it
        print("Domain filters are ready to be saved. Press ENTER when ready.")
        input()
        new_settings = tkinter.filedialog.asksaveasfile(
            mode="w",
            defaultextension=".resbackup",
            filetypes=(("RES Backup", "*.resbackup"), ("All Files", "*.*")),
        )
        new_settings.write(json.dumps(settings))
        new_settings.close()
        json_data.close()


def upload_settings() -> None:
    print("SUCCESS!\n")
    print("Now, you need to use RES's Restore function to upload your new settings")
    print(
        "Press ENTER to open the Restore Settings page. Restore your settings using the new file we just created."
    )
    print(
        "If you backup your RES settings to a cloud service, you may want to manually force a backup so RES doesn't nag you about it."
    )
    input()
    webbrowser.open("https://old.reddit.com/r/all/#res:settings/backupAndRestore")


def print_done_message(domain_errors: List[str]) -> None:
    print("COMPLETE")
    print("Please note, the following domains failed to be filtered:")
    for error in domain_errors:
        print(error)


def main() -> None:
    args = parse_args()
    print_welcome()
    backup_RES_settings(args)

    currently_filtered_domains_map = get_currently_filtered_domains(args)
    urls_to_filter = get_filters(args)
    site_map = get_site_map()
    domains_to_search_for = get_domains_to_search_for(
        urls_to_filter, currently_filtered_domains_map, site_map
    )
    domains_to_add, domain_errors = get_domains_to_add_and_errors(
        domains_to_search_for, site_map
    )
    save_RES_settings(domains_to_add, args)

    upload_settings()
    print_done_message(domain_errors)


if __name__ == "__main__":
    main()
