import math
import itertools
import Payoffs as p

def values_of_information(duplication, cutoff=0.1):
    sender_urns = duplication[1][0]
    receiver_urns = duplication[1][1]
    receiver_payoffs = duplication[1][2]
    rstars = duplication[1][3]
    msg_length = len(sender_urns[0])
    msg_options = len(sender_urns[0][0][0])
    states = len(sender_urns)
    states2 = len(sender_urns) / msg_length
    tmp = [tuple(range(states2))] * msg_length
    states_list = list(itertools.product(*tmp))
    opts = []
    for i in range(msg_length):
        opts.append(range(msg_options))
    msgs = itertools.product(*opts)
    
    values = []
    qs_all = []
    for msg in msgs:
        qs = []
        for i in range(states):
            p = 1.
            for j in range(msg_length):
                p *= sender_urns[i][j][0][msg[j]] / sender_urns[i][j][1]
            if p >= cutoff:
                qs.append(i)
                
        qs_all.append((msg, qs))
                
        if len(qs) == 0:
            values.append((msg, "N/A"))
        else:
            actions = []
            for state in states_list:
                p = 1.0
                for i in range(msg_length):
                    p *= receiver_urns[i][msg[i]][0][state[i]] / receiver_urns[i][msg[i]][1]
                actions.append((states_list.index(state), p))
                
            exp_with_sig = []
            for q in qs:
                exp_with_sig.append(sum([receiver_payoffs[q][j[0]] * j[1] for j in actions]))
            exp_rstars = []
            for rstar in rstars:
                exp_rstars.append([receiver_payoffs[q][rstar] for q in qs])
            
            values.append((msg, [(sum(exp_with_sig) / float(len(qs))) - (sum(exp_rstar) / float(len(qs))) for exp_rstar in exp_rstars]))
            
    return (values, qs_all)

def kl_measures(duplication):
    sender_urns = duplication[1][0]
    receiver_urns = duplication[1][1]
    receiver_payoffs = duplication[1][2]
    rstars = duplication[1][3]
    msg_length = len(sender_urns[0])
    msg_options = len(sender_urns[0][0][0])
    states = len(sender_urns)
    states2 = len(sender_urns) / msg_length
    tmp = [tuple(range(states2))] * msg_length
    states_list = list(itertools.product(*tmp))
    opts = []
    for i in range(msg_length):
        opts.append(range(msg_options))
    msgs = itertools.product(*opts)
    
    info_contents = []
    cprobs_all = []
    cprobs2_all = []
    for msg in msgs:
        cprobs = []
        for state in states_list:
            sind = states_list.index(state)
            #cprobs.append(pr(msg | state))
            p = 1.0
            for i in range(msg_length):
                p *= sender_urns[sind][i][0][msg[i]] / sender_urns[sind][i][1]
            cprobs.append(p)
        
        cprobs_all.append((msg, cprobs))
        
        cprobs2 = []
        info = []
        for state in states_list:
            sind = states_list.index(state)
            # pr(state | msg) = pr(msg | state) * pr(state) / sum([pr(msg | state i) * pr(state i) for i in states])
            prsgm = (cprobs[sind] / float(states)) / sum([cprobs[i] / float(states) for i in range(states)])
            cprobs2.append(prsgm)
            # info.append(log(pr(state | msg) / pr(state))) 
            info.append(math.log(prsgm / (1. / float(states)), 2)) 
        
        info_contents.append((msg, info))
        cprobs2_all.append((msg, cprobs2))
    
    return (info_contents, cprobs_all, cprobs2_all)

if __name__ == '__main__':
    import cPickle
    from optparse import OptionParser
    
    oparser = OptionParser()
    oparser.add_option("-s", "--statsfile", action="store", dest="stats_file", default="../output/aggregate", help="file holding aggregate stats to be parsed")
    oparser.add_option("-f", "--file", action="store", dest="out_file", default="../output/stats", help="file to dump the stats output (not implemented yet)")
    oparser.add_option("-c", "--cutoff", action="store", type="float", default=0.1, dest="voi_cutoff", help="cutoff value for VOI calculations")
	
    (options,args) = oparser.parse_args()
    
    #of = open(options.out_file,"w")
    sf = open(options.stats_file,"rb")
    
    duplications = []
    
    pickle = ""
    i = 0
    for line in sf:
        if line != "\n":
            pickle += line
        else:
            i += 1
            duplications.append((i, cPickle.loads(pickle)))
            pickle = ""
    
    if i == 0:
        print "error"
    sf.close()
    
    for dup in duplications:
        print "-" * 72
        print "Duplication %i" % (dup[0],)
        print "-" * 72
        print "Sender Urns:"
        for urn in dup[1][0]:
            print "\t", urn
            print "\t\t", tuple([[u[0][0] / u[1], u[0][1] / u[1]] for u in urn])
        print "Receiver Urns:"
        for urn in dup[1][1]:
            print "\t", urn
            print "\t\t", tuple([[u[0][0] / u[1], u[0][1] / u[1]] for u in urn])
        (vois, qs) = values_of_information(dup, options.voi_cutoff)
        print "States sending messages (msg : states):"
        for msgv in qs:
            print "\t", msgv[0],":",msgv[1]
        print "Values of Information (msg : value(rstar) : average):"
        for msgv in vois:
            print "\t", msgv[0],":",msgv[1],":",(sum(msgv[1]) / float(len(msgv[1]))) 
        (kls, cprobs, cprobs2) = kl_measures(dup)
        print "Conditional Probabilities (msg : pr(msg | state)):"
        for msgv in cprobs:
            print "\t",msgv[0],":",msgv[1]
        print "Conditional Probabilities (msg : pr(state | msg)):"
        for msgv in cprobs2:
            print "\t",msgv[0],":",msgv[1]
        print "KL Information Measures (msg : I_msg(state) : I(msg)):"
        for msgv in kls:
            print "\t",msgv[0],":",msgv[1],":",sum([cprobs2[kls.index(msgv)][1][i] * msgv[1][i] for i in range(len(msgv[1]))])
        print            
