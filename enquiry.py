import re
from datetime import datetime

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from app import ratelimit
from app.leads import _send_to_sheet, _write_csv

router = APIRouter()

EMAIL_RE = re.compile(r"^[^@\s]{1,64}@[^@\s]{1,255}\.[^@\s]{2,}$")
SERVICES = {"Not sure yet", "AI assistant or chatbot", "Workflow automation",
            "Web or mobile app", "Product consulting", "Website security check"}
HEADERS = ["timestamp", "name", "email", "phone", "service", "message"]


class Enquiry(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: str = Field(min_length=5, max_length=254)
    phone: str = Field(default="", max_length=30)
    service: str = Field(default="", max_length=60)
    message: str = Field(min_length=10, max_length=2000)
    website: str = Field(default="", max_length=200)   # honeypot: real people leave it empty
    elapsed: float = 0                                 # seconds the form was open


def _safe(text, limit, multiline=False):
    if multiline:
        out = "\n".join(" ".join(l.split()) for l in str(text).splitlines())
    else:
        out = " ".join(str(text).split())
    out = out[:limit].strip()
    # stops spreadsheet formula injection
    return "'" + out if out and out[0] in "=+-@" else out


@router.post("/enquiry")
def enquiry(e: Enquiry, request: Request):
    ip = request.client.host if request.client else "unknown"
    if ratelimit.check_enquiry(ip):
        return JSONResponse(status_code=429, content={"ok": False})

    if e.website.strip() or e.elapsed < 3:       # bots: pretend it worked, save nothing
        return {"ok": True}

    email = e.email.strip().lower()
    if not EMAIL_RE.match(email):
        return JSONResponse(status_code=400, content={"ok": False, "error": "email"})
    phone = re.sub(r"[\s\-().]", "", e.phone)
    if phone and not re.fullmatch(r"\+?\d{7,15}", phone):
        return JSONResponse(status_code=400, content={"ok": False, "error": "phone"})

    values = [
        datetime.now().isoformat(timespec="seconds"),
        _safe(e.name, 100), email, phone,
        e.service if e.service in SERVICES else "Not sure yet",
        _safe(e.message, 2000, multiline=True),
    ]

    csv_ok = True
    try:
        _write_csv("enquiries", HEADERS, values)
    except Exception as ex:
        csv_ok = False
        print("Enquiry CSV write failed:", ex)
    try:
        _send_to_sheet(HEADERS, values, "enquiries")
    except Exception as ex:
        print("Enquiry sheet sync failed:", ex)
        print("ENQUIRY NOT SYNCED:", values)       # last-resort record in the host logs
        if not csv_ok:
            return JSONResponse(status_code=500, content={"ok": False})
        _write_csv("enquiries", HEADERS, values, unsynced=True)
    return {"ok": True}
