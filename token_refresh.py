import memcache
import json
import config
from appnexusclient import AppNexusClient

def lambda_handler(event, context):
    mcache = memcache.Client([config.memcache_host, config.memcache_port])
    kwargs = dict(
        key="appnexus{}".format(config.env),
        val=AppNexusClient().token(),
        time=AUTH_TIMEOUT_SEC
    )
    sargs = json.dumps(kwargs)
    print("setting cache {}".format(sargs))
    success = bool(mcache.set(**kwargs))
    if not success:
        raise Exception("Unable to set cache: {}".format(sargs))

