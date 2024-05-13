#!/usr/bin/env python3

# pepe.py
# https://github.com/kism/pepe
# I hate NFTs but Matt Furie is cool, Every NFT collection is a Ponzi scheme

# The NFT collection is incomplete
# I intend to keep pepestxt updated with the latest releases on the repo, i'll be pretty lazy with it though.

import urllib
import os
import sys
import random
import requests
from collections import Counter

debug = False
criticalfileskipped = False

ipfsgatewaylist = [
    "http://cf-ipfs.com/ipfs/",
    "https://ipfs.io/ipfs/",
    "https://gateway.ipfs.io/ipfs/",
    "https://storry.tv/ipfs/",
    "https://ipfs.fleek.co/ipfs/",
    "https://gateway.pinata.cloud/ipfs/",
    "https://ipfs.telos.miami/ipfs/",
    "https://crustwebsites.net/ipfs/",
    "https://ipfs.eternum.io/ipfs/",
    "https://ipfs.yt/ipfs/",
    "https://ipfs.2read.net/",
    "https://ipfs.azurewebsites.net/ipfs/",
    "https://hardbin.com/ipfs/",
    "https://ipfs.tubby.cloud/ipfs/",
    "https://video.oneloveipfs.com/ipfs/",
    "https://ipfs.astyanax.io/ipfs/",
    "https://ipfs.infura-ipfs.io/ipfs/",
    "https://ipfs.dweb.link/ipfs/",
    "https://ipfs.best-practice.se/ipfs/",
    "https://ipfs.2read.net/ipfs/",
    "https://cloudflare-ipfs.com/ipfs/",
    "https://ipfs.mihir.ch/ipfs/",
    "https://jorropo.net/ipfs/",
    "https://ipfs.litnet.work/ipfs/",
    "https://ipfs.lain.la/ipfs/",
    "https://ipfs.subutai.io/ipfs/",
    "https://ipfs.yt/ipfs/",
    "https://trustless-gateway.link/ipfs/",
    "https://ipfs.runfission.com/ipfs/",
    "https://ipfs.eth.aragon.network/ipfs/",
    "https://4everland.io/ipfs/",
    "https://w3s.link/ipfs/",
    "https://nftstorage.link/ipfs/",
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
QmU9wnWqmYQ542GTkhdLjy1nbJT7FRQSTMbq31rxoTv4tH
QmNhVY2gANALdtZTQZW4c6H9oRBz4SKMs4vpGruaGFs1Zo
QmeFdUyA4VyrAutm27DZ99XmHkBQ7e6tbMsRWWpGDwnbjh
QmSZvdKuBcagmxG41fryGQWmBQRzTc1P6JL6Q2hzcJdjWd
QmU3oqor4EWqe4oxtC8SRhR16zr6S64aG22oqXGzXgFi3c
QmeWb7CGiBus78NG77UoCsYYEvAau5hUkjQbYvrJSFQWM8
QmYDwsBKAMdVihs6iY5xMD6EFkTx9X7hdTQF3xmGJQvB6n
Qmf4gQJMsrLCtwW4x6dFedXvSiszSxUpYA7ms62rGZFd48
QmPmdMxjyeTB3H4jN8TYiwRqCfV8nBFyQh44ggtMe3Y4Gr
QmQ7XqiRmUpD2VDMJg9jZcz6w6snpxm6tMvAwS7mJGaeUD
QmS8KVyQQUbnuhwMDTXa5zZsoZDGs8hzyqNLTHL7R54Ge1
Qmei3P3GuNDbZLkrDTHon7nPzYvS8E9vj7m1n4R2B549EF
QmdWJhHZ6QNEVTx6oQLCc7PmJFAJQAkyXr9cyCVqqVEgkd
QmSmcfAExZEkFLu2tsb5CDihEAFSBBE94czJLEXrXa8AP6
QmXK113mihDpY4HmaTDAau4srTcrRvQG3qkr6AvZFSHown
QmX4hv2DGMiSnEE5DqyYnWkHMt4RCg8rTGAsVxyKB47Rci
QmYVVTowpWvspYqSKZthuF5NRn2ZWRksiTYHAe6VzqvGn7
Qmd6dVVESefVFTmKDTHhm96swHLu6xngo3nU1yzbXd29cx
QmTyhsqoEoMip3oFbWG2FMcE4NdMEX8bNuBwUP7B5qNBSU
QmdLwDhHecPe241A3t3tE6R6L5B3Ptd78q3r9krakZZHAS
Qme5EjJGooeSdbH6DyDQeEr4wPmVMiARScsmy7XA8QpZ8v
QmYAZFTeHw5PewmT1F9CQTNeGiYMKdcsew4kJwimMLiJpc
QmQfAguVHDTwD9SUuAwq4CzXecvVUfiw7ndTV73HQCbNZz
QmdrdVACkQRpBKuJxm4b56Z1RYBLbArgsF7DSrCn2Jp8Cg
QmXncM7RAG5rrUqUtwxtfuEB7cfTWZQDNUpAtLrFjayq16
QmTf5ebHkh9wxzNHfQvvxmprFSu8Ly51gz6naE6LoF8cAZ
QmP8op3XAcG996UdHRFUuCPYLfChEBbrwAeQ8qRu8KKgu4
QmUwzMnEgaabejaGi3zEjw9gTknjLk7aW5LSaz2nR8BZoZ
QmbDGJ3bY1jbxdS8pUuLUSoZr5VHeZAJdJaWuA5w5qv9Dx
QmQg3gvgMcdvfACwDt8haAQ212e72YbYznJfF3nvc1i6go
QmeuR33X7pUF6uMt9TZc2oSDoDh2hU7VsDPrftvngoj2hh
QmbETLe17BZZD2XgBSr51CeXtaxQJisJ7C36EqCwswgig2
QmXzHUqmNZyDEUHJJcHNijZuvStqjR7yNegLvzQuVquwPw
QmNvW49pBKQrhKx64TbQ88qQYSicPn34ZSFKrwb7f1TwJS
QmbWyNdVKjrWE4aVTLN2e3T3qHsLrzVExEsjwosjWVBGLu
QmeqQBCcgcTBjZw76seBtTcSXJ4n1S5hQkXb9erGhUFFea
QmYMSYxCTjPUjN2QpQPckQWHAUbEw5HiUkKmrDHaZHPEKG
QmbtBut7yASVEAySTqri5eVq1gk9kf4xYhNCJHGs7jAZDC
QmVEmpoXQtfTj7HG5SJT2VmaCpHn4hDqUUNkPJzNMrnMvr
QmV2L2n3pa7rX3ySTN8Vpv1kjGbJDP6HrpbUWUymSJ5HNy
Qmb1mp9QVPife3BjAHvREmnKkLhpvH1EPjZcqxnt3J2Ndw
QmQ3pyyybJKuuwozBQ9n1TSXVXB7LUk65xdh3PZiMLdp2L
QmcBMGPK6AERBzXFhXaBM34yPPPrWATTNKrqvy7FabovFn
QmfTUAV2UxrNVsyYo8TubwK1V2x92wJiDGfLqGBVxEuHgB
QmZzQmK1McQpBu88be11RHWWWcoFB9U2v8kSCBxYbVRCVp
QmX7kXvnBhsw46RGHEaKwH33KuDajg3eHANS3MYESs9ob2
QmWgWL3k8WBgTxVgsE6cBTckopEeonKY6uZWP2qfr34qve
QmbDcTTVj6px8hmvuTYaazfwk8Bg57h9A5mxM8LrtcYHum
QmYVXEYzZzrtfebkVSodaua9JdDVNJwv7VSYxNxAgucWmZ
QmfWxL1W9u6TgzSK8wbG1X8rzCYcWhVgRBm6k3kmmK9Nne
QmV7mkbRBbBM7knSdLY5YYg59WS7rHm2dHZ4GazJFx2g4e
QmZYAnRqrf5qrohuhujk2Vj4QYmwcVxG5o5TEWwmEXCcnq
QmTCKVo7JUBjEW3V1FKh8TMt8CmD9tEdesYz6L3iiEQ7ah
QmPsEgSgCXh33Kn4X3XNdcF3Hxegk1JAZEG15WULW2hbiN
QmWiNvL6SLjdBHHtjou9rxs3WfeBqYjXc5q8PgyfSBvRjH
QmWk8iarXhQUXzy7Gpbkxj6GGLwD32k8teniEn9seaMHbc
QmZc5Q14xRSGA3SGJD87RfHkGg7i6sRgYuavrhfb28Y2wv
QmR8Bf3PwxGCzRbJL7fjCrT1DQk3eQHvwe41SUKhaxpGfQ
QmWDByBS9oTXDvd8SbroRACsMNFUvcmFgoZBgoYeVbe9xt
QmeJkFMzQM7Bk5ekmweUqQfrpeNaYMtxEtgZ2NL2KbHQDY
QmTLESY6pVuqUyJGLc6kEvXocBzP9b2az4ZMnDh986rCUs
QmdG3rwDK6iLLxqvvPDbUpsmgHmUzxEpB8awiFwteXEXJA
QmPd4JJLdxu8vH92b6FPa8p2wZdQrMMfxiDXPARArtiA6W
QmW2uDqf1Pc7g837YvWeL6NC5paXck3eidmi6CWni9UgGT
QmceXPdttarJoE4Tf1H6a3yWhf6UEUpD1tJug1EJ2xzL2i
QmaKgAsWMMSDsgMEgQZcKT6hjfwThJWdF7ZAyKSf9RybhM
QmR3jDC6zgBwaLwJSkRjk5WTi5jTY4duWyWCQsmeywSwaF
QmU4CoouJGLS1QcjRwPty2iMR94KqMxDCLZmWrsE3MGXCP
Qmadb9vzW1rKKgxmSM3oK1ETrAAxett1tNs4yqKoSfwt2T
QmcCAxNsXtNC5DXY33emWU3hX82HLLMUgJ6vkccQfu2tva
QmYfqRQ8h4Y6RoQqeP9RHbmTkWC9p1WqAE5fDZPGP2A2sD
QmfUq7HbwHoz1SaUUKY1216Az6SnC2TawdwCxs4ofKVrqm
QmWaFvvpnPPy9qoyGLbZH9cR3NJxCNdMubMaHwoVnbCZAf
QmZ6ZwZE4TX36rPAp9ud1tyzwbvfa6M1T3J42dDxg9mMAS
QmQcKc5WaSP5W6SVD7zeaLPteTDtFF4LfW1iMENgAm4Ftf
QmV7wjtYtKS6eNaXwGirLTw5gvTEeoLZESL7ndwXH3hj6C
QmWLG29vFdmFEyY6YTBSRb9gvJ8xkX8quqAmagqmYqzG3T
QmeQUZt3LopXcefYhwXwrmYpgu9Sv8H81fJBmy18LPjW8n
QmXCHLCWNqcdA9i9QwVkpVc1wcEvtNRGp7Wxo3ZpHrkFyn
"""


def print_debug(text):  # Debug messages in yellow if the debug global is true
    if debug:
        print("\033[93m" + text + "\033[0m")


def scan_pepe_file():  # Scan pepetxt var for ipfs links
    pepelist = pepestxt

    listfresh = []
    for element in pepelist.split():
        # Ignore everything that doesn't start with a Q since that's what all them things seem to start with
        if element[0] == "Q":
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

            print(
                "Attempting to download Pepe NFT Asset: '"
                + filename
                + "' from: "
                + url,
                end="\n",
            )

            try:
                urllib.request.urlretrieve(url, "output/" + filename)
                print("  \033[92mSuccess!\033[0m")
                criticalfileskipped = False
                break
            except KeyError:  # TEMP TEMP FIXME
                print("  \033[91mDownload Failed\033[0m", end=", ")
                criticalfileskipped = True
                try:
                    if not url.endswith("mp4"):
                        print("\033[91mremoving from gateway list\033[0m, ", end="")
                        ipfsgatewaylist.remove(gateway)
                    else:
                        print("gateway might not have large file support, ", end="")

                    os.remove(filepath)
                except KeyError:  # TEMP TEMP FIXME
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
    download_pepe(pepenftjson["image"], pepenftjson["name"] + " - " + "card.gif")
    download_pepe(
        pepenftjson["animation_url"], pepenftjson["name"] + " - " + "card.glb"
    )
    download_pepe(
        pepenftjson["hifi_media"]["card_front"],
        pepenftjson["name"] + " - " + "front.png",
    )
    download_pepe(
        pepenftjson["hifi_media"]["card_back"], pepenftjson["name"] + " - " + "back.png"
    )
    download_pepe(
        pepenftjson["hifi_media"]["video"], pepenftjson["name"] + " - " + "video.mp4"
    )


def main():
    global ipfsgatewaylist
    failure = False
    exitcode = 1
    print("\n\033[47m\033[30m pirate\033[92mpepe\033[30m.py \033[0m")
    print_debug("Debug on!\n")

    for item, count in Counter(ipfsgatewaylist).items():
        if count > 1:
            print("Duplicate gateway: " + item)

    ipfsgatewaylist = list(dict.fromkeys(ipfsgatewaylist))

    pepelist = scan_pepe_file()

    for pepeipfs in pepelist:
        print(
            "\n\033[47m\033[30m Looking for \033[92mPepe\033[30m and his NFT json... \033[0m"
        )
        response = None

        # Randomise the gateway list so we try a different gateway first
        random.shuffle(ipfsgatewaylist)

        # Iterate through a list of ipfs gateways since they probably suck
        for gateway in ipfsgatewaylist[:]:
            failure = False
            request = gateway + pepeipfs

            print("Trying: " + request)

            # Here we are getting the json that the nft points to,
            # as I understand the etherium contract points at an ipfs object that
            # has a json file that points to the other assets on ipfs
            response = None
            try:
                response = requests.get(request, timeout=5)
            except requests.exceptions.ConnectionError:
                print("ConnectionError: " + request, end="")
                response = None
            except requests.exceptions.ReadTimeout:
                print("ReadTimeout: " + request, end="")
                response = None

            if not response:
                print("Complete gateway failure: " + gateway)
                ipfsgatewaylist.remove(gateway)
                failure = True
            elif response.status_code != 200 and response.status_code != 400:
                print(
                    "Gateway: "
                    + gateway
                    + " sucks, HTTP: "
                    + str(response.status_code)
                    + ", \033[91mremoving from gateway list\033[0m"
                )
                ipfsgatewaylist.remove(gateway)
                failure = True
            else:
                failure = False
                break  # We have the nfw json

        # we have the nft json, lets grab the assets
        if not failure:
            pepenftjson = response.json()
            print("Found a Rare Pepe!: " + pepenftjson["name"] + "")
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
            print(
                "Some Downloads failed, this probably means that only a gateway that is working for you doesn't have large file support"
            )
    else:
        print("\033[91mEvery ipfs gateway failed lmao\033[0m!")

    if criticalfileskipped:
        print("There will be some missing Pepes")
        print("Run the script again to try again.")
        print(
            "You might want to find some new ipfs gateways and add them to the script, or get a new IP address since some ipfs gateways will rate-limit or block you for downloading too much."
        )

    exit(exitcode)


if __name__ == "__main__":
    if len(sys.argv) > 1 and (sys.argv[1] == "-d" or sys.argv[1] == "--debug"):
        debug = True
    main()
