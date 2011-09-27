import math
import itertools
import gametheory.deception.replicator_comparison.payoffs as p
import sys
import multiprocessing as mp
import cPickle
from sage.all import Graphics, polygon

effective_zero_diff = 1e-11
effective_zero = 1e-10

def graph_receivers(pop):
    s = Graphics()
    for i, (popi, popt) in enumerate(pop):
        if popt == 0: color = (.5, 0, 0)
        elif popt == 1: color = (0, 0, .5)
        elif popt == 2: color = (0, .5, 0)
        s += polygon([(i,0),((i+1), 0),((i+1), popi), (i, popi)], rgbcolor=color)
    
    return s

def graph_senders(pop):
    return graph_receivers([(popi, 2) for popi in pop])

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
    
def receiver_matrix(r, t):
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
        return sender_matrix(r)
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
                 
def interaction(n, s, r, n_r_1):
    if r >= n_r_1: 
        r -= n_r_1
        rt = 1
    else:
        rt = 0
        
    smat = sender_matrix(s)
    rmat = receiver_matrix(r, rt)
    return [(i, rmat[srow.index(1)].index(1)) for i, srow in enumerate(smat)]

def pop_equals(last, this):
    senders_equal = not any(abs(i - j) >= effective_zero_diff for i, j in itertools.izip(last[0], this[0]))
    receivers_equal = not any(abs(i - j) >= effective_zero_diff for (i, ti), (j, tj) in itertools.izip(last[1], this[1]))
    return senders_equal and receivers_equal

def run_simulation(dup_num, s_payoffs, r_payoffs, r_payoff_lambda, r_comb_cost, r_noncomb_cost, filename = None, output_skip = 1, graph_file = None, graph_skip = 10, quiet = False):
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
        graph_senders(initial_senders).save(graph_file % (dup_num, 0, "senders"), ymin=-0.1, ymax=1.1)
        graph_receivers(initial_receivers).save(graph_file % (dup_num, 0, "receivers"), ymin=-0.1, ymax=1.1)
    
    while not pop_equals(last_generation, this_generation):
        generation_count += 1
        last_generation = this_generation
        this_generation = step_generation(interactions, *last_generation, s_payoffs=s_payoffs, r_payoffs=r_payoffs)
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
            graph_senders(this_generation[0]).save(graph_file % (dup_num, generation_count, "senders"), xmin=-0.1, ymin=-0.1, ymax=1.1)
            graph_receivers(this_generation[1]).save(graph_file % (dup_num, generation_count, "receivers"), xmin=-0.1, ymin=-0.1, ymax=1.1)    
    
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
        graph_senders(this_generation[0]).save(graph_file % (dup_num, generation_count, "senders"), xmin=-0.1, ymin=-0.1, ymax=1.1)
        graph_receivers(this_generation[1]).save(graph_file % (dup_num, generation_count, "receivers"), xmin=-0.1, ymin=-0.1, ymax=1.1)
    
    return ((initial_senders, initial_receivers), this_generation, generation_count)

def run_simulation_imap(args):
    return run_simulation(*args)
    
def step_generation(interactions, senders, receivers, s_payoffs, r_payoffs):
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

def go_baby_go(options, s_payoffs, r_payoffs):
    
    output_base = "%s/%%s" % (options.output_dir,)
    graph_file_base = "%s/%s" % (options.output_dir,options.graph_file)
    
    stats = open(output_base % (options.stats_file,), "wb")
    
    def out_name(i):
        if options.file_dump:
            return output_base % (options.output_file % (i + 1,),) 
        else:
            return None
    
    if options.pool_size > 1:
        pool = mp.Pool(options.pool_size)
        if not options.quiet:
            print "Pool: %s" % pool 
        
        logger = mp.log_to_stderr()
        
        if not options.quiet:
            print "Running %i duplications." % (options.dup,)
        
        tasks = [(i, s_payoffs, r_payoffs, options.lam, options.rc_cost, options.rnc_cost, out_name(i), options.skip, graph_file_base, options.graph_skip, options.quiet) for i in range(options.dup)]
        
        results = pool.imap_unordered(run_simulation_imap, tasks)
        finished_count = 0
        print >>stats, cPickle.dumps(options)
        print >>stats
        for result in results:
            finished_count += 1
            if not options.quiet:
                print result[2], result[1], result[0]
            print >>stats, cPickle.dumps(result)
            print >>stats
            stats.flush()
            #os.fsync()
            print "done #%i (%i generations)" % (finished_count,result[2])
    else:
        for i in range(options.dup):
            result = run_simulation(i, s_payoffs, r_payoffs, options.lam, options.rc_cost, options.rnc_cost, out_name(i), options.skip, graph_file_base, options.graph_skip, options.quiet)
            if not options.quiet:
                print result[2], result[1], result[0]
                print >>stats, cPickle.dumps(result)
                print >>stats
                stats.flush()
                
                print "done %i" % (i,)
                            
    stats.close()
    if options.tweet:
        import Twitter
        
        Twitter.tweet(options.tweetmsg, options.tweetat)
        

def run():
    from optparse import OptionParser

    oparser = OptionParser()
    oparser.add_option("-d", "--duplications", type="int", action="store", dest="dup", default=1, help="number of duplications")
    oparser.add_option("-r", "--routine", action="store", choices=["simil0","simil1","simil2"], dest="routine", help="name of routine to run")
    oparser.add_option("-o", "--output", action="store", dest="output_dir", default="./output", help="directory to dump output files")
    oparser.add_option("-f", "--filename", action="store", dest="output_file", default="duplication_%i", help="output file name template")
    oparser.add_option("--nofiledump", action="store_false", dest="file_dump", default=True, help="do not output duplication files")
    oparser.add_option("-k", "--skip", action="store", type="int", dest="skip", default=1, help="number of generations between dumping output -- 0 for only at the end")
    oparser.add_option("-s", "--statsfile", action="store", dest="stats_file", default="aggregate", help="file for aggregate stats to be dumped")
    oparser.add_option("-m", "--poolsize", action="store", type="int", dest="pool_size", default=2, help="number of parallel computations to undertake")
    oparser.add_option("-q", "--quiet", action="store_true", dest="quiet", default=False, help="suppress most standard output")
    oparser.add_option("-l", "--lambda", action="store", type="float", dest="lam", default=.5, help="value of the lambda parameter")
    oparser.add_option("--cc", action="store", type="float", dest="rc_cost", default=4., help="cost parameter for combinatorial receviers")
    oparser.add_option("--nc", action="store", type="float", dest="rnc_cost", default=8., help="cost parameter for non-combinatorial receivers")
    oparser.add_option("-g","--graph", action="store", type="int", dest="graph_skip", default=10, help="graph the population in increments of this many generations (-1 for never, 0 for start and end only)")
    oparser.add_option("--graphfile", action="store", dest="graph_file", default="duplication_%i_gen_%i_%s.png", help="file name template for population graphs")
    oparser.add_option("--tweet", action="store_true", dest="tweet", default=False, help="send tweet when complete")
    oparser.add_option("--tweetmsg", action="store", dest="tweetmsg", default="simulation complete", help="the message to send in the tweet")
    oparser.add_option("--tweetat", action="store", dest="tweetat", default=None, help="twitter/identi.ca username to @-target")

    (options,args) = oparser.parse_args()

    if not options.dup or options.dup <= 0:
        oparser.error("Number of duplications must be positive")

    if options.lam <= 0.:
        oparser.error("Lambda parameter must be positive")

    if options.lam > .5:
        oparser.error("Unable to handle lambda > .5")

    if options.rc_cost <= 0. or options.rnc_cost <= 0.:
        oparser.error("Cost parameters must be positive")

    if options.rc_cost >= options.rnc_cost:
        oparser.error("non-combinatorial cost must be greater than combinatorial cost")

    r_payoffs = p.receiver_sim(options.lam, options.rc_cost, options.rnc_cost)

    if options.routine == "simil0": #common interest
        s_payoffs = p.sender_sim_0()

        go_baby_go(options, s_payoffs, r_payoffs)

    elif options.routine == "simil1": #sender map 1
        s_payoffs = p.sender_sim_1()

        go_baby_go(options, s_payoffs, r_payoffs)

    elif options.routine == "simil2": #sender map 3
        s_payoffs = p.sender_sim_2()

        go_baby_go(options, s_payoffs, r_payoffs)

    else:
        oparser.error("Unknown routine selected")

if __name__ == '__main__':
    run()
