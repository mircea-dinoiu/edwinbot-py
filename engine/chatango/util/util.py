# Python imports
import re
import urllib.parse
import urllib.request
import random

# Project imports
from engine.chatango.common.User import *
from util.util import strip_html


# Get user if exists
def get_user(uid):
    user = USERS.get(uid.lower())
    if not user:
        user = NewUser(uid)
    return user


# PM Auth
def get_auth(name, password):
    """
    Request an auid using name and password.

    @type name: str
    @param name: name
    @type password: str
    @param password: password

    @rtype: str
    @return: auid
    """
    auth_re = re.compile(r"auth\.chatango\.com ?= ?([^;]*)", re.IGNORECASE)

    data = urllib.parse.urlencode({
        "user_id": name,
        "password": password,
        "storecookie": "on",
        "checkerrors": "yes"
    }).encode()
    try:
        resp = urllib.request.urlopen("http://chatango.com/login", data)
        headers = resp.headers
    except Exception:
        return None
    for header, value in headers.items():
        if header.lower() == "set-cookie":
            m = auth_re.search(value)
            if m:
                auth = m.group(1)
                if auth == "":
                    return None
                return auth
    return None


# Anon id
def get_anon_id(n, ssid):
    """Gets the anon's id."""
    if n is None:
        n = "5504"
    try:
        return "".join(list(
            map(
                lambda x: str(x[0] + x[1])[-1],
                list(
                    zip(
                        list(map(lambda x: int(x), n)),
                        list(map(lambda x: int(x), ssid[4:]))
                    )
                )
            )
        ))
    except ValueError:
        return "NNNN"


def parse_font(f):
    """Parses the contents of a f tag and returns color, face and size."""
    #' xSZCOL="FONT"'
    try:
        #TODO: remove quick hack
        size_color, font_face = f.split("=", 1)
        size_color = size_color.strip()
        size = int(size_color[1:3])
        col = size_color[3:6]
        if col == "":
            col = None
        face = f.split("\"", 2)[1]
        return col, face, size
    except:
        return None, None, None


def parse_name_color(n):
    """This just returns its argument, should return the name color."""
    #probably is already the name
    return n


def get_server(group):
    """
    Get the server host for a certain room.

    @type group: str
    @param group: room name

    @rtype: str
    @return: the server's hostname
    """

    try:
        group = group.replace("_", "q")
        group = group.replace("-", "q")
        fnv = float(int(group[0:min(5, len(group))], 36))
        lnv = group[6: (6 + min(3, len(group) - 5))]
        if lnv:
            lnv = float(int(lnv, 36))
            if lnv <= 1000:
                lnv = 1000
        else:
            lnv = 1000
        num = (fnv % lnv) / lnv
        max_num = sum(map(lambda x: x[1], TS_WEIGHTS))
        cum_freq = 0
        sn = 0
        for wgt in TS_WEIGHTS:
            cum_freq += float(wgt[1]) / max_num
            if num <= cum_freq:
                sn = int(wgt[0])
                break
    except:
        sn = 36
    return "s" + str(sn) + ".chatango.com"


def gen_uid():
    return str(random.randrange(10 ** 15, 10 ** 16))


def clean_message(msg):
    """
    Clean a message and return the message, n tag and f tag.

    @type msg: str
    @param msg: the message

    @rtype: str, str, str
    @return: cleaned message, n tag contents, f tag contents
    """
    n = re.search("<n(.*?)/>", msg)
    if n:
        n = n.group(1)
    f = re.search("<f(.*?)>", msg)
    if f:
        f = f.group(1)
    msg = re.sub("<n.*?/>", "", msg)
    msg = re.sub("<f.*?>", "", msg)
    msg = msg.replace("</p><p>", "\n")
    msg = strip_html(msg)
    msg = msg.replace("\n", "<br>")
    msg = msg.replace("&lt;", "<")
    msg = msg.replace("&gt;", ">")
    msg = msg.replace("&quot;", "\"")
    msg = msg.replace("&apos;", "'")
    msg = msg.replace("&amp;", "&")
    return msg, n, f


def username_is_valid(username):
    """
    Checks if a username is valid according to Chatango restrictions

    @type username: str
    @param username: username to check

    @rtype: bool
    @return: True if the username is valid, False otherwise
    """
    valid = False
    to_check = username

    if isinstance(to_check, str):
        to_check = to_check.lower().strip()

        if to_check:
            good = re.sub(r'[^a-z0-9#!]', '', to_check)

            if good == to_check and len(good) <= 20:
                valid = True

    return valid


def room_name_is_valid(room_name):
    """
    Checks if a room name is valid according to Chatango restrictions

    @type room_name: str
    @param room_name: room name to check

    @rtype: bool
    @return: True if the room name is valid, False otherwise
    """
    valid = False
    to_check = room_name

    if isinstance(to_check, str):
        to_check = to_check.lower().strip()

        if to_check:
            good = re.sub(r'[^a-z0-9-]', '', to_check)

            if good == to_check and len(good) <= 20:
                valid = True

    return valid