import random
import logging
import carla

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

    def add_vehicle(self, autopilot:bool=True):
        vehicle_bp = random.choice(self.blueprint_library.filter('vehicle'))
        transform = random.choice(self.world.get_map().get_spawn_points())
        vehicle = self.world.spawn_actor(vehicle_bp, transform)
        self.actor_list.append(vehicle)

        logging.info('created %s' % vehicle.type_id)

        if autopilot:
            vehicle.set_autopilot(True)
        return vehicle, vehicle_bp, transform

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