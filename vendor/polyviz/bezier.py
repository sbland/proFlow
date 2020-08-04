"""https://stackoverflow.com/questions/12643079/b%C3%A9zier-curve-fitting-with-scipy"""

from scipy.special import comb
import numpy as np


def bernstein_poly(i, n, t):
    """
     The Bernstein polynomial of n, i as a function of t
    """

    return comb(n, i) * (t**(n-i)) * (1 - t)**i


def bezier_curve_4pt(x1, y1, x2, y2, s=10, nTimes=10):
    """
       Given a set of control points, return the
       bezier curve defined by the control points.

        nTimes is the number of steps, defaults to 10

        See http://processingjs.nihongoresources.com/bezierinfo/
    """
    xPoints = np.array([x1, x1 + s, x2 - s, x2])
    yPoints = np.array([y1, y1, y2, y2])

    nPoints = len(xPoints)
    # xPoints = np.array([p[0] for p in points])
    # yPoints = np.array([p[1] for p in points])

    t = np.linspace(0.0, 1.0, nTimes)

    polynomial_array = np.array([bernstein_poly(i, nPoints-1, t) for i in range(0, nPoints)])

    xvals = np.dot(xPoints, polynomial_array)
    yvals = np.dot(yPoints, polynomial_array)

    points = [(ptx, yvals[i]) for i, ptx in enumerate(xvals)]
    return points

