receiver_sim_2 = ((2., 1., 1., 0.),
                  (1., 2., 0., 1.),
                  (1., 0., 2., 1.),
                  (0., 1., 1., 2.))

receiver_dist_2 = ((2.,    4./3., 2./3., 0.),
                   (4./3., 2.,    4./3., 2./3.),
                   (2./3., 4./3., 2.,    4./3.),
                   (0.,    2./3., 4./3., 2.))

receiver_sim_3 = ((2., 1., 1., 1., 0., 0., 1., 0., 0.),
                  (1., 2., 1., 0., 1., 0., 0., 1., 0.),
                  (1., 1., 2., 0., 0., 1., 0., 0., 1.),
                  (1., 0., 0., 2., 1., 1., 1., 0., 0.),
                  (0., 1., 0., 1., 2., 1., 0., 1., 0.),
                  (0., 0., 1., 1., 1., 2., 0., 0., 1.),
                  (1., 0., 0., 1., 0., 0., 2., 1., 1.),
                  (0., 1., 0., 0., 1., 0., 1., 2., 1.),
                  (0., 0., 1., 0., 0., 1., 1., 1., 2.))

receiver_dist_3 = ((2.,     14./8., 12./8., 10./8., 1.,     6./8.,  4./8.,  2./8.,  0.),
                   (14./8., 2.,     14./8., 12./8., 10./8., 1.,     6./8.,  4./8.,  2./8.),
                   (12./8., 14./8., 2.,     14./8., 12./8., 10./8., 1.,     6./8.,  4./8.),
                   (10./8., 12./8., 14./8., 2.,     14./8., 12./8., 10./8., 1.,     6./8.),
                   (1.,     10./8., 12./8., 14./8., 2.,     14./8., 12./8., 10./8., 1.),
                   (6./8.,  1.,     10./8., 12./8., 14./8., 2.,     14./8., 12./8., 10./8.),
                   (4./8.,  6./8.,  1.,     10./8., 12./8., 14./8., 2.,     14./8., 12./8.),
                   (2./8.,  4./8.,  6./8.,  1.,     10./8., 12./8., 14./8., 2.,     14./8.),
                   (0.,     2./8.,  4./8.,  6./8.,  1.,     10./8., 12./8., 14./8., 2.))

if __name__ == '__main__':
    from SeltenGame import SeltenGame, run_simulation, run_simulation_imap
    import multiprocessing as mp
    import logging

    duplications = 10
    output_base = "/home/gmcwhirt/Documents/Sources/gametheory/output/%s"
    output_file_base = "duplication_%i"
    #generations = 1e6
    generations = 1e4
    default_weight = 2.

    sg = SeltenGame(2, [2,2],[2,2], receiver_sim_2, receiver_sim_2)

    pool = mp.Pool(2)
    print "Pool: %s" % pool

    logger = mp.log_to_stderr()
    #logger.setLevel(mp.SUBDEBUG)

    print "Running %i duplications of %i generations each." %(duplications, generations)

    tasks = [(sg, output_base % (output_file_base % i,), generations, default_weight) for i in range(duplications)]
    print "Tasks:", tasks
    results = pool.imap_unordered(run_simulation_imap, tasks)
    for result in results:
        print result

    #results = [pool.apply_async(run_simulation, task) for task in tasks]
    #for result in results:
    #    result.get()
