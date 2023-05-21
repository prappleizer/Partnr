import http.client, urllib
conn = http.client.HTTPSConnection("api.pushover.net:443")
conn.request("POST", "/1/messages.json",
  urllib.parse.urlencode({
    "token": "ayfv5abdtabo43scq8z9tqbyq1xbjd",
    "user": "u4sh9dabcqs1gsapp61iku2477xjwf",
    "message": "Imad just wrote you a letter! Check Now: ",
  }), { "Content-type": "application/x-www-form-urlencoded" })
conn.getresponse()