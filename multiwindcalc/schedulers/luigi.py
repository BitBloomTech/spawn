from luigi import build, configuration

from multiwindcalc.generate_tasks import generate_tasks_from_spec

class LuigiScheduler:
    def __init__(self, **config):
        luigi_config = configuration.get_config()
        luigi_config.set('WindGenerationTask', '_runner_type', config['runner_type'])
        luigi_config.set('WindGenerationTask', '_exe_path', config['turbsim_exe_path'])
        luigi_config.set('FastSimulationTask', '_runner_type', config['runner_type'])
        luigi_config.set('FastSimulationTask', '_exe_path', config['fast_exe_path'])
        self._workers = config['workers']
        self._out_dir = config['outdir']
        self._local = config['local']
        self._port = config['port']

    def run(self, spawner, spec):
        tasks = generate_tasks_from_spec(spawner, spec.root_node, self._out_dir)
        build(tasks, local_scheduler=self._local, workers=self._workers, scheduler_port=self._port)
