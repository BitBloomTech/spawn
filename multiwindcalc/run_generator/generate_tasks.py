import os.path as path
from multiwindcalc.simulation_inputs.nrel_simulation_input import FastInput, TurbsimInput
from multiwindcalc.run_generator.fast_simulation_spawner import FastSimulationSpawner, TurbsimSpawner


def generate_tasks(task_spawner, run_list):
    """Generate list of luigi.Task for a flat 1D run list"""
    tasks = []
    for run in run_list:
        branch = task_spawner.branch()
        for k, v in run.items():
            setattr(branch, k, v)
        tasks.append(branch.spawn())
    return tasks


def generate_aeroelastic_simulations(spec):
    """Generate list of aeroelastic simulation tasks including pre-processing tasks"""
    wind_spawner = TurbsimSpawner(path.join(spec['output_base_dir'], 'wind'),
                                  TurbsimInput.from_file(spec['base_wind_input']), spec['wind_executable'])
    task_spawner = FastSimulationSpawner(path.join(spec['output_base_dir'], 'runs'),
                                         FastInput.from_file(spec['base_time_domain_input']),
                                         spec['time_domain_executable'], wind_spawner)
    return generate_tasks(task_spawner, spec['runs'])
