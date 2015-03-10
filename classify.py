from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
import numpy as np
import json
import sys
import time
from analyze import Analyzer # for some train data labelling

def read_json(file, max=None):
    i = 0
    for jsonObject in file:
        data = json.loads(jsonObject)
        message = data["body"].replace('\r\n', '\n')
        yield message
        i = i + 1
        if max is not None and i >= max:
            break

def main(argv):
    group = argv[0] if len(argv) > 0 else "id"
    train_size = int(argv[1]) if len(argv) > 1 else 1000
    display = group == "id"

    train_data = []
    train_labels = []
    analyzer = Analyzer()
    for message in read_json(sys.stdin):
        label = analyzer.analyze(message)[0]
        train_data.append(message)
        train_labels.append(label)

        if len(train_data) >= train_size:
            break

    regressor = Pipeline([('tfidf', TfidfVectorizer(input='content')),
                          ('clf', RandomForestRegressor()),
    ])
    regressor.fit(train_data, train_labels)

    data = read_json(sys.stdin)
    if group != "score":
        data = list(data)

    predicted = regressor.predict(data)
    for i in range(len(predicted)):
        # Take the color for this group of predictions
        c = cmp(predicted[i], 0)
        print("{}{:.2f}{}\t{}".format(analyzer.colors[c] if c != 0 else "", predicted[i], analyzer.END_COLOR, data[i].replace('\n',' ')))


if __name__ == "__main__":
    main(sys.argv[1:])