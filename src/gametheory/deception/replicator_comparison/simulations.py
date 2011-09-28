import gametheory.deception.replicator_comparison.payoffs as p
import math
import itertools
import sys

from gametheory.base.simulation import effective_zero_diff, effective_zero
from gametheory.base.simulation import Simulation as SimBase
from sage.all import Graphics, polygon

class Simulation(SimBase):

    _choices = ["simil0","simil1","simil2"]

    def _setParserOptions(self):
        self._oparser.add_option("-r", "--routine", action="store", choices=self._choices, dest="routine", help="name of routine to run")
        self._oparser.add_option("-l", "--lambda", action="store", type="float", dest="lam", default=.5, help="value of the lambda parameter")
        self._oparser.add_option("--cc", action="store", type="float", dest="rc_cost", default=4., help="cost parameter for combinatorial receviers")
        self._oparser.add_option("--nc", action="store", type="float", dest="rnc_cost", default=8., help="cost parameter for non-combinatorial receivers")
        self._oparser.add_option("--graph", action="store", type="int", dest="graph_skip", default=10, help="graph the population in increments of this many generations (-1 for never, 0 for start and end only)")
        self._oparser.add_option("--graphfile", action="store", dest="graph_file", default="duplication_%i_gen_%i_%s.png", help="file name template for population graphs")
        self._oparser.add_option("--tweet", action="store_true", dest="tweet", default=False, help="send tweet when complete")
        self._oparser.add_option("--tweetmsg", action="store", dest="tweetmsg", default="simulation complete", help="the message to send in the tweet")
        self._oparser.add_option("--tweetat", action="store", dest="tweetat", default=None, help="twitter/identi.ca username to @-target")

    def _checkParserOptions(self):
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


    def _setData(self):
        self._data['r_payoffs'] = p.receiverSim(self._options.lam, self._options.rc_cost, self._options.rnc_cost)

        if self._options.routine == "simil0": #common interest
            self._data['s_payoffs'] = p.senderSim0()

        elif self._options.routine == "simil1": #sender map 1
            self._data['s_payoffs'] = p.senderSim1()

        elif self._options.routine == "simil2": #sender map 3
            self._data['s_payoffs'] = p.senderSim2()

        self._task_dup_num = True

    def _buildTask(self):
        return [self._data['s_payoffs'], self._data['r_payoffs'], self._options.lam, self._options.rc_cost, self._options.rnc_cost, "{0}/{1}".format(self._options.output_dir, self._options.graph_file), self._options.graph_skip]

    def _formatRun(self, result):
        return "{2} {1} {0}".format(*result)

    def _whenDone(self):
        if self._options.tweet:
            import Twitter
            Twitter.tweet(self._options.tweetmsg, self._options.tweetat)

def senderMatrix(s):
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
    
def receiverMatrix(r, t):
    if t != 0 and t != 1: raise ValueError("Type parameter must be 0 or 1")
    
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
        #return ((r & 1,
        #         (r & 2) >> 1,
        #         (r & 4) >> 2,
        #         (~(r & 1) & (~(r & 2) >> 1) & (~(r & 4) >> 2))),
        #        ((r & 8) >> 3,
        #         (r & 16) >> 4,
        #         (r & 32) >> 5,
        #         ((~(r & 8) >> 3) & (~(r & 16) >> 4) & (~(r & 32) >> 5))),
        #        ((r & 64) >> 6,
        #         (r & 128) >> 7,
        #         (r & 256) >> 8,
        #         ((~(r & 64) >> 6) & (~(r & 128) >> 7) & (~(r & 256) >> 8))),
        #        ((r & 512) >> 9,
        #         (r & 1024) >> 10,
        #         (r & 2048) >> 11,
        #         ((~(r & 512) >> 9) & (~(r & 1024) >> 10) & (~(r & 2048) >> 11))))

def runSimulation(args):
    def graphReceivers(pop):
        s = Graphics()
        for i, (popi, popt) in enumerate(pop):
            if popt == 0: color = (.5, 0, 0)
            elif popt == 1: color = (0, 0, .5)
            elif popt == 2: color = (0, .5, 0)
            s += polygon([(i,0),((i+1), 0),((i+1), popi), (i, popi)], rgbcolor=color)

        return s

    def graphSenders(pop):
        return graphReceivers([(popi, 2) for popi in pop])

    def interaction(n, s, r, n_r_1):
        if r >= n_r_1:
            r -= n_r_1
            rt = 1
        else:
            rt = 0

        smat = senderMatrix(s)
        rmat = receiverMatrix(r, rt)
        return [(i, rmat[srow.index(1)].index(1)) for i, srow in enumerate(smat)]

    def popEquals(last, this):
        senders_equal = not any(abs(i - j) >= effective_zero_diff for i, j in itertools.izip(last[0], this[0]))
        receivers_equal = not any(abs(i - j) >= effective_zero_diff for (i, ti), (j, tj) in itertools.izip(last[1], this[1]))
        return senders_equal and receivers_equal

    def stepGeneration(interactions, senders, receivers, s_payoffs, r_payoffs):
        # x_i(t+1) = (a + u(e^i, x(t)))*x_i(t) / (a + u(x(t), x(t)))
        # a is background (lifetime) birthrate -- set to 0

        s_fitness = [0.] * len(senders)
        r_fitness = [0.] * len(receivers)
        for (s, sp), (r, (rp, rt)) in itertools.product(enumerate(senders), enumerate(receivers)):

            state_acts = interactions[(s, r)]
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

    def _run(dup_num, s_payoffs, r_payoffs, r_payoff_lambda, r_comb_cost, r_noncomb_cost, graph_file = None, graph_skip = 10, filename = None, output_skip = 1, quiet = False):
        import numpy.random.mtrand as rand
        dup_num = dup_num + 1

        if filename:
            out_stdout = False
            out = open(filename, "w")
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

        if not out_stdout or not quiet:
            print >>out, "Initial State"
            print >>out, "Senders:"
            print >>out, "\t", initial_senders
            print >>out, "Receivers:"
            print >>out, "\t", initial_receivers
            print >>out

        last_generation = ((0.,),((0., 0),))
        generation_count = 0
        interactions = dict([((s, r), interaction(4, s, r, n_r_1)) for s, r in itertools.product(range(n_s), range(n_r_1 + n_r_2))])

        if graph_skip >= 0:
            graphSenders(initial_senders).save(graph_file % (dup_num, 0, "senders"), ymin=-0.1, ymax=1.1)
            graphReceivers(initial_receivers).save(graph_file % (dup_num, 0, "receivers"), ymin=-0.1, ymax=1.1)

        while not popEquals(last_generation, this_generation):
            generation_count += 1
            last_generation = this_generation
            this_generation = stepGeneration(interactions, *last_generation, s_payoffs=s_payoffs, r_payoffs=r_payoffs)
            #for i in this_generation:
            #    assert(abs(math.fsum(i) - 1.) < effective_zero_diff)

            if (not out_stdout or not quiet) and output_skip and generation_count % output_skip == 0:
                print >>out, "-" * 72
                print >>out, "Generation %i" %(generation_count,)
                print >>out, "Senders:"
                print >>out, "\t", this_generation[0]
                print >>out, "Receivers:"
                print >>out, "\t", this_generation[1]
                print >>out
                out.flush()

            if graph_file and graph_skip > 0 and generation_count % graph_skip == 0:
                graphSenders(this_generation[0]).save(graph_file % (dup_num, generation_count, "senders"), xmin=-0.1, ymin=-0.1, ymax=1.1)
                graphReceivers(this_generation[1]).save(graph_file % (dup_num, generation_count, "receivers"), xmin=-0.1, ymin=-0.1, ymax=1.1)

        if not out_stdout or not quiet:
            print >>out, "=" * 72
            print >>out, "Stable state! (%i generations)" % (generation_count,)
            print >>out, "Senders:"
            print >>out, "\t", this_generation[0]
            for i, pop in enumerate(this_generation[0]):
                if pop != 0.:
                    print >>out, "\t\t",i,":", pop
            print >>out
            print >>out, "Receivers:"
            print >>out, "\t", this_generation[1]
            for i, pop in enumerate(this_generation[1]):
                if pop != 0.:
                    print >>out, "\t\t",i,":", pop

        if not out_stdout:
            out.close()

        if graph_skip >= 0:
            graphSenders(this_generation[0]).save(graph_file % (dup_num, generation_count, "senders"), xmin=-0.1, ymin=-0.1, ymax=1.1)
            graphReceivers(this_generation[1]).save(graph_file % (dup_num, generation_count, "receivers"), xmin=-0.1, ymin=-0.1, ymax=1.1)

        return ((initial_senders, initial_receivers), this_generation, generation_count)
    
    _run(*args)
    

def run():
    sim = Simulation(runSimulation)
    sim.go()

if __name__ == '__main__':
    run()
