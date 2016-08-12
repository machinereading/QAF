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
#print axon.dumps(trainingData)

features = []
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

#    for annotation in features:
#        f.write('[')
#        f.write(annotation)
#        f.write(']')


# 현재 구현은 feature로 target, frame 만 가져오고 있음 (160427)


#print targetFrame
#    dp = dpExtractor(annotation)
#    ws = wsExtractor(annotation)
#    result = {}
#    result.update(targetFrame)
#    result.update(dp)
#    result.update(ws)


#print axon.dumps(features)
