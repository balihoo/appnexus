import logging
import argparse
import json
from appnexusclient import AppNexusResource

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    parser = argparse.ArgumentParser("package and deploy lambda functions")
    parser.add_argument('--id', type=str, help='the advertiser id to get')
    args = parser.parse_args()

    appnexus = AppNexusResource()
    for i, adv in enumerate(appnexus.advertisers()):
        print("{}: {}".format(i, adv.data['name']))
