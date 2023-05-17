import carla
import random
import time

def main():
    try:
        client = carla.Client('localhost', 2000)
        client.set_timeout(2.0)

        world = client.get_world()
        spectator = world.get_spectator()
        blueprint_library = world.get_blueprint_library()

        vehicle_bp = random.choice(blueprint_library.filter('vehicle'))

        transform = random.choice(world.get_map().get_spawn_points())
        vehicle = world.spawn_actor(vehicle_bp, transform)
        spectator.set_transform(vehicle.get_transform())
        vehicle.set_autopilot(True)

        time.sleep(30)


    finally:
        print('destroying actors')
        client.apply_batch([carla.command.DestroyActor(x) for x in world.get_actors()])
        print('done.')

if __name__ == '__main__':
    main()