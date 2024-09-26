from flask import request, redirect
from monster import render, tokeniser, parser, Flask
import sys, json

app = Flask(__name__)

daisyui="<script>"+open("public/pako.js").read()+"</script>"+"""<script>
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
    """+f"""
    var daisycss="{open("public/daisyui.b64").read()}";
    var style=document.createElement("style");
    style.textContent=decompressGzippedString(daisycss);
    document.head.appendChild(style);
    </script>
    """

tailwind="<script>"+open("public/tailwind.js").read()+"</script>"

@app.get("/")
def home():
    signals=open("public/signals.js").read()
    print(tokeniser(open("components/index.html").read()))
    print(parser(tokeniser(open("components/index.html").read())))
    return render("index", locals()|globals())

app.run(host="0.0.0.0", port=int(sys.argv[1]))