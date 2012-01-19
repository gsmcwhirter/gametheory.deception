import gametheory.deception.replicator.payoffs as p
import itertools
import math
import numpy.random as rand
import sys

from gametheory.base.dynamics.discrete_replicator import NPopDiscreteReplicatorDynamics as NPDRD
from gametheory.base.simulation import SimulationBatch as SimBatchBase

class SimulationBatch(SimBatchBase):

    _choices = ["simil0","simil1","simil2","dist0","dist1","dist2"]
    
    def _add_listeners(self):

        def _set_options(this):
            this._oparser.add_option("-r", "--routine", action="store", choices=self._choices, dest="routine", help="name of routine to run")
    
        def _check_options(this):
            if not this._options.routine in this._choices:
                this._oparser.error("Unknown routine selected")
                
        def _set_data(this):
            if this._options.routine == "simil0": #common interest
                this._data['s_payoffs'] = p.receiver_sim_2[0]
                this._data['r_payoffs'] = p.receiver_sim_2[0]
    
            elif this._options.routine == "simil1": #sender map 1
                this._data['s_payoffs'] = p.sender_sim_2_1
                this._data['r_payoffs'] = p.receiver_sim_2[0]
    
            elif this._options.routine == "simil2": #sender map 3
                this._data['s_payoffs'] = p.sender_sim_2_2
                this._data['r_payoffs'] = p.receiver_sim_2[0]
    
            elif this._options.routine == "dist0": #common interest
                this._data['s_payoffs'] = p.receiver_dist_2[0]
                this._data['r_payoffs'] = p.receiver_dist_2[0]
    
            elif this._options.routine == "dist1": #sender map 1
                this._data['s_payoffs'] = p.sender_dist_2_1
                this._data['r_payoffs'] = p.receiver_dist_2[0]
    
            elif this._options.routine == "dist2": #sender map 3
                this._data['s_payoffs'] = p.sender_dist_2_2
                this._data['r_payoffs'] = p.receiver_dist_2[0]
        
        def _format_run(this, result):
            this.finished_count += 1
            if not this._options.quiet:
                print "Generations: {0}\nInitial Population: {1}\nFinal Population: {2}".format(*result)
                print "done #{0}".format(this.finished_count)
            
        
        self.on('oparser set up', _set_options)
        self.on('options parsed', _check_options)
        self.on('options parsed', _set_data)
        
        self.removeAllListeners('result')
        self.on('result', _format_run)
    

class Simulation(NPDRD):
    
    _types = [
        range(265),
        range(16)
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

    def _interaction(self, me, sender, receiver):
        smat = self.sender_matrix(sender)
        rmat = self.receiver_matrix(receiver)
        
        n = 4
        
        state_acts = [(i, rmat[smat[i].index(1)].index(1)) for i in range(n)]
        state_probs = [1. / float(n) for _ in range(n)]
        
        if me == 0:
            return math.fsum(self._data['s_payoffs'][state][act] * state_probs[i] for i, (state, act) in enumerate(state_acts))
        elif me == 1:
            return math.fsum(self._data['r_payoffs'][state][act] * state_probs[i] for i, (state, act) in enumerate(state_acts))
        else:
            raise ValueError("Unknown me value")
