import json
import sys
import argparse
from pathlib import Path
import os
import re

import requests

parser = argparse.ArgumentParser(
    description="providence is an open source to find company domain names based on a given company name",
    epilog="More info: https://github.com/adulau/providence",
)

parser.add_argument("-v", help="increase output verbosity", action="store_true")
parser.add_argument("-n", "--name", type=str, help="Company name to find")
parser.add_argument(
    "-t",
    "--tld",
    type=str,
    help="Limit to a specific TLD (if not, all known TLDs are tested)",
)

args = parser.parse_args()

homedir = str(Path.home())

if not args.name:
    parser.print_usage()
    parser.exit()


def cache_suffixes(url="https://publicsuffix.org/list/public_suffix_list.dat"):
    tlds = set()
    cachedfile = os.path.join(homedir, ".providence-suffix")
    if not os.path.exists(cachedfile):
        r = requests.get(url)
        with open(cachedfile, 'wb') as fd:
            fd.write(r.content)

    with open(cachedfile, 'r') as fd:
        for line in fd:
            tld = line.rstrip()
            if not tld.startswith("//"):
                tlds.add(tld)
    return tlds


def guess_name(name=None, tlds=None):
    guessed_names = set()
    if name is None:
        return False
    for t in tlds:
        guessed_names.add(f"{name}.{t}")
    return guessed_names


if not args.tld:
    tlds = cache_suffixes()
else:
    tlds = [args.tld]

results = set()

if re.search(r' {1,}', args.name):
    # replace with -
    name = args.name
    p = name.replace(" ", "-")
    results.update(guess_name(name=p, tlds=tlds))
    # combined
    p = name.replace(" ", "")
    results.update(guess_name(name=p, tlds=tlds))
    # try with removal of word

else:
    results.update(guess_name(name=args.name, tlds=tlds))

print(results)
