#-*- coding: utf-8 -*-
import json
import numpy as np
import csv
import sys
#import requestService
import re
import axon
import qafTraining
import pickle

#한글 인코딩
reload(sys)
sys.setdefaultencoding('utf-8')

# training data generation (QAF)
qafTraining = qafTraining.QAF()
trainingData = qafTraining.trainingDataGeneration()


features = []
""" Frame Dictionary 만들기
for annotation in trainingData:
    targetFrame = qafTraining.targetFrameExtractor(annotation)
    result = {}
    result.update(targetFrame)
    features.append(result)

#print axon.dumps(features)
# feature 를 file 로 만들기
with open('features.txt', 'wb') as f:
#    f.write(json.dumps(features))
    pickle.dump(features, f)
with open('features_readable.txt', 'w') as f:
    f.write(axon.dumps(features)) 
with open('targetDict.txt.', 'w') as f:
    f.write(json.dumps(features))

"""

# NLQ 에서 valence pattern 만들기

valencePatterns = []
for annotation in trainingData:
    valencePattern = qafTraining.feValencePatternExtractorforNLQ(annotation)
    valencePatterns.append(valencePattern)


print axon.dumps(valencePatterns)
#with open('./NLQvalencePattern.txt', 'wb') as f:
#    pickle.dump(valencePatterns, f)

#ko.FN 에서 데이터 가져오기
#qafTraining.feValencePatternExtractorforKoFN()




"""
#print axon.dumps(features)
# feature 를 file 로 만들기
with open('features.txt', 'wb') as f:
#    f.write(json.dumps(features))
    pickle.dump(features, f)
with open('features_readable.txt', 'w') as f:
    f.write(axon.dumps(features))

with open('targetDict.txt.', 'w') as f:
    f.write(json.dumps(features))
"""

