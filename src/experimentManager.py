import carla

class ExperimentManager():
    def __init__(self, *args, **kwargs):
        self.client = carla.Client(kwargs.get('host'), kwargs.get('port'))
        self.client.set_timeout(kwargs.get('client_timeout'))

        self.world = self.client.get_world()
        self.spectator = self.world.get_spectator()
        self.blueprint_library = self.world.get_blueprint_library()
        self.actor_list = []
        self.sensors = []

    def tear_down(self):
        print('destroying actors')
        for sensor in self.sensors:
            sensor.destroy()
        self.client.apply_batch([carla.command.DestroyActor(x) for x in self.actor_list])
        print('done.')