from monster import render, Flask, escapeString
import sys, json
import hashlib, base64
import resend, secrets_parser
import litedb, re
from flask_compress import Compress
import time

resend.api_key = secrets_parser.parse("variables.txt")["RESEND"]
salt = secrets_parser.parse("variables.txt")["SALT"]

def send_mail(to, subject, html, reply_to="exun@dpsrkp.net"):
    params = {
        "from": "Exun Clan <exun@exun.co>",
        "to": [to],
        "subject": subject,
        "html": html,
        "reply_to": reply_to
    }
    email = resend.Emails.send(params)
    return email

send_mail("mukesh.kumar@dpsrkp.net", "Exun 2024 Registration Invite - "+str(time.time()), open("data/email_invite.html").read())