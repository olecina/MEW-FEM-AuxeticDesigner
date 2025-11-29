import datetime
import glob
import itertools
import json
import os
import shutil
import subprocess
import sys

from PyQt6 import QtWidgets, QtGui, QtCore


# === FILE GENERATORS ===
def generate_gcode(output_dir, design_type, params, i):
	current_dir = os.getcwd()
	try:
		script_dir = os.path.join(current_dir, "scripts/G-code_scripts")
		output_dir = os.path.join(current_dir, output_dir)
		os.chdir(script_dir)

		os.system(f"python gcode_wrapper.py {design_type} {str(params['a'])} {str(params['b'])} {str(params['d'])} {str(params['xr'])} {str(params['yr'])} {str(params['zr'])} {str(i+1)}")

		gcode_name = f"{design_type.lower()}_{i + 1}.gcode"
		src_path = os.path.join(script_dir, gcode_name)
		dst_path = os.path.join(output_dir, gcode_name)

		shutil.move(src_path, dst_path)

	finally:
		os.chdir(current_dir)


def generate_inp(output_dir, design_type, params, i):
	current_dir = os.getcwd()
	try:
		script_dir = os.path.join(current_dir, "scripts/FEM_scripts")
		output_dir = os.path.join(current_dir, output_dir)
		os.chdir(script_dir)
		args = (
			f"abaqus cae noGUI=abaqus_wrapper.py -- {design_type} {str(params['a'])} {str(params['b'])} {str(params['d'])} {str(params['xr'])} {str(params['yr'])} {str(params['zr'])} {str(i+1)}"
		)
		subprocess.run(args, shell=True, check=True)

		inp_name = f"{design_type.lower()}_{i+1}.inp"
		src_path = os.path.join(script_dir, inp_name)
		dst_path = os.path.join(output_dir, inp_name)

		shutil.move(src_path, dst_path)

		if os.path.exists(dst_path):
			rpy_path = os.path.join(script_dir, "abaqus.rpy")
			if os.path.exists(rpy_path):
				os.remove(rpy_path)
		else:
			raise RuntimeError(f"INP file was not successfully moved to: {dst_path}")

	finally:
		os.chdir(current_dir)


def create_session_folder():
	timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
	folder_path = os.path.join("output", f"session_{timestamp}")
	os.makedirs(folder_path, exist_ok=True)
	return folder_path, timestamp


def find_rscript():
	base_dirs = [
		r"C:\Program Files\R",
		r"C:\Program Files (x86)\R"
	]

	for base in base_dirs:
		if os.path.exists(base):
			versions = glob.glob(os.path.join(base, "R-*"))
			if versions:
				# Sort versions by newest
				versions.sort(reverse=True)
				for v in versions:
					candidate = os.path.join(v, "bin", "Rscript.exe")
					if os.path.isfile(candidate):
						return candidate
	return None


class ManualDesignWindow(QtWidgets.QWidget):
	def __init__(self):
		super().__init__()
		self.setWindowTitle("Manual Mode")
		self.setGeometry(100, 100, 650, 450)
		self.layout = QtWidgets.QVBoxLayout()

		# Design type dropdown with image
		self.design_type_label = QtWidgets.QLabel("Select Design Type:")
		self.design_type_combo = QtWidgets.QComboBox()
		self.design_type_combo.addItems(["HCELL", "SREG", "SINV", "STRI"])
		self.design_type_combo.currentTextChanged.connect(self.update_image)

		self.design_image = QtWidgets.QLabel()
		self.design_image.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
		self.update_image(self.design_type_combo.currentText())

		# Input mode selection
		self.input_mode_group = QtWidgets.QGroupBox("Input Mode")
		self.input_mode_layout = QtWidgets.QHBoxLayout()
		self.position_mode = QtWidgets.QRadioButton("Match by position")
		self.combination_mode = QtWidgets.QRadioButton("Generate all combinations")
		self.combination_mode.setChecked(True)
		self.input_mode_layout.addWidget(self.position_mode)
		self.input_mode_layout.addWidget(self.combination_mode)
		self.input_mode_group.setLayout(self.input_mode_layout)

		# Parameter inputs
		self.param_inputs = {}
		param_grid = QtWidgets.QGridLayout()
		params = ['a', 'b', 'd', 'xr', 'yr', 'zr']

		for i, param in enumerate(params):
			row = i // 3  # 0 or 1
			col = i % 3  # 0, 1, 2
			label = QtWidgets.QLabel(f"{param}:")
			input_field = QtWidgets.QLineEdit()
			input_field.textChanged.connect(self.update_preview)
			param_grid.addWidget(label, row * 2, col)
			param_grid.addWidget(input_field, row * 2 + 1, col)
			self.param_inputs[param] = input_field

		self.layout.addLayout(param_grid)

		# Output options
		self.gcode_check = QtWidgets.QCheckBox("Generate G-code")
		self.inp_check = QtWidgets.QCheckBox("Generate ABAQUS .inp")

		# Preview table
		self.preview_label = QtWidgets.QLabel("Preview of Parameter Combinations:")
		self.preview_table = QtWidgets.QTableWidget()
		self.preview_table.setColumnCount(6)
		self.preview_table.setHorizontalHeaderLabels(['a', 'b', 'd', 'xr', 'yr', 'zr'])

		# Generate button
		self.generate_button = QtWidgets.QPushButton("Generate Files")
		self.generate_button.clicked.connect(self.generate_files)

		# Status label
		self.status_label = QtWidgets.QLabel("")

		# Assemble layout
		self.layout.addWidget(self.design_type_label)
		self.layout.addWidget(self.design_type_combo)
		self.layout.addWidget(self.design_image)
		self.layout.addWidget(self.input_mode_group)
		self.layout.addWidget(self.gcode_check)
		self.layout.addWidget(self.inp_check)
		self.layout.addWidget(self.preview_label)
		self.layout.addWidget(self.preview_table)
		self.layout.addWidget(self.generate_button)
		self.layout.addWidget(self.status_label)

		self.setLayout(self.layout)
		self.position_mode.toggled.connect(self.update_preview)
		self.combination_mode.toggled.connect(self.update_preview)
		self.update_preview()

	def update_image(self, design_type):
		image_path = os.path.join("ui_components", "images", f"{design_type.lower()}.png")
		if os.path.exists(image_path):
			pixmap = QtGui.QPixmap(image_path)
			self.design_image.setPixmap(pixmap.scaled(200, 200, QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation))
		else:
			self.design_image.setText("[Image not available]")

	def get_param_combinations(self):
		param_lists = {}
		for param, field in self.param_inputs.items():
			raw = field.text()
			if not raw:
				return [], {}
			param_lists[param] = [x.strip() for x in raw.split(",") if x.strip()]

		if self.position_mode.isChecked():
			lengths = [len(v) for v in param_lists.values()]
			if len(set(lengths)) != 1:
				return [], param_lists
			combinations = [dict(zip(param_lists.keys(), vals)) for vals in zip(*param_lists.values())]
		else:
			keys, values = zip(*param_lists.items())
			combos = itertools.product(*values)
			combinations = [dict(zip(keys, combo)) for combo in combos]

		return combinations, param_lists

	def update_preview(self):
		combinations, _ = self.get_param_combinations()
		self.preview_table.setRowCount(len(combinations))
		for row_idx, combo in enumerate(combinations):
			for col_idx, key in enumerate(['a', 'b', 'd', 'xr', 'yr', 'zr']):
				self.preview_table.setItem(row_idx, col_idx, QtWidgets.QTableWidgetItem(combo.get(key, "")))

	def generate_files(self):
		design_type = self.design_type_combo.currentText()
		generate_g = self.gcode_check.isChecked()
		generate_i = self.inp_check.isChecked()

		param_combinations, param_lists = self.get_param_combinations()
		if not param_combinations:
			self.status_label.setText("Invalid or missing parameters.")
			return

		output_dir, timestamp = create_session_folder()
		generated_files = []

		for i, params in enumerate(param_combinations):
			if generate_g:
				generate_gcode(output_dir, design_type, params, i)
				generated_files.append(f"{design_type.lower()}_{i}.gcode")
			if generate_i:
				generate_inp(output_dir, design_type, params, i)
				generated_files.append(f"{design_type.lower()}_{i}.inp")

		# Write metadata.json
		metadata = {
			"design_type": design_type,
			"input_mode": "position" if self.position_mode.isChecked() else "combinations",
			"parameters": param_lists,
			"timestamp": timestamp,
			"output_files": generated_files
		}
		with open(os.path.join(output_dir, "metadata.json"), "w") as meta_file:
			json.dump(metadata, meta_file, indent=2)

		self.status_label.setText(f"Files and metadata saved in {output_dir}")


class InverseDesignWindow(QtWidgets.QWidget):
	def __init__(self):
		super().__init__()
		self.setWindowTitle("Predictive Mode")
		self.setGeometry(100, 100, 840, 600)
		self.layout = QtWidgets.QVBoxLayout()

		# Target input
		self.prop_label = QtWidgets.QLabel("Enter Target (kPa):")
		self.prop_input = QtWidgets.QLineEdit()

		# Output file options
		self.gcode_check = QtWidgets.QCheckBox("Generate G-code")
		self.inp_check = QtWidgets.QCheckBox("Generate ABAQUS .inp")

		# Predict button
		self.predict_button = QtWidgets.QPushButton("Find Optimal Designs")
		self.predict_button.clicked.connect(self.predict_design)

		# Result table
		self.result_table = QtWidgets.QTableWidget()
		self.result_table.setColumnCount(8)
		self.result_table.setHorizontalHeaderLabels([
			"design", "a", "rba", "d", "yr", "E_aux [kPa]", "ε_aux [-]", "error [%]"
		])
		self.result_table.setEditTriggers(QtWidgets.QAbstractItemView.EditTrigger.NoEditTriggers)
		self.result_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)
		self.result_table.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.MultiSelection)

		# Generate files button
		self.generate_button = QtWidgets.QPushButton("Generate Files for Selected")
		self.generate_button.clicked.connect(self.generate_files)

		# Info label
		self.result_label = QtWidgets.QLabel("Suggested Designs will appear below.")

		# Image display
		self.image_panel_layout = QtWidgets.QHBoxLayout()

		design_types = ["HCELL", "SREG", "SINV", "STRI"]

		for design in design_types:
			vbox_mini = QtWidgets.QVBoxLayout()

			img_label = QtWidgets.QLabel()
			img_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
			img_label.setFrameStyle(QtWidgets.QFrame.Shape.Box | QtWidgets.QFrame.Shadow.Plain)

			image_path = os.path.join("ui_components", "images", f"{design.lower()}.png")

			if os.path.exists(image_path):
				pixmap = QtGui.QPixmap(image_path)
				scaled_pixmap = pixmap.scaled(150, 150, QtCore.Qt.AspectRatioMode.KeepAspectRatio, QtCore.Qt.TransformationMode.SmoothTransformation)
				img_label.setPixmap(scaled_pixmap)
			else:
				img_label.setText(f"[{design}\nNot Found]")

			text_label = QtWidgets.QLabel(design)
			text_label.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
			font = text_label.font()
			font.setBold(True)
			text_label.setFont(font)

			vbox_mini.addWidget(img_label)
			vbox_mini.addWidget(text_label)

			self.image_panel_layout.addLayout(vbox_mini)

		# Layout
		self.layout.addWidget(self.prop_label)
		self.layout.addWidget(self.prop_input)
		self.layout.addWidget(self.gcode_check)
		self.layout.addWidget(self.inp_check)
		self.layout.addWidget(self.predict_button)
		self.layout.addWidget(self.result_label)
		self.layout.addWidget(self.result_table)

		self.layout.addWidget(QtWidgets.QLabel("Available Design Types Reference:"))
		self.layout.addLayout(self.image_panel_layout)

		self.layout.addWidget(self.generate_button)

		self.setLayout(self.layout)

	def predict_design(self):
		target = self.prop_input.text()
		if not target:
			self.result_label.setText("Please enter a target property.")
			return

		current_dir = os.getcwd()
		try:
			script_dir = os.path.join(current_dir, "models")
			if os.path.exists(script_dir):
				os.chdir(script_dir)

			rscript_path = find_rscript()
			if rscript_path is None:
				print("Rscript.exe not found. Please install R or check your environment.")
				self.result_label.setText("Error: Rscript not found")
			else:
				cmd = f'"{rscript_path}" r_predictor.R {str(target)}'
				os.system(cmd)

			json_name = "prediction.json"
			if os.path.exists(json_name):
				with open(json_name, "r") as f:
					results = json.load(f)
					self.show_results(list(results.values()))
			else:
				self.results_label.setText("Prediction failed (no output file).")

		finally:
			os.chdir(current_dir)

	def show_results(self, results):
		self.result_table.setRowCount(0)
		self.result_table.setRowCount(len(results))
		self.designs = results

		for row, entry in enumerate(results):
			for col, key in enumerate(["design", "a", "ab", "d", "yr", "module", "strain", "error"]):
				self.result_table.setItem(row, col, QtWidgets.QTableWidgetItem(str(entry[key])))

	def generate_files(self):
		selected_indexes = self.result_table.selectionModel().selectedRows()
		if not selected_indexes:
			self.result_label.setText("Please select one or more designs.")
			return

		output_dir, timestamp = create_session_folder()
		for idx, model in enumerate(selected_indexes):
			entry = self.designs[model.row()]
			params = {
				"a": entry["a"],
				"b": round(entry["a"] * entry["ab"], 2),
				"d": entry["d"],
				"xr": 6,
				"yr": entry["yr"],
				"zr": 10
			}

			if self.gcode_check.isChecked():
				generate_gcode(output_dir, str(entry["design"]).upper(), params, idx)
			if self.inp_check.isChecked():
				generate_inp(output_dir, str(entry["design"]).upper(), params, idx)

		self.result_label.setText(f"Files saved in {output_dir}")


class MainWindow(QtWidgets.QWidget):
	def __init__(self):
		super().__init__()
		self.setWindowTitle("Auxetic MEW Scaffolds Design Interface")
		self.setGeometry(100, 100, 400, 100)
		self.layout = QtWidgets.QVBoxLayout()

		self.label = QtWidgets.QLabel("Choose Design Mode:")
		self.manual_button = QtWidgets.QPushButton("Manual Mode")
		self.inverse_button = QtWidgets.QPushButton("Predictive Mode")

		self.layout.addWidget(self.label)
		self.layout.addWidget(self.manual_button)
		self.layout.addWidget(self.inverse_button)
		self.setLayout(self.layout)

		self.manual_button.clicked.connect(self.open_manual_design)
		self.inverse_button.clicked.connect(self.open_inverse_design)

	def open_manual_design(self):
		self.manual_window = ManualDesignWindow()
		self.manual_window.show()

	def open_inverse_design(self):
		self.inverse_window = InverseDesignWindow()
		self.inverse_window.show()


if __name__ == '__main__':
	app = QtWidgets.QApplication(sys.argv)
	main_window = MainWindow()
	main_window.show()
	sys.exit(app.exec())
