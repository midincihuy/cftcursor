import urllib.request
import urllib.parse
import json
import markdown
import os
from django import template
from datetime import datetime, timezone
from django.utils.safestring import mark_safe

register = template.Library()

WAHA_URL = os.getenv("WAHA_URL")

def fetch_json(url, params=None, method="GET", data=None):
    try:
        if params:
            url += "?" + urllib.parse.urlencode(params)
        print(f"[DEBUG] Request → {method} {url}")  # show outgoing request
        if data is not None:
            data = json.dumps(data).encode("utf-8")
            req = urllib.request.Request(
                url,
                data=data,
                headers={
                    "Content-Type": "application/json", 
                    "X-Api-Key" : os.getenv("WAHA_X_API_KEY"), 
                    "Accept" : "application/json"
                    },
                method=method,
            )
        else:
            req = urllib.request.Request(url, method=method, headers={
                    "Content-Type": "application/json", 
                    "X-Api-Key" : os.getenv("WAHA_X_API_KEY"), 
                    "Accept" : "application/json"
                    },)

        with urllib.request.urlopen(req) as resp:
            raw = resp.read().decode("utf-8")
            parsed = json.loads(raw)
            print("DEBUG raw response:", raw)  # 👈 see exact WAHA JSON
            if isinstance(parsed, dict) and "data" in parsed:
                return parsed["data"]
            return parsed
            # return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print("HTTP error:", e)
        return []


@register.filter
def ts_to_date(value):
    try:
        return datetime.fromtimestamp(int(value), tz=timezone.utc)
    except Exception:
        return value

@register.filter
def get_profile(value):
    try:
        # do get profile
        response = fetch_json(f"{WAHA_URL}/contacts?session=default&contactId={(value)}")
        # return response
        if response["name"]:
            return response["name"]
        elif response["pushname"]:
            return response["pushname"]
        else:
            return response["number"]

    except Exception:
        return value

@register.filter
def render_markdown(text):
    if not text:
        return ""
    html = markdown.markdown(
        text,
        extensions=["fenced_code", "tables", "nl2br"]
    )
    return mark_safe(html)  # safe because markdown returns HTML