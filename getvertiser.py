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
    #adv = appnexus.advertiser_by_name("Globalizer")
    adv = appnexus.advertiser_by_id(1000000000056230)
    print(json.dumps(adv.data, indent=4) if adv else "NOPE")
    #for i, adv in enumerate(appnexus.advertisers()):
    #    print("{}: {}".format(i, adv.data['name']))
