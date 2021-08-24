import urllib.request, re
from advertools import sitemaps # pip install advertools
from datetime import date

site_to_scrape = input('Enter a domain to scrape: ')

# -------------------------- Configuration --------------------------

regex_email = "[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4}"
regex_phone = '^((((0{2}?)|(\+){1})46)|0)[7-8][\d]{8}'

sitemap_paths = ['/sitemap_index.xml', '/sitemap.xml', '/robots.txt']


# ---------------------------- Functions ----------------------------


# Gets all the paths to sitemaps, finds the first viable one and extracts all the sub-sitemaps & URLS
def extract_sitemap(domain):
    for ext in sitemap_paths:
        try:
            print(f'---------- {ext} -------------')
            return sitemaps.sitemap_to_df(f'{domain}{ext}', recursive=True)
        except:
            pass

    return None


# Takes all the data from sitemaps, parses the URLS
def enumerate_urls(dataframe):
    urllist = []
    for ele in dataframe.values.tolist():
        for subele in ele:
            try:
                if 'https:' in subele:  # Find URLS with <HTTPS:> tag
                    if '.xml' not in subele:  # From those URLS, ignore <.xml> as it's most likely just a sitemap
                        urllist.append(subele)
                else:
                    pass
            except:
                pass  # Makes sure it doesn't get stuck on NaN values
    return urllist


# Extracts emails and phonenumbers, removing duplicate values, populating a list to save
def extract_data(urls):
    # To be populated
    master_emaillist = []
    master_phonelist = []

    # For tracking progress
    progress = 0
    progress_target = len(urls)

    for url in urls:
        request = str(urllib.request.urlopen(url).read())
        emails = re.findall(regex_email, request)
        phones = re.findall(regex_phone, request)
        email_list = list(set(emails))  # Removes duplicate values
        phone_list = list(set(phones))  # Removes duplicate values

        for email in email_list:
            if email not in master_emaillist:
                master_emaillist.append(email)

        for number in phone_list:
            if number not in master_phonelist:
                master_phonelist.append(number)

        # CLI status bar
        print(f'Sites read: {progress}/{progress_target}')
        progress += 1

    return master_emaillist, master_phonelist


# Saves the list provided as a text file, with timestamp
def write_to_file(list_to_write, name):
    timestamp = date.today().strftime("%m-%d-%y")
    with open(f'Output/{name} {timestamp}.txt','w') as file:
        for ele in list_to_write:
            file.write(str(ele) + "\n")


# ------------------------------- Run -------------------------------

sitemap = extract_sitemap(site_to_scrape)
if sitemap is None:
    print('ERROR: Could not find Sitemap')
else:
    enum_list = enumerate_urls(sitemap)
    all_emails, all_numbers = extract_data(enum_list)
    write_to_file(all_emails, 'Emails')
    write_to_file(all_numbers, 'Numbers')
