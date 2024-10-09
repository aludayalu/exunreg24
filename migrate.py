import litedb, json
import hashlib

events=litedb.get_conn("events")

data=json.loads(open("data/events.json").read())

for event in data["events"]:
    events.set(hashlib.sha256(event.encode()).hexdigest()[:6], data["default"] | {"image":data["events"][event],
        "name":event,
        "descriptions":{
            "long":data["descriptions"][event]["long"],
            "short":data["descriptions"][event]["short"]},
        "open_to_all":data["open_to_all"][event],
        "eligibility":data["eligibility"][event],
        "participants":data["participants"][event],
        "mode":data["mode"][event],
        "independant_registration": data["individual"][event],
        "points":data["points"][event]
    })