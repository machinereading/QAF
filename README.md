# QAF: Frame-semantic-based QA system

## QAF
- converts natural language question (NLQ) to SPARQL query

## Scope
QAF module deals with 1) Korean, 2) single question sentence, and 3) pseudo query generation. In the next version, pseudo query would be converted to DBpedia SPARQL query to retrive answer directly.

## prerequisite
* python 2.7
* `pip install pyaxon` (to see the Korean result in log file)
* `pip install httplib2` 
* `pip install numpy`

## How to run
```
python qaf-parser.py -i "input sentence" -o outputfile
```
`qaf-parser.py` would print detail logs on your screen, and the result (pseudo query) would be saved at outputfile (e.g. output.txt).

## Example
Let input NLQ be: `python qaf-parser.py -i " 이순신 장군이 1597년에 명량해협에서 지휘한 해전은 무엇인가?" -o outputfile`
then output would be:
```
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix frdf-event: <http://frdf.kaist.ac.kr/event/> .
@prefix frame: <http://frdf.kaist.ac.kr/frame/> .
@prefix fe: <http://frdf.kaist.ac.kr/fe/> .

frdf-event:해전#1 rdf:type frame:Event .
frdf-event:해전#1 fe:event ?answer .
frdf-event:지휘하#2 rdf:type frame:Leadership .
frdf-event:지휘하#2 fe:leader "이순신 장군" .
frdf-event:지휘하#2 fe:time "1597년" .
frdf-event:지휘하#2 fe:place "명량해협" .
frdf-event:지휘하#2 fe:location "frdf-event:해전#1" .
frdf-event:해전#1 fe:description "이순신 장군이 1597년에 명량해협에서 지휘한 해전" . 
```

## How to add LUs manually?
FRDF system is based on the Korean frame-semantic parser we developed. The first step of frame-semantic parsing is identification of the *TARGET word*(in above example, the word '해전') in the input sentence. Because of lack of training data, sometimes this parser does not detect the *TARGET words* and disambiguate it. To improve the performance immediately, you can add just LUs at this file:
```
./dictionary/Manual_LU.txt
```

## Licenses
* `CC BY-NC-SA` [Attribution-NonCommercial-ShareAlike](https://creativecommons.org/licenses/by-nc-sa/2.0/)

## Citation
(Submitted to Coling 2016)

## Project Web Page
[http://machinereading.github.io/FRDF/] (http://machinereading.github.io/FRDF/)

## Acknowledgement
This work was supported by Institute for Information & communications Technology Promotion(IITP) grant funded by the Korea government(MSIP) (No. R0101-15-0054, WiseKB: Big data based self-evolving knowledge base and reasoning platform)

## Contact
* Author: Younggyun Hahm (hahmyg@kaist.ac.kr)
* Publisher: Machine Reading Lab @ KAIST (http://machinereading.kaist.ac.kr)
