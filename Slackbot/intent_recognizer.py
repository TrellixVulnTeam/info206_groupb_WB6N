import os
import requests

WIT_AI_ACCESS_TOKEN = os.environ.get("WIT_AI_ACCESS_TOKEN")

class Intent:
  pass

class BARTQueryIntent(Intent):
  def __init__(self, dictionary = None):
    stops = dictionary.get("entities", {}).get("stop")
    if stops is not None:
      if len(stops) > 1:
        self.origin = stops[0].get("value")
        self.destination = stops[1].get("value")
      elif len(stops) > 0:
        self.origin = stops[0].get("value")

class BusQueryIntent(Intent):
  def __init__(self, dictionary = None):
    stops = dictionary.get("entities", {}).get("stop")
    routes = dictionary.get("entities", {}).get("bus_route")
    if stops is not None:
      if len(stops) > 1:
        self.origin = stops[0].get("value")
        self.destination = stops[1].get("value")
      elif len(stops) > 0:
        self.origin = stops[0].get("value")

    if routes is not None:
      if len(routes) > 1:
        self.route = routes[0].get("value")

class HelpIntent(Intent):
  def __init__(self):
    pass

class IntentRecognizer: 
  def __init__(self):
    self.access_token = WIT_AI_ACCESS_TOKEN

  def recognize(self, message):
    message = message.replace('&', '%26')
    headers= { 'Authorization': 'Bearer ' + self.access_token, 'Content-Type': 'application/json' }
    r = requests.get('https://api.wit.ai/message?v=20171011&q=' + message, headers=headers)
    json = r.json()
    print(json)
    intents = json.get("entities", {}).get("intent", [])
    if(len(intents) > 0):
      intent_type = intents[0].get("value", None)
      if intent_type == "bart_query":
        return BARTQueryIntent(dictionary = json)
      elif intent_type == "bus_query":
        return BusQueryIntent(dictionary = json)
    return HelpIntent()