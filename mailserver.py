import flask, mail as gmail, secrets_parser

SALT=secrets_parser.parse("variables.txt")["SALT"]

app=flask.Flask(__name__)

@app.get("/mail")
def mail():
    args=dict(flask.request.args)
    if args["salt"]==SALT:
        gmail.mail_request(args["to"], args["subject"], args["html"])
        return "true"
    return "false"
