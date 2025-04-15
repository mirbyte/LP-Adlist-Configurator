import os
import urllib.request
import urllib.error
import concurrent.futures


URLS_TO_FETCH = [
    "https://raw.githubusercontent.com/AdguardTeam/AdguardFilters/master/BaseFilter/sections/adservers.txt",
    "https://raw.githubusercontent.com/AdguardTeam/AdguardFilters/master/BaseFilter/sections/adservers_firstparty.txt",
    "https://raw.githubusercontent.com/AdguardTeam/AdguardFilters/master/MobileFilter/sections/adservers.txt",
    "https://raw.githubusercontent.com/AdguardTeam/AdguardFilters/master/MobileFilter/sections/antiadblock.txt",
    "https://raw.githubusercontent.com/AdguardTeam/AdguardFilters/master/MobileFilter/sections/general_url.txt",
    "https://raw.githubusercontent.com/AdguardTeam/AdguardFilters/master/SpywareFilter/sections/mobile.txt",
    "https://raw.githubusercontent.com/AdguardTeam/AdguardFilters/master/SpywareFilter/sections/tracking_servers.txt",
    "https://raw.githubusercontent.com/AdguardTeam/AdguardFilters/master/SpywareFilter/sections/tracking_servers_firstparty.txt"
]

OUTPUT_FILENAME = "AdsBlockList_user_edit.txt"
FACEBOOK_LIST_FILENAME = 'facebook_urls.txt'
ADDITIONAL_LIST_FILENAME = 'additional_urls.txt'

# defaults from lp app
DEFAULT_HTTP_BLOCKLIST = [
    '/ads', '.ads.', '-ads.', '.ad.', '/ad.', 'advert', '.gstatic.com', '.admob.com', '.analytics.localytics.com',
    '.greystripe.com', 'inmobi.com', 'admax.nexage.com', 'my.mobfox.com', '.plus1.wapstart.ru', '.madnet.ru',
    '.inmobi.com', '.mp.mydas.mobi', 'millennialmedia.com', '.g.doubleclick.net', '.appsdt.com', 'run.admost.com',
    'mobile.admost.com', 'amazon-adsystem.com', '.appnext.com', '.flurry.com', 'googlesyndication.com', 'google.com/dfp',
    'inmobicdn.net', 'moatads', '.mopub.com', 'unityads.unity3d.com', 'adc3-launch', 'adcolony.com',
    'mobile-static.adsafeprotected', 'applovin.com', 'applvn.com', 'appnext.hs', 'live.chartboost.com',
    'www.dummy.com', '.api.vungle.com', 'pubnative.net', 'supersonicads.com', 'info.static.startappservice.com',
    'init.startappservice.com', 'req.startappservice.com', 'imp.startappservice.com', 'sb.scorecardresearch.com',
    'crashlytics.com', 'udm.scorecardresearch.com', 'adz.wattpad.com', 'ad.api.kaffnet.com', 'dsp.batmobil.net',
    '61.145.124.238', 'alta.eqmob.com', 'graph.facebook.', 't.appsflyer.com', 'net.rayjump.com', '.yandex.net',
    'appodeal.com', 'amazonaws.com', '.baidu.com', '.tapas.net', '.duapps.com', 'smaato.', 'ad-mail.ru',
    'yandexadexchange.', 'yandex.com', 'tapjoyads.com', 'tapjoy.com'
]
DEFAULT_STRINGS_BLOCKLIST = [
    'com.google.android.gms.ads.identifier.service.START', 'ads.mopub.com', 'doubleclick.net',
    'googleadservices.com', 'googlesyndication.com'
]


SCRIPT_DIRECTORY = os.path.dirname(os.path.abspath(__file__))
OUTPUT_FILE_PATH = os.path.join(SCRIPT_DIRECTORY, OUTPUT_FILENAME)


def clean_line(line):
    """Removes unwanted characters and comments from a line."""
    if not line or line.startswith(('#', '!', '[')):
        return None
    if line.startswith('-'):
        line = line[1:].lstrip()
    # Define symbols that indicate the start of comments or parameters
    symbols = ['!', '$', '#', '[', ']', '&', '%']
    cut_index = len(line)
    for symbol in symbols:
        index = line.find(symbol)
        if index != -1:
            cut_index = min(cut_index, index)
    cleaned_line = line[:cut_index].strip()
    # Remove specific characters used in filter syntax that might interfere
    cleaned_line = cleaned_line.replace('|', '').replace('^', '').replace('*', '').replace('@', '')
    return cleaned_line if cleaned_line else None


def fetch_and_clean_url(url):
    """Fetches content from a URL and returns a set of cleaned lines."""
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            # Check for successful HTTP status
            if response.status != 200:
                print(f"\nWarning: Failed to fetch {url} - Status code: {response.status}")
                return set()
            try:
                content = response.read().decode('utf-8', errors='ignore').splitlines()
            except Exception as decode_err:
                 print(f"\nWarning: Failed to decode content from {url}: {decode_err}")
                 return set()

        cleaned_lines = set()
        for line in content:
            cleaned = clean_line(line)
            if cleaned:
                cleaned_lines.add(cleaned)
        print(f".", end='', flush=True) # progress indicator
        return cleaned_lines
    except urllib.error.URLError as e:
        # Handle network-related errors
        print(f"\nWarning: Network error fetching {url}: {e.reason}")
        return set()
    except Exception as e:
        # Handle other potential errors
        print(f"\nWarning: Error processing {url}: {e}")
        return set()


def read_list_from_file(filename):
    """Reads lines from a local file into a set."""
    full_path = os.path.join(SCRIPT_DIRECTORY, filename)
    try:
        # Open and read the file, adding non-empty lines to a set
        with open(full_path, 'r', encoding='utf-8') as file:
            # Use clean_line to ensure consistency with fetched lists
            return set(cleaned for line in file if (cleaned := clean_line(line.strip())))
    except FileNotFoundError:
         print(f"\nWarning: File not found - {filename}. Skipping.")
         return set()
    except Exception as e:
        # Print error if reading fails
        print(f"\nWarning: Error reading {filename}: {e}")
        return set()


def http_fix(file_to_fix):
    try:
        # Read all lines from the file
        with open(file_to_fix, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        # Create a new list excluding lines that are exactly 'http' or 'https' (case-insensitive)
        corrected_lines = [line for line in lines if line.strip().lower() not in ('http', 'https')]
        with open(file_to_fix, 'w', encoding='utf-8') as file:
            file.writelines(corrected_lines)
    except Exception as e:
        print(f"\nError during http_fix for {file_to_fix}: {e}")


def get_yes_no_input(prompt):
    while True:
        response = input(prompt + " (y/n): ").strip().lower()
        if response in ('y', 'n'):
            return response
        print("Invalid input. Please enter 'y' or 'n'.")


def main():
    print("Fetching and formatting adguard blocklists...")
    combined_list = set()
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        future_to_url = {executor.submit(fetch_and_clean_url, url): url for url in URLS_TO_FETCH}
        # Process results as they complete
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                result = future.result()
                if result:
                   combined_list.update(result)
            except Exception as exc:
                print(f'\nWarning: {url} generated an exception: {exc}')
    #print("\nFetching complete.")

    include_defaults = get_yes_no_input(f"\nInclude LuckyPatcher defaults?")
    add_additionals = get_yes_no_input(f"Include {ADDITIONAL_LIST_FILENAME} contents?")
    add_facebook = get_yes_no_input(f"Block facebook.com (using {FACEBOOK_LIST_FILENAME})?")
    duplicate_to_strings = get_yes_no_input("Duplicate [http] entries into [ALL_STRINGS]?")


    facebook_blocklist = set()

    if add_facebook == 'y' or duplicate_to_strings == 'y':
        facebook_blocklist = read_list_from_file(FACEBOOK_LIST_FILENAME)

    additional_blocklist = set()
    if add_additionals == 'y':
        additional_blocklist = read_list_from_file(ADDITIONAL_LIST_FILENAME)


    final_http_list = set()
    final_strings_list = set()


    if include_defaults == 'y':
        final_http_list.update(DEFAULT_HTTP_BLOCKLIST)
        final_strings_list.update(DEFAULT_STRINGS_BLOCKLIST)

    if add_facebook == 'y':
        final_http_list.update(facebook_blocklist)
        final_strings_list.update(facebook_blocklist) # Also add to strings if blocking FB

    if add_additionals == 'y':
        final_http_list.update(additional_blocklist)
        if duplicate_to_strings == 'y':
             final_strings_list.update(additional_blocklist)

    final_http_list.update(combined_list)
    if duplicate_to_strings == 'y':
        final_strings_list.update(combined_list)
        
        if include_defaults == 'y':
             final_strings_list.update(DEFAULT_HTTP_BLOCKLIST)
        if add_facebook == 'y':
             final_strings_list.update(facebook_blocklist)


    try:
        with open(OUTPUT_FILE_PATH, 'w', encoding='utf-8') as file:
            # Write the [http] section
            file.write("[http]\n")
            for line in sorted(final_http_list):
                file.write(line + '\n')

            # Add spacing and [ALL_STRINGS] section header
            file.write('\n' * 4)
            file.write("[ALL_STRINGS]\n")
            for line in sorted(final_strings_list):
                file.write(line + '\n')

        print(f"File successfully saved at: {OUTPUT_FILE_PATH}")

        # Run the fix function AFTER writing the file
        http_fix(OUTPUT_FILE_PATH)

    except Exception as e:
        print(f"\nError writing the file: {e}")


    print("")
    input("Press Enter to exit...")


# --- Script Entry Point ---
if __name__ == "__main__":
    main()
