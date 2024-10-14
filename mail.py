import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart, MIMEImage
import secrets_parser, time
import threading

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
    with open("public/mail/pfp.jpeg", "rb") as img_file:
        img = MIMEImage(img_file.read())
        img.add_header('Content-ID', '<profile_picture>')
        msg.attach(img)
    try:
        server.sendmail(smtp_user, to, msg.as_string())
        return True
    except Exception as e:
        return False

def mail_request(to, subject, html):
    queue_lock.acquire()
    mail_queue.append({"to":to, "subject":subject, "html":html})
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
        internal_mail(mail["to"], mail["subject"], mail["html"])

threading.Thread(target=mail_thread).start()