import re

mails=open("mails.txt").read().split("\n")
sorted_mails=set()

def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    if re.match(pattern, email):
        return True
    return False

def clean(x):
    return x.strip(" ,\t\n\r\"'-.").replace(" ", "").replace("\t", "").replace("\r", "").replace("-", "")
for x in mails:
    x=clean(x)
    inner_mails=x.split(",")
    for y in [clean(x) for x in inner_mails if clean(x)!="" and is_valid_email(x)]:
        sorted_mails.add(y.lower())
open("out_mails.txt", "w").write("\n".join(sorted_mails))
