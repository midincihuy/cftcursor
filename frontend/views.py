import json
import urllib.request
import urllib.parse
import os
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
# Create your views here.

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


def index(request):
    # return HttpResponse("Hello, world. You're at the polls index.")
    # Fetch chat list from WAHA

    try:
        chats = fetch_json(f"{WAHA_URL}/default/chats/overview?limit=50")
        print("DEBUG chats response:", chats)  # 👈 add this line
    except Exception as e:
        chats = []
        print("Error fetching chats:", e)

    # Get selected chat
    chat_id = request.GET.get("chat_id")

    # Fetch messages for that chat
    messages = []
    if chat_id:
        try:
            messages = fetch_json(
                f"{WAHA_URL}/default/chats/{chat_id}/messages?downloadMedia=false&limit=10"
            )
            print("DEBUG messages response:", messages)  # 👈 add this too
        except Exception as e:
            print("Error fetching messages:", e)

    return render(
        request,
        "frontend/index.html",
        {"chats": chats, "messages": messages, "chat_id": chat_id},
    )
    
@csrf_exempt
def chat_send(request):
    if request.method == "POST":
        chat_id = request.POST["chat_id"]
        text = request.POST["text"]
        fetch_json(
            f"{WAHA_URL}/default/messages",
            method="POST",
            data={"chat_id": chat_id, "text": text},
        )
        return redirect(f"/?chat_id={chat_id}")