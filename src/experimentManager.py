import carla
import random

class ExperimentManager():
    def __init__(self, config, *args, **kwargs):
        self.client = carla.Client(config.HOST, config.PORT)
        self.client.set_timeout(config.CLIENT_TIMEOUT)

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

        if autopilot:
            vehicle.set_autopilot(True)
        return vehicle, vehicle_bp, transform

    def tear_down(self):
        print('destroying actors')
        for sensor in self.sensors:
            sensor.destroy()
        self.client.apply_batch([carla.command.DestroyActor(x) for x in self.actor_list])
        print('done.')