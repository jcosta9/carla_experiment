import carla
import random

def main():
    client = carla.Client('localhost', 2000)
    n_walkers = 15      
    n_vehicles = 40     
    
    try:
        world = client.get_world()      
        setting = world.get_settings()
        spectator = world.get_spectator()

        setting.synchronous_mode = True
        setting.fixed_delta_seconds = 0.05  
        world.apply_settings(setting)

        #the     default port is 8000 (important to assign vehcile to a tm) since running multiple tm is possible       
        traffic_manager = client.get_trafficmanager()       
        tm_port = traffic_manager.get_port()        

        #con    figuring the tm manually        
        traffic_manager.set_global_distance_to_leading_vehicle(1.5)     
        traffic_manager.set_synchronous_mode(True)      

        #the hybrid physics mode requires to assign one vehicle as the "hero" vehicle since for only vehicle in closer proximity to the         
        #hero vehicle will be fully simulated, the other will be teleported, removing the simulation bottleneck!        
        traffic_manager.set_hybrid_physics_mode(True)       
        traffic_manager.set_hybrid_physics_radius(70.0)     

        #here the settings can be changed like rendering of screen for example and      

        #getting the blueprint librarys and spawn points        
        bpl = world.get_blueprint_library()     
        vehicle_blueprints = bpl.filter("*vehicle*")        
        walker_blueprints = bpl.filter('*walker*')      
        vehicle_sp = world.get_map().get_spawn_points()

        ###
        # spawning the vehicles
        ##

        ego_spawn = random.choice(vehicle_sp)
        ego_bp = random.choice(vehicle_blueprints)
        ego_bp.set_attribute('role_name', 'hero')
        ego_vehicle = world.spawn_actor(ego_bp, ego_spawn)
        spectator.set_transform(ego_vehicle.get_transform())

        for spawn_point in random.choices(vehicle_sp, k=n_vehicles):
            # @todo: avoiding attempt to spawn on ego vehicles location 
            if spawn_point == ego_spawn:
                continue
            world.try_spawn_actor(random.choice(vehicle_blueprints), spawn_point)
        
        #in synchronous mode the sever needs a tick, else it will freeze. The tick tells the server to compute the next frame.      
        while True:     
            world.tick()        
    

    #ensuring that synchronous mode is disabled, else a new script cannot be started
    finally:
        setting.synchronous_mode = False
        setting.no_rendering_mode = False  
        world.apply_settings(setting)    

if __name__ == "__main__":
    main()