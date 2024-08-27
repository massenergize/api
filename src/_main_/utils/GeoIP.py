import geoip2.database
# import geoip2.webservice
import socket
from user_agents import parse
from _main_.settings import RUN_SERVER_LOCALLY
from _main_.utils.massenergize_logger import log

def ip_valid(ip):

    try:
      socket.inet_aton(ip)
      return True
    except socket.error:
      return False


class GeoIP:
  def __init__(self):
    try:
      dbFile = './_main_/utils/GeoLite2-City/GeoLite2-City.mmdb'
      self.reader = geoip2.database.Reader(dbFile)

    except Exception as e:
      # presumably file not found, in the case of running locally
      if not RUN_SERVER_LOCALLY:
        log.exception(e)

      self.reader = None  # open in first call to GetGeo to avoid crashing developers running locally: geoip2.database.Reader('_main_/utils/GeoLite2-City/GeoLite2-City.mmdb')

  def getBrowser(self, request):
    ua_string = request.META.get('HTTP_USER_AGENT')
    if not ua_string:   # as in unit testing
      return None

    # iPhone's user agent string
    #ua_string = 'Mozilla/5.0 (iPhone; CPU iPhone OS 5_1 like Mac OS X) AppleWebKit/534.46 (KHTML, like Gecko) Version/5.1 Mobile/9B179 Safari/7534.48.3'
    user_agent = parse(ua_string)
    #print(user_agent)

    client = {}
    # Accessing user agent's browser attributes
    #user_agent.browser  # returns Browser(family=u'Mobile Safari', version=(5, 1), version_string='5.1')
    client["browser"] = user_agent.browser.family  # returns 'Mobile Safari'
    #user_agent.browser.version  # returns (5, 1)
    client["browser_version"] = user_agent.browser.version_string   # returns '5.1'

    # Accessing user agent's operating system properties
    #user_agent.os  # returns OperatingSystem(family=u'iOS', version=(5, 1), version_string='5.1')
    client["os"] = user_agent.os.family  # returns 'iOS'
    #user_agent.os.version  # returns (5, 1)
    client["os_version"] = user_agent.os.version_string  # returns '5.1'

    # Accessing user agent's device properties
    #user_agent.device  # returns Device(family=u'iPhone', brand=u'Apple', model=u'iPhone')
    #user_agent.device.family  # returns 'iPhone'
    client["device"] = user_agent.device.brand # returns 'Apple'
    client["model"] = user_agent.device.model # returns 'iPhone'

    # Viewing a pretty string version
    # returns "iPhone / iOS 5.1 / Mobile Safari 5.1"
    return client

  def getIP(self,request):

    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')

    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')

    if not ip_valid(ip):
      print("GeoIP: IP address is NOT valid")
      return None

    return ip

  def getGeo(self, ip):

    try:

      if not self.reader:
        return None

      response = self.reader.city(ip)

      geo = {}
      # for the full name, otherwise country.iso_code
      geo["country"] = response.country.name
      # again, for the full name, otherwise most_specific.iso_code
      geo["state"] = response.subdivisions.most_specific.name

      geo["city"] = response.city.name
      geo["zipcode"] = response.postal.code
      geo["latitude"] = response.location.latitude
      geo["longitude"] = response.location.longitude

      return geo

    #self.reader.close()
    except Exception as e:
      # print(e)
      return e
