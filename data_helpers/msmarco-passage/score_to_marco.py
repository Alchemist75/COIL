import argparse
from collections import defaultdict

parser = argparse.ArgumentParser()
parser.add_argument('--score_file', required=True)
parser.add_argument('--run_id', default='marco')
parser.add_argument('--firstp', action='store_true')
parser.add_argument("--qmap")
parser.add_argument("--dmap")
args = parser.parse_args()

with open(args.score_file) as f:
    lines = f.readlines()

if args.qmap:
    qmdic = {}
    with open(args.qmap) as f:
        for line in f.readlines():
            line = line.strip().split()
            qmdic[line[0]] = line[1]
if args.dmap:
    dmdic = {}
    with open(args.dmap) as f:
        for line in f.readlines():
            line = line.strip().split()
            dmdic[line[0]] = line[1]

all_scores = defaultdict(dict)

for line in lines:
    if len(line.strip()) == 0:
        continue
    qid, did, score = line.strip().split()
    score = float(score)
    if len(did.split('-')) == 2:
        did, chunk = did.split('-')
        if args.firstp and int(chunk) > 0:
            continue
    qid = qmdic[qid] if args.qmap else qid
    did = dmdic[did] if args.dmap else did
    if did in all_scores[qid]:
        all_scores[qid][did] = max(score, all_scores[qid][did])
    else:
        all_scores[qid][did] = score

qq = list(all_scores.keys())

firstp_sfx = '.fp' if args.firstp else ''
with open(args.score_file + f'{firstp_sfx}.marco', 'w') as f:
    with open(args.score_file + f'{firstp_sfx}.trec', 'w') as ftrec:
        for qid in qq:
            score_list = sorted(list(all_scores[qid].items()), key=lambda x: x[1], reverse=True)
            for rank, (did, score) in enumerate(score_list):
                f.write(f'{qid}\t{did}\t{rank+1}\n')
                ftrec.write(f'{qid}\t0\t{did}\t{rank+1}\t{score}\t{args.run_id}\n')

