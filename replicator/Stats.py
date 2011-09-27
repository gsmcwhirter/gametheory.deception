import math
import itertools
import Payoffs as p
from Simulations import effective_zero, sender_matrix, receiver_matrix, interaction

def values_of_information(final_sender, final_receiver, r_payoffs, n=2):
    msgs = list(itertools.product(range(n), range(n)))
    states = list(itertools.product(range(n), range(n)))
    receiver_payoffs, rstars = r_payoffs
    
    values = []
    qs_all = []
    
    for i, msg in enumerate(msgs):
        qs = []
        for j, state in enumerate(states):
            if any(sender_matrix(s)[j][i] == 1 for (s, s_prob) in final_sender):
                qs.append(j)
                
        qs_all.append((msg, qs))
                
        if len(qs) == 0:
            values.append((msg, "N/A"))
        else:
            actions = []
            for j, state in enumerate(states):
                p = 0.
                for (r, r_prob) in final_receiver:
                    if receiver_matrix(r)[i][j] == 1:
                        p += r_prob
                
                actions.append((j, p))
                
            #exp_with_sig = math.fsum(math.fsum(receiver_payoffs[q][j] * p for (j, p) in actions) for q in qs) / float(len(qs))
            exp_with_sig = math.fsum(math.fsum(receiver_payoffs[q][j] * p for (j, p) in actions) for q in qs) / float(len(states))
            #exp_rstars = [(math.fsum(receiver_payoffs[q][rstar] for q in qs) / float(len(qs)), rstar) for rstar in rstars]
            exp_rstars = math.fsum(receiver_payoffs[q][rstar] for rstar in rstars for q in qs) / float(len(rstars)) / float(len(states))
            
            #values.append((msg, [(exp_with_sig - exp_rstar, rstar) for (exp_rstar, rstar) in exp_rstars]))
            values.append((msg, exp_with_sig - exp_rstars))
            
    return (values, qs_all)

def kl_measures(final_sender, final_receiver, n=2):
    msgs = list(itertools.product(range(n), range(n)))
    states = list(itertools.product(range(n), range(n)))
    
    info_contents = []
    cprobs_m_s_all = []
    cprobs_s_m_all = []
    for i, msg in enumerate(msgs):
        cprobs_m_s = []
        for j, state in enumerate(states):
            #cprobs.append(pr(msg | state))
            p = 0.
            for (s, sprob) in final_sender:
                if sender_matrix(s)[j][i] == 1:
                    p += sprob
            
            cprobs_m_s.append(p)
        
        cprobs_m_s_all.append((msg, cprobs_m_s))
        
        cprobs_s_m = []
        info = []
        for j, state in enumerate(states):
            # pr(state | msg) = pr(msg | state) * pr(state) / sum([pr(msg | state i) * pr(state i) for i in states])
            if math.fsum(cprobs_m_s) > 0.:
                pr_s_m = (cprobs_m_s[j] / float(len(states))) / (math.fsum(cprobs_m_s) / float(len(states)))
            else:
                pr_s_m = float('inf')
            cprobs_s_m.append(pr_s_m)
            # info.append(log(pr(state | msg) / pr(state)))
            if pr_s_m > 0. and not math.isinf(pr_s_m):
                info.append(math.log(pr_s_m / (1. / float(len(states))), 2))
            else: 
                info.append(- float('inf'))
        
        info_contents.append((msg, info))
        cprobs_s_m_all.append((msg, cprobs_s_m))
    
    return (info_contents, cprobs_m_s_all, cprobs_s_m_all)

def output_summary(duplications, options):
    end_states = {}
    
    for (final_sender, final_receiver, generations) in duplications:
        end_state = [[], []]
        
        if options.verbose or len(final_sender) <= 4:
            for i, state in final_sender:
                state_tmp = round(state, 5)
                if state_tmp < 1e-3: state_tmp = 0.
                end_state[1].append((i, state_tmp))
        else:
            end_state[1] = [("mixed","")]
            
        
        for i, state in final_receiver:
            if options.verbose or len(final_receiver) == 1:
                state_tmp = round(state, 5)
                if state_tmp < 1e-3: state_tmp = 0.
            else:
                state_tmp = "some"
            end_state[0].append((i, state_tmp))
                
        end_state = tuple((tuple(end_state[0]), tuple(end_state[1])))
        
        if end_state in end_states:
            end_states[end_state][0] += 1
            end_states[end_state][1].append(generations)
        else:
            end_states[end_state] = [1, [generations]]
        
    ks = end_states.keys()
    ks.sort()
    
    for e in ks:
        print "-" * 72
        for rec, snd in itertools.izip_longest(e[0], e[1], fillvalue=False):
            print "\t",
            if rec:
                print rec[0],":",rec[1],
            else:
                print " ",
            print "\t\t",
            if snd:
                print snd[0],":",snd[1]
            else:
                print " "
        print "\t\t\t\t\t(%i times, %.2f avg gen)" % (end_states[e][0], float(sum(end_states[e][1])) / float(len(end_states[e][1])))
    
    print "=" * 72

def output_voistats(duplications, options, r_payoffs):
    times_neg_value, times_neg_value_avg = 0, 0
    
    for (final_sender, final_receiver, generations) in duplications:
        (vois, qs) = values_of_information(final_sender, final_receiver, r_payoffs)
        if not options.quiet:
            print "States sending messages (msg : states):"
            for (msg, mqs) in qs:
                print "\t", msg,":",mqs
            #print "Values of Information (msg : [value(rstar) for rstar in rstars] : average):"
            #for (msg, vals) in vois:
            #    print "\t", msg,":",vals,
            #    if vals != "N/A":
            #        print ":",(sum(v for (v, rstar) in vals) / float(len(vals)))
            #    else:
            #        print
            print "Values of Information (msg : expected voi):"
            for (msg, val) in vois:
                print "\t", msg,":",vals
            print
        
        if any(val < 0. for (msg, val) in vois if val != "N/A"):    
            times_neg_value_avg += 1
        #if any((sum(v for (v, rstar) in vals) / float(len(vals))) < 0. for (msg, vals) in vois if vals != "N/A"): 
        #    times_neg_value_avg += 1
        
        #if any(v < 0. for (msg, vals) in vois if vals != "N/A" for (v, rstar) in vals): 
        #    times_neg_value += 1

    #print "Number of duplications with a negative VoI message: %i" % (times_neg_value,)
    print "Number of duplications with a negative average VoI: %i" % (times_neg_value_avg,)
    print "=" * 72
    
def misinfo(msg_i, infos, cprobs_m_s):
    for state_i, pr_m_s in enumerate(cprobs_m_s[msg_i][1]):
        if pr_m_s > 0. and any(info_j > 0. for state_j, info_j in enumerate(infos) if state_j != state_i):
            return True
    return False

def output_klstats(duplications, options, r_payoffs, s_payoffs):
    times_misinformation = 0
    times_sender_decept = 0
    times_receiver_decept = 0
    times_full_decept = 0 
    avg_s_hdecept = []
    avg_r_hdecept = []
    avg_s_decept = []
    avg_r_decept = []
    
    for dup_i, (final_sender, final_receiver, generations) in enumerate(duplications):
        misinfo_msgs = []
        
        (kls, cprobs, cprobs2) = kl_measures(final_sender, final_receiver)
        
        if not options.quiet:
            print "Conditional Probabilities (msg : [pr(msg | state) for state in states]):"
            for (msg, cps) in cprobs:
                print "\t",msg,":",cps
            print "Conditional Probabilities (msg : [pr(state | msg) for state in states]):"
            for (msg, cps) in cprobs2:
                print "\t",msg,":",cps
            print "KL Information Measures (msg : I_msg(state) : I(msg)):"
            for i, (msg, infos) in enumerate(kls):
                print "\t",msg,":",infos,":",sum(cprobs2[i][1][j] * pj for j, pj in enumerate(infos) if not math.isinf(pj))
        
        misinfo_msgs = [msg_i for msg_i, (msg, infos) in enumerate(kls) if misinfo(msg_i, infos, cprobs)]
        if len(misinfo_msgs) > 0:        
            times_misinformation += 1
            
        #working here on determining deception
        probs_hdeception_senders = [0.] * len(final_sender)
        probs_hdeception_receivers = [0.] * len(final_receiver)
        probs_deception_senders = [0.] * len(final_sender)
        probs_deception_receivers = [0.] * len(final_receiver)
        
        s_decept = False
        r_decept = False
        f_decept = False
        
        for s_i, (s, sprob) in enumerate(final_sender):
            smat = sender_matrix(s)
            for msg_i in misinfo_msgs:
                states = [state_i for state_i, row in enumerate(smat) if row[msg_i] == 1] 
                for r_i, (r, rprob) in enumerate(final_receiver):
                    rmat = receiver_matrix(r)
                    act_i = rmat[msg_i].index(1)
                    for state_i in states:
                        receiver_actual = r_payoffs[state_i][act_i]
                        receiver_if_knew = max(r_payoffs[state_i])
                        
                        act_if_knew = r_payoffs[state_i].index(receiver_if_knew)
                        
                        sender_actual = s_payoffs[state_i][act_i]
                        sender_if_knew = s_payoffs[state_i][act_if_knew]
                        
                        if sender_actual > sender_if_knew:
                            sender_benefit = True
                            if not s_decept:
                                times_sender_decept += 1
                                s_decept = True
                            probs_hdeception_senders[s_i] += sprob * rprob / 4.
                        else:
                            sender_benefit = False
                            
                        if receiver_actual < receiver_if_knew:
                            receiver_detriment = True
                            if not r_decept:
                                times_receiver_decept += 1
                                r_decept = True
                            probs_hdeception_receivers[r_i] += sprob * rprob / 4.
                        else:
                            receiver_detriment = False
                            
                        if sender_benefit and receiver_detriment:
                            if not f_decept:
                                times_full_decept += 1
                                f_decept = True
                            probs_deception_senders[s_i] += sprob * rprob / 4.
                            probs_deception_receivers[r_i] += sprob * rprob / 4.
         
        avg_s_hdecept.append(sum(probs_hdeception_senders))
        avg_r_hdecept.append(sum(probs_hdeception_receivers))
        avg_s_decept.append(sum(probs_deception_senders))
        avg_r_decept.append(sum(probs_deception_receivers))

    print "Number of duplications with misinformation: %i" % (times_misinformation,)
    print "Number of duplications with selfish senders: %i" % (times_sender_decept,)
    print "Average sender selfishness: %.2f" % (math.fsum(avg_s_hdecept) / float(len(avg_s_hdecept)),)
    print "Number of duplications with hurt receivers: %i" % (times_receiver_decept,)
    print "Average receiver hurt: %.2f" % (math.fsum(avg_r_hdecept) / float(len(avg_r_hdecept)),)
    print "Number of duplications with deception: %i" % (times_full_decept,)
    print "Average deception probability (by sender): %.2f" % (math.fsum(avg_s_decept) / float(len(avg_s_decept)),)
    print "Average deception probability (by receiver): %.2f" % (math.fsum(avg_r_decept) / float(len(avg_r_decept)),)
    print "=" * 72
    
    
if __name__ == '__main__':
    import cPickle
    from optparse import OptionParser
    
    oparser = OptionParser()
    oparser.add_option("-f", "--statsfile", action="store", dest="stats_file", default="../output/aggregate", help="file holding aggregate stats to be parsed")
    #oparser.add_option("-f", "--file", action="store", dest="out_file", default="../output/stats", help="file to dump the stats output (not implemented yet)")
    oparser.add_option("-v", "--verbose", action="store_true", dest="verbose", default=False, help="detailed output?")
    oparser.add_option("-l", "--voistats", action="store_true", dest="voi", default=False, help="calculate value of information stats")
    oparser.add_option("-n", "--nosumm", action="store_false", dest="summary", default=True, help="do not output summary statistics")
    oparser.add_option("-k", "--klstats", action="store_true", dest="kl", default=False, help="caluclate KL value stats")
    oparser.add_option("-r", "--rpayoffs", action="store", dest="rpoffs", choices=["simil", "dist"], default="simil", help="receiver payoff type")
    oparser.add_option("-s", "--spayoffs", action="store", dest="spoffs", type="int", default=0, help="sender payoff structure index")
    oparser.add_option("-q", "--quied", action="store_true", dest="quiet", default=False, help="only output VoI / KL aggregates")
	
    (options,args) = oparser.parse_args()

    if options.spoffs < 0 or options.spoffs > 2:
        oparser.error("Sender payoff index out of bounds")
    
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
    
    massaged_dups = []
    
    for dup in duplications:
        initial = dup[1][0]
        final_sender, final_receiver = dup[1][1]
        generations = dup[1][2]
        
        final_sender = [(j, st) for (j, st) in enumerate(final_sender) if st >= 10. * effective_zero]
        final_receiver = [(j, st) for (j,st) in enumerate(final_receiver) if st >= 10. * effective_zero]
        
        massaged_dups.append((final_sender, final_receiver, generations))
        
    print "Total Duplications: %i, avg generations: %.2f" % (len(massaged_dups), float(sum(i[2] for i in massaged_dups)) / float(len(massaged_dups)))
        
    if options.rpoffs == "simil": 
        r_payoffs = p.receiver_sim_2
    else:
        r_payoffs = p.receiver_dist_2    
        
    if options.summary:
        output_summary(massaged_dups, options)
            
    if options.voi:
        output_voistats(massaged_dups, options, r_payoffs)
        
    if options.kl:
        if options.spoffs == 0:
            s_payoffs = r_payoffs[0]
        elif options.spoffs == 1:
            if options.rpoffs == "simil":
                s_payoffs = p.sender_sim_2_1
            else:
                s_payoffs = p.sender_dist_2_1
        elif options.spoffs == 2:            
            if options.rpoffs == "simil":    
                s_payoffs = p.sender_sim_2_2
            else:
                s_payoffs = p.sender_dist_2_2
                
        output_klstats(massaged_dups, options, r_payoffs[0], s_payoffs)
        
