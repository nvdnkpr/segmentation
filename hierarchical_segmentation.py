import numpy as np
#import matplotlib.pyplot as plt
from scipy.misc import imsave
from scipy import sparse

from sklearn.cluster import Ward
from skimage.segmentation import mark_boundaries

from msrc_first_try import load_data


def get_colors(img, sps):
    reds = np.bincount(sps.ravel(), weights=img[:, :, 0].ravel())
    greens = np.bincount(sps.ravel(), weights=img[:, :, 1].ravel())
    blues = np.bincount(sps.ravel(), weights=img[:, :, 2].ravel())
    counts = np.bincount(sps.ravel())
    reds /= counts
    greens /= counts
    blues /= counts
    return np.vstack([reds, greens, blues]).T


def get_centers(sps):
    gridx, gridy = np.mgrid[:sps.shape[0], :sps.shape[1]]
    n_vertices = len(np.unique(sps))
    centers = np.zeros((n_vertices, 2))
    for v in xrange(n_vertices):
        centers[v] = [gridy[sps == v].mean(), gridx[sps == v].mean()]
    return centers


def main():
    X, Y, image_names, images, all_superpixels = load_data(
        "train", independent=False)
    for x, name, image, sps in zip(X, image_names, images, all_superpixels):
        feats, edges = x
        colors = get_colors(image, sps)
        centers = get_centers(sps)
        graph = sparse.coo_matrix((np.ones(edges.shape[0]), edges.T))
        ward = Ward(n_clusters=25, connectivity=graph)
        color_feats = np.hstack([colors, centers * 5])
        segments = ward.fit_predict(color_feats)
        boundary_image = mark_boundaries(mark_boundaries(image, sps),
                                         segments[sps], color=[1, 0, 0])
        imsave("hierarchy_sp/%s.png" % name, boundary_image)


if __name__ == "__main__":
    main()
