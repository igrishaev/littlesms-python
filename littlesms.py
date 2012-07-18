"""
API client class for LittleSMS.ru service.

Ivan Grishaev, 2011.
ivan@grishaev.me
"""

from hashlib import md5, sha1
import urllib

# Find JSON lib
try:
    import json # Python >= 2.6
except ImportError:
    try:
        import simplejson as json # Python <= 2.5
    except ImportError:
        try:
            from django.utils import simplejson as json # Django
        except ImportError:
            raise ImportError("JSON lib not found.")


API_URL = "%s://littlesms.ru/api/%s"


def urllib_opener():
    def opener(url):
        return urllib.urlopen(url).read()
    return opener


def curl_opener(proxy=None, port=None, user=None, passw=None):
    """cURL opener fabric."""
    import curl
    c = curl.Curl()
    c.set_option(curl.pycurl.HTTPPROXYTUNNEL, True)
    c.set_option(curl.pycurl.SSL_VERIFYPEER, False)

    if proxy:
        c.set_option(curl.pycurl.PROXY, proxy)
    if port:
        c.set_option(curl.pycurl.PROXYPORT, port)
    if user and passw:
        c.set_option(curl.pycurl.PROXYUSERPWD, "%s:%s" % (user, passw))

    def opener(url):
        return c.get(url)
    return opener


def gae_opener():
    """Google APP Engine opener fabric."""
    from google.appengine.api import urlfetch

    def opener(url):
        return urlfetch.fetch(url).content
    return opener


class ApiError(Exception):
    """Service exception class."""
    def __init__(self, code, message):
        self.code = code
        self.message = message

    def __str__(self):
        return u"Error %d: %s" % (self.code, self.message)


class Api(object):
    """Main API class.

    Params:
        user: user name;
        key: secret API key;
        secure: use https chema instead http;
        opener: callable object for URL retrieving;
        logger: logger for request/response logging.

    """
    def __init__(self, user, key, secure=True, opener=None, logger=None):
        self.user = user
        self.key = key
        self.secure = secure
        self.logger = logger
        self.opener = opener or urllib_opener()

    def balance(self):
        """Get current balance."""
        path = "user/balance"
        return self._request(path)

    def send(self, message, recipients, sender=None, test=False):
        """Send message.

        See http://littlesms.ru/doc-messages#message-send

        Params:
            message: sms text, str or unicode;
            recipients: phone number or list/tuple of phone numbers;
            sender: sender name, 11 symbols max;
            test: testing flag.

        Sample response:
            {
                u'count': 1,
                u'status': u'success',
                u'recipients': [u'7xxxxxxxxxx'],
                u'price': 0.5,
                u'parts': 1,
                u'test': 0,
                u'balance': 0.5,
                u'messages_id': [u'236234623']
            }
        """
        path = "message/send"
        params = dict(message=message, recipients=recipients)
        if sender is not None:
            params.update(sender=sender)
        if test:
            params.update(test="1")
        return self._request(path, **params)

    def status(self, ids):
        """Get message status by id.

        See http://littlesms.ru/doc-messages#message-status

        Params:
            ids: message id or list/tuple of ids.
        """
        path = "message/status"
        params = dict(messages_id=ids)
        return self._request(path, **params)

    def price(self, message, recipients):
        """Get pricing info.

        See http://littlesms.ru/doc-messages#message-price

        Params:
            message: sms text, str or unicode;
            recipients: phone number or list/tuple of phone numbers.
        """
        path = "message/price"
        params = dict(message=message, recipients=recipients)
        return self._request(path, **params)

    def history(self, **kwargs):
        """Get history info.

        See http://littlesms.ru/doc-messages#message-history

        Shows full info without filters.

        Kwargs params (filters):
            history_id: history id;
            recipient: phone number;
            sender: sender name;
            status: message status;
            date_from: low date limit;
            date_to: hi date limit;
            id: message id.
        """
        path = "message/history"
        params = kwargs.copy()
        return self._request(path, **params)

    def _sign(self, **params):
        """Calculates signature."""
        keys = params.keys()
        keys.sort()
        values = [params[key] for key in keys]
        values.insert(0, self.user)
        values.append(self.key)

        return md5(sha1("".join(values)).hexdigest()).hexdigest()

    def _request(self, path, **params):
        """Make API request.

        Returns parsed JSON or raise ApiError.
        """
        arguments = params.copy()
        for k, v in arguments.iteritems():
            if isinstance(v, unicode):
                arguments[k] = v.encode("utf8")
            if isinstance(v, (int, long)):
                arguments[k] = str(v)
            if isinstance(v, (list, tuple)):
                arguments[k] = ",".join(map(str, v))

        sign = self._sign(**arguments)
        query = arguments.copy()
        query.update(sign=sign, user=self.user)
        qs = urllib.urlencode(query)

        scheme = "https" if self.secure else "http"
        base_url = API_URL % (scheme, path)

        url = base_url + "?" + qs
        if self.logger:
            self.logger.info(url)

        response = self.opener(url)
        if self.logger:
            self.logger.info(response)

        data = json.loads(response)

        if data["status"] == u"error":
            raise ApiError(data["error"], data["message"])
        else:
            return data
