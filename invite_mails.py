import threading
from monster import render, Flask, escapeString
import sys, json
import hashlib, base64
import secrets_parser, mail, smtplib

emails=open("out_mails.txt").read().split("\n")
done=open("done.txt").read().split("\n")

def callback(mail):
    done.append(mail["to"])
    open("done.txt", "w").write("\n".join(done))

for email in emails:
    break
    mail.mail_request(f"{email}", "Exun 2024 Registration Invite", open("data/email_invite.html").read(), callback)

mail.mail_request("shreyansh.a.007@gmail.com", "Exun 2024 Registration Invite", open("data/email_invite.html").read(), callback)
