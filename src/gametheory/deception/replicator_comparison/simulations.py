import gametheory.deception.replicator_comparison.payoffs as p
import itertools
import math
import numpy.random as rand
import sys

from gametheory.base.dynamics.discrete_replicator import NPopDiscreteReplicatorDynamics as SimBase
from gametheory.base.simulation import SimulationBatch as SimBatchBase

_nograpics = False
try:
    from sage.all import Graphics, polygon
except ImportError:
    _nographics = True

effective_zero = 1e-10

class SimulationBatch(SimBatchBase):

    _choices = ["simil0","simil1","simil2"]

    def _set_options(self):
        self._oparser.add_option("-r", "--routine", action="store", choices=self._choices, dest="routine", help="name of routine to run")
        self._oparser.add_option("-l", "--lambda", action="store", type="float", dest="lam", default=.5, help="value of the lambda parameter")
        self._oparser.add_option("--cc", action="store", type="float", dest="rc_cost", default=4., help="cost parameter for combinatorial receviers")
        self._oparser.add_option("--nc", action="store", type="float", dest="rnc_cost", default=8., help="cost parameter for non-combinatorial receivers")
        self._oparser.add_option("--graph", action="store", type="int", dest="graph_skip", default=10, help="graph the population in increments of this many generations (-1 for never, 0 for start and end only)")
        self._oparser.add_option("--graphfile", action="store", dest="graph_file", default="duplication_{0}_gen_{1}_{2}.png", help="file name template for population graphs")

    def _check_options(self):
        if not self._options.routine in self._choices:
            self._oparser.error("Unknown routine selected")

        if self._options.lam <= 0.:
            self._oparser.error("Lambda parameter must be positive")

        if self._options.lam > .5:
            self._oparser.error("Unable to handle lambda > .5")

        if self._options.rc_cost <= 0. or self._options.rnc_cost <= 0.:
            self._oparser.error("Cost parameters must be positive")

        if self._options.rc_cost >= self._options.rnc_cost:
            self._oparser.error("non-combinatorial cost must be greater than combinatorial cost")


    def _set_data(self):
        self._data['r_payoffs'] = p.receiver_sim(self._options.lam, self._options.rc_cost, self._options.rnc_cost)

        if self._options.routine == "simil0": #common interest
            self._data['s_payoffs'] = p.sender_sim_0()

        elif self._options.routine == "simil1": #sender map 1
            self._data['s_payoffs'] = p.sender_sim_1()

        elif self._options.routine == "simil2": #sender map 3
            self._data['s_payoffs'] = p.sender_sim_2()

        self._data['gphx_file'] = "{0}/{1}".format(self._options.output_dir, self._options.graph_file)
        self._data['gphx_skip'] = self._options.graph_skip

    def _format_run(self, result):
        return "{2} {1} {0}".format(*result)

class Simulation(SimBase):
    
    _types = [
        range(256),
        range(256 + 16)
    ]

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
    def receiver_matrix(r, t):
        if t != 0 and t != 1:
            raise ValueError("Type parameter must be 0 or 1")

        if t == 0:
            return (((r & 1) & ((r & 4) >> 2),
                     (r & 1) & (~(r & 4) >> 2),
                     (~(r & 1) & ((r & 4) >> 2)) & 1,
                     (~(r & 1) & (~(r & 4) >> 2)) & 1),
                    ((r & 1) & ((r & 8) >> 3),
                     (r & 1) & (~(r & 8) >> 3),
                     (~(r & 1) & ((r & 8) >> 3)) & 1,
                     (~(r & 1) & (~(r & 8) >> 3)) & 1),
                    (((r & 2) >> 1) & ((r & 4) >> 2),
                     ((r & 2) >> 1) & (~(r & 4) >> 2),
                     ((~(r & 2) >> 1) & ((r & 4) >> 2)) & 1,
                     ((~(r & 2) >> 1) & (~(r & 4) >> 2)) & 1),
                    (((r & 2) >> 1) & ((r & 8) >> 3),
                     ((r & 2) >> 1) & (~(r & 8) >> 3),
                     ((~(r & 2) >> 1) & ((r & 8) >> 3)) & 1,
                     ((~(r & 2) >> 1) & (~(r & 8) >> 3)) & 1))
        elif t == 1:
            return senderMatrix(r)

    @classmethod
    def graph_receivers(cls, pop):
        if not _nographics:
            s = Graphics()
            for i, (popi, popt) in enumerate(pop):
                if popt == 0: color = (.5, 0, 0)
                elif popt == 1: color = (0, 0, .5)
                elif popt == 2: color = (0, .5, 0)
                s += polygon([(i,0),((i+1), 0),((i+1), popi), (i, popi)], rgbcolor=color)

            return s
        else:
            return None

    @classmethod
    def graph_senders(cls, pop):
        return cls.graph_receivers([(popi, 2) for popi in pop])
        
    def _interaction(self, me, sender, receiver):
        n = 4
        n_r_1 = 256
        
        if receiver >= n_r_1:
            reciever -= n_r_1
            rt = 1
        else:
            rt = 0
            
        smat = self.sender_matrix(sender)
        rmat = self.receiver_matrix(reciever, rt)
        
        state_acts = [(i, rmat[srow.index(1)].index(1)) for i, srow in enumerate(smat)]
        state_probs = [1. / float(n) for _ in xrange(len(smat))]
        
        self._interactions = dict([((s, r), self._interaction(4, s, r, n_r_1)) for s, r in itertools.product(range(n_s), range(n_r_1 + n_r_2))])

    def step_generation(self, senders, receivers):
        # x_i(t+1) = (a + u(e^i, x(t)))*x_i(t) / (a + u(x(t), x(t)))
        # a is background (lifetime) birthrate -- set to 0

        s_payoffs = self._data['s_payoffs']
        r_payoffs = self._data['r_payoffs']
        s_fitness = [0.] * len(senders)
        r_fitness = [0.] * len(receivers)

        for (s, sp), (r, (rp, rt)) in itertools.product(enumerate(senders), enumerate(receivers)):
            state_acts = self._interactions[(s, r)]
            s_fitness[s] += math.fsum(s_payoffs[state][act] * rp for state, act in state_acts) / 4.
            r_fitness[r] += math.fsum(r_payoffs[rt][state][act] * sp for state, act in state_acts) / 4.

        avg_s = math.fsum(s_fitness[s] * sp for s, sp in enumerate(senders))
        avg_r = math.fsum(r_fitness[r] * rp for r, (rp, rt) in enumerate(receivers))

        new_senders = [s_fitness[s] * sp / avg_s for s, sp in enumerate(senders)]
        new_receivers = [(r_fitness[r] * rp / avg_r, rt) for r, (rp, rt) in enumerate(receivers)]

        for s, sp in enumerate(new_senders):
            if sp < effective_zero:
                new_senders[s] = 0.
        for r, (rp, rt) in enumerate(new_receivers):
            if rp < effective_zero:
                new_receivers[r] = (0., rt)

        return (tuple(new_senders), tuple(new_receivers))

    def run(self):
        rand.seed()
        dup_num = self._iteration + 1

        if self._outfile:
            out_stdout = False
            out = open(self._outfile, "w")
        else:
            out_stdout = True
            out = sys.stdout

        n_s = 256
        n_r_1 = 16
        n_r_2 = 256
        rand.seed()
        initial_senders = tuple(rand.dirichlet([1] * n_s))
        tlist = [0] * n_r_1
        tlist.extend([1] * n_r_2)
        initial_receivers = tuple(zip(rand.dirichlet([1] * (n_r_1 + n_r_2)), tlist))
        this_generation = (initial_senders, initial_receivers)

        if not out_stdout or not this._quiet:
            print >>out, "Initial State"
            print >>out, "Senders:"
            print >>out, "\t", initial_senders
            print >>out, "Receivers:"
            print >>out, "\t", initial_receivers
            print >>out

        last_generation = ((0.,),((0., 0),))
        generation_count = 0

        

        if self._data['gphx_skip'] >= 0:
            self.graph_senders(initial_senders).save(self._data['gphx_file'].format(dup_num, 0, "senders"), ymin=-0.1, ymax=1.1)
            self.graph_receivers(initial_receivers).save(self._data['gphx_file'].format(dup_num, 0, "receivers"), ymin=-0.1, ymax=1.1)

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

            if self._data['gphx_file'] and self._data['gphx_skip'] > 0 and generation_count % self._data['gphx_skip'] == 0:
                self.graph_senders(this_generation[0]).save(self._data['gphx_file'].format(dup_num, generation_count, "senders"), xmin=-0.1, ymin=-0.1, ymax=1.1)
                self.graph_receivers(this_generation[1]).save(self._data['gphx_file'].format(dup_num, generation_count, "receivers"), xmin=-0.1, ymin=-0.1, ymax=1.1)

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

        if self._data['gphx_skip'] >= 0:
            self.graph_senders(this_generation[0]).save(self._data['gphx_file'].format(dup_num, generation_count, "senders"), xmin=-0.1, ymin=-0.1, ymax=1.1)
            self.graph_receivers(this_generation[1]).save(self._data['gphx_file'].format(dup_num, generation_count, "receivers"), xmin=-0.1, ymin=-0.1, ymax=1.1)

        return ((initial_senders, initial_receivers), this_generation, generation_count)
        