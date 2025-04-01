# -*- coding: utf-8 -*-
"""SamuModel

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/14Q5IHidVVd9xf6Uo7_g9plvo1FGmdXDi
"""

!pip install ultralytics

from ultralytics import YOLO
import os
from IPython.display import Image, clear_output
from IPython import display
display.clear_output()
!yolo checks

!pip install roboflow

from roboflow import Roboflow
rf = Roboflow(api_key="6d82EoqNfCYB1bpOIlfW")
project = rf.workspace("m-lspoq").project("co-detection")
version = project.version(1)
dataset = version.download("yolov8")

!yolo task=detect mode= train model=yolov8m.pt data={dataset.location}/data.yaml epochs=300 imgsz=640

!pip install onnx-simplifier

!python -m onnxsim /content/best.onnx /content/best_simplified.onnx

!yolo version

from google.colab import files
files.download('yolov8m.onnx')  # Change path if needed

import onnx
from onnx import helper

# Load the ONNX model
model_path = "/content/best_simplified.onnx"
model = onnx.load(model_path)

# Iterate over nodes to find "Split" operations
for node in model.graph.node:
    if node.op_type == "Split":
        has_split_attr = any(attr.name == "split" for attr in node.attribute)

        # If "split" attribute is missing, add it explicitly
        if not has_split_attr:
            print(f"Fixing Split attribute for node: {node.name}")
            split_attr = helper.make_attribute("split", [1, 1])  # Set explicit split values
            node.attribute.append(split_attr)

# Save the fixed ONNX model
fixed_model_path = "/content/best_simplified_fixed.onnx"
onnx.save(model, fixed_model_path)
print(f"Fixed ONNX model saved as: {fixed_model_path}")

!pip install onnx onnx_graphsurgeon

import onnx
import onnx_graphsurgeon as gs
import numpy as np

# Load ONNX model
model_path = "/content/best_simplified.onnx"
model = onnx.load(model_path)

# Convert model to GraphSurgeon format
graph = gs.import_onnx(model)

# Iterate through nodes and fix "Split"
for node in graph.nodes:
    if node.op == "Split":
        # Remove "split" attribute if present
        node.attrs.pop("split", None)

        # Define explicit split sizes (modify if needed)
        split_sizes = np.array([1, 1], dtype=np.int64)

        # Create a new tensor for split sizes
        split_tensor = gs.Constant(name=node.name + "_split", values=split_sizes)

        # Add split tensor as an input instead of an attribute
        node.inputs.append(split_tensor)

        print(f"Fixed Split node: {node.name}")

# Export the modified model
fixed_model_path = "/content/best_simplified_fixed.onnx"
onnx.save(gs.export_onnx(graph), fixed_model_path)
print(f"Fixed model saved as: {fixed_model_path}")

!pip install onnxconverter-common
from onnxconverter_common import float16

model = onnx.load(fixed_model_path)
model_fp16 = float16.convert_float_to_float16(model)  # Convert to FP16
onnx.save(model_fp16, "/content/best_simplified_opset10.onnx")
print("Converted to Opset 10.")

import onnx

model = onnx.load("best_simplified_opset10.onnx")
print([inp.name for inp in model.graph.input])

!python -m ultralytics export --weights best.pt --format onnx --dynamic

from ultralytics import YOLO

# Load trained YOLOv8 model
model = YOLO("best.pt")  # Replace with your model path

# Export to ONNX format
model.export(format="onnx", dynamic=True, opset=11)

import os
print("ONNX file exists:", os.path.exists("best.onnx"))

from google.colab import files
files.download("best.onnx")

!pip install onnx onnxruntime-tools

!python -m onnxsim best.onnx best_simplified.onnx --input-shape 1,3,640,640

from ultralytics import YOLO

# Load trained YOLOv8 model
model = YOLO("best.pt")  # Replace with the correct model file if needed

# Export to ONNX format
model.export(format="onnx", dynamic=True, opset=12)

import onnx
from onnxsim import simplify

# Load the original model
model_path = "best.onnx"
onnx_model = onnx.load(model_path)

# Simplify the ONNX model
simplified_model, check = simplify(onnx_model)

# Save the simplified model
simplified_model_path = "best_simplified.onnx"
onnx.save(simplified_model, simplified_model_path)

print("ONNX model simplified successfully.")

import onnx
import onnxsim

# Load your ONNX model
model_path = "best.onnx"
simplified_model_path = "best_simplified.onnx"

# Simplify model
model = onnx.load(model_path)
simplified_model, check = onnxsim.simplify(model)

# Save simplified model
onnx.save(simplified_model, simplified_model_path)
print(f"Simplified model saved at: {simplified_model_path}")

!pip install onnx onnxruntime onnxsim

!pip install onnx onnxruntime onnxsim

from google.colab import files
files.download("best_simplified_o1_cpu.onnx")

import onnx

# Load ONNX model
model_path = "best_simplified.onnx"
onnx_model = onnx.load(model_path)

# Print model input/output info
for input_tensor in onnx_model.graph.input:
    print(f"Input: {input_tensor.name}, Shape: {input_tensor.type}")

for output_tensor in onnx_model.graph.output:
    print(f"Output: {output_tensor.name}, Shape: {output_tensor.type}")

import onnx
from onnx import helper

model_path = "best_simplified.onnx"
onnx_model = onnx.load(model_path)

# Modify input shape to fixed dimensions (e.g., batch=1, height=224, width=224)
for input_tensor in onnx_model.graph.input:
    if input_tensor.type.tensor_type.HasField("shape"):
        input_tensor.type.tensor_type.shape.dim[0].dim_value = 1  # Batch size = 1
        input_tensor.type.tensor_type.shape.dim[2].dim_value = 224  # Height = 224
        input_tensor.type.tensor_type.shape.dim[3].dim_value = 224  # Width = 224

# Save the modified model
onnx.save(onnx_model, "fixed_model.onnx")

for node in onnx_model.graph.node:
    if node.op_type in ["Unsqueeze", "Expand"]:
        print(node)

from google.colab import files
files.download("fixed_model.onnx")