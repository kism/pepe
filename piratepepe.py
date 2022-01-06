#!/usr/bin/env python3

import json
import requests
import os
from requests import api
from requests.models import RequestEncodingMixin

debug = True

def print_debug(text):
    if debug:
        print('\033[93m' + text + '\033[0m')


def scanpepefile():
    # Open File, dump tolist
    file = open("pepes.txt", 'r')
    pepelist = file.readlines()
    file.close()
    listfresh = []
    for element in pepelist:
        if element[0] == 'Q':
            listfresh.append(element.strip())
    pepelist = listfresh
    print(pepelist)

    file.close()

    return pepelist

def processpepenftjson(pepenftjson):
    nftjson = (str(pepenftjson).replace("'",'"'))
    try:
        os.mkdir(pepenftjson['name'])
    except FileExistsError:
        pass
        
    nftjsonfile = open(pepenftjson['name'] + "/" + "nft.json", "w")
    print_debug(nftjson)
    nftjsonfile.write(nftjson)
    nftjsonfile.close()

def main():
        pepelist = scanpepefile()

        for pepeipfs in pepelist:
            print("\nFound Pepe!")

            request = "https://ipfs.io/ipfs/" + pepeipfs

            print("http request url: " + request)

            try:
                response = requests.get(request)
            except:
                pass

            print("http response: " + str(response))

            if response.status_code != 200 and response.status_code != 400:
                print("All is heck, HTTP: " + str(response.status_code))
                exit(1)

            pepenftjson = response.json()

            processpepenftjson(pepenftjson)

if __name__ == '__main__':
    main()