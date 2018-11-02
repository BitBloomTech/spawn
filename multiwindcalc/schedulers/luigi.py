""":mod:`multiwindcalc` scheduler for luigi
"""
from luigi import build, configuration

from multiwindcalc.generate_tasks import generate_tasks_from_spec

class LuigiScheduler:
    """Scheduler implementation for Luigi

    Because this is currently the only scheduler implementation it's probable
    that the interface will evolve in time.
    """
    def __init__(self, config):
        """Initialise the :class:`LuigiScheduler`

        :param config: Keyword arguments containing config values
        :type config: kwargs

        Config Values
        =============
        runner_type         The type of runner to use. ("process")
        turbsim_exe_path    The path to the TurbSim exe. (path-like)
        fast_exe_path       The path to the FAST exe. (path-like)
        workers             The number of workers (int)
        outdir              The output directory (path-like)
        local               ``True`` if running locally; otherwise, ``False``. (bool)
        port                The port on which the remote scheduler is running, if ``local`` is ``False``. (int)
        """
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
        """Run the spec by generating tasks using the spawner
        
        :param spawner: The task spawner
        :type spawner: :class:`TaskSpawner`
        :param spec: The specification
        :type spec: :class:`SpecificationModel`
        """
        tasks = generate_tasks_from_spec(spawner, spec.root_node, self._out_dir)
        build(tasks, local_scheduler=self._local, workers=self._workers, scheduler_port=self._port)
