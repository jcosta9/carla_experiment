import sys
import os
import logging
import time

import carla

from experimentManager import ExperimentManager
from config import get_config
from utils.logger import setup_logger

def main():
    try:
        os.chdir(sys.path[0])
        setup_logger('auto_sanity')
        
        logging.info("Starting: Scenario 1")
        logging.info(f"Current path: {os.getcwd()}")

        config = get_config('project_config')
        exp = ExperimentManager(config)

        
        vehicle, _, transform = exp.add_vehicle()
        #walker, _, transform = exp.add_pedestrian()
        exp.spectator.set_transform(transform)

        camera_bp = exp.blueprint_library.find('sensor.camera.rgb')
        camera_transform = carla.Transform(carla.Location(x=1.5, z=2.4))
        camera_rgb = exp.world.spawn_actor(camera_bp, camera_transform, attach_to=vehicle)
        #camera_rgb.listen(lambda image: image.save_to_disk('../_out/%06d.png' % image.frame))
        exp.actor_list.append(camera_rgb)
        exp.sensors.append(camera_rgb)

        sem_cam = exp.add_sensor(vehicle, 'sensor.camera.semantic_segmentation', image_size_x=1920, image_size_y = 1020, fov = 110)
        # This time, a color converter is applied to the image, to get the semantic segmentation view
        # sem_cam.listen(lambda image: image.save_to_disk('../tutorial/new_sem_output/%.6d.jpg' % image.frame,carla.ColorConverter.CityScapesPalette))


        time.sleep(config.EXP_LENGTH)


    finally:
        exp.tear_down()

if __name__ == '__main__':
    main()