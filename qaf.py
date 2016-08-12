#-*- coding: utf-8 -*-
import json
import httplib2
import urllib2
import numpy as np
import csv
import sys
import requestService
import pickle
import re
import axon

#한글 인코딩
reload(sys)
sys.setdefaultencoding('utf-8')

"""
qFrame class 설명
Q-Frame target identification
Q-Frame text identification
Q-Frame FE identification
"""

class TypeAnalyzer:
    def __init__(self):
        pass

    def questionType(self, dp):
        for eojeol in dp:
            if eojeol["head"] == -1 and eojeol["label"] == "VNP": #e.g.: ...해전은 무엇인가?
                qType = 1
            elif eojeol["head"] == -1 and eojeol["label"] == "NP": #e.g.: ...해전? or ...무엇?
                qType = 4
            elif eojeol["head"] == -1 and eojeol["label"] == "VP": #e.g.: ...해전은 무엇인지 말해보시오
                qType = 3
            elif eojeol["head"] == -1 and eojeol["label"] == "NP_SBJ": #e.g.: ...해전은?
                qType = 2
            else:
                qType = 4

        if qType == 4:
            for eojeol in dp:
                if eojeol["head"] == -1:
                    head_id = eojeol["id"]
            for eojeol in dp:
                if eojeol["head"] == head_id and eojeol["label"] == "NP_SBJ": #e.g.: ...해전은 무엇?
                    qType = 1
                elif eojeol["head"] == head_id and eojeol["label"] is not "NP_SBJ": #e.g.: ...지휘한 해전?
                    qType = 2

        return qType

    def qTypePrint(self, qType):
        if qType == 1:
            print "Question Type: 1 (Input question includes interrogative pronoun)"
        elif qType == 2:
            print "Question Type : 2 (Input question does not include interrogative pronoun)"
        elif qType == 3:
            print "Question Type : 3 (Input question is a declarative sentence)"
        elif qType == 4:
            print "OUT OF SCOPE! I can't analyze the type about your question yet :P"

class Parser:
    def __init__(self):
        pass

    def targetIdentifier(self, morp, word_id, dp, srl, wsd, qType):

        if qType == 1:
            for eojeol in dp:
                if eojeol["head"] == -1:
                    head_id = eojeol["id"]
            for eojeol in dp:
                if eojeol["head"] == head_id and eojeol["label"] == "NP_SBJ":
                    target_id = eojeol["id"]

        elif qType == 2:
            for eojeol in dp:
                if eojeol["head"] == -1:
                    head_id = eojeol["id"]
                    target_id = head_id

        elif qType == 3:
            for eojeol in dp:
                if eojeol["head"] == -1:
                    head_id = eojeol["id"]
            for eojeol in dp:
                if eojeol["head"] == head_id and eojeol["label"] == "NP_OBJ":
                    target_id = eojeol["id"]
                elif eojeol["head"] == head_id:
                    head_child_id = eojeol["id"]
            for eojeol in dp:
                if eojeol["head"] == head_child_id and eojeol["label"] == "NP_SBJ":
                    target_id = eojeol["id"]
        else:
            target_id = 0

        # get MA result using eojeol ID. e.g.: 해전은 --> 해전/NNG+은/JX
        for eojeol in morp:
            if eojeol["id"] == target_id:
                target_ma = eojeol["result"]

        # Stemmping. e.g.: 해전/NNG+은/JX --> 해전
        stemmer = requestService.Stemmer()
        target_word = stemmer.stem(target_ma)

        wsdService = requestService.WSD()

        # get WSD result
        for eojeol in word_id:
            if eojeol["id"] == target_id:
                morp_id = eojeol["begin"]

        targetDict = wsdService.disambiguator(target_word, morp_id, wsd)

        spans = []
        span = {}
        span['start'] = target_id
        span['end'] = target_id
        span['text'] = targetDict['text']
        spans.append(span)
        targetDict['spans'] = spans
        targetDict['id'] = 0
        del targetDict['text']
        targetList = []
        targetList.append(targetDict)

        return targetList

    def qFrameIdentifier(self, qFrame):
        target_word = qFrame['spans'][0]['text']

	# QAF annotation LU
        with open('./dictionary/QAF_LU.txt', 'rb') as f:
            lus = pickle.load(f)

	# Hand-crafted LU
        d = {}
        with open('./dictionary/Manual_LU.txt', 'rb') as f:
            f.next()
            f.next()
            for raw in csv.reader(f, delimiter='\t'):
                d['frame'] = raw[0]
                d['target'] = raw[1]
                lus.append(d)
                d = {}

        frame_candidates = []
        for i in lus:
            if target_word in i['target']:
                frame_candidates.append(i['frame'])
            else:
                pass
        if not frame_candidates:
            frame = "UNKNOWN"
        else:
            for i in frame_candidates:
                frame = i
        return frame


    def qFEIdentifier(self, qType, qFrame, morp, dp):
        
        if qType == 1:
            for eojeol in dp:
                if eojeol["head"] == -1:
                    qfe_id = eojeol["id"]
            for eojeol in morp:
                if eojeol["id"] == qfe_id:
                    qfe_ma = eojeol["result"]
            stemmer = requestService.Stemmer()
            qFE_text = stemmer.stem(qfe_ma)
        elif qType == 2:
            qFE_text = "omitted"
        elif qType == 3:
            qFE_text = "omitted"
        else:
            qFE_text = "omitted"

        qFEList = []
        qFEDict = {}
        qFEDict['text'] = qFE_text
        qFEDict['qType'] = qType
        qFEDict['id'] = 0
        qFEList.append(qFEDict)
        return qFEList


    def qFEDisambiguator(self, qType, qFrame, qFEDict):
        if qType == 1:
            if qFrame == "Event":
                if qFEDict['text'] == "무엇":
                    qFETag = "?event"
                else:
                    qFETag = "?event"
            elif qFrame == "People":
                if qFEDict['text'] == "누구":
                    qFETag = "?person"
                else:
                    qFETag = "?person"
            elif qFrame == "Locale":
                if qFEDict['text'] == "어디":
                    qFETag = "?name"
                else:
                    qFETag = "?name"
            elif qFrame == "Artifact":
                if qFEDict['text'] == "무엇":
                    qFETag = "?name"
                else:
                    qFETag = "?name"
            elif qFrame == "Location_in_time":
                if qFEDict['text'] == "언제":
                    qFETag = "?focal_time"
                else:
                    qFETag = "?focal_time"
            elif qFrame == "Organization":
                if qFEDict['text'] == "무엇":
                    qFETag = "?name"
                else:
                    qFETag = "?name"
            else:
                qFETag = "?name"
        else:
            if qFrame == "Event":
                qFETag = "?event"
            elif qFrame == "People":
                qFETag = "?person"
            elif qFrame == "Locale":
                qFETag = "?name"
            elif qFrame == "Artifact":
                qFETag = "?name"
            elif qFrame == "Location_in_time":
                qFETag = "focal_time"
            elif qFrame == "Organization":
                qFETag = "?name"
            elif qFrame == "Location_in_time":
                qFETag = "focal_time"
            else:
                qFETag = "?name"

        return qFETag

    def descriptionGenerator(self, qafSkeleton):
        desc_end_id = qafSkeleton['qFrame'][0]['target']['spans'][0]['end']
        desc_end = qafSkeleton['qFrame'][0]['target']['spans'][0]['text']
        desc_text = " ".join(qafSkeleton['tokens'][0:desc_end_id])
        desc_text_full = desc_text+" "+str(desc_end)
        desc_span = {}
        desc_spans = []
        desc_span['start'] = 0
        desc_span['end'] = desc_end_id
        desc_span['text'] = desc_text_full
        desc_spans.append(desc_span)
        desc_fe = {}
        desc_fes = []
        desc_fe['fe'] = "description"
        desc_fe['spans'] = desc_spans
        desc_fe['id'] = 0
        desc_fes.append(desc_fe)

        description = {}
        description['fes'] = desc_fes
        description['target'] = qafSkeleton['qFrame'][0]['target']

        return description




class ErrorCorrector:
    def __init__(self):
        pass

    def FEerror(self, qafSkeleton, dp, morp, feList):
        qframe_target_id = qafSkeleton['qFrame'][0]['target']['spans'][0]['end']
        stemmer = requestService.Stemmer()
        affixes = [line.rstrip('\n') for line in open('./dictionary/KoreanAffixList.txt', 'r')]
        affixes.remove('SE')
        affixes.remove('SF')
        affixes.remove('SO')
        affixes.remove('SP')
        affixes.remove('SS')

        qframe_target_josa = {}
        for dep in dp:
            if dep['id'] == qframe_target_id:
                target_dp_label = dep['label']
        for mp in morp:
            if mp['word_id'] == qframe_target_id:
                ma_result = mp['result']
                original_text = stemmer.stem(ma_result)
                morpWithPosTuple = re.split('[+]', ma_result)
                morpPosPairList = []
                for morpWithPos in morpWithPosTuple:
                    morpPosPair = re.split('[/]',morpWithPos)
                    morpPosPairList.append(morpPosPair)
                for morpPosPair in morpPosPairList:
                    if morpPosPair[-1] in affixes:
                        qframe_target_josa['josa'] = morpPosPair[0]
                        qframe_target_josa['pos'] = morpPosPair[-1]
	id_list = []
	for frames in feList:
            for fes in frames['fes']:
		if not any(span['end'] == qframe_target_id for span in fes['spans']) and fes:
                    id_list.append(fes['id'])

	added_fe = {}
	for frames in feList:
            if not any(fe['spans'][0]['end'] == qframe_target_id for fe in frames['fes']) and frames['fes']:
		added_id = max(f['id'] for f in frames['fes']) + 1
		added_fe['dp_label'] = target_dp_label
		added_fe['id'] = added_id
		added_fe['spans'] = qafSkeleton['qFrame'][0]['target']['spans']
		added_fe['josa'] = qframe_target_josa
		added_fe['pos'] = qafSkeleton['qFrame'][0]['target']['pos']
		added_fe['srl_label'] = "ARG1"

		print "\n", "### 3.3.2 FE error correction"
		frames['fes'].append(added_fe)
		print "added FE: ", axon.dumps(added_fe['spans'])
		print "\n", "revised FE Identification Result: "
                print "target: ", axon.dumps(frames['target']['spans'])
                print "fes :"
		print axon.dumps(frames['fes']), "\n"
		added_fe = {}


class QueryGenerator:
    def __init__(self):
        pass

    def mappingFrames(self, qafSkeleton, feList):
        qframe_target_id = qafSkeleton['qFrame'][0]['target']['spans'][0]['end']
        qFrame = qafSkeleton['qFrame']

	mappingFrames = []
	mappingTuple = []
	mappingFrame = {}
	mapFrameDict_A = {}
	mapFrameDict_B = {}
	for frames in feList:
            for fes in frames['fes']:
		for span in fes['spans']:
                    if span['end'] == qframe_target_id:
                        mapFrameDict_A['target_id'] = qFrame[0]['target']['id']
                        mapFrameDict_A['fe_id'] = 'null'
                        mapFrameDict_A['type'] = "qFrame"

                        mapFrameDict_B['target_id'] = frames['target']['id']
                        mapFrameDict_B['fe_id'] = fes['id']
                        mapFrameDict_B['type'] = "subFrames"
                        mappingTuple.append(mapFrameDict_A)
                        mappingTuple.append(mapFrameDict_B)
                        mappingFrame['mapping'] = mappingTuple
                        mappingFrames.append(mappingFrame)

                        mapFrameDict_A = {}
                        mapFrameDict_B = {}
                        mappingTuple = []
                        mappingFrame = {}


                    else:
                        pass

                    for fr in feList:
                        for f in fr['fes']:
                            for sp in f['spans']:
                                if span['end'] == sp['end'] and frames['target']['frame'] is not fr['target']['frame']:
                                    mapFrameDict_A['target_id'] = frames['target']['id']
                                    mapFrameDict_A['fe_id'] = fes['id']
                                    mapFrameDict_A['type'] = "subFrames"
                                    mapFrameDict_B['target_id'] = fr['target']['id']
                                    mapFrameDict_B['fe_id'] = f['id']
                                    mapFrameDict_B['type'] = "subFrames"
                                    mappingTuple.append(mapFrameDict_A)
                                    mappingTuple.append(mapFrameDict_B)
                                    mappingFrame['mapping'] = mappingTuple
                                    mappingFrames.append(mappingFrame)

                                    mapFrameDict_A = {}
                                    mapFrameDict_B = {}
                                    mappingTuple = []
                                    mappingFrame = {}

                                else:
                                    pass

        return mappingFrames


    def pseudoQuery(self, qafSkeleton):
        event_id = 0
        f = open('temporal_output.txt', 'w')

        # prefix 선언
        f.write("@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> ."+"\n")
        f.write("@prefix frdf-event: <http://frdf.kaist.ac.kr/event/> ."+"\n")
        f.write("@prefix frame: <http://frdf.kaist.ac.kr/frame/> ."+"\n")
        f.write("@prefix fe: <http://frdf.kaist.ac.kr/fe/> ."+"\n")
        qframe_event = qafSkeleton['qFrame'][0]['target']['spans'][0]['text']

        # To do : event_id 가 계속 추가되도록...지금은 안함 (160713)
        event_id = event_id + 1
        qframe_frame = qafSkeleton['qFrame'][0]['target']['frame']
        qframe_subject = "frdf-event:"+qframe_event+"#"+str(event_id)
        if qframe_frame is not "UNKNOWN": #add qframe rdf:type
            f.write(qframe_subject+" "+"rdf:type"+" "+"frame:"+qframe_frame+" "+"."+"\n")
        else:
            pass

        # 다시 설계할 필요있음 - 특정 list input 에 대해 triple 을 생성하는 LOOP
        qframe_fe = qafSkeleton['qFrame'][0]['qFE']['fe']
        if str(qframe_fe).startswith('?') and qframe_fe:
            qframe_fe = re.sub('[?]','',qframe_fe)
            f.write(qframe_subject+" "+"fe:"+qframe_fe+" "+"?answer"+" "+"."+"\n")

        event_id

        event_list = []
        sbj_list = []
        for subframe in qafSkeleton['subFrames']:
            event = subframe['target']['spans'][0]['text']
            event_id = event_id + 1
            target_id = subframe['target']['id']
            frame = subframe['target']['frame']
            if subframe['fes']:
                fe = subframe['fes'][0]
            else:
                fe = {}
                fe['fe'] = "no fe"
            if frame is not "UNKNOWN" and fe['fe'] is not "description":
                f.write("frdf-event:"+event+"#"+str(event_id)+" "+"rdf:type"+" "+"frame:"+frame+" "+"."+"\n")
                subject = "frdf-event:"+event+"#"+str(event_id)
                sbj_list.append(subject)
            elif fe['fe'] is "description":
                subject = qframe_subject
                sbj_list.append(subject)
            elif fe == "no fe":
                pass
            else:
                subject = "frdf-event:"+event+"#"+str(event_id)
                subject_list.append(subject)

            for fes in subframe['fes']:
                arg = fes['spans'][0]['text']
                if 'fe' in fes:
                    fe = fes['fe']
                else:
                    fe = "null"

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
                    if target_id == subframe['target']['id']:
                        if fes['id'] == fe_id:
                            arg = qframe_subject
                    else:
                        pass
                else:
                    pass

                f.write(subject+" "+"fe:"+fe+" "+"\""+arg+"\""+" "+"."+"\n")

            if subframe['target']['id'] is "quantifier":
                quant_subject = "frdf-event:"+event+"#"+str(event_id)
                sbj_list.pop(-1)

        # for Quantifier
        for subframe in qafSkeleton['subFrames']:
            if subframe['target']['id'] is "quantifier":
                event = subframe['target']['spans'][0]['text']
                event_id = event_id + 1
                target_id = subframe['target']['id']
                frame = subframe['target']['frame']
                for sbj in sbj_list:
                    f.write(quant_subject+" "+"fe:quantARG"+" "+"\""+sbj+"\""+" "+"."+"\n")
        # 현재 모든 target 에 대해 quantifier 가 작동하는 방식. 이는 quantifer 의 실제 argument 를 찾는 모듈이 개발되면 수정되어야 함

        f.close
        f = open('temporal_output.txt', 'r')
        pseudoQuery = f.read()
        return pseudoQuery

