import setup
from models import Playthrough
import sys

# play1 = Playthrough(sys.argv[1])
# play2 = Playthrough(sys.argv[2])


def autosplit(play):
    splits = []
    used = {}
    for i, item_name in enumerate(play.data['item_names']):
        if item_name in used:
            continue
        used[item_name] = True
        splits.append([item_name, play.data['item_frames'][i]])
    return splits

# splits1 = get_major_splits(play1)
# splits1 = get_major_splits(play2)

all_splits = []

for p in Playthrough.load_all('ypx'):
    splits = autosplit(p)
    all_splits.append(splits)

for row in zip(*all_splits):
    print(set([c[0] for c in row]))