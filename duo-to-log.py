#!/usr/bin/python2

""" MODULE IMPORTS """

from __future__ import print_function
from datetime import datetime
import ConfigParser
import duo_client
import optparse
import sys
import time

""" COMMAND LINE OPTION PARSING """
usage = "USAGE: %prog [options] arg1 arg2 .. argN"
parser = optparse.OptionParser(usage=usage)
parser.add_option('-I', action="store", help="Duo Integration Key", type="string")
parser.add_option('-S', action="store", help="Duo Secret Key", type="string")
parser.add_option('-H', action="store", help="Duo API Host", type="string")
parser.add_option('-L', action="store", help="External Syslog Server IP", type="string")
parser.add_option('-c', action="store", default="duo.conf", help="Use custom conf file [default: %default]", type="string")
parser.add_option('-M', action="store", default="15", help="Minutes to query [default: %default Minutes(s)]", type="int")
options, args = parser.parse_args()

""" ARG COUNT CHECK """
#if len(sys.argv[1:]) == 0:
#    parser.print_help()
#    sys.exit(0)

""" Connect and get duo logs """

def get_logs(proxy=None, proxy_port=None):

    admin_api = duo_client.Admin(
        ikey=INTEGRATION_KEY,
        skey=SECRET_KEY,
        host=API_HOST)

    if proxy and proxy_port:
        admin_api.set_proxy(proxy, proxy_port)

    # Check to see if DELTA is 0. If so, retrieve all logs.
    if mintime == utc_date:
        admin_log = admin_api.get_administrator_log()
        auth_log = admin_api.get_authentication_log()
    else:
        admin_log = admin_api.get_administrator_log(mintime=mintime)
        auth_log = admin_api.get_authentication_log(mintime=mintime)

    """
    Print events in k=v pair.
    Not the most efficient way, but it give us the flexibility on the logger side
    """

    for event in admin_log:
        event['actionlabel'] = {
            'admin_login': "Admin Login",
            'admin_create': "Create Admin",
            'admin_update': "Update Admin",
            'admin_delete': "Delete Admin",
            'customer_update': "Update Customer",
            'group_create': "Create Group",
            'group_udpate': "Update Group",
            'group_delete': "Delete Group",
            'integration_create': "Create Integration",
            'integration_update': "Update Integration",
            'integration_delete': "Delete Integration",
            'phone_create': "Create Phone",
            'phone_update': "Update Phone",
            'phone_delete': "Delete Phone",
            'user_create': "Create User",
            'user_update': "Update User",
            'user_delete': "Delete User"}.get(
        event['action'], event['action'])

    fmtstr = '%(timestamp)s,' \
     'eventtype="%(eventtype)s", ' \
     'username="%(username)s", ' \
     'action="%(actionlabel)s"'
    if event['object']:
        fmtstr += ', object="%(object)s"'
    if event['description']:
        fmtstr += ', description="%(description)s"'

    print(fmtstr % event)


    for event in auth_log:
        event['access_device_os'] = str(event['access_device']['os']) + ' ' +str(event['access_device']['os_version'])
        fmtstr = (
            '%(timestamp)s,'
            'eventtype="%(eventtype)s", '
            'username="%(username)s", '
            'access_device_os="%(access_device_os)s", '
            'factor="%(factor)s", '
            'result="%(result)s", '
            'reason="%(reason)s", '
            'ip="%(ip)s", '
            'integration="%(integration)s", '
            'newenrollment="%(new_enrollment)s"'
        )
        print(fmtstr % event)

if __name__ == "__main__":
    try:
        config = ConfigParser.ConfigParser()
        config.read(options.c)

        INTEGRATION_KEY = config.get('duo', 'ikey')
        SECRET_KEY = config.get('duo', 'skey')
        API_HOST = config.get('duo', 'host')

        minutes_diff = options.M if options.M else config.getint('duo','delta')
        DELTA = (minutes_diff * 60)

        PROXY_ENABLE = config.getboolean('duo', 'proxy_enable')

        if PROXY_ENABLE:
            PROXY_SERVER = config.get('duo', 'PROXY_SERVER')
            PROXY_PORT = config.getint('duo', 'PROXY_PORT')


        date = datetime.utcnow()
        utc_date = calendar.timegm(date.utctimetuple())
        mintime = utc_date - DELTA


        if PROXY_ENABLE:
            get_logs(proxy=PROXY_SERVER, proxy_port=PROXY_PORT)
        else:
            get_logs()

    except Exception, e:
        with open('exceptions.log', 'a+') as exception_file:
            print(datetime.utcnow(), e, file=exception_file)

