import itertools
import math
import numpy.random as rand
import sys

from gametheory.base.simulation import SimulationBatch as SimBatchBase
from gametheory.base.simulation import Simulation as SimBase

import gametheory.deception.replicator.payoffs as p

effective_zero = 1e-10

class SimulationBatch(SimBatchBase):

    _choices = ["simil0","simil1","simil2","dist0","dist1","dist2"]

    def _set_options(self):
        self._oparser.add_option("-r", "--routine", action="store", choices=self._choices, dest="routine", help="name of routine to run")

    def _check_options(self):
        if not self._options.routine in self._choices:
            self._oparser.error("Unknown routine selected")


    def _set_data(self):
        if self._options.routine == "simil0": #common interest
            self._data['s_payoffs'] = p.receiver_sim_2[0]
            self._data['r_payoffs'] = p.receiver_sim_2[0]

        elif self._options.routine == "simil1": #sender map 1
            self._data['s_payoffs'] = p.sender_sim_2_1
            self._data['r_payoffs'] = p.receiver_sim_2[0]

        elif self._options.routine == "simil2": #sender map 3
            self._data['s_payoffs'] = p.sender_sim_2_2
            self._data['r_payoffs'] = p.receiver_sim_2[0]

        elif self._options.routine == "dist0": #common interest
            self._data['s_payoffs'] = p.receiver_dist_2[0]
            self._data['r_payoffs'] = p.receiver_dist_2[0]

        elif self._options.routine == "dist1": #sender map 1
            self._data['s_payoffs'] = p.sender_dist_2_1
            self._data['r_payoffs'] = p.receiver_dist_2[0]

        elif self._options.routine == "dist2": #sender map 3
            self._data['s_payoffs'] = p.sender_dist_2_2
            self._data['r_payoffs'] = p.receiver_dist_2[0]

    def _format_run(self, result):
        return "{2} {1} {0}".format(*result)

class Simulation(SimBase):

    @staticmethod
    def sender_matrix(s):
        return (   (
                        (s & 1) & ((s & 16) >> 4),
                        (s & 1) & (~(s & 16) >> 4),
                        (~(s & 1) & ((s & 16) >> 4)) & 1,
                        (~(s & 1) & (~(s & 16) >> 4)) & 1
                    ),
                    (
                        ((s & 2) >> 1) & ((s & 32) >> 5),
                        ((s & 2) >> 1) & (~(s & 32) >> 5),
                        ((~(s & 2) >> 1) & ((s & 32) >> 5)) & 1,
                        ((~(s & 2) >> 1) & (~(s & 32) >> 5)) & 1
                    ),
                    (
                        ((s & 4) >> 2) & ((s & 64) >> 6),
                        ((s & 4) >> 2) & (~(s & 64) >> 6),
                        ((~(s & 4) >> 2) & ((s & 64) >> 6)) & 1,
                        ((~(s & 4) >> 2) & (~(s & 64) >> 6)) & 1
                    ),
                    (
                        ((s & 8) >> 3) & ((s & 128) >> 7),
                        ((s & 8) >> 3) & (~(s & 128) >> 7),
                        ((~(s & 8) >> 3) & ((s & 128) >> 7)) & 1,
                        ((~(s & 8) >> 3) & (~(s & 128) >> 7)) & 1
                    )
                )

    @staticmethod
    def receiver_matrix(r):
        return (    (
                        (r & 1) & ((r & 4) >> 2),
                        (r & 1) & (~(r & 4) >> 2),
                        (~(r & 1) & ((r & 4) >> 2)) & 1,
                        (~(r & 1) & (~(r & 4) >> 2)) & 1
                    ),
                    (
                        (r & 1) & ((r & 8) >> 3),
                        (r & 1) & (~(r & 8) >> 3),
                        (~(r & 1) & ((r & 8) >> 3)) & 1,
                        (~(r & 1) & (~(r & 8) >> 3)) & 1
                    ),
                    (
                        ((r & 2) >> 1) & ((r & 4) >> 2),
                        ((r & 2) >> 1) & (~(r & 4) >> 2),
                        ((~(r & 2) >> 1) & ((r & 4) >> 2)) & 1,
                        ((~(r & 2) >> 1) & (~(r & 4) >> 2)) & 1
                    ),
                    (
                        ((r & 2) >> 1) & ((r & 8) >> 3),
                        ((r & 2) >> 1) & (~(r & 8) >> 3),
                        ((~(r & 2) >> 1) & ((r & 8) >> 3)) & 1,
                        ((~(r & 2) >> 1) & (~(r & 8) >> 3)) & 1
                    )
                )


    @classmethod
    def interaction(cls, n, s, r):
        smat = cls.sender_matrix(s)
        rmat = cls.receiver_matrix(r)
        return [(i, rmat[smat[i].index(1)].index(1)) for i in range(n)]

    @staticmethod
    def pop_equals(last, this):
        senders_equal = not any(abs(i - j) >= effective_zero for i, j in itertools.izip(last[0], this[0]))
        receivers_equal = not any(abs(i - j) >= effective_zero for i, j in itertools.izip(last[1], this[1]))
        return senders_equal and receivers_equal

    def step_generation(self, senders, receivers):
        # x_i(t+1) = (a + u(e^i, x(t)))*x_i(t) / (a + u(x(t), x(t)))
        # a is background (lifetime) birthrate -- set to 0

        s_payoffs = self._data['s_payoffs']
        r_payoffs = self._data['r_payoffs']

        n_s = len(senders)
        n_r = len(receivers)

        s_fitness = [0] * n_s
        r_fitness = [0] * n_r
        for s, r in itertools.product(range(n_s), range(n_r)):
            state_acts = self.interaction(4, s, r)
            s_fitness[s] += math.fsum(s_payoffs[state][act] * receivers[r] for state, act in state_acts) / 4.
            r_fitness[r] += math.fsum(r_payoffs[state][act] * senders[s] for state, act in state_acts) / 4.

        avg_s = math.fsum(s_fitness[s] * senders[s] for s in range(n_s))
        avg_r = math.fsum(r_fitness[r] * receivers[r] for r in range(n_r))

        new_senders = [s_fitness[s] * senders[s] / avg_s for s in range(n_s)]
        new_receivers = [r_fitness[r] * receivers[r] / avg_r for r in range(n_r)]

        for s in range(n_s):
            if new_senders[s] < effective_zero:
                new_senders[s] = 0.
        for r in range(n_r):
            if new_receivers[r] < effective_zero:
                new_receivers[r] = 0.

        return (tuple(new_senders), tuple(new_receivers))

    def run(self):
        rand.seed()

        if self._outfile:
            out_stdout = False
            out = open(self._outfile, "w")
        else:
            out_stdout = True
            out = sys.stdout

        n_s = 256
        n_r = 16
        rand.seed()
        initial_senders = tuple(rand.dirichlet([1] * n_s))
        initial_receivers = tuple(rand.dirichlet([1] * n_r))
        this_generation = (initial_senders, initial_receivers)

        if not out_stdout or not self._quiet:
            print >>out, "Initial State"
            print >>out, "Senders:"
            print >>out, "\t", initial_senders
            print >>out, "Receivers:"
            print >>out, "\t", initial_receivers
            print >>out

        last_generation = ((0.,),(0.,))
        generation_count = 0
        while not self.pop_equals(last_generation, this_generation):
            generation_count += 1
            last_generation = this_generation
            this_generation = self.step_generation(*last_generation)

            if (not out_stdout or not self._quiet) and self._skip and generation_count % self._skip == 0:
                print >>out, "-" * 72
                print >>out, "Generation {0}".format(generation_count)
                print >>out, "Senders:"
                print >>out, "\t{0}".format(this_generation[0])
                print >>out, "Receivers:"
                print >>out, "\t{0}".format(this_generation[1])
                print >>out
                out.flush()

        if not out_stdout or not self._quiet:
            print >>out, "=" * 72
            print >>out, "Stable state! ({0} generations)".format(generation_count)
            print >>out, "Senders:"
            print >>out, "\t{0}".format(this_generation[0])
            for i, pop in enumerate(this_generation[0]):
                if pop != 0.:
                    print >>out, "\t\t{0}: {1}".format(i, pop)
            print >>out
            print >>out, "Receivers:"
            print >>out, "\t{0}".format(this_generation[1])
            for i, pop in enumerate(this_generation[1]):
                if pop != 0.:
                    print >>out, "\t\t{0}: {1}".format(i, pop)

        if not out_stdout:
            out.close()

        return ((initial_senders, initial_receivers), this_generation, generation_count)
