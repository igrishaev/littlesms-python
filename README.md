# API client class for LittleSMS.ru service

## Sample usage:

    import littlesms

    # Class init.
    api = littlesms.Api("user", "API_key")

    # Balance check.
    print api.balance()
    >>> {u'status': u'success', u'balance': 0.5}

    # Send sms.
    print api.send(u"Hello, World!", "7xxxxxxxxxx")
    >>> {u'count': 1, u'status': u'success', u'recipients': [u'7xxxxxxxxxx'], u'price': 0.5, u'parts': 1, u'test': 0, u'balance': 0.5, u'messages_id': [u'xxxxxx']}

    # Send sms to multiple recipients with custom sender name.
    print api.send(u"Hello, World!", ["7xxxxxxxxx1", "7xxxxxxxxx2", "7xxxxxxxxx3"], sender="Anonym")
    >>> {u'count': 1, u'status': u'success', u'recipients': [u'7xxxxxxxxx1', u'7xxxxxxxxx2', u'7xxxxxxxxx3'], u'price': 0.5, u'parts': 1, u'test': 0, u'balance': 0.5, u'messages_id': [u'xxxxxx1', u'xxxxxx2', u'xxxxxx3']}

    # Using behind proxy.
    PROXY = {
        "proxy": "172.27.86.8",
        "port": 3128,
        "user": "ivan",
        "passw": "secret"
    }
    opener = littlesms.curl_opener(**PROXY)
    api = littlesms.Api("user", "API_key", opener=opener)

    # Using App Engine.
    opener = littlesms.gae_opener()
    api = littlesms.Api("user", "API_key", opener=opener)

    # Exception example.
    try:
        print api.send(u"Hello, World!", "7xxxxxxxxxx", sender="TooLongSender!!!111")
    except littlesms.ApiError, e:
        print e
        >>> Error 7: incorrect sender