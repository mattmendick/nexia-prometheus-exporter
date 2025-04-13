# nexia-prometheus-exporter
Prometheus exporter for Nexia thermostats

## Status
This is a work in progress, and tied to a specific branch of the bdraco/nexia library: https://github.com/bdraco/nexia/tree/ux360_state_reporting/nexia, corresponding to the WIP PR https://github.com/bdraco/nexia/pull/111 for my thermostat, the UX360. It might work for others but right now I only know it works for mine. Future steps here would be to get that PR merged in the bdraco/nexia project and then add more metrics based on normal functions exposed by the library since the UX360 seems to do things differently.

## Example Prometheus metrics
```
# HELP python_gc_objects_collected_total Objects collected during gc
# TYPE python_gc_objects_collected_total counter
python_gc_objects_collected_total{generation="0"} 1621.0
python_gc_objects_collected_total{generation="1"} 115.0
python_gc_objects_collected_total{generation="2"} 0.0
# HELP python_gc_objects_uncollectable_total Uncollectable objects found during GC
# TYPE python_gc_objects_uncollectable_total counter
python_gc_objects_uncollectable_total{generation="0"} 0.0
python_gc_objects_uncollectable_total{generation="1"} 0.0
python_gc_objects_uncollectable_total{generation="2"} 0.0
# HELP python_gc_collections_total Number of times this generation was collected
# TYPE python_gc_collections_total counter
python_gc_collections_total{generation="0"} 40.0
python_gc_collections_total{generation="1"} 3.0
python_gc_collections_total{generation="2"} 0.0
# HELP python_info Python platform information
# TYPE python_info gauge
python_info{implementation="CPython",major="3",minor="13",patchlevel="3",version="3.13.3"} 1.0
# HELP nexia_temperature_celsius_degrees Temperature readings in degrees Celsius
# TYPE nexia_temperature_celsius_degrees gauge
nexia_temperature_celsius_degrees{thermostat_id="12345ABCDE",thermostat_type="123456789ABCDEFG",type="outdoor",zone_name="outdoor"} 11.666666666666666
nexia_temperature_celsius_degrees{thermostat_id="12345ABCDE",thermostat_type="123456789ABCDEFG",type="current",zone_name="Zone 1"} 20.0
nexia_temperature_celsius_degrees{thermostat_id="12345ABCDE",thermostat_type="123456789ABCDEFG",type="cooling_setpoint",zone_name="Zone 1"} 29.444444444444443
nexia_temperature_celsius_degrees{thermostat_id="12345ABCDE",thermostat_type="123456789ABCDEFG",type="heating_setpoint",zone_name="Zone 1"} 20.0
# HELP nexia_relative_humidity_ratio Relative humidity reading (0-1 ratio)
# TYPE nexia_relative_humidity_ratio gauge
nexia_relative_humidity_ratio{thermostat_id="12345ABCDE",thermostat_type="123456789ABCDEFG"} 0.47
# HELP nexia_compressor_speed_ratio Compressor speed as ratio from 0 to 1
# TYPE nexia_compressor_speed_ratio gauge
nexia_compressor_speed_ratio{thermostat_id="12345ABCDE",thermostat_type="123456789ABCDEFG",type="current"} 0.0
nexia_compressor_speed_ratio{thermostat_id="12345ABCDE",thermostat_type="123456789ABCDEFG",type="requested"} 0.0
# HELP nexia_zone_mode_active Zone mode state (1=active, 0=inactive)
# TYPE nexia_zone_mode_active gauge
nexia_zone_mode_active{mode="off",thermostat_id="12345ABCDE",thermostat_type="123456789ABCDEFG",zone_name="Zone 1"} 0.0
nexia_zone_mode_active{mode="auto",thermostat_id="12345ABCDE",thermostat_type="123456789ABCDEFG",zone_name="Zone 1"} 0.0
nexia_zone_mode_active{mode="cool",thermostat_id="12345ABCDE",thermostat_type="123456789ABCDEFG",zone_name="Zone 1"} 0.0
nexia_zone_mode_active{mode="heat",thermostat_id="12345ABCDE",thermostat_type="123456789ABCDEFG",zone_name="Zone 1"} 1.0
nexia_zone_mode_active{mode="em heat",thermostat_id="12345ABCDE",thermostat_type="123456789ABCDEFG",zone_name="Zone 1"} 0.0
# HELP nexia_zone_status_active Zone status state (1=active, 0=inactive)
# TYPE nexia_zone_status_active gauge
nexia_zone_status_active{status="fan_running",thermostat_id="12345ABCDE",thermostat_type="123456789ABCDEFG",zone_name="Zone 1"} 0.0
nexia_zone_status_active{status="idle",thermostat_id="12345ABCDE",thermostat_type="123456789ABCDEFG",zone_name="Zone 1"} 1.0
nexia_zone_status_active{status="heating",thermostat_id="12345ABCDE",thermostat_type="123456789ABCDEFG",zone_name="Zone 1"} 0.0
nexia_zone_status_active{status="emergency_heating",thermostat_id="12345ABCDE",thermostat_type="123456789ABCDEFG",zone_name="Zone 1"} 0.0
nexia_zone_status_active{status="cooling",thermostat_id="12345ABCDE",thermostat_type="123456789ABCDEFG",zone_name="Zone 1"} 0.0
nexia_zone_status_active{status="waiting",thermostat_id="12345ABCDE",thermostat_type="123456789ABCDEFG",zone_name="Zone 1"} 0.0
```
