import logging
import argparse
import json
from appnexus.appnexusclient import AppNexusResource

from config import config
logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    parser = argparse.ArgumentParser("package and deploy lambda functions")
    parser.add_argument('--id', type=str, help='the advertiser id to get')
    args = parser.parse_args()

    appnexus = AppNexusResource(config)
    #adv = appnexus.advertiser_by_name("Balihoo API Test")
    adv = appnexus.create_advertiser("Balihoo API Test", state="inactive")
    print(json.dumps(adv.data, indent=4) if adv else "NOPE")
    adv.data['code'] = 'Gerry'
    adv.save()
    adv = appnexus.advertiser_by_id(adv.data['id'])
    if adv.data['code'] == 'Gerry':
        print('code match')
    advid = adv.data['id']
    adv.delete()
    adv = appnexus.advertiser_by_id(advid)
    print(json.dumps(adv.data, indent=4) if adv else "GONE")

    #for i, adv in enumerate(appnexus.advertisers()):
    #    print("{}: {}".format(i, adv.data['name']))
