# Balihoo AppNexus API SDK
The Balihoo AppNExus API SDK provides an easy pythonic interface to interact with the App Nexus API

## Resource
To start using the API using the SDK, first create an AppNexus Resouce:
```
    appnexus = AppNexusResource(config)
```
The parameter `config` is a dictionary with configuration options:
```
config = {
    'username': "my@username",
    'password': "nunyobiz",
    'env': "dev",
    'token_file': "token"
    'memcache_host': "mycache.cache.amazonaws.com",
    'memcache_port': "11211",
}
```
`username` and `password` are credentials you got from AppNexus.
`env`: The environment defines whether or not to use the AppNexus production or test api. Any value other "prod" will use the test api
`token_file`: is the name of a file on disk in which to store auth tokens. This is mostly handy for local testing when your AppNexusResource has a short timespan, and you like to reuse your auth token between instantiations. If this parameter is not in your config, the Resource will re-auth when instantiated. Regardless of this variable, the Resource will reuse a token while instantiated, automatically re-authenticating every hour, or when authorization fails.
Both memcache parameters allow you to store a token in memcache. This is convenient for independent, short running / parallel processes, such as AWS Lambda functions

## Advertisers
To manage advertisers, the SDK uses Advertiser objects containing all advertiser specific data and functionality. You can use the Resource to create or fetch one or more advertisers,

### Creating an Advertiser
```
adv = appnexus.create_advertiser("Balihoo API Test", state="inactive")
print(json.dumps(adv.data, indent=4))
adv.data['code'] = 'SomeCode'
advid = adv.save()
```
The `create_advertiser` call takes as parameters any of the fields specified in the App Nexus Advertiser API Documentation, Any of these fields can also be accessed after creating the object, through the 'data' dictionary.
The `save` call stores the object remotely

### Fetching and updating an advertiser
```
adv = appnexus.advertiser_by_id(adv.data['id'])
if adv not is None:
    adv.data['code'] = 'MyCode'
    advid = adv.save()
```

### Deleting an advertiser
```
adv = appnexus.advertiser_by_id(adv.data['id'])
if adv not is None:
    adv.delete()
``` 
