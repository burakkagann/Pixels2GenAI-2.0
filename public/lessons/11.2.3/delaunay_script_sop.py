import numpy as np
import scipy.spatial as sc

def cook(scriptOp):

    scriptOp.clear()

    # Get input points (face landmarks from MediaPipe)
    input_sop = scriptOp.inputs[0]
    if input_sop is None or len(input_sop.points) < 3:
        return

    # Extract 2D points (x, y) for Delaunay triangulation
    # MediaPipe provides 3D landmarks but we triangulate in 2D
    points = [[p.x, p.y] for p in input_sop.points]

    # Compute Delaunay triangulation
    # Returns simplices (triangle vertex indices)
    tri = sc.Delaunay(points)

    # Create triangular polygons from the triangulation
    for ia, ib, ic in tri.simplices:
        # Create a 3-vertex closed polygon (triangle)
        poly = scriptOp.appendPoly(3, closed=True)

        # Assign vertex positions from original 3D landmarks
        for idx, pt_idx in enumerate([ia, ib, ic]):
            p = input_sop.points[pt_idx]
            poly[idx].point.P = (p.x, p.y, p.z)

    return
