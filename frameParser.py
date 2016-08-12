#-*- coding: utf-8 -*-
import json
import numpy as np
import csv
import sys
import requestService
import axon
import pickle
import re

# Korean encoding
reload(sys)
sys.setdefaultencoding('utf-8')


class Parser:
    def __init__(self):
        pass

    def targetIdentifier(self, morp, word_id, srl, wsd):
        stemmer = requestService.Stemmer()

        targetCandidates_id = []
        # considering targets only have argements (targets without arguments are errors in many cases
        for eojeol in srl:
            if eojeol['argument']:   
                targetCandidates_id.append(eojeol["word_id"])
            else:
                pass

        targetCandidates = []
        for eojeol in morp:
            if eojeol["id"] in targetCandidates_id:
                targetCandidate = {}
                target_word = stemmer.stem(eojeol["result"])
                targetCandidate['text'] = target_word
                targetCandidate['morp_id'] = eojeol["m_begin"]
                targetCandidates.append(targetCandidate)

        wsdService = requestService.WSD()

        targetList = []
        spans = []
        span = {}
        id_number = 0
        for ta in targetCandidates:
            target_word = ta['text']
            morp_id = ta['morp_id']
            for eojeol in morp:
                if eojeol["m_begin"] == morp_id:
                    target_id = eojeol["id"]
            target = wsdService.disambiguator(target_word, morp_id, wsd)
            span['start'] = target_id
            span['end'] = target_id
            span['text'] = target['text']
            spans.append(span)
            target['spans'] = spans
            target['id'] = id_number
            del target['text']
            targetList.append(target)

            id_number = id_number +1
            span = {}
            spans = []
        return targetList

    def frameIdentifier(self, target):

        target_word = target['spans'][0]['text']
        
        # QAF annotation LU
        with open('./dictionary/QAF_LU.txt', 'rb') as f:
            lus = pickle.load(f)
        
        # Korean FrameNet LU
        koFNlu = {}
        with open('./dictionary/koFN_LU.txt', 'rb') as f:
            for raw in csv.reader(f, delimiter='\t'):
                koFNlu['frame'] = raw[1]
                koFNlu['target'] = raw[0]
                lus.append(koFNlu)
                koFNlu = {}

        # Hand-crafted LU
        luDict = {}
        with open('./dictionary/Manual_LU.txt', 'rb') as f:
            f.next()
            f.next()
            for raw in csv.reader(f, delimiter='\t'):
                luDict['frame'] = raw[0]
                luDict['target'] = raw[1]
                lus.append(luDict)
                luDict = {}

        frame_candidates = []
        for i in lus:
            if target_word in i['target']:
                frame_candidates.append(i['frame'])
            else:
                pass
        if not frame_candidates:
            frame = "UNKNOWN"
            #만약 Q-Frame 이면 일괄적으로 Artifact 이런거 줘도 될듯 함
            #만약 FE identification 에서도, 앞부분을 모두 Type 등으로 가져오는 코드도 필요
        else:
            for i in frame_candidates:
                frame = i # Frame disambiguation 은 구현되지 못함

        return frame


    def feIdentifier(self, frame, srl, dp, morp):
        stemmer = requestService.Stemmer()
        fes = []

        affixes = [line.rstrip('\n') for line in open('./dictionary/KoreanAffixList.txt', 'r')]
        josa = {}
        spans = []
        span = {}
        for verb in srl:
            #print 'srl in qafparser:', axon.dumps(verb)
#            if frame['word_id'] == verb['word_id']:
            for sp in frame['spans']:
                if sp['end'] == verb['word_id']:
                    argumentList = verb['argument']
#여기에 SRL 으로 못찾은 걸 넣어줘야함
#앞에 있는 명사구들 가져오기
#        print "argumentList:", axon.dumps(argumentList)
        id_number = 0
        for argument in argumentList:
            original_text =  argument['text']
            token_id = argument['word_id']
            end_id = token_id
            start_id = token_id
            srl_label = argument['type']
            for phrase in dp:
                if token_id == phrase['id']:
                    dp_label = phrase['label']
            for morpheme in morp:
                if token_id == morpheme['word_id']:
                    ma_result = morpheme['result']
                    original_text = stemmer.stem(ma_result)
#                    print "ma_result:", axon.dumps(ma_result)
            morpWithPosTuple = re.split('[+]', ma_result)
            morpPosPairList = []
            for morpWithPos in morpWithPosTuple:
                morpPosPair = re.split('[/]',morpWithPos)
                morpPosPairList.append(morpPosPair)
            if morpPosPairList[-1][-1] in affixes:
                josa['josa'] = morpPosPairList[-1][0]
                josa['pos'] = morpPosPairList[-1][-1]

            for phrase in dp:
                if token_id == phrase['id'] and phrase['mod']:
                    childsList = phrase['mod']
                    child_node_id = phrase['mod'][-1]
                    for phrase in dp:
                        if phrase['id'] == child_node_id and "NP" in phrase['label']:
                            before_text = phrase['text']
                            original_text = before_text + " " + original_text

                            for phrase in dp:
                                while phrase['id'] == child_node_id and phrase['mod']:
                                    if phrase['id'] == child_node_id and phrase['mod']:
                                        child_node_id = phrase['mod'][-1]
                                    for phrase in dp:
                                        if phrase['id'] == child_node_id and "NP" in phrase['label']:
                                            before_text = phrase['text']
                                            original_text = before_text + " " + original_text
                                            start_id = phrase['id']
                    for child_node_ids in childsList:
                        for phrase in dp:
                            if phrase['id'] == child_node_ids and phrase['label'] == "NP_CNJ":
                                before_text = phrase['text']
                                original_text = before_text + " " + original_text
                                if phrase['mod']:
                                    child = phrase['mod'][-1]
                                    for phrase in dp:
                                        if phrase['id'] == child:
                                            if phrase['id'] == child and phrase['mod']:
                                                child = phrase['mod'][-1]
                                            for phrase in dp:
                                                if phrase['id'] == child and "NP" in phrase['label']:
                                                    before_text = phrase['text']
                                                    original_text = before_text + " " + original_text
                                                    start_id = phrase['id']

            span['text'] = original_text
            span['start'] = start_id
            span['end'] = end_id
            spans.append(span)

            fe = {}
            fe['id'] = id_number
            fe['spans'] = spans
            fe['josa'] = josa
            fe['dp_label'] = dp_label
            fe['srl_label'] = srl_label
            fes.append(fe)

            id_number = id_number + 1
            spans = []
            span = {}
            josa = {}

        return fes

    def feDisambiguator(self, feList):
        for subframes in feList:
            for fes in subframes['fes']:
                arg = fes['spans'][0]['text']
                if 'fe' not in fes:
                    fe = fes['srl_label']
                    fes['fe'] = fe
                else:
                    pass

    def quantifierIdentifier(self, dp, morp):
        quantifierTargetList = [] 
        d = {}
        with open('./dictionary/Quantifier.txt', 'rb') as f:
            f.next()
            f.next()
            for raw in csv.reader(f, delimiter='\t'):
                d['frame'] = raw[0]
                d['target'] = raw[1]
                quantifierTargetList.append(d)
                d = {} 
 
        quantifier_candidates = []
        quantifier_candidate = {}
        spans = []
        span = {}
        target = {}
        target['fes'] = []
        stemmer = requestService.Stemmer()
        for eojeol in dp:
            for quant in quantifierTargetList:
                if quant['target'] in eojeol['text']:
                    if quant['frame'] ==  "Proportional_quantity":
                        quant_eojeol_id = eojeol['id']
                        quant_va_id = quant_eojeol_id + 1
                        for mp in morp:
                            if quant_va_id == mp['word_id']:
                                ma_result = mp['result']
                                original_text = stemmer.stem(ma_result)
                        quantifier_frame = quant['frame']
                        quantifier_candidate['frame'] = quantifier_frame
                        span['end'] = quant_va_id
                        span['start'] = quant_eojeol_id
                        span['text'] = (quant['target'] + " " + original_text)
                        spans.append(span)
                        quantifier_candidate['spans'] = spans
                        quantifier_candidate['id'] = "quantifier"
                        target['target'] = quantifier_candidate
                        quantifier_candidates.append(target)
                    else:
                        quant_eojeol_id = eojeol['id']  #Proportional_quantity 의 경우, 뒤의 ARG에 대해 처리해야함
                        quantifier_frame = quant['frame']
                        quantifier_candidate['frame'] = quantifier_frame
                        span['end'] = quant_eojeol_id
                        span['start'] = quant_eojeol_id
                        span['text'] = (quant['target'])
                        spans.append(span)
                        quantifier_candidate['spans'] = spans
                        quantifier_candidate['id'] = "quantifier"
                        target['target'] = quantifier_candidate
                        quantifier_candidates.append(target)
                    span = {}
                    spans = []
                    target = {}
                else:
                    pass
        return quantifier_candidates



#    def feDisambiguator(self, frame, srl, dp, morp):


class Generator:
    def __init__(self):
        pass

    def pseudoQuery(self, qafSkeleton):
        # qframe
        event_id = 0
#        event_list = []
        f = open('temporal_output.txt', 'w')
        # prefix 선언
#        f.write("@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns# ."+"\n")
#        f.write("@prefix frdf-event: <http://frdf.kaist.ac.kr/event/ ."+"\n")
#        f.write("@prefix frame: <http://frdf.kaist.ac.kr/frame/ ."+"\n")
#        f.write("@prefix fe: <http://frdf.kaist.ac.kr/fe/ ."+"\n")
        qframe_event = qafSkeleton['qFrame'][0]['target']['spans'][0]['text']
        # To do : event_id 가 계속 추가되도록...지금은 안함 (160713)
        event_id = event_id + 1
        qframe_frame = qafSkeleton['qFrame'][0]['target']['frame']
        qframe_arg = "frdf-event:"+qframe_event+"#"+str(event_id)
        if qframe_frame is not "UNKNOWN": #add qframe rdf:type
            f.write(qframe_arg+" "+"rdf:type"+" "+"frame:"+qframe_frame+" "+"."+"\n")
        else:
            pass

        # 다시 설계할 필요있음 - 특정 list input 에 대해 triple 을 생성하는 LOOP
        qframe_fe = qafSkeleton['qFrame'][0]['qFE']['fe']
        if str(qframe_fe).startswith('?') and qframe_fe:
            qframe_fe = re.sub('[?]','',qframe_fe)
            f.write(qframe_arg+" "+"fe:"+qframe_fe+" "+"?answer"+" "+"."+"\n")

        event_id

        event_list = []
        rel_list = []
        for subframe in qafSkeleton['subFrames']:
#            print 'subframe: ', subframe['target']['spans'], '\n'
            event = subframe['target']['spans'][0]['text']
            event_id = event_id + 1
            target_id = subframe['target']['id']
            frame = subframe['target']['frame']
#            target_id = subframe['target']['id']
            if frame is not "UNKNOWN":
                f.write("frdf-event:"+event+"#"+str(event_id)+" "+"rdf:type"+" "+"frame:"+frame+" "+"."+"\n")
                rels = "frdf-event:"+event+"#"+str(event_id)
                rel_list.append(rels)
            else:
                rels = "frdf-event:"+event+"#"+str(event_id)
                rel_list.append(rels)

            for fes in subframe['fes']:
                arg = fes['spans'][0]['text']
                if 'fe' in fes:
                    fe = fes['fe']
                else:
                    fe = fes['srl_label']
                
                fe_id = 100
                for m in qafSkeleton['mappingFrames']:
                    for mapping in m['mapping']:
                        if mapping['type'] is "qFrame":
                            for mapped_frame in m['mapping']:
                                if mapped_frame['type'] is 'subFrames' and mapped_frame['target_id'] == target_id:
                                    fe_id = mapped_frame['fe_id']
                        else:
                            pass

                if fe_id is not 100:
#                    print 'subframe: ', subframe
                    if target_id == subframe['target']['id']:
                        if fes['id'] == fe_id:
                            arg = qframe_arg
                    else:
                        pass
                else:
                    pass

                f.write("frdf-event:"+event+"#"+str(event_id)+" "+"fe:"+fe+" "+"\""+arg+"\""+" "+"."+"\n")
                



            if subframe['target']['id'] is "quantifier":
                quant_rel = "frdf-event:"+event+"#"+str(event_id)
                rel_list.pop(-1)

        for subframe in qafSkeleton['subFrames']:
            if subframe['target']['id'] is "quantifier":
                event = subframe['target']['spans'][0]['text']
                event_id = event_id + 1
                target_id = subframe['target']['id']
                frame = subframe['target']['frame']
                for rel in rel_list:
                    f.write(quant_rel+" "+"fe:quantARG"+" "+"\""+rel+"\""+" "+"."+"\n")



                



        f.close 
        f = open('temporal_output.txt', 'r')
        pseudoQuery = f.read()
#        pseudoQuery = filter(lambda x: not re.match(r'^\s*$',x), pseudoQuery_before)
        return pseudoQuery
"""                    
                    fe = fes['fe']
                    arg = fes['spans'][0]['text']
                    f.write("frdf-event:"+event+"#"+str(event_id)+" "+"fe:"+fe+" "+"\""+arg+"\""+" "+"."+"\n")
                else:
                    fe = fes['srl_label']
                    # mapping
                    fe_id = 100
                    for m in qafSkeleton['mappingFrames']:
                        for mapping in m['mapping']:
                            if mapping['type'] is "qFrame":
                                for mapped_frame in m['mapping']:
                                    if mapped_frame['type'] is "subFrames":
                                        fe_id = mapped_frame['fe_id']
                    if fe_id is not 100:
                        for fes in subframe['fes']:
                            if fes['id'] == fe_id:
                                arg = qframe_arg
                            else:
                                arg = fes['spans'][0]['text']
                    else:
                        arg = fes['spans'][0]['text']
                    
                    f.write("frdf-event:"+event+"#"+str(event_id)+" "+"fe:"+fe+" "+"\""+arg+"\""+" "+"."+"\n")


        f.close

        f = open('output.txt', 'r')
        pseudoQuery = f.read()
#        pseudoQuery = filter(lambda x: not re.match(r'^\s*$',x), pseudoQuery_before)


        return pseudoQuery

"""




#        stemmer = requestService.Stemmer()
#        for eojeol in morp:
#            if target[3] == morp["id"]:
