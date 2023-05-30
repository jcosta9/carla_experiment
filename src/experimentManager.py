import os
import random
import logging
from datetime import date
import numpy as np
import carla

############################################
# Add this to a sensor handler class
############################################
'''
The labels below match the ones found in the cpp file carla/LibCarla/source/carla/rpc/ObjectLabel.h
We belive that the documentation hasn't been updated, since it ranges only from 0 to 22, and larger 
tag values were found. Besides, the order changes a bit.
'''
DETECTED_TAGS = {
    
    0 : "None",
    1 : "Roads",
    2 : "Sidewalks",
    3 : "Buildings",
    4 : "Walls",
    5 : "Fences",
    6 : "Poles",
    7 : "TrafficLight",
    8 : "TrafficSigns",
    9 : "Vegetation",
    10 : "Terrain",
    11 : "Sky",
    12 : "Pedestrians",
    13 : "Rider",
    14 : "Car",
    15 : "Truck",
    16 : "Bus",
    17 : "Train",
    18 : "Motorcycle",
    19 : "Bicycle",
    20 : "Static",
    21 : "Dynamic",
    22 : "Other",
    23 : "Water",
    24 : "RoadLines",
    25 : "Ground",
    26 : "Bridge",
    27 : "RailTrack",
    28 : "GuardRail",
}

def to_bgra_array(image):
    array = np.frombuffer(image.raw_data, dtype=np.dtype("uint8"))
    array = np.reshape(array, (image.height, image.width, 4))
    return array

def labels_to_array(image):
    return to_bgra_array(image)[:, :, 2]

def get_image_contents(image, config) -> np.array:
   today = date.today().strftime('%Y%m%d')
   frame = '%.6d' % image.frame

   semseg_raw_path = os.path.join(*config.DATA_OUTPUT, 'semseg_raw')
   if not os.path.exists(semseg_raw_path):
       os.makedirs(semseg_raw_path)

   semseg_labels_path = os.path.join(*config.DATA_OUTPUT, 'semseg_labels')
   if not os.path.exists(semseg_labels_path):
       os.makedirs(semseg_labels_path)

   red_channel = labels_to_array(image)
   red_channel_txt = np.vectorize(DETECTED_TAGS.get)(red_channel)
   unique_ids = np.unique(red_channel)
   unique_labels = np.vectorize(DETECTED_TAGS.get)(unique_ids)

   image.save_to_disk(os.path.join(semseg_raw_path, f'{today}_{frame}.jpg'))
   image.save_to_disk(os.path.join(semseg_raw_path, f'{today}_{frame}_colored.jpg'), carla.ColorConverter.CityScapesPalette)

   red_channel.tofile(os.path.join(semseg_raw_path, f'{today}_{frame}_redchannel.csv'), sep = ',')
   red_channel_txt.tofile(os.path.join(semseg_labels_path, f'{today}_{frame}_rawlabels.csv'), sep = ',')
   unique_ids.tofile(os.path.join(semseg_labels_path, f'{today}_{frame}_unique.csv'), sep = ',')
   unique_labels.tofile(os.path.join(semseg_labels_path, f'{today}_{frame}_unique_labels.csv'), sep = ',')
  


class ExperimentManager():
    def __init__(self, config, *args, **kwargs):
        self.client = carla.Client(config.HOST, config.PORT)
        self.client.set_timeout(config.CLIENT_TIMEOUT)

        logging.info(f"Setting Client Host: {config.HOST}")
        logging.info(f"Setting Client Port: {config.PORT}")
        logging.info(f"Setting Client Client Timeout: {config.CLIENT_TIMEOUT}")

        self.world = self.client.get_world()
        self.spectator = self.world.get_spectator()
        self.blueprint_library = self.world.get_blueprint_library()
        self.actor_list = []
        self.sensors = []
        self.spawn_points = self.world.get_map().get_spawn_points()
        random.shuffle(self.spawn_points)
        self.sensor_list = []

    def add_vehicle(self, autopilot:bool=True):
        vehicle_bp = random.choice(self.blueprint_library.filter('vehicle'))
        transform = self.spawn_points.pop()
        vehicle = self.world.spawn_actor(vehicle_bp, transform)
        self.actor_list.append(vehicle)

        logging.info('created %s' % vehicle.type_id)

        if autopilot:
            vehicle.set_autopilot(True)
        return vehicle, vehicle_bp, transform
    
    def add_sensor(self, ego_vehicle : carla.Actor, sensor: str, *args,**kwargs) -> list:
        try:
            sensor_bp = self.blueprint_library.find(sensor)
        except IndexError:
            print(f'{sensor} was not found in the blueprint library')
            return
        if kwargs != None:
            for key in kwargs:
                sensor_bp.set_attribute(f'{key}',str(kwargs[key]))
        #the relative position to the ego vehicle could be quite crucial depending on type of vehicle
        transform = carla.Transform(carla.Location(x=2,z=1))
        sensor = self.world.spawn_actor(sensor_bp, transform, attach_to=ego_vehicle, attachment_type=carla.AttachmentType.Rigid)
        self.actor_list.append(sensor)
        return sensor
    
    def listen_to_sensor(self,sensor: carla.Sensor):
        sensor_type = sensor.type_id.replace('sensor.', '')
        sensor.listen(lambda image: image.save_to_disk(f'../_out/{sensor_type}/%06d.png' % image.frame))
    
    
    def add_pedestrian(self):
        #spawning the walker
        walker_bp = random.choice(self.blueprint_library.filter('walker'))
        transform = carla.Transform()
        loc = self.world.get_random_location_from_navigation()
        transform.location = loc
        walker = self.world.spawn_actor(walker_bp, transform)
        self.actor_list.append(walker)

        SpawnActor = carla.command.SpawnActor
        #spawning the walkerAIcontroller
        walker_controller_bp = self.world.get_blueprint_library().find('controller.ai.walker')
        controller = self.world.spawn_actor(walker_controller_bp, carla.Transform(), walker)
        res = self.client.apply_batch_sync([controller], True)
        controller = self.world.get_actor(res[0].actor_id)

        #making them walk
        walk_to = self.world.get_random_location_from_navigation()
        controller.start()
        controller.go_to_location(walk_to)
        controller.set_max_speed(1.4)
        print(loc, walk_to, controller.parent, controller.actor_state, walker.actor_state, controller.get_location())
        return walker, walker_bp, transform
    
    
    def tear_down(self):
        logging.info(f"Destroying actors.")

        for sensor in self.sensors:
            try:
                sensor.destroy()
            except Exception as e:
                logging.error("Error at %", 'destroying', exc_info=e)

        try:
            self.client.apply_batch([carla.command.DestroyActor(x) for x in self.actor_list])
        except Exception as e:
            logging.error("Error at %", 'destroying', exc_info=e)

        print('done.')