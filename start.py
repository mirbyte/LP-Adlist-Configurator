import os
import urllib.request


urls = [
    "https://raw.githubusercontent.com/AdguardTeam/AdguardFilters/master/BaseFilter/sections/adservers.txt",
    "https://raw.githubusercontent.com/AdguardTeam/AdguardFilters/master/BaseFilter/sections/adservers_firstparty.txt",
    "https://raw.githubusercontent.com/AdguardTeam/AdguardFilters/master/MobileFilter/sections/adservers.txt",
    "https://raw.githubusercontent.com/AdguardTeam/AdguardFilters/master/MobileFilter/sections/antiadblock.txt",
    "https://raw.githubusercontent.com/AdguardTeam/AdguardFilters/master/MobileFilter/sections/general_url.txt",
    "https://raw.githubusercontent.com/AdguardTeam/AdguardFilters/master/SpywareFilter/sections/mobile.txt",
    "https://raw.githubusercontent.com/AdguardTeam/AdguardFilters/master/SpywareFilter/sections/tracking_servers.txt",
    "https://raw.githubusercontent.com/AdguardTeam/AdguardFilters/master/SpywareFilter/sections/tracking_servers_firstparty.txt"
]

file_name = "AdsBlockList_user_edit.txt"
script_directory = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(script_directory, file_name)


def clean_line(line):
    if line.startswith('-'):
        line = line[1:].lstrip()
    symbols = ['!', '$', '#', '[', ']', '&', '%']
    cut_index = len(line)
    for symbol in symbols:
        index = line.find(symbol)
        if index != -1:
            cut_index = min(cut_index, index)
    cleaned_line = line[:cut_index].strip()
    cleaned_line = cleaned_line.replace('|', '').replace('^', '').replace('*', '').replace('@', '')
    return cleaned_line


def fetch_and_clean_url(url):
    try:
        response = urllib.request.urlopen(url)
        content = response.read().decode('utf-8').splitlines()
        cleaned_lines = set()
        for line in content:
            cleaned_line = clean_line(line)
            if cleaned_line:
                cleaned_lines.add(cleaned_line)
        return cleaned_lines
    except Exception as e:
        print("")
        print(f"An error occurred while processing {url}: {e}")
        return set()

combined_list = set()
for url in urls:
    combined_list.update(fetch_and_clean_url(url))


def read_list_from_file(filename):
    try:
        with open(filename, 'r') as file:
            return set(line.strip() for line in file if line.strip())
    except Exception as e:
        print("")
        print(f"An error occurred while reading {filename}: {e}")
        return set()


facebook_urls_file = 'facebook_urls.txt'
fuckfacebook = read_list_from_file(facebook_urls_file)


default_http = [
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

default_strings = [
    'com.google.android.gms.ads.identifier.service.START', 'ads.mopub.com', 'doubleclick.net',
    'googleadservices.com', 'googlesyndication.com'
]

include_default_http = input("Do you want to include LuckyPatcher defaults? (y/n): ").strip().lower()
add_facebook = input("Do you want to block facebook.com? (y/n): ").strip().lower()
duplicate_http_to_all_strings = input("Do you want to duplicate everything from [http] into [ALL_STRINGS])? (y/n): ").strip().lower()

try:
    with open(file_path, 'w') as file:
        file.write("[http]\n")
        
        if include_default_http == 'y':
            for line in default_http:
                file.write(line + '\n')
        
        if add_facebook == 'y':
            for line in fuckfacebook:
                file.write(line + '\n')
        
        for line in sorted(combined_list):
            file.write(line + '\n')
        
        file.write('\n' * 4)
        file.write("[ALL_STRINGS]\n")
        
        if include_default_http == 'y':
            for line in default_strings:
                file.write(line + '\n')
        
        if add_facebook == 'y':
            for line in fuckfacebook:
                file.write(line + '\n')

        if duplicate_http_to_all_strings == 'y':
            for line in sorted(combined_list):
                file.write(line + '\n')
    
    print("")
    print(f"File successfully saved at: {file_path}")
    

except Exception as e:
    print("")
    print(f"error: {e}")

print("")
print("")
print("")
input("Press Enter to exit...")
