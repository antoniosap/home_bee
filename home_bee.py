#
# home-bee controller 14.5.2022
# hardware: ESP8266, 2 buttons, 8 relay
# firmware: tasmota 11.1.0
# for productions rus inside ha-appdaemon add-on
#
# button left   = GPIO1 --> Button 1
# button right  = GPIO3 --> Button 2
#
# configuration:
# SetOption73 1
# Interlock 1,2,3,4,5,6,7,8
# Interlock on
#

TOPIC_HOME_BEE_RESULT = "stat/tasmota_13C583/RESULT"
TOPIC_HOME_BEE_CMND = "cmnd/tasmota_13C583/"
TOPIC_HOME_BEE_CMND_RELAY = TOPIC_HOME_BEE_CMND + "Power"

METEO_EVENT = "weather.casatorino2022"
METEO_STATE = METEO_EVENT

# --------------------------------------------------------------------
# end of configuration
# --------------------------------------------------------------------

import appdaemon.plugins.hass.hassapi as hass
import appdaemon.plugins.mqtt.mqttapi as mqtt
import json
import datetime as dt

METEO_RELAY = {
    "clear-night": 1,
    "cloudy": 2,
    "exceptional": 5,
    "fog": 6,
    "hail": 5,
    "lightning": 8,
    "lightning-rainy": 8,
    "partlycloudy": 7,
    "pouring": 3,
    "rainy": 3,
    "snowy": 5,
    "snowy-rainy": 5,
    "sunny": 1,
    "windy": 4,
    "windy-variant": 4,
    "unavailable": 0
}


class HomeBee(hass.Hass):

    def initialize(self):
        # mqtt buttons
        self.mqtt = self.get_plugin_api("MQTT")
        self.mqtt.mqtt_subscribe(topic=TOPIC_HOME_BEE_RESULT)
        self.mqtt.listen_event(self.mqttEvent, "MQTT_MESSAGE", topic=TOPIC_HOME_BEE_RESULT, namespace='mqtt')
        # meteo events
        self.meteoRelay = METEO_RELAY[self.get_state(METEO_STATE)]
        if (self.meteoRelay == 0):
            self.allOff()
        self.listen_event(self.meteoEvent, 'state_changed', entity_id=METEO_EVENT)

    def allOff(self):
        self.mqtt.mqtt_publish(TOPIC_HOME_BEE_CMND_RELAY + '0', '0')

    def mqttEvent(self, event_name, data, *args, **kwargs):
        pld = json.loads(data['payload'])

    def meteoEvent(self, event_name, data, kwargs):
        try:
            self.meteoRelay = METEO_RELAY[data['new_state']['state']]
            if (self.meteoRelay == 0):
                self.allOff()
            else:
                self.mqtt.mqtt_publish(TOPIC_HOME_BEE_CMND_RELAY + str(self.meteoRelay), '1')
        except KeyError:
            self.meteoRelay = 0
            self.allOff()
