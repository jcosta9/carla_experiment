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
        sensors = []

        vehicle_bp = random.choice(blueprint_library.filter('vehicle'))

        transform = random.choice(world.get_map().get_spawn_points())
        vehicle = world.spawn_actor(vehicle_bp, transform)
        actor_list.append(vehicle)
        vehicle.set_autopilot(True)

        spectator.set_transform(transform)

        camera_bp = blueprint_library.find('sensor.camera.rgb')
        camera_transform = carla.Transform(carla.Location(x=1.5, z=2.4))
        camera_rgb = world.spawn_actor(camera_bp, camera_transform, attach_to=vehicle)
        camera_rgb.listen(lambda image: image.save_to_disk('../_out/%06d.png' % image.frame))
        actor_list.append(camera_rgb)
        sensors.append(camera_rgb)

        sem_bp = world.get_blueprint_library().find('sensor.camera.semantic_segmentation')
        sem_bp.set_attribute("image_size_x",str(1920))
        sem_bp.set_attribute("image_size_y",str(1080))
        sem_bp.set_attribute("fov",str(105))
        sem_location = carla.Location(2,0,1)
        sem_rotation = carla.Rotation(0,0,0)
        sem_transform = carla.Transform(sem_location,sem_rotation)
        sem_cam = world.spawn_actor(sem_bp,sem_transform,attach_to=vehicle, attachment_type=carla.AttachmentType.Rigid)
        # This time, a color converter is applied to the image, to get the semantic segmentation view
        sem_cam.listen(lambda image: image.save_to_disk('../tutorial/new_sem_output/%.6d.jpg' % image.frame,carla.ColorConverter.CityScapesPalette))


        time.sleep(5)


    finally:
        print('destroying actors')
        for sensor in sensors:
            sensor.destroy()
        client.apply_batch([carla.command.DestroyActor(x) for x in actor_list])
        print('done.')

if __name__ == '__main__':
    main()