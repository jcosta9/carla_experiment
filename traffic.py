import carla
import random

def main():
    client = carla.Client('localhost', 2000)
    n_walkers = 15
    n_vehicles = 40
    vehicles_list = []

    try:
        world = client.get_world()
        setting = world.get_settings()
        spectator = world.get_spectator()

        # setting.synchronous_mode = True
        synchronous_master = True
        # setting.fixed_delta_seconds = 0.05
        # world.apply_settings(setting)

        #the     default port is 8000 (important to assign vehcile to a tm) since running multiple tm is possible
        traffic_manager = client.get_trafficmanager()
        tm_port = traffic_manager.get_port()

        #con    figuring the tm manually
        traffic_manager.set_global_distance_to_leading_vehicle(2.5)
        traffic_manager.set_synchronous_mode(True)

        #the hybrid physics mode requires to assign one vehicle as the "hero" vehicle since for only vehicle in closer proximity to the
        #hero vehicle will be fully simulated, the other will be teleported, removing the simulation bottleneck!
        traffic_manager.set_hybrid_physics_mode(True)
        traffic_manager.set_hybrid_physics_radius(70.0)

        #here the settings can be changed like rendering of screen for example and

        #getting the blueprint librarys and spawn points
        bpl = world.get_blueprint_library()
        vehicle_blueprints = bpl.filter('vehicle.*')

        vehicle_blueprints = sorted(vehicle_blueprints, key=lambda bp: bp.id)

        vehicle_sp = world.get_map().get_spawn_points()
        print("number of spawn points:", len(vehicle_sp))

        # @todo cannot import these directly.
        SpawnActor = carla.command.SpawnActor
        SetAutopilot = carla.command.SetAutopilot
        FutureActor = carla.command.FutureActor

        ###
        # spawning the vehicles
        ##

        batch = []
        for n, transform in enumerate(vehicle_sp):
            if n >= 30:
                break
            blueprint = random.choice(vehicle_blueprints)
            if blueprint.has_attribute('color'):
                color = random.choice(blueprint.get_attribute('color').recommended_values)
                blueprint.set_attribute('color', color)
            if blueprint.has_attribute('driver_id'):
                driver_id = random.choice(blueprint.get_attribute('driver_id').recommended_values)
                blueprint.set_attribute('driver_id', driver_id)
            else:
                blueprint.set_attribute('role_name', 'autopilot')

            # spawn the cars and set their autopilot and light state all together
            batch.append(SpawnActor(blueprint, transform)
                .then(SetAutopilot(FutureActor, True, traffic_manager.get_port())))

        for response in client.apply_batch_sync(batch, synchronous_master):
            if response.error:
                print(response.error)
            else:
                vehicles_list.append(response.actor_id)

        # Example of how to use Traffic Manager parameters
        traffic_manager.global_percentage_speed_difference(30.0)

        while True:
            if synchronous_master:
                world.tick()
            else:
                world.wait_for_tick()

    #ensuring that synchronous mode is disabled, else a new script cannot be started
    finally:
        setting.synchronous_mode = False
        setting.no_rendering_mode = False
        world.apply_settings(setting)

        print('\ndestroying %d vehicles' % len(vehicles_list))
        client.apply_batch([carla.command.DestroyActor(x) for x in vehicles_list])

if __name__ == "__main__":
    main()