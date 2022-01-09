#!/usr/bin/env python3

import json
import requests
import urllib
import io
import os
from requests import api
from requests.models import RequestEncodingMixin

debug = True
ipfsgateway = "http://cf-ipfs.com/ipfs/"
#ipfsgateway = "https://ipfs.io/ipfs/"

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

def downloadpepe(name, url, filename):

    filepath = name + "/" + filename

    url = url.replace("https://ipfs.io/ipfs/", ipfsgateway)

    

    if not os.path.isfile(filepath):
        print('Downloading NFT: ' + filepath + ' from: ' + url)
        try:
            urllib.request.urlretrieve(url, name + "/" + filename )
        except:
            try:
                os.remove(filepath)
            except:
                pass
    else:
        print_debug('Already downloaded: ' + filepath)

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

    downloadpepe(pepenftjson['name'], pepenftjson['image'],                     "card.gif")
    downloadpepe(pepenftjson['name'], pepenftjson['animation_url'],             "card.glb")
    downloadpepe(pepenftjson['name'], pepenftjson['hifi_media']['card_front'],  "front.png")
    downloadpepe(pepenftjson['name'], pepenftjson['hifi_media']['card_back'],   "back.png")
    downloadpepe(pepenftjson['name'], pepenftjson['hifi_media']['video'],       "video.mp4")

def main():
        pepelist = scanpepefile()

        for pepeipfs in pepelist:
            print("\nFound Pepe!")

            request = ipfsgateway + pepeipfs

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