#!/usr/bin/env python3

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


def print_debug(text):  # Debug messages in yellow if the debug global is true
    if debug:
        print("\033[93m" + text + "\033[0m")


def no_pepes():
    print("No Pepes found, go back to http://github.com/kism/pepe and grab it, or create and fill a file called pepes.txt with 'Rarepepe by Matt Furie' tokenURIs.")
    exit(1)


def scan_pepe_file():  # Scan pepes.text for ipfs links
    # Open File, dump tolist
    try:
        file = open("pepes.txt", "r")
    except:
        no_pepes()

    pepelist = file.readlines()
    file.close()
    listfresh = []
    for element in pepelist:
        if element[0] == "Q":  # Ignore everything that doesnt start with a Q since thats what all them things seem to start with
            listfresh.append(element.strip())
        else:
            print_debug("Not a pepe: " + element.strip())
    pepelist = listfresh
    print_debug("Pepe list: " + str(pepelist))

    file.close()

    if len(pepelist) == 0:
        no_pepes()
    else:
        print("Found " + str(len(pepelist)) + " tokenURIs to look for Pepe")

    return pepelist


def download_pepe(name, url, filename):
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
                break
            except:
                print("  \033[91mDownload Failed\033[0m", end=', ')
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

    # Save the json file of the nft, this is the only thing on the etherium blockchain
    nftjsonfile = open("output/" + pepenftjson["name"] + ".json", "w")
    print_debug(nftjson)
    nftjsonfile.write(nftjson)
    nftjsonfile.close()

    # Download all the things from the json, these are ipfs links
    download_pepe(pepenftjson["name"], pepenftjson["image"],                    pepenftjson["name"] + ' - ' + "card.gif")
    download_pepe(pepenftjson["name"], pepenftjson["animation_url"],            pepenftjson["name"] + ' - ' + "card.glb")
    download_pepe(pepenftjson["name"], pepenftjson["hifi_media"]["card_front"], pepenftjson["name"] + ' - ' + "front.png")
    download_pepe(pepenftjson["name"], pepenftjson["hifi_media"]["card_back"],  pepenftjson["name"] + ' - ' + "back.png")
    download_pepe(pepenftjson["name"], pepenftjson["hifi_media"]["video"],      pepenftjson["name"] + ' - ' + "video.mp4")


def main():
    failure = False
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
        print("All the Pepes should be downloaded!")
    else:
        print("\033[91mEvery ipfs gateway failed\033[0m!")
        print("There will be some missing Pepes")
        print("Run the script again to try again.")
        print("You might want to find some new ipfs gateways and add them to the script, or get a new IP address since some ipfs gateways will rate-limit or block you for downloading too much.")


if __name__ == "__main__":
    if len(sys.argv) > 1 and (sys.argv[1] == "-d" or sys.argv[1] == "--debug"):
        debug = True

    main()
