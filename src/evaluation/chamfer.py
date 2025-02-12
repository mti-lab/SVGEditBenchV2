import math
import numpy as np
import os
import re
import xml.etree.ElementTree as ET
from glob import glob
from svgpathtools.svg_to_paths import rect2pathd, ellipse2pathd, polygon2pathd, polyline2pathd, parse_path
from tqdm import tqdm

XMLNS = 'http://www.w3.org/2000/svg'

class shape:
  def __init__(self, tag: str, attributes: dict, transform: np.ndarray):
    self.tag = tag
    self.attributes = attributes
    self.transform = transform
  
def parse_transform(transform: str) -> np.ndarray:
  """
  Parses a transform string into a 2D transformation matrix.
  """
  result = np.eye(3)
  transforms = re.findall('[^( ]*\\([^)]*\\)', transform)
  for t in transforms:
    op, arg = t.split('(')
    args = re.findall('[+-]?[\\d.]+', arg)
    args = [float(a) for a in args]
    
    if op == "translate":
      if len(args) > 2:
        raise ValueError(f"translate transform must have 1 or 2 arguments, got {len(args)}")
      if len(args) == 2:
        x, y = args
      else:
        x, y = args[0], 0
      result = result @ np.array([[1, 0, x], [0, 1, y], [0, 0, 1]])
    elif op == "scale":
      if len(args) > 2:
        raise ValueError(f"scale transform must have 1 or 2 arguments, got {len(args)}")
      if len(args) == 2:
        x, y = args
      else:
        x, y = args[0], args[0]
      result = result @ np.array([[x, 0, 0], [0, y, 0], [0, 0, 1]])
    elif op == "rotate":
      if len(args) > 3 or len(args) == 2:
        raise ValueError(f"rotate transform must have 1 or 3 arguments, got {len(args)}")
      if len(args) == 1:
        angle, cx, cy = args[0], 0, 0
      else:
        angle, cx, cy = args
      angle = math.radians(angle)
      result = result @ np.array([[1, 0, -cx], [0, 1, -cy], [0, 0, 1]]) # Move the center to the origin
      result = result @ np.array([[math.cos(angle), -math.sin(angle), 0], [math.sin(angle), math.cos(angle), 0], [0, 0, 1]]) # Rotate
      result = result @ np.array([[1, 0, cx], [0, 1, cy], [0, 0, 1]]) # Move the center back
    elif op == "matrix":
      if len(args) != 6:
        raise ValueError(f"matrix transform must have 6 arguments, got {len(args)}")
      result = result @ np.array([[args[0], args[2], args[4]], [args[1], args[3], args[5]], [0, 0, 1]])
    else:
      raise ValueError(f"Unknown transform operation: {op}")
  return result

def parse_svg(e : ET.Element, transform: np.ndarray) -> list[shape]:
  """
  Parses an SVG element into a list of shapes.
  """
  shapes = []
  for child in e:
    tag = child.tag.removeprefix(f'{{{XMLNS}}}')
    if "transform" in child.attrib:
      dt = parse_transform(child.attrib["transform"])
    else:
      dt = np.eye(3)
    if tag == "g":
      shapes.extend(parse_svg(child, transform @ dt))
    elif tag in ["rect", "circle", "ellipse", "line", "polygon", "path", "polyline"]:
      shapes.append(shape(tag, child.attrib, transform @ dt))
    elif tag in ["radialGradient", "linearGradient", "defs", "mask"]: #known tags to ignore
      pass
    else:
      raise ValueError(f"Unknown tag: {tag}")
  return shapes

def get_point_cloud(path: str, num_points: int) -> list[list[complex]]:
  """
  Returns the list of points on the contour of the shape / the path of the SVG.
  """
  tree = ET.parse(path)
  root = tree.getroot()
  if root.tag.removeprefix(f'{{{XMLNS}}}') != "svg":
    raise ValueError("Root tag must be <svg>")
  if "transform" in root.attrib:
    transform = parse_transform(root.attrib["transform"])
  else:
    transform = np.eye(3)
  shapes = parse_svg(root, transform)
  
  points = []
  for s in shapes:
    assert s.tag in ["rect", "circle", "ellipse", "line", "polygon", "path", "polyline"]
    if s.tag == "rect":
      d_string = rect2pathd(s.attributes)
    elif s.tag in ["circle", "ellipse"]:
      d_string = ellipse2pathd(s.attributes)
    elif s.tag == "line":
      l = s.attributes
      d_string = 'M' + l['x1'] + ' ' + l['y1'] + 'L' + l['x2'] + ' ' + l['y2']
    elif s.tag == "polygon":
      d_string = polygon2pathd(s.attributes)
    elif s.tag == "path":
      d_string = s.attributes["d"]
    elif s.tag == "polyline":
      d_string = polyline2pathd(s.attributes)

    path = parse_path(d_string)
    arr = []
    for i in range(num_points):
      point = path.point(i/num_points)
      transformed = s.transform @ np.array([point.real, point.imag, 1])
      arr.append(transformed[0] + 1j * transformed[1])
    points.append(arr)
  return points

def chamfer_distance(f1: str, f2: str, num_points: int) -> float:
  P1 = get_point_cloud(f1, num_points)
  P2 = get_point_cloud(f2, num_points)

  def distance_between_shapes(S1: list[complex], S2: list[complex]) -> float:
    """
    Returns the distance between two shapes.
    """
    D1 = 0
    for p1 in S1:
      d = min([abs(p1 - p2)**2 for p2 in S2])
      D1 += d
  
    D2 = 0
    for p2 in S2:
      d = min([abs(p1 - p2)**2 for p1 in S1])
      D2 += d
    return D1 / len(S1) + D2 / len(S2)

  D1 = 0
  for S1 in P1:
    d = min([distance_between_shapes(S1, S2) for S2 in P2])
    D1 += d
  
  D2 = 0
  for S2 in P2:
    d = min([distance_between_shapes(S1, S2) for S1 in P1])
    D2 += d
  return D1 / len(P1) + D2 / len(P2)

def calculate_chamfer(prediction_svg: str, prediction_png: str, reference: str) -> dict[str, float]:
  metric = {}
  for file in tqdm(glob(f"{prediction_png}/*.png")):
    triplet_id = os.path.basename(file).removesuffix(".png")
    img_pred = os.path.join(prediction_svg, f"{triplet_id}.svg")
    img_ref = os.path.join(reference, triplet_id, "after.svg")
    try:
      metric[triplet_id] = chamfer_distance(img_pred, img_ref, 100)
    except Exception as e:
      print(f"Error on {triplet_id}: {e}")
  return metric