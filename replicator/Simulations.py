import math
import itertools
import Payoffs as p
import sys
import multiprocessing as mp
import logging
import cPickle

effective_zero_diff = 1e-11
effective_zero = 1e-10

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

def interaction(n, s, r):
    smat = sender_matrix(s)
    rmat = receiver_matrix(r)
    return [(i, rmat[smat[i].index(1)].index(1)) for i in range(n)]

def pop_equals(last, this):
    senders_equal = not any(abs(i - j) >= effective_zero_diff for i, j in itertools.izip(last[0], this[0]))
    receivers_equal = not any(abs(i - j) >= effective_zero_diff for i, j in itertools.izip(last[1], this[1]))
    return senders_equal and receivers_equal

def run_simulation(s_payoffs, r_payoffs, filename = None, output_skip = 1, quiet = False):
    import numpy.random.mtrand as rand
    if filename:
        out_stdout = False
        out = open(filename, "w")
    else:
        out_stdout = True
        out = sys.stdout
    
    n_s = 256 #S_s = range(n_s)
    n_r = 16 #S_r = range(n_r)
    rand.seed()
    initial_senders = tuple(rand.dirichlet([1] * n_s))
    initial_receivers = tuple(rand.dirichlet([1] * n_r))
    this_generation = (initial_senders, initial_receivers)
    
    if not out_stdout or not quiet:
        print >>out, "Initial State"
        print >>out, "Senders:"
        print >>out, "\t", initial_senders
        print >>out, "Receivers:"
        print >>out, "\t", initial_receivers
        print >>out
    
    last_generation = ((0.,),(0.,))
    generation_count = 0
    while not pop_equals(last_generation, this_generation):
        generation_count += 1
        last_generation = this_generation
        this_generation = step_generation(*last_generation, s_payoffs=s_payoffs, r_payoffs=r_payoffs)
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
    
    return ((initial_senders, initial_receivers), this_generation, generation_count)

def run_simulation_imap(args):
    return run_simulation(*args)
    
def step_generation(senders, receivers, s_payoffs, r_payoffs):
    # x_i(t+1) = (a + u(e^i, x(t)))*x_i(t) / (a + u(x(t), x(t)))
    # a is background (lifetime) birthrate -- set to 0
    
    n_s = len(senders)
    n_r = len(receivers)
    
    s_fitness = [0] * n_s
    r_fitness = [0] * n_r
    for s, r in itertools.product(range(n_s), range(n_r)):
        state_acts = interaction(4, s, r)
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

def go_baby_go(options, s_payoffs, r_payoffs):
    
    output_base = "%s/%%s" % (options.output_dir,)
    
    stats = open(output_base % (options.stats_file,), "wb")
    
    pool = mp.Pool(options.pool_size)
    if not options.quiet:
        print "Pool: %s" % pool 
    
    logger = mp.log_to_stderr()
    
    if not options.quiet:
        print "Running %i duplications." % (options.dup,) 
    
    if options.file_dump:
        tasks = [(s_payoffs, r_payoffs, output_base % (options.output_file % (i + 1,),), options.skip) for i in range(options.dup)]
    else:
        tasks = [(s_payoffs, r_payoffs, None, options.skip, options.quiet)] * options.dup
    results = pool.imap_unordered(run_simulation_imap, tasks)
    finished_count = 0
    for result in results:
        finished_count += 1
        if not options.quiet:
            print result[2], result[1], result[0]
        print >>stats, cPickle.dumps(result)
        print >>stats
        stats.flush()
        #os.fsync()
        print "done #%i" % (finished_count,)
    
    stats.close()

if __name__ == '__main__':
    from optparse import OptionParser
    
    oparser = OptionParser()
    oparser.add_option("-d", "--duplications", type="int", action="store", dest="dup", default=1, help="number of duplications")
    oparser.add_option("-r", "--routine", action="store", choices=["simil0","simil1","simil2","dist0","dist1","dist2"], dest="routine", help="name of routine to run")
    oparser.add_option("-o", "--output", action="store", dest="output_dir", default="./output", help="directory to dump output files")
    oparser.add_option("-f", "--filename", action="store", dest="output_file", default="duplication_%i", help="output file name template")
    oparser.add_option("-g", "--nofiledump", action="store_false", dest="file_dump", default=True, help="do not output duplication files")
    oparser.add_option("-k", "--skip", action="store", type="int", dest="skip", default=1, help="number of generations between dumping output -- 0 for only at the end")
    oparser.add_option("-s", "--statsfile", action="store", dest="stats_file", default="aggregate", help="file for aggregate stats to be dumped")
    oparser.add_option("-m", "--poolsize", action="store", type="int", dest="pool_size", default=2, help="number of parallel computations to undertake")
    oparser.add_option("-q", "--quiet", action="store_true", dest="quiet", default=False, help="suppress standard output")
    
    (options,args) = oparser.parse_args()
    
    if not options.dup or options.dup <= 0:
        oparser.error("Number of duplications must be positive")

    if options.routine == "simil0": #common interest
        s_payoffs = p.receiver_sim_2[0]
        r_payoffs = p.receiver_sim_2[0]


        go_baby_go(options, s_payoffs, r_payoffs)
            
    elif options.routine == "simil1": #sender map 1
        s_payoffs = p.sender_sim_2_1
        r_payoffs = p.receiver_sim_2[0]

        go_baby_go(options, s_payoffs, r_payoffs)
    
    elif options.routine == "simil2": #sender map 3
        s_payoffs = p.sender_sim_2_2
        r_payoffs = p.receiver_sim_2[0]

        go_baby_go(options, s_payoffs, r_payoffs)
    
    elif options.routine == "dist0": #common interest
        s_payoffs = p.receiver_dist_2[0]
        r_payoffs = p.receiver_dist_2[0]

        go_baby_go(options, s_payoffs, r_payoffs)
    
    elif options.routine == "dist1": #sender map 1
        s_payoffs = p.sender_dist_2_1
        r_payoffs = p.receiver_dist_2[0]

        go_baby_go(options, s_payoffs, r_payoffs)
    
    elif options.routine == "dist2": #sender map 3
        s_payoffs = p.sender_dist_2_2
        r_payoffs = p.receiver_dist_2[0]

        go_baby_go(options, s_payoffs, r_payoffs)
    
    else:
        oparser.error("Unknown routine selected")
