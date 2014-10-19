from google.appengine.ext import ndb

class Reference(ndb.Model):
    name = ndb.StringProperty(required = True)
    reference = ndb.StringProperty(required = True)

class Result(ndb.Model):
    name = ndb.StringProperty(required = True)
    address = ndb.StringProperty(required = True)
    phone = ndb.StringProperty(required = True)
    website = ndb.StringProperty(required = True)
    plusurl = ndb.StringProperty(required = True)

AUTH_KEY1 = 'AIzaSyABvOHW6S0n-ydSegFas3FEC6atHvdXaFg'
AUTH_KEY2 = 'AIzaSyDupXdbRCd0_gY-UhOtjXmie4GHzQbGbjw'
AUTH_KEY3 = 'AIzaSyAhowESt6YRBGddLfAbnn3Cfc2dn1tVXKU'
AUTH_KEYS = [AUTH_KEY1, AUTH_KEY2, AUTH_KEY3]

# themes:
# lists of keywords
themes = {
    'hipster': ['vibe', 'atmosphere'],
    'family': ['kid-friendly', 'family-friendly', 'kids', 'fun'],
    'music': ['venue', 'concert', 'band', 'orchestra', 'music'],
    'historic': ['museum', 'castle', 'landmark', 'tour']
}
