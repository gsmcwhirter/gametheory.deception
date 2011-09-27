from Immutable import *
import itertools
import functools
import random
import sys

class SeltenGame(Immutable):

    @mutablemethod
    def __init__(self, num_aspects, num_states, num_messages, sender_payoffs, receiver_payoffs):
        if len(num_states) != num_aspects:
            raise ValueError('num_states should have the same length as the value of num_aspects')

        if len(num_messages) != num_aspects:
            raise ValueError('num_messages should have the same length as the value of num_aspects')

        self.num_aspects = num_aspects
        self.state_lists = tuple([tuple(range(i)) for i in num_states])
        self.state_tuples = tuple(itertools.product(*self.state_lists))
        self.num_states = len(self.state_tuples)
        self.num_actions = self.num_states
        self.message_lists = tuple([tuple(range(i)) for i in num_messages])
        self.message_tuples = tuple(itertools.product(*self.message_lists))
        self.sender_payoffs = sender_payoffs
        self.receiver_payoffs = receiver_payoffs

        self._check_simulation()

    def _check_simulation(self):
        if len(self.sender_payoffs) != self.num_states:
            raise ValueError('sender_payoffs should have the same length as num_actions')

        if any(len(i) != self.num_actions for i in self.sender_payoffs):
            raise ValueError('sender_payoff entries should all have the same length as num_actions')

        if len(self.receiver_payoffs) != self.num_states:
            raise ValueError('receiver_payoffs should have the same length as num_actions')

        if any(len(i) != self.num_actions for i in self.receiver_payoffs):
            raise ValueError('receiver_payoff entries should all have the same length as num_actions')

        return True

class SimpleUrn:
    _total = 0.
    _type_count = []
    _cumulative_count = []
    _num_types = 0

    def __init__(self, num_types, default_weight):
        self._num_types = int(num_types)
        if self._num_types == 0:
            raise ValueError("num_types cannot be 0")
        default_weight = float(default_weight)

        self._type_count = [default_weight for i in range(self._num_types)]
        self._update_cumulative_count()

    def _update_cumulative_count(self):
        self._cumulative_count = [sum(self._type_count[i:]) for i in range(self._num_types)]
        self._total = self._cumulative_count[0]

    def __unicode__(self):
        return unicode("%s (%s)" % (self._type_count,self.get_proportions()))

    __str__ = __unicode__

    def get_random(self):
        rand_float = random.uniform(0., self._total)
        #print rand_float
        func = functools.partial(lambda z, x: x >= z, rand_float)
        cumulative_slice = list(itertools.takewhile(func, self._cumulative_count))
        #print cumulative_slice

        return len(cumulative_slice) - 1

    def get_proportions(self):
        return [i / self._total for i in self._type_count]

    def reinforce(self, index, amount):
        self._type_count[index] = self._type_count[index] + amount
        self._update_cumulative_count()
    
    def dump(self):
        return (self._type_count, self._total)

def run_simulation_imap(args):
    return run_simulation(*args)

def run_simulation(sg, fname, generations, default_weight=2., output_skip=0):
    #assumes check_simulation passed
    if fname is not None:
        fout = open(fname, "w")
    else:
        fout = sys.stdout

    generations = int(generations)
    default_weight = float(default_weight)

    sender_urns = [tuple([SimpleUrn(len(sg.message_lists[j]), default_weight)
                          for j in range(sg.num_aspects)])
                   for i in range(sg.num_states)]

    receiver_urns = [tuple([SimpleUrn(len(sg.state_lists[j]), default_weight)
                            for k in sg.message_lists[j]])
                     for j in range(sg.num_aspects)]

    print >>fout,"State Lists: %s" % (sg.state_lists,)
    print >>fout,"State Tuples: %s" % (sg.state_tuples,)
    print >>fout,"Message Lists: %s" % (sg.message_lists,)
    print >>fout,"Message Tuples: %s" % (sg.message_tuples,)
    print >>fout,"Sender Payoffs: %s" % (sg.sender_payoffs,)
    print >>fout,"Receiver Payoffs: %s" % (sg.receiver_payoffs,)
    print >>fout,"Initial Sender Urns: %s" % ([[str(k) for k in j] for j in sender_urns],)
    print >>fout,"Initial Receiver Urns: %s" % ([[str(k) for k in j] for j in receiver_urns],)
    print >>fout,"="*72
    print >>fout

    for i in xrange(generations):
        state = tuple([random.randint(0,len(j) - 1) for j in sg.state_lists])
        state_index = sg.state_tuples.index(state)
        message = tuple([j.get_random() for j in sender_urns[state_index]])
        action = tuple([receiver_urns[k][message[k]].get_random() for k in range(len(message))])
        action_index = sg.state_tuples.index(action)

        sender_result = sg.sender_payoffs[state_index][action_index]
        receiver_result = sg.receiver_payoffs[state_index][action_index]

        for j in range(sg.num_aspects):
            sender_urns[state_index][j].reinforce(message[j],sender_result)
            receiver_urns[j][message[k]].reinforce(action[j],receiver_result)

        if output_skip != 0 and (i + 1) % output_skip == 0:
            print >>fout, "Generation: %s" % (i+1,)
            print >>fout, "\t","State: %s (%s) Message: %s Action: %s (%s)" % (state, state_index ,message,action,action_index)
            print >>fout, "\t","Sender Payoff: %s Receiver Payoff: %s" % (sender_result, receiver_result)
            print >>fout, "\t","Sender Urns:"
            for j in sender_urns:
                print >>fout, "\t\t",
                for k in j:
                    print >>fout,k,
                print >>fout
            print >>fout, "\t","Receiver Urns:"
            for j in receiver_urns:
                print >>fout, "\t\t",
                for k in j:
                    print >>fout,k,
                print >>fout
            print >>fout, "-"*72
            print >>fout

    print >>fout, "Results after %i generations:" % (generations,)
    print >>fout, "Sender Urns:"
    for j in sender_urns:
        print >>fout, "\t",
        for k in j:
            print >>fout, k,
        print >>fout
    print >>fout, "Receiver Urns:"
    for j in receiver_urns:
        print >>fout, "\t",
        for k in j:
            print >>fout,k,
        print >>fout
    
    if fname is not None:
        fout.close()

    return (fname, tuple([tuple([urn.dump() for urn in urns]) for urns in sender_urns]), tuple([tuple([urn.dump() for urn in urns]) for urns in receiver_urns]), sg.receiver_payoffs)
