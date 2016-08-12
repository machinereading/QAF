#-*- coding: utf-8 -*-
import json
import httplib, urllib, urllib2
import sys
import re
#import csv

#한글 인코딩
reload(sys)
sys.setdefaultencoding('utf-8')

#사용법
#main 함수에
#parser = requestService.Parser()
#espresso = parser.espresso(text)

class TypeAnalyzer:
    def __init__(self):
#        print "...Loading Type Analyzer..."
        pass

    def questionType(self, dp):

        for eojeol in dp:
            if eojeol["head"] == -1 and eojeol["label"] == "VNP": #예: ...해전은 무엇인가?
                qType = 1
            elif eojeol["head"] == -1 and eojeol["label"] == "NP": #예: ...해전? or ...무엇?
                qType = 4
            elif eojeol["head"] == -1 and eojeol["label"] == "VP": #예: ...해전은 무엇인지 말해보시오
                qType = 3
            elif eojeol["head"] == -1 and eojeol["label"] == "NP_SBJ": #예: ...해전은?
                qType = 2
            else:
                qType = 4

        if qType == 4: #예: ...해전? or ...무엇? 에 대한 분류
            for eojeol in dp:
                if eojeol["head"] == -1:
                    head_id = eojeol["id"]
            for eojeol in dp:
                if eojeol["head"] == head_id and eojeol["label"] == "NP_SBJ": #예: ...해전은 무엇?
                    qType = 1
                elif not eojeol["head"] == head_id and eojeol["label"] == "NP_SBJ": #예: ...지휘한 해전?
                    qType = 2

        #qType 출력
        if qType == 1:
            print "Question Type: 1 (Input question includes interrogative pronoun)", "\n"
        elif qType == 2:
            print "Question Type : 2 (Input Question does not include interrogative pronoun)", "\n"
        elif qType == 3:
            print "Question Type : 3 (Input question is a declarative sentence)", "\n"
        elif qType == 4:
            print "OUT OF SCOPE! I can't analyze the type about your question yet :P", "\n"

        return qType


class Parser:
    def __init__(self):
#        print "...Loading NLP parser..."
    # 입력 text에 대해서 API 호출 후, JSON 값 반환

        pass
    
    def espresso(self, text):
        request = urllib2.Request('http://143.248.135.60:31996/espresso_parser', json.dumps({'text':text}))
        response = urllib2.urlopen(request)
        result = response.read().decode('utf-8')

        return json.loads(result)

    def etri(self, text):
#        request = urllib2.Request('http://211.109.9.71:31998/etri_parser', json.dumps({'text':text})) (기존버전)
        request = urllib2.Request('http://143.248.135.60:31235/etri_parser', json.dumps({'text':text})) #(2016.04버전)
        response = urllib2.urlopen(request)
        result = response.read().decode('utf-8')

        return json.loads(result)

class Stemmer:
    def __init__(self):
#        print "...Loading Stemmer..."
        pass
    #입력 예: 해전/NNG+은/JX
    #출력 예: stem method: 해전 

    def stem(self, morp):
        morpWithPosTuple = re.split('[+]',morp) # + 단위로 tuple 생성 
        morpPosPairList = []
        morpList = []

        #stemming 시 지우는 POS tag 리스트 생성
        affixes = [line.rstrip('\n') for line in open('./dictionary/KoreanAffixList.txt', 'r')]

        for morpWithPos in morpWithPosTuple:
            morpPosPair = re.split('[/]',morpWithPos) # / 단위로 tuple 생성 후 리스트에 추가 (예: [(해전, NNG), (은, JX)]
            morpPosPairList.append(morpPosPair)

        for morpPosPair in morpPosPairList:
            if morpPosPair[1] not in affixes:
                morpList.append(morpPosPair[0])

        stem = ''.join(morpList) # stemming 된 형태소들을 합쳐줌. 예: "대한" "민국"


        for morpPosPair in morpPosPairList:
            if not morpPosPair[1] == affixes: # POS가 affixex가 아닐 경우
                morpList.append(morpPosPair[0]) # tuple 에서 POS를 제거

        return stem
        #return morpList
        #return morpPosPairList
        #return morpWithPosTuple

    def stemWithPos(self, morp):
        morpWithPosTuple = re.split('[+]',morp)
        morpPosPairList = []
        morpList = []
        affixes = ('JX')
        for morpWithPos in morpWithPosTuple:
            morpPosPair = re.split('[/]',morpWithPos)
            morpPosPairList.append(morpPosPair)

        for morpPosPair in morpPosPairList:
            if not morpPosPair[1] == affixes:
                morpList.append(morpPosPair[0])

        return morpList

class WSD:
    def __init__(self):
#        print "...Loading WSD module..."
        pass
    def disambiguator(self, word, morp_id, wsd):
        
        for morp in wsd:
            if morp["begin"] == morp_id:
                posTag = morp["type"]
                scode = morp["scode"]
#        wsdList = ["target", "POSTag", "Sense code"]
        wsdDict = {}
        wsdDict['text'] = word
        wsdDict['pos'] = posTag
        wsdDict['ws_code'] = scode

        return wsdDict

class remove:
    def dictInList(condition, yourlist):
        for k in xrange(len(yourlist)):
            if condition(yourlist[k]):
                del yourlist[k]
                break
        return yourlist



"""Old version
    def espresso(self, text):

        url = '143.248.135.60'
        params = urllib.urlencode({'text':text.encode('utf-8')})
        headers = {"Content-Type":"application/json"}

        conn = httplib.HTTPConnection(host=url, port=31996)
        conn.request("POST", "/espresso_parser", params, headers)
        response = conn.getresponse()
        data = response.read()
        conn.close()

#        return json.loads(data)
        return data


    def etri(self, text):
        url = '211.109.9.71'
        params = urllib.urlencode({'text':text})
        headers = {"Content-type":"application/json"}

        conn = httplib.HTTPConnection(host=url, port=31998)
        conn.request("POST", "/etri_parser", params, headers)
        response = conn.getresponse()
        data = response.read().decode('utf-8')
        conn.close()

        return json.loads(data)
"""


