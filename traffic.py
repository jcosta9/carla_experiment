import carla
import random

client = carla.Client('localhost', 2000)
world = client.get_world()

#the default port is 8000 (important to assign vehcile to a tm)
traffic_manager = client.get_trafficmanager()

