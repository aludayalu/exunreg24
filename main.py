from flask import request, redirect, Response
from werkzeug.wrappers import response
from monster import render, tokeniser, parser, Flask
import sys, json
import jwt
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib, ssl

app = Flask(__name__)

# temp
registered = []
key = "zResKRyB9NX4tUn7yp/Hyg2V/7oxVMwzJzD5uGtPbbI="


def make_response(data, mimetype=None, status=None):
    if type(data) in [str, int, float, bool, list, dict]:
        data = json.dumps(data)
    resp = Response(data, mimetype=mimetype, status=status)
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Origin"] = "*"
    resp.headers["Access-Control-Allow-Credentials"] = "true"
    resp.headers["Access-Control-Allow-Methods"] = "GET,HEAD,OPTIONS,POST,PUT"
    resp.headers["Access-Control-Allow-Headers"] = (
        "Access-Control-Allow-Headers, Origin,Accept, X-Requested-With, Content-Type, Access-Control-Request-Method, Access-Control-Request-Headers"
    )
    return resp


def parse(path):
    env = {}
    lines = open(path).read().split("\n")
    for x in lines:
        x = x.strip()
        if "=" in x:
            env[x.split("=", 1)[0]] = json.loads(x.split("=", 1)[1])
    return env


password = parse("variables.txt")["password"]


def mail(to, subject, content):
    sender_email = "Exun Clan <exun@dpsrkp.net>"
    sender_password = password
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = to
    msg["Subject"] = subject
    msg.attach(MIMEText(content, "html"))
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login("exun@dpsrkp.net", sender_password)
        text = msg.as_string()
        server.sendmail(sender_email, to, text)
        print("Email sent successfully!")
    except Exception as e:
        print(f"Failed to send email: {e}")
    finally:
        server.quit()


daisyui = (
    "<script>"
    + open("public/pako.js").read()
    + "</script>"
    + """<script>
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
    """
    + f"""
    var daisycss="{open("public/daisyui.b64").read()}";
    var style=document.createElement("style");
    style.textContent=decompressGzippedString(daisycss);
    document.head.appendChild(style);
    </script>
    """
)

tailwind = "<script>" + open("public/tailwind.js").read() + "</script>"


@app.get("/")
def home():
    signals = open("public/signals.js").read()
    print(tokeniser(open("components/index.html").read()))
    print(parser(tokeniser(open("components/index.html").read())))
    return render("index", locals() | globals())


@app.get("/register")
def register():
    name = request.args.get("name")
    email = request.args.get("email")
    password = request.args.get("password")
    conf_password = request.args.get("confirmPassword")

    if password != conf_password:
        return "Password not same or sum"

    user = {"name": name, "email": email, "password": password}

    if not user in registered:
        registered.append(user)
        return name

    return "User already exists"


@app.get("/login")
def login():
    name = request.args.get("name")
    email = request.args.get("email")
    password = request.args.get("password")

    token = request.cookies.get("token")
    if token:
        return "User is already logged in"

    user = {"name": name, "email": email, "password": password}
    res = {}

    if user not in registered:
        return "User doesn't exists"

    for usr in registered:
        print(usr)
        if usr["name"] == user["name"]:
            res = usr

    if res["password"] != user["password"]:
        return "Password incorrect"

    # do jwt stuff
    token = jwt.encode(payload=user, key=key)
    resp = make_response("Logged in")
    resp.set_cookie("token", token, secure=True)

    return resp


@app.get("/auth")
def auth():
    token = request.cookies.get("token")
    if not token:
        return "User is logged out"

    user = jwt.decode(token, key=key, algorithms=["HS256"])

    res = {}

    for usr in registered:
        if usr["name"] == user["name"]:
            res = usr

    return res


@app.get("/logout")
def logout():
    resp = make_response("Logged out")
    resp.delete_cookie("token")
    return resp


app.run(host="0.0.0.0", port=int(sys.argv[1]))
