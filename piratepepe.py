#!/usr/bin/env python3
"""pepe.py main."""

# pepe.py
# https://github.com/kism/pepe
# I hate NFTs but Matt Furie is cool, Every NFT collection is a Ponzi scheme

# The NFT collection is incomplete
# I intend to keep pepes_txt updated with the latest releases on the repo, i'll be pretty lazy with it though.

import argparse
import contextlib
import os
import random
import sys
import time
from collections import Counter

import magic
import requests
from colorama import Back, Fore, Style
from urllib3.exceptions import ReadTimeoutError

debug = False
files_skipped = []
start_point = 0
output_folder = "output"
slow_mode = False
shitlist = {}
headers = {"User-Agent": "Safari/537.3"}
HTTP_TIMEOUT = 10

ipfs_gateway_list = [
    "https://gateway.pinata.cloud/ipfs/",
    "https://ipfs.io/ipfs/",
    "https://storry.tv/ipfs/",
    "https://dweb.link/ipfs/",
    "https://ipfs.runfission.com/ipfs/",
    "https://trustless-gateway.link/ipfs/",
    "https://ipfs.eth.aragon.network/ipfs/",
    "https://4everland.io/ipfs/",
    "https://w3s.link/ipfs/",
    "https://nftstorage.link/ipfs/",
    "https://gateway.ipfs.io/ipfs/",
    "https://cloudflare-ipfs.com/ipfs/",
    "https://chainsaw.mypinata.cloud/ipfs/",
]

# This is a big list of NFT tokenURIs for the Matt Furie Rare Pepe NFT Collection
# The Project's website is https://rarepepe.fun
# To get more pepes, go to
# https://etherscan.io/token/0x937a2cd137fe77db397c51975b0caaaa29559cf7?a=1#readContract
# Expand "17. tokenURI"
# Enter the number of the token that you want to retreive
# Click Query
# Paste the string that is after ipfs://
pepes_txt = """
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
# These two seem unlisted on the website, kinda weird
QmWLG29vFdmFEyY6YTBSRb9gvJ8xkX8quqAmagqmYqzG3T
QmeQUZt3LopXcefYhwXwrmYpgu9Sv8H81fJBmy18LPjW8n
# Last one on the website as of checking 2024-05-14
QmXCHLCWNqcdA9i9QwVkpVc1wcEvtNRGp7Wxo3ZpHrkFyn
"""


def print_debug(text: str) -> None:
    """Debug messages in yellow if the debug global is true."""
    if debug:
        print(f"{Fore.YELLOW}{text}{Style.RESET_ALL}")


def add_to_ipfs_shitlist(gateway: str, error: str) -> None:
    """Keep a tally of gateway failures."""
    print(f"{Fore.RED}Gateway failure{Style.RESET_ALL}: {error}")

    if gateway not in shitlist:
        shitlist[gateway] = {}

    if "nfails" not in shitlist[gateway]:
        shitlist[gateway]["nfails"] = 0
    shitlist[gateway]["nfails"] += 1

    if "fails" not in shitlist[gateway]:
        shitlist[gateway]["fails"] = {}

    if error not in shitlist[gateway]["fails"]:
        shitlist[gateway]["fails"][error] = 0
    shitlist[gateway]["fails"][error] += 1


def scan_pepe_file(start_point: int) -> list:
    """Scan pepe_txt var for ipfs links."""
    pepe_list = pepes_txt

    listfresh = []
    for element in pepe_list.split():
        # Ignore everything that doesn't start with a Q since that's what all them things seem to start with
        if element[0] == "Q":
            listfresh.append(element.strip())
        else:
            print_debug(f"Not a pepe: {element.strip()}")
    pepe_list = listfresh
    print_debug(f"Pepe list: [{pepe_list!s}")

    print(f"Found {len(pepe_list)} tokenURIs to look for Pepe")

    if start_point > -1:
        pepe_list = pepe_list[start_point:]
        print(f"Trimming first {start_point} tokenURIs in list")

    return pepe_list


def check_file(file_path: str, gateway: str) -> bool:
    """Check if a file is heck."""
    failure = False
    mime = magic.Magic(mime=True, uncompress=True)

    try:
        file_type = mime.from_file(file_path)

        print(f"Found file type: {file_type}")
        if file_type.startswith("text"):
            add_to_ipfs_shitlist(gateway, f"FileWrongFormat {file_type}")
            failure = True

    except FileNotFoundError:
        pass

    return failure


def download_pepe_asset(stripped_url: str, file_name: str) -> bool:
    """Try all gateways to download asset."""
    file_downloaded = False
    file_path = output_folder + os.sep + file_name

    random.shuffle(ipfs_gateway_list)

    for gateway in ipfs_gateway_list[:]:
        if slow_mode:
            print("Waiting a minute before downloading")
            time.sleep(60)

        gw_failure = False
        url = gateway + stripped_url

        print(f"Attempting to download Pepe NFT Asset: '{file_name}' from: {url}")

        # Try download the file
        try:
            with requests.get(url, stream=True, headers=headers, timeout=HTTP_TIMEOUT) as r, open(file_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    print(".", end="")
                    # If you have chunk encoded response uncomment if
                    # and set chunk_size parameter to None.
                    # if chunk:
                    f.write(chunk)
            print()
        except requests.exceptions.ConnectionError:
            print()
            print(f"{Fore.RED}Download Failed{Style.RESET_ALL}")
            if not url.endswith("mp4"):
                add_to_ipfs_shitlist(gateway, "ConnectionError")
                gw_failure = True
            else:
                print("gateway might not have large file support")
        except (requests.exceptions.ReadTimeout, ReadTimeoutError):
            print()
            print(f"Timeout of {HTTP_TIMEOUT} seconds reached")
            add_to_ipfs_shitlist(gateway, "ReadTimeout")
            gw_failure = True

        gw_failure = check_file(file_path, gateway) or gw_failure

        if gw_failure:
            print("Gateway didn't give us the file correctly, removing file if it exists")
            with contextlib.suppress(FileNotFoundError):
                os.remove(file_path)
        else:
            print(f"{Back.WHITE}{Fore.GREEN} Success! {Style.RESET_ALL}")
            file_downloaded = True
            break

        print("trying next gateway...")

    return file_downloaded


def download_pepe(url: str, file_name: str) -> bool:
    """Download the asset, hardcoded to output."""
    file_downloaded = False
    file_path = output_folder + os.sep + file_name

    # the nft json for this collection has the ipfs.io gateway hardcoded in lmao, maybe this is normal 🤷
    stripped_url = url.replace("https://ipfs.io/ipfs/", "")

    # Randomise the gateway list so we try a different gateway first
    random.shuffle(ipfs_gateway_list)

    # In theory this one should always work, chainsaw nfs should be hosting the assets...
    if "https://chainsaw.mypinata.cloud/ipfs/" not in ipfs_gateway_list:
        ipfs_gateway_list.append("https://chainsaw.mypinata.cloud/ipfs/")

    if not os.path.isfile(file_path):  # This is where the magic happens
        file_downloaded = download_pepe_asset(stripped_url, file_name)
    else:
        print(f"Already downloaded: {file_name}")
        file_downloaded = True

    if not file_downloaded:
        files_skipped.append(file_name)

    return file_downloaded


def process_pepe_nft_json(pepe_nft_json: str) -> None:
    """Process the json for the toke, call the download functions."""
    # No idea why python json uses a single quote
    nftjson = str(pepe_nft_json).replace("'", '"')
    with contextlib.suppress(FileExistsError):
        os.mkdir("output")

    # Save the json file of the nft, this might be whats considered the ipfs object metadata
    with open("output/" + pepe_nft_json["name"] + ".json", "w") as nftjsonfile:
        nftjsonfile.write(nftjson)

    # Download all the things from the json, these are ipfs links
    download_pepe(pepe_nft_json["image"], pepe_nft_json["name"] + " - " + "card.gif")
    download_pepe(pepe_nft_json["animation_url"], pepe_nft_json["name"] + " - " + "card.glb")

    try:
        download_pepe(
            pepe_nft_json["hifi_media"]["card_front"],
            pepe_nft_json["name"] + " - " + "front.png",
        )
    except KeyError:
        print("No key 'card_front', this is the case with some of the Sparklers.")
    try:
        download_pepe(
            pepe_nft_json["hifi_media"]["card_back"],
            pepe_nft_json["name"] + " - " + "back.png",
        )
    except KeyError:
        print("No key 'card_back', this is the case with the Sparklers.")

    download_pepe(pepe_nft_json["hifi_media"]["video"], pepe_nft_json["name"] + " - " + "video.mp4")


def process_ipfs_gateway_list(ipfs_gateway_list: str) -> list:
    """Clean up the ipfs gateway list."""
    for item, count in Counter(ipfs_gateway_list).items():
        if count > 1:
            print(f"Duplicate gateway: {item}")

    return list(dict.fromkeys(ipfs_gateway_list))


def grab_pepe_json(pepe_ipfs: str) -> str:
    """Iterate through gateways to get Pepe's json."""  # since they probably suck
    pepe_nft_json = None
    failure = False

    random.shuffle(ipfs_gateway_list)

    for gateway in ipfs_gateway_list[:]:
        request = gateway + pepe_ipfs

        if slow_mode:
            print("Waiting a minute before downloading")
            time.sleep(60)

        print(f"Trying: {request}")

        # Here we are getting the json that the nft points to,
        # as I understand the etherium contract points at an ipfs object that
        # has a json file that points to the other assets on ipfs
        response = None
        try:
            response = requests.get(request, headers=headers, timeout=HTTP_TIMEOUT)
            if not response:
                add_to_ipfs_shitlist(gateway, "None")
        except requests.exceptions.ConnectionError:
            add_to_ipfs_shitlist(gateway, "ConnectionError")
            response = None
        except requests.exceptions.ReadTimeout:
            add_to_ipfs_shitlist(gateway, "ReadTimeout")
            response = None

        if not response:
            failure = True
        elif not response.ok:
            add_to_ipfs_shitlist(gateway, f"HTTP {response.status_code}")
            failure = True
        else:
            try:
                pepe_nft_json = response.json()
                failure = False
                break
            except requests.exceptions.JSONDecodeError:
                add_to_ipfs_shitlist(gateway, "GarbageJson")
                failure = True

    if failure:
        print("All gateways failed getting the json...")

    return pepe_nft_json


def process_pepes(pepe_list: str) -> None:
    """Iterate through the pepes."""
    for pepe_ipfs in pepe_list:
        print(
            f"{Back.WHITE}{Fore.BLACK} Looking for {Fore.GREEN}Pepe{Fore.BLACK} and his NFT json... {Style.RESET_ALL}",
        )

        pepe_nft_json = grab_pepe_json(pepe_ipfs)

        if pepe_nft_json:
            print(f"Found a Rare Pepe! : {pepe_nft_json['name']}")
            process_pepe_nft_json(pepe_nft_json)
        else:
            print(f"{Fore.RED}All is heck{Style.RESET_ALL} every defined ipfs gateway sucks")
            files_skipped.append("Entire Pepe Json: " + pepe_ipfs)


def main() -> None:
    """Main."""
    exitcode = 1
    print(f"{Back.WHITE}{Fore.BLACK} pirate{Fore.GREEN}pepe {Fore.BLACK}.py {Style.RESET_ALL}")
    print_debug("Debug on!\n")

    pepe_list = scan_pepe_file(start_point)

    process_pepes(pepe_list)

    print(f"\n {Back.WHITE}{Fore.BLACK} Done! {Style.RESET_ALL}")

    if len(shitlist.items()) > 0:
        print("ipfs gateway scoreboard:")
        sorted_shitlist = dict(sorted(shitlist.items(), key=lambda item: item[1]["nfails"], reverse=True))
        for gateway, failures in sorted_shitlist.items():
            print(f"Gateway: {gateway}")
            print(f"    Fails: {failures['nfails']}")
            print(" Specific:")
            sorted_fails = dict(sorted(failures["fails"].items(), key=lambda item: item[1], reverse=True))
            for error, count in sorted_fails.items():
                print(f"           {count}: {error}")

    else:
        print(f"{Fore.RED}Every ipfs gateway failed lmao{Style.RESET_ALL}")

    if len(files_skipped) > 0:
        print("Some Downloads failed")
        print()
        print(f"{Fore.RED}Missing Pepe Assets{Style.RESET_ALL}:")
        for file in files_skipped:
            print(f" {file}")
        print()
        print("Run the script again to try again.")
        print(
            "You might want to find some new ipfs gateways and add them to the script, "
            "or get a new IP address since some ipfs gateways will rate-limit or block you for downloading too much.",
        )
    else:
        print("All the Pepes should be downloaded!")
        exitcode = 0

    sys.exit(exitcode)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Matt Furie rarepepes.fun downloader")
    parser.add_argument("-d", "--debug", action="store_true", help="Increase output verbosity")
    parser.add_argument("--slow", action="store_true", help="Wait a minute before each download attempt")
    parser.add_argument("-s", "--start", type=int, default=0, help="Number of times to run")
    parser.add_argument("-o", "--output", type=str, default="output", help="Number of times to run")
    args = parser.parse_args()
    start_point = args.start + -1
    debug = args.debug
    output_folder = args.output
    slow_mode = args.slow

    ipfs_gateway_list = process_ipfs_gateway_list(ipfs_gateway_list)
    try:
        main()
    except KeyboardInterrupt:
        print()
        print("🙋‍♀️ Bye")
