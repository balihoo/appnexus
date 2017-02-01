import requests
from requests.compat import urljoin, quote_plus
import contextlib
from time import time
import json
import logging
import os

import config

class DataException(Exception):
    pass

class AuthException(Exception):
    pass

class ApiException(Exception):
    pass

class NotFoundException(Exception):
    pass

class AppNexusResource(object):
    def __init__(self):
        self._client = AppNexusClient()

    def _paginator(self, term, collection_name, cls):
        """ returns a generator that fetches elements as needed """
        res = self._client.get(term)
        if res["status"] == "OK":
            for item in res[collection_name]:
                yield cls(client=self._client, data=item)
            thusfar = res["start_element"] + res["num_elements"]
            separator = '&' if '?' in term else '?'
            while res["count"] > thusfar:
                res = self._client.get('{}{}start_element={}'.format(term, separator, thusfar))
                if res["status"] != "OK":
                    return
                for item in res[collection_name]:
                    yield cls(client=self._client, data=item)
                thusfar = res["start_element"] + res["num_elements"]

    def create_advertiser(self, name, **kwargs):
        """ create a new advertiser """
        data = { 'name': name }
        data.update(kwargs)
        return Advertiser(self._client, data=data)

    def advertisers(self):
        """ return all advertisers """
        return self._paginator('advertiser', 'advertisers', Advertiser)

    def advertisers_by_ids(self, advertiser_ids):
        """ return multiple advertisers by id """
        term = 'advertiser?id={}'.format(','.join(advertiser_ids))
        return self._paginator(term, 'advertisers', Advertiser)

    def advertiser_by_id(self, advertiser_id):
        """ return a specific advertiser """
        a_id = quote_plus(str(advertiser_id))
        try:
            res = self._client.get('advertiser?id={}'.format(a_id))
            return Advertiser(client=self._client, data=res["advertiser"])
        except NotFoundException:
            return None

    def advertiser_by_name(self, name):
        """ return the first advertiser with this exact name"""
        term = 'advertiser?name={}'.format(quote_plus(name))
        it = self._paginator(term, 'advertisers', Advertiser)
        return next(it, None)

class Advertiser(object):
    def __init__(self, client, data):
        self._client = client
        self.data = data

    def save(self):
        """ creates or updates the advertiser remotely """
        payload = { 'advertiser': self.data }
        if self.data.get('id') is None:
            #new
            res = self._client.post('advertiser', payload)
            self.data['id'] = res['id']
        else:
            #update
            self._client.put('advertiser?id={}'.format(self.data['id']), payload)
        return True

    def delete(self):
        """ deletes the advertiser remotely.
        Saving it after this will recreate it with a new id
        """
        if not self.data.get('id') is None:
            res = self._client.delete('advertiser?id={}'.format(self.data['id']))
            print(json.dumps(res, indent=4))
            self.data['id'] = None
        else:
            raise DataException("unable to delete advertiser without an id")


class AppNexusClient(object):
    AUTH_TIMEOUT_SEC = 7200 #times out every 2h (7200 sec)
    TEST_URI = "http://api-test.appnexus.com"
    PROD_URI = "http://api.appnexus.com"
    CONTENT_HDR = {'Content-type': 'application/json; charset=UTF-8'}

    def __init__(self):
        """ Basic low level wrapper for the app nexus REST API """
        self.uri = self.PROD_URI if config.env == "prod" else self.TEST_URI
        self._token = None
        self._token_ts = 0
        self._token_file = None
        self.refresh_from_memcache = False
        #check if we have a filesystem stored token
        if hasattr(config, 'token_file'):
            self._token_file = config.token_file
            if os.path.exists(self._token_file):
                self._token_ts = os.path.getmtime(self._token_file)
                with open(self._token_file) as f:
                    self._token = f.read().strip()
        #check if we have a memcache stored token
        elif hasattr(config, 'memcache_host'):
            self.refresh_from_memcache = True
            import memcache
            self.mcache = memcache.Client([config.memcache_host, config.memcache_port])

    def __error_checked(reqf):
        """ decorator to check for AUTH, HTTP or API error response. """
        tried = False
        def checked_reqf(self, *args, **kwargs):
            r = reqf(self, *args, **kwargs)
            res = r.json().get('response', {})
            if res.get('status') == "OK":
                return res
            if res.get('error_id') == "NOAUTH":
                if not tried:
                    self._refresh_token()
                    return checked_reqf()
                logging.error("AUTH FAILED TWICE")
            r.raise_for_status()
            errid = res.get('error_id')
            error = res.get('error')
            errdesc = res.get('error_description')
            if errid == "SYNTAX" and error == "resource not found":
                raise NotFoundException(r.url)
            raise ApiException("{}: {} {} ({})".format(errid, error, errdesc, r.url))
        return checked_reqf

    def token(self):
        """ get a valid auth token to use in api calls """
        #preemtively reauth at 80% of expiration time
        if time() - self._token_ts > (0.8 * self.AUTH_TIMEOUT_SEC):
            logging.info("re-auth due to time")
            self._refresh_token()
        return self._token

    def _apiuri(self, term):
        """ prepend the base uri to a term """
        return urljoin(self.uri, term)

    def _apihdr(self, hdr=None):
        """ add auth and content type to any custom headers """
        headers = hdr.copy() if hdr else {}
        headers.update(self.CONTENT_HDR)
        headers.update({'Authorization': self.token()})
        return headers

    def _refresh_token(self):
        """ gets a token from memcache, if so configured, or goes out to get it from
        the appnexus auth api. Note that we do NOT attempt to store the token in memcache
        here; the whole point of memcache is to avoid concurrent auth calls: if memcache is
        used, there ought to be a separate process to populate it
        """
        if self.refresh_from_memcache:
            key="appnexus{}".format(config.env)
            token = self.mcache.get(key)
            if not token:
                raise AuthException("Unable to get token from cache with {}".format(key))
            self.token = token
        else:
            data = json.dumps({'auth': {'username':config.username, 'password':config.password}})
            uri = self._apiuri('auth')
            res = requests.post(uri, data=data, headers=self.CONTENT_HDR).json()['response']
            if res.get('status') == "OK":
                self._token = res['token']
                self._token_ts = time()
                logging.info("new token: [{}] @ {}".format(self._token, self._token_ts))
                if self._token_file:
                    with open(self._token_file, 'w') as f:
                        f.write(self._token)
            else:
                raise AuthException("Unable to refresh token: {}".format(json.dumps(res, indent=4)))

    @__error_checked
    def get(self, what, headers=None):
        """ basic api get request """
        uri = self._apiuri(what)
        hdrs = self._apihdr(headers)
        logging.info("GET {}".format(uri))
        return requests.get(uri, headers=hdrs)

    @__error_checked
    def post(self, what, data, headers=None):
        """ basic api post request """
        uri = self._apiuri(what)
        headers = self._apihdr(headers)
        data = json.dumps(data)
        logging.info("POST {}: {}".format(uri, data))
        return requests.post(uri, data=data, headers=headers)

    @__error_checked
    def put(self, what, data, headers=None):
        """ basic api put request """
        uri = self._apiuri(what)
        headers = self._apihdr(headers)
        data = json.dumps(data)
        logging.info("PUT {}: {}".format(uri, data))
        return requests.put(uri, data=data, headers=headers)

    @__error_checked
    def delete(self, what, headers=None):
        """ basic api delete request """
        uri = self._apiuri(what)
        headers = self._apihdr(headers)
        logging.info("DELETE {}".format(uri))
        return requests.delete(uri, headers=headers)
