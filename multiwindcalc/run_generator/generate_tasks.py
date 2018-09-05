from multiwindcalc.specification.specification import SpecificationNode


def generate_tasks(task_spawner, run_list):
    """Generate list of luigi.Task for a flat 1D run list"""
    tasks = []
    for run in run_list:
        branch = task_spawner.branch()
        for k, v in run.items():
            setattr(branch, k, v)
        task = branch.spawn()
        task.metadata.update(run)
        tasks.append(task)
    return tasks


def generate_tasks_from_spec(task_spawner, node):
    """Generate list of luigi.Task for a multiwindcalc.SpecificationNode"""
    if not isinstance(node, SpecificationNode):
        raise ValueError('node must be of type ' + SpecificationNode)
    if not node.is_root:
        setattr(task_spawner, node.property_name, node.property_value)
    if not node.children:   # (leaf)
        task = task_spawner.spawn()
        task.metadata.update(node.collected_properties)
        return [task]
    else:   # (branch)
        tasks = []
        for child in node.children:
            branch = task_spawner.branch()
            tasks += generate_tasks_from_spec(branch, child)
        return tasks
