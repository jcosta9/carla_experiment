import carla
import random

client = carla.Client('localhost', 2000)
world = client.get_world()

n_walkers = 15
n_vehicles = 40

#the default port is 8000 (important to assign vehcile to a tm) since running multiple tm is possible
traffic_manager = client.get_trafficmanager()
tm_port = traffic_manager.get_port()

#configuring the tm manually
traffic_manager.set_global_distance_to_leading_vehicle(1.5)
traffic_manager.set_synchronous_mode(True)
#the hybrid physics mode requires to assign one vehicle as the "hero" vehicle since for only vehicle in closer proximity to the 
#hero vehicle will be fully simulated, the other will be teleported, removing the simulation bottleneck!
traffic_manager.set_hybrid_physics_mode(True)


bpl = world.get_blueprint_library()
vehicle_blueprints = bpl.filter("*vehicle*")
walker_blueprints = bpl.filter('*walker*')
spawn_points = world.get_map().get_spawn_points()

print(len(vehicle_blueprints), len(vehicle_blueprints), len(spawn_points))