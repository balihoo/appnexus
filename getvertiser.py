import logging
import argparse
import json
from appnexusclient import AppNexusClient

logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    parser = argparse.ArgumentParser("package and deploy lambda functions")
    parser.add_argument('--token', type=str, help='auth token to use')
    args = parser.parse_args()

    client = AppNexusClient(token=args.token)
    res = client._get('advertiser')
    print(json.dumps(res, indent=2))
