#!/usr/bin/env python3

# pepe.py
# https://github.com/kism/pepe
# I hate NFTs but Matt Furie is cool, Every NFT collection is a Ponzi scheme

# The NFT collection is incomplete
# I intend to keep pepestxt updated with the latest releases.

import json
from socket import IP_DEFAULT_MULTICAST_LOOP
import requests
import urllib
import io
import os
import sys
import random
from requests import api
from requests.models import RequestEncodingMixin

debug = False
criticalfileskipped = False

ipfsgatewaylist = [
    "http://cf-ipfs.com/ipfs/",
    "https://ipfs.io/ipfs/",
    "https://gateway.ipfs.io/ipfs/",
    "https://ipfs.fleek.co/ipfs/",
    "https://gateway.pinata.cloud/ipfs/",
    "https://ipfs.telos.miami/ipfs/",
    "https://ipfs.mihir.ch/ipfs/",
    "https://crustwebsites.net/ipfs/",
    "https://ipfs.eternum.io/ipfs/",
    "https://ipfs.yt/ipfs/",
    "https://ipfs.2read.net/",
    "https://ipfs.azurewebsites.net/ipfs/",
    "https://hardbin.com/ipfs/",
    "https://ipfs.tubby.cloud/ipfs/",
    "https://video.oneloveipfs.com/ipfs/",
]

# This is a big list of NFT tokenURIs for the Matt Furie Rare Pepe NFT Collection
# The Project's website is https://rarepepe.fun
# To get more pepes, go to
# https://etherscan.io/token/0x937a2cd137fe77db397c51975b0caaaa29559cf7?a=1#readContract
# Expand "17. tokenURI"
# Enter the number of the token that you want to retreive
# Click Query
# Paste the string that is after ipfs://
pepestxt = """
QmTUTQw7AqGYgDQEJECxzcNqZbVSWVYFbiMvvLUY6PZSbk
QmSWExPQTeMF873sQKSR31R1R9bxiUYfNJmmEbYvSt72dS
QmTTTDrBxZnD3bybvRitcn7ptbHF9qgBH3zNWm13VRpcqZ
QmRU7LPbApzbauzwqLvo5WRukt4UdpozuiHgHukghGM2HG
QmdjbRhj7TGUtBHxmWQko8YuXiQFpJZH3GGgvTLpM7ThDB
QmcjPwyQzCcm4ss9GnxxbZy5bpt2pXe4yLS5v7kvfUfGXe
QmWyHdusyDaZwXUfyMm5jZGjdpmSPaBBpdBxVcf4TPproq
QmccrhaUKXSf6tiw4PQGkzfjnVVmWdeg1BF6682a2E7j4F
QmfFsoWAD1ABdvvZsWZErCmX7rhfEeHKgpD7svoBNLacTV
QmQTzRiw1suHjWdLbbsNGDrtLApqjcoN38CV7bQmqydzkH
QmQLMS1fzGed6pkAEsTLee5JmWWXeF5oF3sPs5CQ76j91W
QmcDV1dyTaF5vft5FPcDizei7rgZLQ6cY5zq3Z37N5sWz4
QmV8RHoEEv774ixawjfNtDvvfayh7hxsL7kdyBQCs4r9F6
QmXxkKtH87jmGzub4hyvDH9PVa6VHvzwErdjmhxC2p9Tsf
QmaNQv7vKppAivXtChKwzQukq92osP3yZs9HZqtBHd26dL
QmZNMMmUJYZazvECuRss9harpEzzaNSMxTtrjx3f2vGE9T
QmdLGoAZjDyGnYDksoVfygkyXaWDJMTopwPH4fcM5tq2a6
Qma3DFyPptKT5YRr5LQZaoWbUqd3Ej7xsNcgWFAKYmT6Ap
QmPnxLBttNXPfJKBYfXpxMsUzQ7fRan4mpFBZ3YiWFE8p1
QmPJRS29vAQwRRJh5pAhKHHEPeytCEwwG9ho52RX77dmZE
QmRA1brW5hZsivXNMdk8ec9aQcaTFXSysxwHyfrtYzkGzt
QmeAvgc7xuqLY6NifkMGoaC6ffVCwnTvhQSYn4rMC9Uv8Y
QmZ5T5CVJgweN1FNA6eoFKKby7NNnYRSS7VD9dnkCxHLvA
QmRnzMxFA2aesbeuHWSzhTDK5wUKjef1r8PrDdHXHc6AUB
"""

def print_debug(text):  # Debug messages in yellow if the debug global is true
    if debug:
        print("\033[93m" + text + "\033[0m")


def scan_pepe_file():  # Scan pepetxt var for ipfs links
    pepelist = pepestxt

    listfresh = []
    for element in pepelist.split():
        if element[0] == "Q":  # Ignore everything that doesnt start with a Q since thats what all them things seem to start with
            listfresh.append(element.strip())
        else:
            print_debug("Not a pepe: " + element.strip())
    pepelist = listfresh
    print_debug("Pepe list: " + str(pepelist))

    print("Found " + str(len(pepelist)) + " tokenURIs to look for Pepe")

    return pepelist


def download_pepe(url, filename):
    global criticalfileskipped
    filepath = "output/" + filename
    
    # the nft json for this collection has the ipfs.io gateway hardcoded in lmao, maybe this is normal 🤷
    strippedurl = url.replace("https://ipfs.io/ipfs/", "")

    # Randomise the gateway list so we try a different gateway first
    random.shuffle(ipfsgatewaylist)

    if not os.path.isfile(filepath):  # if the asset hasn't already been downloaded
        # try all gateways to download asset
        for gateway in ipfsgatewaylist[:]:
            url = gateway + strippedurl

            print("Attempting to download Pepe NFT Asset: '" + filename + "' from: " + url, end='\n')

            try:
                urllib.request.urlretrieve(url, "output/" + filename)
                print("  \033[92mSuccess!\033[0m")
                criticalfileskipped = False
                break
            except:
                print("  \033[91mDownload Failed\033[0m", end=', ')
                criticalfileskipped = True
                try:
                    if not url.endswith("mp4"):
                        print("\033[91mremoving from gateway list\033[0m, ", end='')
                        ipfsgatewaylist.remove(gateway)
                    else:
                        print("gateway might not have large file support, ", end='')
   
                    os.remove(filepath)
                except:
                    pass

            print("trying next gateway...")
    else:
        print("Already downloaded: " + filename)


def process_pepe_nft_json(pepenftjson):
    # No idea why python json uses a single quote
    nftjson = str(pepenftjson).replace("'", '"')
    try:
        os.mkdir("output")
    except FileExistsError:
        pass

    # Save the json file of the nft, this might be whats considered the ipfs object metadata
    nftjsonfile = open("output/" + pepenftjson["name"] + ".json", "w")
    print_debug(nftjson)
    nftjsonfile.write(nftjson)
    nftjsonfile.close()

    # Download all the things from the json, these are ipfs links
    download_pepe(pepenftjson["image"],                    pepenftjson["name"] + ' - ' + "card.gif")
    download_pepe(pepenftjson["animation_url"],            pepenftjson["name"] + ' - ' + "card.glb")
    download_pepe(pepenftjson["hifi_media"]["card_front"], pepenftjson["name"] + ' - ' + "front.png")
    download_pepe(pepenftjson["hifi_media"]["card_back"],  pepenftjson["name"] + ' - ' + "back.png")
    download_pepe(pepenftjson["hifi_media"]["video"],      pepenftjson["name"] + ' - ' + "video.mp4") # So far I only expect some ipfs gateways will reject .mp4 downloads

def main():
    failure = False
    exitcode = 1
    print("\n\033[47m\033[30m pirate\033[92mpepe\033[30m.py \033[0m")
    print_debug("Debug on!\n")

    pepelist = scan_pepe_file()

    for pepeipfs in pepelist:
        print("\n\033[47m\033[30m Looking for \033[92mPepe\033[30m and his NFT json... \033[0m")

        # Randomise the gateway list so we try a different gateway first
        random.shuffle(ipfsgatewaylist)

        # Iterate through a list of ipfs gateways since they probably suck
        for gateway in ipfsgatewaylist[:]:
            request = gateway + pepeipfs

            print("Trying: " + request)

            # Here we are getting the json that the nft points to, as I understand the etherium contract points at an ipfs object that has a json file that points to the other assets on ipfs
            response = None
            try:
                response = requests.get(request, timeout=5)
            except:
                pass

            if response != None:
                if response.status_code != 200 and response.status_code != 400:
                    print("Gateway: " + gateway + " sucks, HTTP: " + str(response.status_code) + ", \033[91mremoving from gateway list\033[0m")
                    ipfsgatewaylist.remove(gateway)
                    failure = True
                else:
                    failure = False
                    break
            else:
                print("Gateway: " + gateway + " timed out, \033[91mremoving from gateway list\033[0m")
                ipfsgatewaylist.remove(gateway)
                failure = True

        # we have the nft json, lets grab the assets
        if not failure:

            pepenftjson = response.json()
            print("Found a Rare Pepe!: " + pepenftjson['name'] + "")
            process_pepe_nft_json(pepenftjson)
        else:
            print("\033[91mAll is heck\033[0m, every defined ipfs gateway sucks")

    print("\n\033[47m\033[30m Done! \033[0m")

    if len(ipfsgatewaylist) > 0:
        print_debug("ipfs gateways that made it to the end: " + str(ipfsgatewaylist))
        if not criticalfileskipped:
            print("All the Pepes should be downloaded!")
            exitcode = 0
        else:
            print("Some Downloads failed, this probably means that only a gateway that is working for you doesn't have large file support")
    else:
        print("\033[91mEvery ipfs gateway failed lmao\033[0m!")
        
    if criticalfileskipped:
        print("There will be some missing Pepes")
        print("Run the script again to try again.")
        print("You might want to find some new ipfs gateways and add them to the script, or get a new IP address since some ipfs gateways will rate-limit or block you for downloading too much.")

    exit(exitcode)

if __name__ == "__main__":
    if len(sys.argv) > 1 and (sys.argv[1] == "-d" or sys.argv[1] == "--debug"):
        debug = True
    main()
