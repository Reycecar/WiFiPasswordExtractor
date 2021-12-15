'''
@Author Reyce Salisbury
12/14/2021
Wi-Fi Password Extractor
'''

import os
import subprocess
import re
import configparser
from collections import namedtuple

def get_saved_ssids_win():
    #Returns a list of saved SSIDs through netsh
    message = subprocess.check_output("netsh wlan show profiles").decode()
    #store ssids in a list
    ssids = []
    profiles = re.findall(r"All User Profile\s(.*)", message)
    for profile in profiles:
        #get rid of spaces and the colon from the netsh wlan show profiles
        ssid = profile.strip().strip(":").strip()
        ssids.append(ssid)
    return ssids

def print_wifi_profile_win(profile):
    #prints a singula wifi profile on windows
    print(f"{profile.ssid:25}\t\t{profile.ciphers:15}\t{profile.key:50}")

def get_saved_passwords_win():
    #gets saved Wi-Fi passwords saved on a Windows machine, produses a list of extracted profiles (["ssid", "ciphers", "key"])

    ssids = get_saved_ssids_win()
    Profile = namedtuple("Profile", ["ssid", "ciphers", "key"])
    WiFi_profiles = []
    for id in ssids:
        #Error arrises with commas and apostrophes, specifically with iPhone hotspots so replace apostrophe with comma
        newid = id.replace("'", "’")
        details = subprocess.check_output(f"""netsh wlan show profile "{newid}" key=clear""").decode(encoding='cp1252')

        ciphers = re.findall(r"Cipher\s(.*)", details)
        #ditch the spaces and the colon
        ciphers = "/".join([text.strip().strip(":").strip() for text in ciphers])

        #get the pass
        key = re.findall(r"Key Content\s(.*)", details)

        try:
            #try to get rid of spaces and colon; if fails, key must be None.
            key = key[0].strip().strip(":").strip()
        except:
            key = "None"

        WiFi_profile = Profile(ssid=id, ciphers=ciphers, key=key)
        print_wifi_profile_win(WiFi_profile)

        WiFi_profiles.append(WiFi_profile)

    return WiFi_profiles

def get_saved_passwords_lin():
    net_connections_path = "/etc/NetworkManager/system-connections/"
    targets = ["ssid", "auth-alg", "key-mgmt", "psk"]
    Profile = namedtuple("Profile", ["ssid", "auth_alg", "key_mgmt", "psk"])
    WiFi_profiles = []
    for file in os.listdir(net_connections_path):
        data = {option.replace("-", "_"):None for option in targets}
        parser = configparser.ConfigParser()
        parser.read(os.path.join(net_connections_path, file))
        for _, section in parser.items():
            for target, value in section.items():
                if target in targets:
                    data[target.replace("-", "_")] = value

        WiFi_profile = Profile(**data)
        print_wifi_profile_lin(WiFi_profile)
        WiFi_profiles.append(WiFi_profile)
    return WiFi_profiles

def print_wifi_profile_lin(profile):
    #prints a singula wifi profile on linux
    print(f"{str(profile.ssid):25}\t\t{str(profile.auth_alg):5}{str(profile.key_mgmt):10}{str(profile.psk):50}")
        
def print_wifi_profiles(os):
    #prints the wifi profiles created based on the os of the machine
    
    if(os == "nt"):
        print("SSID\t\t\t\t\tCIPHER(S)\tKEY")
        print("-"*75)
        get_saved_passwords_win()
    else:
        print("SSID\t\t\t\t\tAUTH KEY-MGMT\tKEY")
        print("-"*75)
        get_saved_passwords_lin()

def main():
    operating_system = os.name
    
    if(operating_system != "nt" and operating_system != "posix"):
        raise ValueError("Dog, this shit only works for linux or windows, my bad")
    else:
        print_wifi_profiles(operating_system)
    
if __name__ == "__main__":
    main()