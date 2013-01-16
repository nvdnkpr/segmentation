import os
from glob import glob

import numpy as np
import matplotlib.pyplot as plt
#from scipy.misc import imread

from sklearn.externals.joblib import Memory
#from sklearn.preprocessing import StandardScaler

#from datasets.msrc import MSRCDataset
from pystruct.utils import make_grid_edges


from IPython.core.debugger import Tracer
tracer = Tracer()

memory = Memory(cachedir="cache")

classes = np.array(['building', 'grass', 'tree', 'cow', 'sheep', 'sky',
                    'aeroplane', 'water', 'face', 'car', 'bicycle', 'flower',
                    'sign', 'bird', 'book', 'chair', 'road', 'cat', 'dog',
                    'body', 'boat', 'void', 'mountain', 'horse'])

base_path = "/home/VI/staff/amueller/datasets/aurelien_msrc_features/msrc/"


@memory.cache
def load_data(dataset="train"):
    mountain_idx = np.where(classes == "mountain")[0]
    horse_idx = np.where(classes == "horse")[0]
    void_idx = np.where(classes == "void")[0]

    ds_dict = dict(train="Train", val="Validation", test="Test")
    if dataset not in ds_dict.keys():
        raise ValueError("dataset must be one of 'train', 'val', 'test',"
                         " got %s" % dataset)
    ds_path = ds_dict[dataset]
    features = []
    labels = []
    for f in glob(ds_path + "/*.dat"):
        name = os.path.basename(f).split('.')[0]
        labels.append(np.loadtxt("labels/%s.txt" % name, dtype=np.int))
        feat = [np.loadtxt("%s/%s.local%s" % (ds_path, name, i))
                for i in xrange(1, 7)]
        features.append(np.hstack(feat))
    features = np.vstack(features)
    labels = np.hstack(labels)
    features = features[(labels != mountain_idx) * (labels != void_idx)
                        * (labels != horse_idx)]
    labels = labels[(labels != mountain_idx) * (labels != void_idx)
                    * (labels != horse_idx)]
    return features, labels


def region_graph(regions):
    edges = make_grid_edges(regions)
    n_vertices = regions.size

    crossings = edges[regions.ravel()[edges[:, 0]]
                      != regions.ravel()[edges[:, 1]]]
    crossing_hash = crossings[:, 0] + n_vertices * crossings[:, 1]
    # find unique connections
    unique_hash = np.unique(crossing_hash)
    # undo hashing
    unique_crossings = np.asarray([[x % n_vertices, x / n_vertices]
                                   for x in unique_hash])
    if True:
        # compute region centers:
        gridx, gridy = np.mgrid[:regions.shape[0], :regions.shape[1]]
        centers = np.zeros((n_vertices, 2))
        for v in xrange(n_vertices):
            centers[v] = [gridy[regions == v].mean(),
                          gridx[regions == v].mean()]
        # plot labels
        plt.imshow(regions)
        # overlay graph:
        for edge in edges:
            plt.plot([centers[edge[0]][0], centers[edge[1]][0]],
                     [centers[edge[0]][1], centers[edge[1]][1]])
        plt.show()
    tracer()
    return unique_crossings


def main():
    # load training data
    # let's just do images with cars first.
    car_idx = np.where(classes == "car")[0]
    ds_path = base_path + "Train"
    image_names = []
    X = []
    for f in glob(ds_path + "/*.dat"):
        name = os.path.basename(f).split('.')[0]
        labels = np.loadtxt(base_path + "labels/%s.txt" % name, dtype=np.int)
        if car_idx not in labels:
            continue
        image_names.append(name)
        # features
        feat = np.hstack([np.loadtxt("%s/%s.local%s" % (ds_path, name, i)) for
                          i in xrange(1, 7)])
        # superpixels
        superpixels = np.fromfile("%s/%s.dat" % (ds_path, name),
                                  dtype=np.int32)
        superpixels = superpixels.reshape(superpixels.shape[:-1][::-1]).T
        # generate graph
        graph = region_graph(superpixels)
        X.append((feat, graph))


if __name__ == "__main__":
    main()