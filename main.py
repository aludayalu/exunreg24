from flask import request, redirect, Response
from werkzeug.wrappers import response
from monster import render, Flask
import sys, json

app = Flask(__name__)

def make_response(data, mimetype=None, status=None):
    if type(data) in [str, int, float, bool, list, dict]:
        data = json.dumps(data)
    resp = Response(data, mimetype=mimetype, status=status)
    resp.headers["Access-Control-Allow-Origin"] = "*"
    return resp


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
    return render("index", locals() | globals())


app.run(host="127.0.0.1", port=int(sys.argv[1]))
