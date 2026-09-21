SERVICES = ["Driveway Cleaning","Pressure Washing","Siding Restoration","Gutter Care"]

def classify(text):
    t=text.lower()
    groups={
      "handoff":["human","person","owner","representative","complaint","damage","injury","emergency"],
      "pricing":["price","cost","quote","estimate","how much"],
      "schedule":["schedule","appointment","book","available","availability"],
      "services":["service","offer","clean","washing","gutter","siding","driveway"],
      "area":["area","where","location","serve","detroit"],
      "photos":["photo","picture","image"],
      "greeting":["hello","hi","hey","good morning","good afternoon"]
    }
    for intent,words in groups.items():
        if any(w in t for w in words): return intent
    return "unknown"

def reply(text):
    intent=classify(text)
    replies={
      "handoff":"This needs a team member. I won't guess about complaints, damage, emergencies, or other sensitive issues. Submit your contact information and the request can be reviewed by a person.",
      "pricing":"Pricing depends on the service and property details. I can collect your address, service type, job details, and photos for the team to prepare a quote.",
      "schedule":"I can collect a preferred date and time. It stays marked Requested until an A to Z team member confirms it.",
      "services":"A to Z Power Washing offers driveway cleaning, pressure washing, siding restoration, and gutter care.",
      "area":"A to Z Power Washing serves the Detroit-area market described in the project proposal. The team should confirm whether a specific address is in the service area.",
      "photos":"Yes. You can attach job photos when submitting a quote request so the team can review the property.",
      "greeting":"Hi! I'm the A to Z customer assistant. I can explain services, start a quote request, collect job photos, or help request an appointment.",
      "unknown":"I can help with A to Z services, quote requests, job photos, and scheduling. If I'm not certain, I'll leave the question for a team member rather than make up an answer."
    }
    return intent,replies[intent]
