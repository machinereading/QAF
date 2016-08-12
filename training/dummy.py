#-*- coding: utf-8 -*-
import json
import numpy as np
import csv
import sys
import requestService
import re

reload(sys)
sys.setdefaultencoding('utf-8')

with open('./features_readable.txt', 'r') as f:
    for line in f:
        json_data = json.load(line)
        print json_data
    
    #    print f
#    for line in f:
#        print line['target']
