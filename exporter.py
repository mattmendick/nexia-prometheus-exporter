from prometheus_client import start_http_server, Gauge
import asyncio
import aiohttp
import logging
import os
from dotenv import load_dotenv
from nexia.home import NexiaHome

load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Define Prometheus metrics
TEMPERATURE_GAUGE = Gauge('nexia_temperature_celsius_degrees', 
    'Temperature readings in degrees Celsius', 
    ['thermostat_id', 'thermostat_type', 'zone_name', 'type'])  # type = current, cooling_setpoint, heating_setpoint, outdoor

HUMIDITY_GAUGE = Gauge('nexia_relative_humidity_ratio', 
    'Relative humidity reading (0-1 ratio)', 
    ['thermostat_id', 'thermostat_type'])

COMPRESSOR_SPEED_GAUGE = Gauge('nexia_compressor_speed_ratio', 
    'Compressor speed as ratio from 0 to 1', 
    ['thermostat_id', 'thermostat_type', 'type'])  # type = current, requested

# Zone mode and status metrics (1 if active, 0 if not)
ZONE_MODE_GAUGE = Gauge('nexia_zone_mode_active', 
    'Zone mode state (1=active, 0=inactive)', 
    ['thermostat_id', 'thermostat_type', 'zone_name', 'mode'])

ZONE_STATUS_GAUGE = Gauge('nexia_zone_status_active', 
    'Zone status state (1=active, 0=inactive)', 
    ['thermostat_id', 'thermostat_type', 'zone_name', 'status'])

class NexiaExporter:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.client = None
        self.session = None
        self.logged_capabilities = set()

    async def connect(self):
        self.session = aiohttp.ClientSession()
        self.client = NexiaHome(
            session=self.session,
            username=self.username,
            password=self.password
        )
        await self.client.login()
        await self.client.update()

    def fahrenheit_to_celsius(self, fahrenheit):
        return (fahrenheit - 32) * 5/9

    def update_zone_mode_metrics(self, zone, thermostat_id, thermostat_type):
        current_mode = zone.get_current_mode().lower()
        labels = {
            'thermostat_id': thermostat_id,
            'thermostat_type': thermostat_type,
            'zone_name': zone.get_name()
        }
        
        # All possible modes
        modes = ['off', 'auto', 'cool', 'heat', 'em heat']
        for mode in modes:
            ZONE_MODE_GAUGE.labels(**labels, mode=mode).set(1 if current_mode == mode else 0)

    def update_zone_status_metrics(self, zone, thermostat_id, thermostat_type):
        current_status = zone.get_status().lower()
        labels = {
            'thermostat_id': thermostat_id,
            'thermostat_type': thermostat_type,
            'zone_name': zone.get_name()
        }
        
        # All possible statuses
        statuses = ['fan_running', 'idle', 'heating', 'emergency_heating', 'cooling', 'waiting']
        for status in statuses:
            ZONE_STATUS_GAUGE.labels(**labels, status=status).set(1 if current_status == status else 0)

    async def collect_metrics(self):
        while True:
            try:
                await self.client.update()
                
                for thermostat_id in self.client.get_thermostat_ids():
                    thermostat = self.client.get_thermostat_by_id(thermostat_id)
                    thermostat_type = thermostat.get_type()

                    # Log variable fan speed capability once per thermostat
                    if thermostat_id not in self.logged_capabilities:
                        has_variable_speed = thermostat.has_variable_fan_speed()
                        logging.info(f"Thermostat {thermostat_id} ({thermostat_type}) variable fan speed support: {has_variable_speed}")
                        self.logged_capabilities.add(thermostat_id)

                    # Compressor speeds
                    COMPRESSOR_SPEED_GAUGE.labels(
                        thermostat_id=thermostat_id,
                        thermostat_type=thermostat_type,
                        type='current'
                    ).set(thermostat.get_current_compressor_speed())
                    
                    COMPRESSOR_SPEED_GAUGE.labels(
                        thermostat_id=thermostat_id,
                        thermostat_type=thermostat_type,
                        type='requested'
                    ).set(thermostat.get_requested_compressor_speed())

                    # Get and convert outdoor temperature if needed
                    outdoor_temp = thermostat.get_outdoor_temperature()
                    if thermostat.get_unit() == 'F':
                        outdoor_temp = self.fahrenheit_to_celsius(outdoor_temp)
                    TEMPERATURE_GAUGE.labels(
                        thermostat_id=thermostat_id,
                        thermostat_type=thermostat_type,
                        zone_name='outdoor',
                        type='outdoor'
                    ).set(outdoor_temp)

                    # Get relative humidity
                    HUMIDITY_GAUGE.labels(
                        thermostat_id=thermostat_id,
                        thermostat_type=thermostat_type
                    ).set(thermostat.get_relative_humidity())

                    for zone in thermostat.zones:
                        # Update mode and status metrics
                        self.update_zone_mode_metrics(zone, thermostat_id, thermostat_type)
                        self.update_zone_status_metrics(zone, thermostat_id, thermostat_type)

                        # Get all temperatures
                        temp = zone.get_temperature()
                        cooling_setpoint = zone.get_cooling_setpoint()
                        heating_setpoint = zone.get_heating_setpoint()
                        
                        # Convert temperatures to Celsius if the unit is Fahrenheit
                        if thermostat.get_unit() == 'F':
                            temp = self.fahrenheit_to_celsius(temp)
                            cooling_setpoint = self.fahrenheit_to_celsius(cooling_setpoint)
                            heating_setpoint = self.fahrenheit_to_celsius(heating_setpoint)
                        
                        # Set all temperature metrics
                        base_labels = {
                            'thermostat_id': thermostat_id,
                            'thermostat_type': thermostat_type,
                            'zone_name': zone.get_name()
                        }
                        
                        TEMPERATURE_GAUGE.labels(**base_labels, type='current').set(temp)
                        TEMPERATURE_GAUGE.labels(**base_labels, type='cooling_setpoint').set(cooling_setpoint)
                        TEMPERATURE_GAUGE.labels(**base_labels, type='heating_setpoint').set(heating_setpoint)

            except Exception as e:
                print(f"Error collecting metrics: {e}")
            
            await asyncio.sleep(60)  # Collect every 60 seconds

    async def cleanup(self):
        if self.session:
            await self.session.close()

async def main():
    # Get credentials from environment variables
    username = os.getenv('NEXIA_USERNAME')
    password = os.getenv('NEXIA_PASSWORD')

    if not username or not password:
        raise ValueError("NEXIA_USERNAME and NEXIA_PASSWORD environment variables must be set")

    # Start Prometheus HTTP server
    start_http_server(8000)
    
    exporter = NexiaExporter(username, password)
    try:
        await exporter.connect()
        await exporter.collect_metrics()
    finally:
        await exporter.cleanup()

if __name__ == '__main__':
    asyncio.run(main())