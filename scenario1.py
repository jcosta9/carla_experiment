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
        actor_list = []

        vehicle_bp = random.choice(blueprint_library.filter('vehicle'))

        transform = random.choice(world.get_map().get_spawn_points())
        vehicle = world.spawn_actor(vehicle_bp, transform)
        actor_list.append(vehicle)
        vehicle.set_autopilot(True)

        camera_bp = blueprint_library.find('sensor.camera.rgb')
        camera_transform = carla.Transform(carla.Location(x=1.5, z=2.4))
        camera_rgb = world.spawn_actor(camera_bp, camera_transform, attach_to=vehicle)
        camera_rgb.listen(lambda image: image.save_to_disk('../_out/%06d.png' % image.frame))
        actor_list.append(camera_rgb)

        spectator.set_transform(camera_rgb.get_transform())

        time.sleep(15)


    finally:
        print('destroying actors')
        camera_rgb.destroy()
        client.apply_batch([carla.command.DestroyActor(x) for x in actor_list])
        print('done.')

if __name__ == '__main__':
    main()