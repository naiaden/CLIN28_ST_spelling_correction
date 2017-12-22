class Applicator:
    def apply(sentence, correction):
        """
        This function tries to apply a correction on the sentence.
        
        Returns the corrected sentence.
        """
        print("AIS\t" + str(correction))
        if correction['class'] == "runonerror":
            for iter,id in enumerate(sentence):
                if id[0] == correction['span'][0]:
                    id[1] = correction['text'].split(" ")[0]
                    #print(id[1] + " " + str(iter))
                    id[2] = classencoder.buildpattern(correction['text'].split(" ")[0], allowunknown=False, autoaddunknown=True)
                    break
            new_entry = [id[0] + "R",
                         correction['text'].split(" ")[1],
                         classencoder.buildpattern(correction['text'].split(" ")[1], allowunknown=False, autoaddunknown=True),
                         item['space'],
                         item['in']]
            sentence.insert(iter+1, new_entry)
        if correction.get('superclass', "") == "replace":
            for iter,id in enumerate(sentence):
                if id[0] == correction['span'][0]:
                    id[1] = correction['text']
                    id[2] = classencoder.buildpattern(correction['text'], allowunknown=False, autoaddunknown=True)
                    break
        if correction['class'] == "spliterror":
            for iter,id in enumerate(sentence):
                if id[0] == correction['span'][0]:
                    id[1] = correction['text']
                    id[2] = classencoder.buildpattern(correction['text'], allowunknown=False, autoaddunknown=True)
                if id[0] == correction['span'][1]:
                    break
            del sentence[iter]
        if correction['class'] == "missingword":
            for iter, id in enumerate(sentence):
                if id[0] == correction['after']:
                    #print("MW:\t" + str(iter) + "\t" + str(id))
                    break
            new_entry = [id[0] + "." + str(random.randint(1,100)) + "M",
                         correction['text'],
                         classencoder.buildpattern(correction['text'], allowunknown=False, autoaddunknown=True),
                         item['space'],
                         item['in']]
            sentence.insert(iter+1, new_entry)

        return sentence
    
    def apply_on_corrections(correction, corrections, sentence):
        """
        This function checks whether a correction is due to be applied on
        another correction, in which case it will try to gracefully handle
        the situation by updating the previous correction (with the word,
        not a new correction class).
        
        Returns a tuple (r1, r2) where
            r1 = the correction has been applied on another correction,
            r2 = the updated sentence.
            
            
        >>> correction = {'class': 'spliterror', 'span': ['page1.text.div.4.p.1.s.2.w.18', 'page1.text.div.4.p.1.s.2.w.18.47M'], 'text': 'zonet'}    
        >>> corrections = [{'class': 'missingword', 'after': 'page1.text.div.4.p.1.s.2.w.18', 'text': 'net'}]
        >>> sentence = [['page1.text.div.4.p.1.s.2.w.16', 'en', bp('en'), True, 'page1.text.div.4.p.1.s.2'], 
                        ['page1.text.div.4.p.1.s.2.w.17', 'wist', bp('wist'), True, 'page1.text.div.4.p.1.s.2'], 
                        ['page1.text.div.4.p.1.s.2.w.18', 'zo', bp('zo'), True, 'page1.text.div.4.p.1.s.2'], 
                        ['page1.text.div.4.p.1.s.2.w.18.47M', 'net', bp('net'), True, 'page1.text.div.4.p.1.s.2'], 
                        ['page1.text.div.4.p.1.s.2.w.19', 'de', bp('de'), True, 'page1.text.div.4.p.1.s.2']]
        >>> apply_on_corrections(c1, C1, s1)
        (True, [['page1.text.div.4.p.1.s.2.w.16', 'en', <colibricore.Pattern at 0x7f253cf80b70>, True, 'page1.text.div.4.p.1.s.2'],
                ['page1.text.div.4.p.1.s.2.w.17', 'wist', <colibricore.Pattern at 0x7f253cf809d0>, True, 'page1.text.div.4.p.1.s.2'],
                ['page1.text.div.4.p.1.s.2.w.18', 'zonet', <colibricore.Pattern at 0x7f253cf80950>, True, 'page1.text.div.4.p.1.s.2'], 
                ['page1.text.div.4.p.1.s.2.w.19', 'de', <colibricore.Pattern at 0x7f253cf80270>, True, 'page1.text.div.4.p.1.s.2']])
        """  
        rv = False
        if correction.get('superclass', "") == 'replace':
            if correction['span'][0].endswith("M"):
                print("correction: " + str(correction))
                f_id = correction['span'][0]

                for c in corrections:
                    print("          : " + str(c))
                    if 'span' in c and c['span'][0] == f_id:
                        c['text'] = correction['text']
                        print("          :>" + str(c))
                        rv = True

                        for id in sentence:
                            if id[0] == f_id:
                                id[1] = correction['text']
                                id[2] = classencoder.buildpattern(correction['text'], allowunknown=False, autoaddunknown=True)
                                break

                        break
                    if 'after' in c and c['after'] == ".".join(f_id.split(".")[0:-1]):
                        c['text'] = correction['text']
                        print("          :>" + str(c))
                        rv = True

                        for id in sentence:
                            if id[0] == f_id:
                                id[1] = correction['text']
                                id[2] = classencoder.buildpattern(correction['text'], allowunknown=False, autoaddunknown=True)
                                break

                        break
        if correction['class'] == 'spliterror':
            if fid(correction['span'][0]) == fid(correction['span'][1]) and correction['span'][1].endswith("M"):
                
                for iter, wid in enumerate(sentence):
                    print(wid)
                    if wid[0] == correction['span'][0]:
    #                    print("--" + str(wid))                    
                        wid[1] = correction['text']
                        wid[2] = classencoder.buildpattern(correction['text'], allowunknown=False, autoaddunknown=True)
                        
                        rv = True
                    if  wid[0] == correction['span'][1]:
    #                    print(">>" + str(wid) + "\t\t(" + str(iter) + ")")
                        break
                if sentence[iter][0].endswith("M"):
                    del sentence[iter]
        return (rv, sentence)
