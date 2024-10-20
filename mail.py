import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import secrets_parser, time
import threading
import traceback

GMAIL_PASSWORD=secrets_parser.parse("variables.txt")["GMAIL_PASSWORD"]

mail_queue=[]
queue_lock=threading.Lock()

smtp_server = "smtp.gmail.com"
smtp_port = 587
smtp_user = "exun@dpsrkp.net"
smtp_password = GMAIL_PASSWORD
server = None

def internal_mail(to, subject, html):
    msg = MIMEMultipart()
    msg['From'] = "Exun Clan <exun@dpsrkp.net>"
    msg['To'] = to
    msg['Subject'] = subject
    msg.attach(MIMEText(html, 'html'))
    try:
        server.sendmail(smtp_user, to, msg.as_string())
        return True
    except Exception as e:
        traceback.print_exc()
        return False

def mail_request(to, subject, html, callback=lambda request:None):
    queue_lock.acquire()
    mail_queue.append({"to":to, "subject":subject, "html":html, "callback":callback})
    queue_lock.release()

def mail_thread():
    global mail_queue
    global server
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(smtp_user, smtp_password)
    while True:
        while len(mail_queue)==0:
            time.sleep(0.1)
        queue_lock.acquire()
        mail=mail_queue[0]
        mail_queue=mail_queue[1:]
        queue_lock.release()
        if internal_mail(mail["to"], mail["subject"], mail["html"]):
            mail["callback"](mail)

threading.Thread(target=mail_thread).start()
