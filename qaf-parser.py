#-*- coding: utf-8 -*-
# main function for QAF parser
import requestService
import json
import re
import sys, getopt
import axon
import qaf
import frameParser

# Korean encoding
reload(sys)
sys.setdefaultencoding('utf-8')

# I/O function
input_file = ''
output_file = ''
ioOPT, arg = getopt.getopt(sys.argv[1:], "i:o:")
for o,a in ioOPT:
    if o == '-i':
        input_file = a
    elif o == '-o':
        output_file = a
    else:
        print "USAGE: %s -i input - output" % sys.argv[0]

# Version information
versionInfo = open('version.txt','r')
print versionInfo.read()
versionInfo.close()

# input question
nlq = input_file

# preprocessing: natural language processing
print "\n", "### 0. Preprocessing: importing Korean NLP tool"
print "Input sentence: ", nlq
parser = requestService.Parser()
nlpResult = parser.etri(nlq) #etri parser, April, 2016
dp = nlpResult[0]["dependency"] # dependency parse
srl = nlpResult[0]["SRL"] # semantic role labeling
morp = nlpResult[0]["morp_eval"] # morphological analysis
morp_id = nlpResult[0]["morp"] # for morpheme ID
word_id = nlpResult[0]["word"] # for eojeol ID
wsd = nlpResult[0]["WSD"] # word sense disambiguation
print "NLP is done"

# 1. Question Type Analysis
print "\n","### 1. Question Type Identifier"
typeAnalyzer = qaf.TypeAnalyzer()
qType = typeAnalyzer.questionType(dp)

typeAnalyzer.qTypePrint(qType) # print qType

# 2. Q-Frame Parser
qFrameParser = qaf.Parser()

# 2.1 qFocus Identification
print "\n", "### 2.1 qFocus Identifier"
qFocus = qFrameParser.targetIdentifier(morp, word_id, dp, srl, wsd, qType)
print "qFocus :", axon.dumps(qFocus)

# 2.2 qFrame Disambiguation
print "\n", "### 2.2 qFrame Disambiguator"
qFrame = qFrameParser.qFrameIdentifier(qFocus[0])
qFocus[0]['frame'] = qFrame
print "qFrame :", qFrame
print "qFocus :", axon.dumps(qFocus)

# 2.3 qWord Identification
print "\n", "### 2.3 qWord Identifier"
qWord = qFrameParser.qFEIdentifier(qType, qFrame, morp, dp)
print "qWord :", axon.dumps(qWord)

# 2.4 qFE Disambiguation
print "\n", "### 2.4 qFE Disambiguator"
qFE = qFrameParser.qFEDisambiguator(qType, qFrame, qWord[0])
qWord[0]['fe'] = qFE
print "qFE :", qFE
print "qWord :", axon.dumps(qWord)

# 2.5 QAF SKELETON GENERATION (1/2)
qafSkeleton = {}
qFrame = []
qFrameDict = {}
qFrameDict['target'] = qFocus[0]
qFrameDict['qFE'] = qWord[0]
qFrame.append(qFrameDict)
qafSkeleton['qFrame'] = qFrame
qafSkeleton['tokens'] = nlq.split()
print "\n", "### 2.5 QAF SKELETON GENERATION (1/2)"
print axon.dumps(qafSkeleton)

# 3 Frame Parser
print "\n", "### 3. Frame-semantic parser"
frameParser = frameParser.Parser()

# 3.1 Target Identification
print "### 3.1 Target Identification"
target_candidates = frameParser.targetIdentifier(morp, word_id, srl, wsd)
if target_candidates:
    print "Target Words: ", axon.dumps(target_candidates)
else:
    pass
# 3.2 Frame Disambiguation
print "\n", "### 3.2 Frame Disambiguation"
frameList = []
for tw in target_candidates:
    frame = frameParser.frameIdentifier(tw)
    tw['frame'] = frame
    frameList.append(tw)
    print "...identified frame:\"", frame, "\"", "for target word:\"", tw['spans'][0]['text'], "\""
if not frameList:
    print "no frames"
else:
    print "Frame Disambiguation result :", axon.dumps(frameList)

# 3.3 FE Identification
print "\n", "### 3.3 FE Identification"
feList = []
feDict = {}
for frame in frameList:
    fes = frameParser.feIdentifier(frame,srl,dp,morp)
    feDict['target'] = frame
    feDict['fes'] = fes
    feList.append(feDict)
    feDict = {}
if not feList:
    print "no arguments"
else:
    print "FE Identification Result:"
    for fe in feList:
        print "target :", axon.dumps(fe['target']['spans'])
        print "fes: "
        print axon.dumps(fe['fes']), "\n"

# 3.3.1 Description FE generation
print "### 3.3.1 Description FE generation"
description = qFrameParser.descriptionGenerator(qafSkeleton)
print "Description :"
print axon.dumps(description)

# 3.3.2 FE error correction
errorCorrector = qaf.ErrorCorrector()
errorCorrector.FEerror(qafSkeleton, dp, morp, feList)


# 3.4 Quantifier Identification
print "\n", "### 3.4 Quantifier Identification"
quantifierList = frameParser.quantifierIdentifier(dp,morp)
if quantifierList:
    print "Quantifier :", axon.dumps(feList)
else:
    print "\"no quantifier is detected\""

# 3.5 FE Disambiguation
print "\n", "### 3.5 FE Disambiguation"
print "...disambiguating FEs..."
frameParser.feDisambiguator(feList)
#print axon.dumps(feList)

# 4. QAF Skeleton Generation (2/2)
print "\n", "### 4. QAF Skeleton Generation (2/2)"

# Frame Mapping
print "...mapping connected Frames..."
queryGenerator = qaf.QueryGenerator()
mappingFrames = queryGenerator.mappingFrames(qafSkeleton, feList)
qafSkeleton['mappingFrames'] = mappingFrames

# adding Quantifier Frames
if quantifierList:
    print "...adding Quantifier Frames..."
    for quantifier in quantifierList:
        feList.append(quantifier)
else:
    pass

# adding Description FEs
print "...adding Description FEs..."
feList.append(description)
qafSkeleton['subFrames'] = feList


print "\n", "QAF SKELETON Result: ", "\n"
print axon.dumps(qafSkeleton)

# 5. Pseudo Query Generation
pseudoQuery = queryGenerator.pseudoQuery(qafSkeleton)

print "\n", "##################### PSEUDO QUERY #############################################","\n"
print pseudoQuery
print "################################################################################"
print "\n","YOUR RESULT WOULD BE SAVED AS", output_file
# SAVE THE RESULT
with open(output_file,'w') as f:
    f.write("NLQ :"+input_file+"\n"+"\n"+pseudoQuery)
