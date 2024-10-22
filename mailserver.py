import flask, mail as gmail, secrets_parser

SALT=secrets_parser.parse("variables.txt")["SALT"]

app=flask.Flask(__name__)

@app.get("/mail")
def mail():
    args=dict(flask.request.args)
    if args["salt"]==SALT:
        otp_render=open("components/mail/mail.html").read()
        key=args["key"]
        for x in range(0, 6):
            otp_render=otp_render.replace(f"{{digit{x+1}}}", key[x])
        gmail.mail_request(args["to"], args["subject"], otp_render)
        return "true"
    return "false"
