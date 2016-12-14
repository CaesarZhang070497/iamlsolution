from __future__ import division
import requests, pickle, argparse, sys
import numpy as np

all_uuns = set(['s1421803', 's1337682', 's1413927', 's1408218', 's1324885', 's1418923', 's1453013', 's1453391', 's1449640', 's1452896', 's1430428', 's1447357', 's1368635', 's1308568', 's1362882', 's1447681', 's1409854', 's1431261', 's1409857', 's1436674', 's1410047', 's1444306', 's1432877', 's1427590', 's1451572', 's1441731', 's1445541', 's1402411', 's1401631', 's1427856', 's1411403', 's1441759', 's1452672', 's1410031', 's1424285', 's1449315', 's1431686', 's1452923', 's1451986', 's1450697', 's1442231', 's1345382', 's1455220', 's1551411', 's1452133', 's1432790', 's1671501', 's1407470', 's1449090', 's1407472', 's1302265', 's1675478', 's1436084', 's1436898', 's1421057', 's1454527', 's1411707', 's1410016', 's1438687', 's1443483', 's1326437', 's1342226', 's1241857', 's1569197', 's1225708', 's1332950', 's1432213', 's1456255', 's1408714', 's1454439', 's1330027', 's1448851', 's1428984', 's1346558', 's1402587', 's1452352', 's1442772', 's1322909', 's1475975', 's1440799', 's1456127', 's1333465', 's1452595', 's1317642', 's1407459', 's1447638', 's1443575', 's1103154', 's1446364', 's1448499', 's1450710', 's1453274', 's1415713', 's1445757', 's1431875', 's1457539', 's1424248', 's1408733', 's1513402', 's1442105', 's1444974', 's1406123', 's1444242', 's1449363', 's1402967', 's1321070', 's1412880', 's1432223', 's1405324', 's1456537', 's1434630', 's1443062', 's1455152', 's1450390', 's1453370', 's1670821', 's1419115', 's1408726', 's1455790', 's1417085', 's1451552'])

def get_percentile(value, values):
    perc = np.percentile(values, 100)
    i = 100
    while i > 0 and perc > value:
        i -= 1
        perc = np.percentile(values, i)
    return i

def pretty_results(result, content, relevance, presentation):
    print("Content:\t%d%%" % (get_percentile(result['content'], content)))
    print("Relevance:\t%d%%" % (get_percentile(result['relevance'], relevance)))
    print("Presentation:\t%d%%" % (get_percentile(result['presentation'], presentation)))
    print("Comments:")
    for comment in result['comment']:
        print(comment)

def normalise_results(single_result):
    minimum = np.min(single_result)
    single_result = [x - minimum for x in single_result]
    maximum = np.max(single_result)
    return [x / maximum for x in single_result]

def load_results():
    with open('results.pickle', 'rb') as handle:
        results = pickle.load(handle)
    return results

def save_results(results):
    with open('results.pickle', 'wb') as handle:
        pickle.dump(results, handle)

def convert_values(values):
    v1 = values['-1']
    v2 = values['0']
    v3 = values['+1']
    return ((1 * v1) + (2 * v2) + (3 * v3)) / (3 * (v1 + v2 + v3))

def process_results(results):
    processed_results = {}
    content = []
    relevance = []
    presentation = []
    for uun, result in results.iteritems():
        uun = str(uun)
        a = {}
        a['content'] = convert_values(result['content'])
        a['relevance'] = convert_values(result['relevance'])
        a['presentation'] = convert_values(result['presentation'])
        a['comment'] = result['comment']
        processed_results[uun] = a
        content.append(a['content'])
        relevance.append(a['relevance'])
        presentation.append(a['presentation'])
    return processed_results, content, relevance, presentation
                

def get_score(student):
    s=requests.get("http://homepages.inf.ed.ac.uk/mfourman/pi-videos/2016/data.txt").text
    score={'content':{'0':0,'+1':0,'-1':0},'presentation':{'0':0,'+1':0,'-1':0},'relevance':{'0':0,'+1':0,'-1':0},'comment':set()};
    gs=[i[len(student):].split(":") for i in s.replace("\n", "").replace("\r", "").split(",") if i[:len(student)] == student];
    for g in gs:
        if g[0] == "comment":
            score[g[0]].add(g[1])
        else:
            score[g[0]][g[1][1:-1]] +=1;
    return score

def get_all_scores(all_uuns):
    results = {}
    for i in all_uuns:
        print("Getting " + str(i))
        result = get_score(str(i))
        if sum(result['content'].values()) != 0 or sum(result['relevance'].values()) != 0 or sum(result['presentation'].values()) != 0:
            results[str(i)] = result
    return results

if __name__ == "__main__":
    results = load_results()
    processed_results, content, relevance, presentation = process_results(results)
    parser = argparse.ArgumentParser(description='''Get details about your PI video results''', formatter_class = argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('-u', '--uun', default=None, help='Your UUN')
    commands = sys.argv[1:]
    args = parser.parse_args(commands)
    if args.uun == None:
        uun = raw_input("Please enter your UUN: ")
    else:
        uun = args.uun
    pretty_results(processed_results[uun], content, relevance, presentation)
