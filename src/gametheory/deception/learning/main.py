def run():
    from gametheory.deception.learning.seltengame import SeltenGame, run_simulation, run_simulation_imap
    import gametheory.deception.learning.payoffs as p
    import multiprocessing as mp
    import logging
    import cPickle
    from optparse import OptionParser

    oparser = OptionParser()
    oparser.add_option("-g", "--generations", type="int", action="store", dest="gen", help="number of generations")
    oparser.add_option("-d", "--duplications", type="int", action="store", dest="dup", default=1, help="number of duplications")
    oparser.add_option("-r", "--routine", action="store", choices=["testing"], dest="routine", help="name of routine to run")
    oparser.add_option("-o", "--output", action="store", dest="output_dir", default="./output", help="directory to dump output files")
    oparser.add_option("-f", "--filename", action="store", dest="output_file", default="duplication_%i", help="output file name template")
    oparser.add_option("-w", "--weight", type="float", action="store", dest="default_weight", default=2., help="default weight for bins")
    oparser.add_option("-k", "--skip", action="store", type="int", dest="skip", default=1, help="number of generations between dumping output -- 0 for only at the end")
    oparser.add_option("-s", "--statsfile", action="store", dest="stats_file", default="aggregate", help="file for aggregate stats to be dumped")
    oparser.add_option("-p", "--poolsize", action="store", type="int", dest="pool_size", default=2, help="number of parallel computations to undertake")

    (options,args) = oparser.parse_args()

    if not options.gen or options.gen <= 0:
        oparser.error("Number of generations must be positive")

    if not options.dup or options.dup <= 0:
        oparser.error("Number of duplications must be positive")

    output_base = "%s/%%s" % (options.output_dir,)

    stats = open(output_base % (options.stats_file,), "wb")

    if options.routine == "testing":
        sg = SeltenGame(2, [2,2],[2,2], p.receiver_sim_2[0], p.receiver_sim_2[0])
        rstars = p.receiver_sim_2[1]

        pool = mp.Pool(options.pool_size)
        print "Pool: %s" % pool

        mp.log_to_stderr()

        print "Running %i duplications of %i generations each." % (options.dup, options.gen)

        tasks = [(sg, output_base % (options.output_file % (i + 1,),), options.gen, options.default_weight, options.skip) for i in range(options.dup)]
        #print "Tasks:", tasks
        results = pool.imap_unordered(run_simulation_imap, tasks)
        for result in results:
            print result[0]
            print >>stats, cPickle.dumps((result[1], result[2], result[3], rstars))
            print >>stats

        #results = [pool.apply_async(run_simulation, task) for task in tasks]
        #for result in results:
        #    result.get()
    else:
        oparser.error("Unknown routine selected")

if __name__ == '__main__':
    run()
