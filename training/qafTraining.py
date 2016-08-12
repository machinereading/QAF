#-*- coding: utf-8 -*-
import json
import numpy as np
import csv
import sys
import requestService
import re
import axon

#한글 인코딩
reload(sys)
sys.setdefaultencoding('utf-8')

class QAF:
    def __init__(self):
        pass
    def trainingDataGeneration(self):
        raw_sentences_list = []
        # 1. raw sentence objectation
        with open('../data/NLQ1-1/q1-1_raw.txt','r') as f:
            for line in f:
                if line not in ['\n', '\r\n']: #빈줄이 아닐 경우
                    tokens = line.split()
                    raw_sentence_id = tokens[0]
                    raw_sentences = {}
                    raw_sentences['sentence_id'] = raw_sentence_id
                    raw_sentence = re.sub(r'.*\t', '', line)
                    raw_sentences['raw_sentence'] = raw_sentence
                    raw_sentences_list.append(raw_sentences)
                else:
                    pass
#        print "raw_sentence_list:",axon.dumps(raw_sentences_list)
        # 2. annotation objectation
        annotation_list = []
        with open('../data/NLQ1-1/q1-1_annotation.txt', 'r') as f:
            for line in f:
                if line not in ['\n', '\r\n']: #빈줄이 아닐 경우
                    revSent = re.sub('Target, ', 'Target,', line)
                    wordsList = revSent.split()
                    sentence_id = wordsList[0]
                    revSent2 = re.sub(r'.*\t', '', line)
                    annotations = {}
                    annotations['sentence_id'] = sentence_id
                    annotations['annotation'] = revSent2
#                    print raw_sentences_list[0]['sentence_id']
                    for raw_sentence in raw_sentences_list:
                        if raw_sentence['sentence_id'] == sentence_id:
                            annotations['raw_sentence'] = raw_sentence['raw_sentence']
                    annotation_list.append(annotations)
                else:
                    pass
        return annotation_list

    def targetFrameExtractor(self, trainingData):

        parser = requestService.Parser()
#        print trainingData['raw_sentence']
        nlpResult = parser.etri(trainingData['raw_sentence'])
        dp = nlpResult[0]["dependency"]
        morp = nlpResult[0]["morp_eval"]
        wsd = nlpResult[0]["WSD"]


        # annotation tokenization (target identification 전용)
#        tokens_in_annotation = []
        revSent = re.sub('Target, ', 'Target,', trainingData['annotation'])
        tokens = revSent.split()
        token_list = []
        for i in range(len(tokens)):
            each_token_dict = {}
            each_token_dict['id'] = i
            each_token_dict['text'] = tokens[i]
            token_list.append(each_token_dict)
        token_dict = {}
        token_dict['sentence_id'] = trainingData['sentence_id']
        token_dict['tokens'] = token_list
#        tokens_in_annotation.append(token_dict)
#        print axon.dumps(token_dict)
        targetFrameDict = {}
        for tokens in token_dict['tokens']:
#            print "tokens", tokens
#            print "tokens['text']", tokens['text']
            if "Target" in tokens['text']:
                token_id = tokens['id']
#                print "token['text']:", tokens['text']
#                print "token['id']:", tokens['id']
                f = re.sub(r'\[', '', tokens['text']).split(']')
#                f = k.split('|')
#                print axon.dumps(f)
                for i in f:
#                    k = i.split('|')
#                    print axon.dumps(k)
#                    print i
                    if "Target" in i:
#                        print i
                        k = i.split('|')
#                        print axon.dumps(k)
                        for i in k:
#                            print i
                            if "Target" not in i:
#                                print i
                                for eojeol in morp:
#                                    print axon.dumps(eojeol)
#                                    print "print target:", i
#                                    print "print eojeol[id]:", eojeol["id"]
#                                    print "print token_id:", token_id

                                    if eojeol["id"] == token_id:
                                        target_ma = eojeol["result"]
#                                        print "target_ma:", target_ma
                                        stemmer = requestService.Stemmer()
                                        target = stemmer.stem(target_ma)
#                                        print "target:", target
                                        targetFrameDict['target'] = target
                            else:
                                frames = i.split(',')
                                for i in frames:
                                    if "Target" not in i:
                                        frame = i
                                        targetFrameDict['frame'] = i
                                    else:
                                        pass
                    else:
                        pass

        return targetFrameDict



    def feValencePatternExtractorforNLQ(self, trainingData):
        affixes = [line.rstrip('\n') for line in open('./dictionary/KoreanAffixList.txt', 'r')]
        stemmer = requestService.Stemmer()
        parser = requestService.Parser()
        nlpResult = parser.etri(trainingData['raw_sentence'])
        dp = nlpResult[0]['dependency']
        morp = nlpResult[0]['morp_eval']
        wsd = nlpResult[0]['WSD']
        srl = nlpResult[0]['SRL']

        revSent = re.sub('Target, ', 'Target,', trainingData['annotation'])
        tokens = revSent.split()
        token_list = []
        for i in range(len(tokens)):
            each_token_dict = {}
            each_token_dict['id'] = i
            each_token_dict['text'] = tokens[i]
            token_list.append(each_token_dict)
        token_dict = {}
        token_dict['sentence_id'] = trainingData['sentence_id']
        token_dict['tokens'] = token_list

#        print axon.dumps(token_dict)


        valencePattern = {}
        patterns = []
        pattern = {}
        josa = {}
        for tokens in token_dict['tokens']:
            if "Target" in tokens['text']:
                valencePattern['frame'] = re.search(r'(?<=Target,).*?(?=\])', tokens['text']).group(0)
            elif "|" in tokens['text'] and "Target" not in tokens['text']:
                pattern['fe'] = re.search(r'(?<=\|).*?(?=\])', tokens['text']).group(0)
                token_id = tokens['id']

                for phrase in dp:
                    if token_id == phrase['id']:
                        dp_label = phrase['label']
                pattern['dp_label'] = dp_label

                for morpheme in morp:
                    if token_id == morpheme['word_id']:
                        ma_result = morpheme['result']
                        text = stemmer.stem(ma_result)
                        morpWithPosTuple = re.split('[+]', ma_result)
                        morpPosPairList = []
                        for morpWithPos in morpWithPosTuple:
                            morpPosPair = re.split('[/]',morpWithPos)
                            morpPosPairList.append(morpPosPair)
                        if morpPosPairList[-1][-1] in affixes:
                            josa['josa'] = morpPosPairList[-1][0]
                            josa['pos'] = morpPosPairList[-1][-1]
                pattern['josa'] = josa
                josa = {}

                for phrase in srl:
                    if token_id == phrase['word_id']:
                        argumentList = phrase['argument']
                        for argument in argumentList:
                            srl_label = argument['type']
                            pattern['srl_label'] = srl_label
                patterns.append(pattern)
            else:
                pass
            pattern = {}
        valencePattern['pattern'] = patterns
        #valancePatterns.append(valancePattern)
        return valencePattern


"""
    def feValencePatternExtractorforKoFN(self):
        affixes = [line.rstrip('\n') for line in open('./dictionary/KoreanAffixList.txt', 'r')]
        stemmer = requestService.Stemmer()
        parser = requestService.Parser()

        koFN = []
        for i in range(1,3):
            f = open('../data/KoFN/' + str(i) + '.json')
            data = json.loads(f.read())
            f.close
            koFN.append(data)

        for annotation in koFN:
            nlpResult = parser.etri(annotation['raw_sentence'])
            dp = nlpResult[0]['dependency']
            morp = nlpResult[0]['morp_eval']
            wsd = nlpResult[0]['WSD']
            srl = nlpResult[0]['SRL']

"""
            






