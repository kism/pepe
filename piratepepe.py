#!/usr/bin/env python3

import json
import requests
import urllib
import io
import os
from requests import api
from requests.models import RequestEncodingMixin

debug = True
ipfsgatewaylist = ["http://cf-ipfs.com/ipfs/", "https://ipfs.io/ipfs/","https://gateway.ipfs.io/ipfs/","https://ipfs.fleek.co/ipfs/","https://gateway.pinata.cloud/ipfs/","https://ipfs.telos.miami/ipfs/","https://ipfs.mihir.ch/ipfs/","https://crustwebsites.net/ipfs/","https://ipfs.eternum.io/ipfs/","https://ipfs.eternum.io/ipfs/","https://video.oneloveipfs.com/ipfs/"]

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
        else:
            print_debug("Not a pepe: " + element.strip())
    pepelist = listfresh
    print(pepelist)

    file.close()

    return pepelist

def downloadpepe(name, url, filename):
    filepath = name + "/" + filename

    strippedurl = url.replace("https://ipfs.io/ipfs/", "")

    if not os.path.isfile(filepath):
        for gateway in ipfsgatewaylist:
            url = gateway + strippedurl

            print('Attempting to download NFT: ' + filepath + ' from: ' + url, end='')

            try:
                urllib.request.urlretrieve(url, name + "/" + filename )
                print(" \033[92mSuccess!\033[0m")
                break
            except:
                try:
                    print(" \033[91mDownload Failed\033[0m",end='')
                    os.remove(filepath)
                except:
                    pass

            print(" trying next gateway...")
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
        failure = False
        pepelist = scanpepefile()

        for pepeipfs in pepelist:
            print("\nFound Pepe!")

            for gateway in ipfsgatewaylist:
                request = gateway + pepeipfs

                print("http request url: " + request)

                try:
                    response = requests.get(request)
                except:
                    pass

                if response.status_code != 200 and response.status_code != 400:
                    print("All is heck, HTTP: " + str(response.status_code))
                    failure = True
                else:
                    failure = False
                    break

            if not failure:
                pepenftjson = response.json()
                processpepenftjson(pepenftjson)
            else:
                print("Every defined ipfs gateway sucks")

if __name__ == '__main__':
    main()