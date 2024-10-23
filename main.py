from flask import request, Response
from mailserver import SALT
from monster import render, Flask, escapeString
import sys, json
import hashlib, base64
import resend, secrets_parser
import litedb, re
import requests
from flask_compress import Compress

accounts=litedb.get_conn("accounts")
events=litedb.get_conn("events")

app = Flask(__name__)

app.config['COMPRESS_LEVEL'] = 9
app.config['COMPRESS_MIN_SIZE'] = 500

Compress(app)

events_order=list(json.loads(open("data/events.json").read())["events"].keys())

DB_IP=secrets_parser.parse("variables.txt")["DB_IP"]

def order_events(events):
    sorted_events=[None]*len(events)
    for event_id in events:
        event_name=events[event_id]["name"]
        sorted_events[events_order.index(event_name)]=[event_id, events[event_id]]
    return dict(sorted_events)

def redirect(path):
    resp = Response(f"""<script>window.location.href="{path}"</script>""")
    resp.headers["Access-Control-Allow-Origin"] = "*"
    return resp

def make_response(data, mimetype=None, status=None):
    if type(data) in [str,int, float, bool, list, dict]:
        data = json.dumps(data)
    resp = Response(data, mimetype=mimetype, status=status)
    resp.headers["Access-Control-Allow-Origin"] = "*"
    return resp

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

daisyui = "<script>"+ open("public/pako.js").read()+ "</script>"+ """<script>
    function decompressGzippedString(base64String) {
        try {
            const binaryString = atob(base64String);
            const len = binaryString.length;
            const bytes = new Uint8Array(len);
            for (let i = 0; i < len; i++) {
                bytes[i] = binaryString.charCodeAt(i);
            }
            const decompressedData = pako.inflate(bytes, { to: 'string' });
            return decompressedData;
        } catch (err) {
            console.error('An error occurred while decompressing the string:', err);
            return null;
        }
    }
    """+ f"""
    var daisycss="{open("public/daisyui.b64").read()}";
    var style=document.createElement("style");
    style.textContent=decompressGzippedString(daisycss);
    document.head.appendChild(style);
    </script>
    """

tailwind = "<script>eval(atob(`" + base64.b64encode(open("public/tailwind.js").read().encode()).decode() + "`))</script>"

def auth_token(a):
    if type(a) == str:
        a = a.encode()+salt.encode()
    return hashlib.sha256(a).hexdigest()

def otp(a):
    hex_dig = auth_token(a)
    array = int(hex_dig[-6:], 16) % (10 ** 6)
    otp_str = f"{array:06d}"
    return [int(digit) for digit in otp_str]

def authd():
    try:
        if "auth_token" not in request.cookies or "email" not in request.cookies:
            return False
        if request.cookies["auth_token"]==auth_token(request.cookies["email"]):
            return True
        return False
    except:
        return False

def account_details():
    account=accounts.get(request.cookies["email"])
    return account

@app.get("/")
def home():
    return render("index", locals() | globals())

@app.get("/login")
def login():
    if not authd():
        return render("login/login", locals() | globals())
    account=account_details()
    if account==None:
        return redirect("/complete_signup")
    return render("login/login", locals() | globals())

@app.get("/email")
def email_send():
    try:
        args=dict(request.args)
        key="".join([str(x) for x in otp(args["email"])])
        requests.get("http://"+DB_IP+":5555/mail?salt="+SALT+"&to="+escapeString(args["email"])+"&subject="+escapeString("Exun Registration Authentication OTP - "+key)+"&key="+key)
    except Exception as e:

        return make_response(False)
    return make_response(True)

@app.get("/submit_otp")
def submit_otp():
    args=dict(request.args)
    if "".join([str(x) for x in otp(args["email"])])==args["otp"]:
        resp=make_response(True)
        resp.set_cookie("email", args["email"])
        resp.set_cookie("auth_token", auth_token(args["email"]))
        return resp
    else:
        resp=make_response(False)
        resp.delete_cookie("email")
        resp.delete_cookie("auth_cookie")
        return resp

@app.get("/events")
def events_page():
    if authd() and account_details()==None:
        return redirect("/complete_signup")
    return render("events/events_page", locals() | globals())

@app.get("/complete_signup")
def complete_signup():
    if not authd():
        return redirect("/login")
    account=account_details()
    if account!=None:
        return redirect("/")
    return render("signup/complete", locals() | globals())

@app.get("/api/complete_signup")
def api_for_completing_signup():
    if not authd():
        return make_response(False)
    account=account_details()
    if account!=None:
        return make_response(False)
    args=dict(request.args)
    email=request.cookies["email"]
    fullname=args["fullname"].strip().upper()
    phone_number=args["phone_number"].strip()
    principals_email=args["principals_email"].strip()
    individual=args["individual"].strip()
    for x in [fullname, phone_number, principals_email, individual]:
        if x=="":
            return make_response(False)
    out={"name":fullname, "phone_number":phone_number, "principals_email":principals_email, "registrations":{}, "email":email, "individual":individual}
    for x in ["institution_name", "address", "principals_name"]:
        if args[x].strip()=="":
            return make_response(False)
        out[x]=args[x].upper()
    accounts.set(email, out)
    return make_response(True)

def name_hash(x):
    return hashlib.sha256((x.replace(" ", "").replace("\t", "").lower()).encode()).hexdigest()

@app.get("/event")
def event_page():
    if authd() and account_details()==None:
        return redirect("/complete_signup")
    if authd():
        account=account_details()
    else:
        account={"registrations":{}}
    args=dict(request.args)
    try:
        id=args["id"]
    except:
        return redirect("/events")
    event=events.get(id)
    ignore=[]
    participant_details={}
    if account!=None:
        for x in account["registrations"]:
            for y in account["registrations"][x]:
                if y["email"] in participant_details and name_hash(participant_details[y["email"]]["name"])!=name_hash(y["name"]):
                    ignore.append(y["email"])
                    del participant_details[y["email"]]
                    continue
                if y["email"] not in ignore:
                    participant_details[y["email"]]=y
    if event==None:
        return redirect("/events")
    return render("events/event", locals() | globals())

@app.get("/admin")
def admin():
    if not authd():
        return redirect("/login")
    account=account_details()
    if account==None:
        return redirect("/complete_signup")
    if request.cookies["email"]=="exun@dpsrkp.net":
        return render("admin", locals() | globals())
    else:
        return redirect("/")


def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if re.match(pattern, email):
        return True
    return False

@app.post("/submit_registrations")
def submit_registrations():
    data = request.get_json()
    if not authd():
        return redirect("/login")
    account=account_details()
    if account==None:
        return redirect("/complete_signup")
    event=events.get(data["id"])
    if not event['independant_registration'] and account!=None and "individual" in account and account["individual"]=='true':
        return make_response(False)
    for x in data["data"]:
        x["name"]=x["name"].upper()
        if not is_valid_email(x["email"]):
            return make_response(False)
        x["class"]=int(x["class"])
        if not (event["eligibility"][1]>=x["class"] and x["class"]>=event["eligibility"][0]):
            return make_response(False)
        if len(str(x["phone"]))!=10:
            return make_response(False)
    account["registrations"][data["id"]]=data["data"]
    accounts.set(request.cookies["email"], account)
    return make_response(True)

@app.get("/brochure")
def brochure():
    return render("brochure", locals() | globals())

@app.get("/invite")
def invite_redirect():
    return redirect("/brochure")

@app.get("/summary")
def summary():
    if not authd():
        return redirect("/login")
    account=account_details()
    if account==None:
        return redirect("/complete_signup")
    registrations=account["registrations"]
    return render("summary/summary", locals() | globals())
