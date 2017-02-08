
def paginator(client, term, collection_name, cls):
    """ returns a generator that fetches elements as needed """
    res = client.get(term)
    if res["status"] == "OK":
        for item in res[collection_name]:
            yield cls(client=client, data=item)
        thusfar = res["start_element"] + res["num_elements"]
        separator = '&' if '?' in term else '?'
        while res["count"] > thusfar:
            res = client.get('{}{}start_element={}'.format(term, separator, thusfar))
            for item in res[collection_name]:
                yield cls(client=client, data=item)
            thusfar = res["start_element"] + res["num_elements"]
