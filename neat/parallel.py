"""
Runs evaluation functions in parallel subprocesses
in order to evaluate multiple genomes at once.
"""
from multiprocessing import Pool


class ParallelEvaluator(object):
    def __init__(self, num_workers, fitness_function, constraint_function=None, timeout=None):
        """
        fitness_function should take one argument, a tuple of
        (genome object, config object), and return
        a single float (the genome's fitness).
        constraint_function should take one argument, a tuple of
        (genome object, config object), and return
        a single bool (the genome's validity).
        """
        self.num_workers = num_workers
        self.fitness_function = fitness_function
        self.constraint_function = constraint_function
        self.timeout = timeout
        self.pool = Pool(num_workers)

    def __del__(self):
        self.pool.close() # should this be terminate?
        self.pool.join()

    def evaluate_fitness(self, genomes, config, generation):
        jobs = []
        for genome_id, genome in genomes:
            jobs.append(self.pool.apply_async(self.fitness_function, (genome, config, genome_id, generation)))

        # assign the fitness back to each genome
        for job, (genome_id, genome) in zip(jobs, genomes):
            genome.fitness = job.get(timeout=self.timeout)

    def evaluate_constraint(self, genomes, config, generation):
        jobs = []
        for genome_id, genome in genomes:
            jobs.append(self.pool.apply_async(self.constraint_function, (genome, config, genome_id, generation)))

        # return the validity of each genome
        validity = []
        for job, (genome_id, genome) in zip(jobs, genomes):
            validity.append(job.get(timeout=self.timeout))
        return validity
