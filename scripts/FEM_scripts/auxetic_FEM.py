from abaqus import *
from abaqusConstants import *
from math import *


def sinv(a, b, diameter, x_rep, y_rep, z_rep, id):
	"""
				Creates an auxetic model with S_INVERTED geometry design written to .inp file.

				Args:
					- a (float):
					- b (float):
					- diameter (float):
					- x_rep (int):
					- y_rep (int):
					- z_rep (int):
	"""

	# ------------------ GLOBAL VARIABLES ----------------------------

	# -----------------------
	# GENERAL VARIABLE NAMES:
	# -----------------------

	model_name = 'auxetic_model'
	part_name = 'auxetic cell'
	material_name = 'PCL'
	section_name = 'beam_section'
	instance_name = 'assembly_instance'
	merged_part_name = 'merged_part'
	merged_part_instance_name = 'merged_part_instance'
	step_name = 'loading_step'
	set_fix_nodes_name = 'fix_nodes'
	set_left_nodes_name = 'left_nodes'
	set_bottom_nodes_name = 'bottom_nodes'
	set_right_nodes_name = 'right_nodes'
	set_top_nodes_name = 'top_nodes'
	boundary_condition_fix_nodes_name = 'fix_nodes_bc'
	boundary_condition_bottom_name = 'bottom_bc'
	boundary_condition_top_name = 'top_bc'
	boundary_condition_left_name = 'left_bc'
	boundary_condition_right_name = 'right_bc'
	left_rf_output_name = 'left_RF_output'
	left_u_output_name = 'left_U_output'
	bottom_rf_output_name = 'bottom_RF_output'
	bottom_u_output_name = 'bottom_U_output'
	right_rf_output_name = 'right_RF_output'
	right_u_output_name = 'right_U_output'
	top_rf_output_name = 'top_RF_output'
	top_u_output_name = 'top_U_output'
	job_name = 'sinv_' + str(id)

	# ------------------
	# AUXILIAR VARIABLES:
	# ------------------

	elem_size = 10 * diameter  # global size of elements

	g_offset = 10  # small margin to avoid rounding issues

	step_time = 20

	timeInterv = 0.1

	x_spacing = 4 * a
	y_spacing = 4 * a
	z_spacing = diameter

	x_size = 4 * a * x_rep
	y_size = 4 * a * y_rep

	frame_length = 10 * a

	displacement_x = 3 * x_rep * sqrt(a ** 2 + b ** 2)
	displacement_y = 3 * y_rep * sqrt(a ** 2 + b ** 2)

	# -----------------------
	# BOUNDARY SETS CONDITIONS:
	# -----------------------

	xmin_left = - g_offset
	xmax_left = + g_offset
	ymin_bottom = - g_offset
	ymax_bottom = g_offset
	xmin_right = x_size + frame_length - g_offset
	xmax_right = x_size + frame_length + g_offset
	ymin_top = y_size + frame_length - g_offset
	ymax_top = y_size + frame_length + g_offset

	# ----------------------------------------------------------------
	# START MODEL GENERATION:
	# ----------------------------------------------------------------

	# This line is required to make the ABAQUS viewport display nothing

	session.viewports['Viewport: 1'].setValues(displayedObject=None)

	# Model creation
	# By default, ABAQUS creates a model named Model-1.

	auxetic_model = mdb.Model(name=model_name)

	auxetic_model.setValues(noPartsInputFile=OFF)

	# Material creation

	import material

	# Scaffold material is Polycaprolactone (PCL)

	cell_material = auxetic_model.Material(name=material_name)

	cell_material.Density(table=((1.145 * 10 ** -12,),))  # Density - Units: [10^15 kg/m^3]

	cell_material.Elastic(table=((0.1, 0.3),))  # Elastic props. (Young's modulus, Poisson's ratio)

	cell_material.Plastic(table=((0.012, 0.0), (0.0145, 0.25), (0.017, 0.5), (0.0195, 1),))

	# ----------------------------------------------------------------
	# Part creation

	import sketch
	import part

	# -----------------------
	# Basic Part (auxetic cell)

	part_sketch = auxetic_model.ConstrainedSketch(name='Part sketch', sheetSize=2000)

	part_sketch.Spline(points=((0.0, 0.0), (b, a), (0.0, 2 * a)))
	part_sketch.Spline(points=((0.0, 2 * a), (- b, 3 * a), (0.0, 4 * a)))

	part_sketch.Spline(points=((0.0, 0.0), (a, - b), (2 * a, 0.0)))
	part_sketch.Spline(points=((2 * a, 0.0), (3 * a, b), (4 * a, 0.0)))

	part_sketch.Spline(points=((2 * a, 0.0), (2 * a - b, a), (2 * a, 2 * a)))
	part_sketch.Spline(points=((2 * a, 2 * a), (2 * a + b, 3 * a), (2 * a, 4 * a)))

	part_sketch.Spline(points=((0.0, 2 * a), (a, 2 * a + b), (2 * a, 2 * a)))
	part_sketch.Spline(points=((2 * a, 2 * a), (3 * a, 2 * a - b), (4 * a, 2 * a)))

	part_sketch.Line(point1=(0.0, y_size), point2=(0.0, y_size + frame_length))

	part_sketch.Line(point1=(x_size, 0.0), point2=(x_size + frame_length, 0.0))

	g = part_sketch.geometry

	part_sketch.linearPattern(geomList=(g[2], g[3]), vertexList=(),
							  number1=x_rep + 1, spacing1=x_spacing, angle1=0.0,
							  number2=y_rep, spacing2=y_spacing, angle2=90.0)

	part_sketch.linearPattern(geomList=(g[4], g[5]), vertexList=(),
							  number1=x_rep, spacing1=x_spacing, angle1=0.0,
							  number2=y_rep + 1, spacing2=y_spacing, angle2=90.0)

	part_sketch.linearPattern(geomList=(g[6], g[7], g[8], g[9]), vertexList=(),
							  number1=x_rep, spacing1=x_spacing, angle1=0.0,
							  number2=y_rep, spacing2=y_spacing, angle2=90.0)

	part_sketch.linearPattern(geomList=(g[10],), vertexList=(),
							  number1=2 * x_rep + 1, spacing1=x_spacing / 2, angle1=0.0,
							  number2=1, spacing2=y_spacing, angle2=90.0)

	part_sketch.linearPattern(geomList=(g[11],), vertexList=(),
							  number1=1, spacing1=x_spacing, angle1=0.0,
							  number2=2 * y_rep + 1, spacing2=y_spacing / 2, angle2=90.0)

	part = auxetic_model.Part(name=part_name, dimensionality=THREE_D, type=DEFORMABLE_BODY)
	part.BaseWire(sketch=part_sketch)

	# -----------------------------------------------------------------
	# Assembly creation

	import assembly

	model_assembly = auxetic_model.rootAssembly

	model_assembly.Instance(name=instance_name, part=part, dependent=OFF)

	model_assembly.LinearInstancePattern(instanceList=(instance_name,),
										 direction1=(1.0, 0.0, 0.0), direction2=(0.0, 0.0, 1.0),
										 number1=1, number2=z_rep, spacing1=1.0, spacing2=z_spacing)

	model_assembly.InstanceFromBooleanMerge(name=merged_part_name, instances=model_assembly.instances.values(),
											originalInstances=DELETE, domain=GEOMETRY)

	model_assembly.features.changeKey(fromName=merged_part_name + '-1', toName=merged_part_instance_name)

	# -----------------------------------------------------------------
	# Section creation and assignment

	import section
	import regionToolset

	auxetic_model.CircularProfile(name='circular_profile', r=diameter / 2)

	auxetic_model.BeamSection(name=section_name, integration=DURING_ANALYSIS, poissonRatio=0.3,
							  profile='circular_profile', material=material_name)

	merged_part = auxetic_model.parts[merged_part_name]

	merged_region = regionToolset.Region(edges=merged_part.edges)

	merged_part.SectionAssignment(region=merged_region, sectionName=section_name)

	merged_part.assignBeamSectionOrientation(region=merged_region, method=N1_COSINES, n1=(0.0, 0.0, -1.0))

	# -----------------------------------------------------------------
	# Mesh

	import mesh

	merged_part.seedPart(size=elem_size, deviationFactor=0.1, minSizeFactor=0.8)

	elem_type = mesh.ElemType(elemCode=B31, elemLibrary=STANDARD)

	merged_part.generateMesh()

	merged_part.setElementType(regions=(merged_part.edges,), elemTypes=(elem_type,))

	# -----------------------------------------------------------------
	# Step creation

	import step

	auxetic_model.ExplicitDynamicsStep(name=step_name, previous='Initial', nlgeom=ON, timePeriod=step_time, maxIncrement=0.00012)

	# -----------------------------------------------------------------
	# Sets definition + Constraint (TIE) on crossed-fiber nodes through layers

	all_nodes = merged_part.nodes

	fix_nodes = []

	left_nodes = []
	bottom_nodes = []
	right_nodes = []
	top_nodes = []

	x_coord_list, y_coord_list = [i * x_spacing / 2 for i in range(2 * x_rep + 1)], \
								 [j * y_spacing / 2 for j in range(2 * y_rep + 1)]

	x_coord_list.append(x_size + frame_length)
	y_coord_list.append(y_size + frame_length)

	rows, columns = len(y_coord_list), len(x_coord_list)

	model_constraints = [[{'ref_node': [], 'node_region': []} for _ in range(columns)] for _ in range(rows)]

	tol = 0.001 * diameter

	for n in all_nodes:
		xcoord = n.coordinates[0] if n.coordinates[0] < - tol or n.coordinates[0] > tol else 0.0
		ycoord = n.coordinates[1] if n.coordinates[1] < - tol or n.coordinates[1] > tol else 0.0
		zcoord = n.coordinates[2] if n.coordinates[2] < - tol or n.coordinates[2] > tol else 0.0

		if xcoord in x_coord_list and ycoord in y_coord_list:
			if xcoord != x_coord_list[-1] or ycoord != y_coord_list[-1]:
				i = x_coord_list.index(xcoord)
				j = y_coord_list.index(ycoord)
				if -0.01 < zcoord < 0.01:
					model_constraints[j][i]['ref_node'].append(n)
				else:
					model_constraints[j][i]['node_region'].append(n)

		if xcoord < g_offset and ycoord < g_offset:
			fix_nodes.append(n)
		if xmin_left < xcoord < xmax_left and ymax_bottom < ycoord < ymax_top - frame_length:
			left_nodes.append(n)
		if ymin_bottom < ycoord < ymax_bottom and xmax_left < xcoord < xmax_right - frame_length:
			bottom_nodes.append(n)
		if xmin_right < xcoord < xmax_right and ycoord < ymin_top:
			right_nodes.append(n)
		if ymin_top < ycoord < ymax_top and xcoord < xmin_right:
			top_nodes.append(n)

	import interaction

	for j, row in enumerate(model_constraints):
		for i, constraint in enumerate(row):
			if j != len(model_constraints) - 1 or i != len(row) - 1:
				name = 'constraint' + str(i) + str(j)

				mesh_ref_node = mesh.MeshNodeArray(constraint['ref_node'])
				set_ref_node_name = name + 'ref node'
				merged_part.Set(nodes=mesh_ref_node, name=set_ref_node_name)
				set_ref_node = auxetic_model.rootAssembly.instances[merged_part_instance_name].sets[set_ref_node_name]

				mesh_node_region = mesh.MeshNodeArray(constraint['node_region'])
				set_node_region_name = name + 'node_region'
				merged_part.Set(nodes=mesh_node_region, name=set_node_region_name)
				set_node_region = auxetic_model.rootAssembly.instances[merged_part_instance_name].sets[
					set_node_region_name]

				auxetic_model.RigidBody(name=name, refPointRegion=set_ref_node, tieRegion=set_node_region)


	mesh_fix_nodes = mesh.MeshNodeArray(fix_nodes)
	merged_part.Set(nodes=mesh_fix_nodes, name=set_fix_nodes_name)

	mesh_left_nodes = mesh.MeshNodeArray(left_nodes)
	merged_part.Set(nodes=mesh_left_nodes, name=set_left_nodes_name)

	mesh_bottom_nodes = mesh.MeshNodeArray(bottom_nodes)
	merged_part.Set(nodes=mesh_bottom_nodes, name=set_bottom_nodes_name)

	mesh_right_nodes = mesh.MeshNodeArray(right_nodes)
	merged_part.Set(nodes=mesh_right_nodes, name=set_right_nodes_name)

	mesh_top_nodes = mesh.MeshNodeArray(top_nodes)
	merged_part.Set(nodes=mesh_top_nodes, name=set_top_nodes_name)

	set_fix_nodes = auxetic_model.rootAssembly.instances[merged_part_instance_name].sets[set_fix_nodes_name]
	set_left_nodes = auxetic_model.rootAssembly.instances[merged_part_instance_name].sets[set_left_nodes_name]
	set_bottom_nodes = auxetic_model.rootAssembly.instances[merged_part_instance_name].sets[set_bottom_nodes_name]
	set_right_nodes = auxetic_model.rootAssembly.instances[merged_part_instance_name].sets[set_right_nodes_name]
	set_top_nodes = auxetic_model.rootAssembly.instances[merged_part_instance_name].sets[set_top_nodes_name]

	# -----------------------------------------------------------------
	# Boundary conditions and loads

	vel_x = displacement_x / step_time
	vel_y = displacement_y / step_time

	# FIX NODES BC
	auxetic_model.EncastreBC(name=boundary_condition_fix_nodes_name, createStepName=step_name, region=set_fix_nodes)

	# BOTTOM BC
	auxetic_model.YsymmBC(name=boundary_condition_bottom_name, createStepName=step_name, region=set_bottom_nodes)

	# TOP BC
	auxetic_model.VelocityBC(name=boundary_condition_top_name, createStepName=step_name,
							 region=set_top_nodes, v1=0.0, v2=vel_y, v3=0.0)

	# LEFT BC
	auxetic_model.XsymmBC(name=boundary_condition_left_name, createStepName=step_name, region=set_left_nodes)

	# RIGHT BC
	auxetic_model.VelocityBC(name=boundary_condition_right_name, createStepName=step_name,
							 region=set_right_nodes, v1=vel_x, v2=0.0, v3=0.0)

	# -----------------------------------------------------------------
	# History Output

	auxetic_model.HistoryOutputRequest(name=left_rf_output_name, createStepName=step_name,
									   variables=('RF1',), timeInterval=timeInterv, region=set_left_nodes)
	auxetic_model.HistoryOutputRequest(name=left_u_output_name, createStepName=step_name,
									   variables=('U1',), timeInterval=timeInterv, region=set_left_nodes)
	auxetic_model.HistoryOutputRequest(name=bottom_rf_output_name, createStepName=step_name,
									   variables=('RF2',), timeInterval=timeInterv, region=set_bottom_nodes)
	auxetic_model.HistoryOutputRequest(name=bottom_u_output_name, createStepName=step_name,
									   variables=('U2',), timeInterval=timeInterv, region=set_bottom_nodes)
	auxetic_model.HistoryOutputRequest(name=right_rf_output_name, createStepName=step_name,
									   variables=('RF1',), timeInterval=timeInterv, region=set_right_nodes)
	auxetic_model.HistoryOutputRequest(name=right_u_output_name, createStepName=step_name,
									   variables=('U1',), timeInterval=timeInterv, region=set_right_nodes)
	auxetic_model.HistoryOutputRequest(name=top_rf_output_name, createStepName=step_name,
									   variables=('RF2',), timeInterval=timeInterv, region=set_top_nodes)
	auxetic_model.HistoryOutputRequest(name=top_u_output_name, createStepName=step_name,
									   variables=('U2',), timeInterval=timeInterv, region=set_top_nodes)

	# -----------------------------------------------------------------
	# Job creation

	mdb.Job(name=job_name, model=model_name, description='', type=ANALYSIS, atTime=None,
			waitMinutes=0, waitHours=0, queue=None, memory=90, memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True,
			explicitPrecision=DOUBLE, nodalOutputPrecision=SINGLE, parallelizationMethodExplicit=DOMAIN,
			numDomains=16, echoPrint=OFF, modelPrint=OFF, contactPrint=OFF, historyPrint=OFF,
			userSubroutine='', scratch='', multiprocessingMode=DEFAULT, numCpus=4)

	mdb.jobs[job_name].writeInput(consistencyChecking=OFF)

	# -----------------------------------------------------------------


def sreg(a, b, diameter, x_rep, y_rep, z_rep, id):
	"""
				Creates an auxetic model with S_REGULAR geometry design written to .inp file.

				Args:
					- a (float):
					- b (float):
					- diameter (float):
					- x_rep (int):
					- y_rep (int):
					- z_rep (int):
	"""

	# ------------------ GLOBAL VARIABLES ----------------------------

	# -----------------------
	# GENERAL VARIABLE NAMES:
	# -----------------------

	model_name = 'auxetic_model'
	part_name = 'auxetic cell'
	material_name = 'PCL'
	section_name = 'beam_section'
	instance_name = 'assembly_instance'
	merged_part_name = 'merged_part'
	merged_part_instance_name = 'merged_part_instance'
	step_name = 'loading_step'
	set_fix_nodes_name = 'fix_nodes'
	set_left_nodes_name = 'left_nodes'
	set_bottom_nodes_name = 'bottom_nodes'
	set_right_nodes_name = 'right_nodes'
	set_top_nodes_name = 'top_nodes'
	boundary_condition_fix_nodes_name = 'fix_nodes_bc'
	boundary_condition_bottom_name = 'bottom_bc'
	boundary_condition_top_name = 'top_bc'
	boundary_condition_left_name = 'left_bc'
	boundary_condition_right_name = 'right_bc'
	left_rf_output_name = 'left_RF_output'
	left_u_output_name = 'left_U_output'
	bottom_rf_output_name = 'bottom_RF_output'
	bottom_u_output_name = 'bottom_U_output'
	right_rf_output_name = 'right_RF_output'
	right_u_output_name = 'right_U_output'
	top_rf_output_name = 'top_RF_output'
	top_u_output_name = 'top_U_output'
	job_name = 'sreg_' + str(id)

	# ------------------
	# AUXILIAR VARIABLES:
	# ------------------

	elem_size = 10 * diameter  # global size of elements

	g_offset = 10  # small margin to avoid rounding issues

	step_time = 20

	timeInterv = 0.1

	x_spacing = 4 * a
	y_spacing = 4 * a
	z_spacing = diameter

	x_size = 4 * a * x_rep
	y_size = 4 * a * y_rep

	frame_length = 10 * a

	displacement_x = 3 * x_rep * sqrt(a ** 2 + b ** 2)
	displacement_y = 3 * y_rep * sqrt(a ** 2 + b ** 2)

	# -----------------------
	# BOUNDARY SETS CONDITIONS:
	# -----------------------

	xmin_left = - g_offset
	xmax_left = + g_offset
	ymin_bottom = - g_offset
	ymax_bottom = g_offset
	xmin_right = x_size + frame_length - g_offset
	xmax_right = x_size + frame_length + g_offset
	ymin_top = y_size + frame_length - g_offset
	ymax_top = y_size + frame_length + g_offset

	# ----------------------------------------------------------------
	# START MODEL GENERATION:
	# ----------------------------------------------------------------

	# This line is required to make the ABAQUS viewport display nothing

	session.viewports['Viewport: 1'].setValues(displayedObject=None)

	# Model creation
	# By default, ABAQUS creates a model named Model-1.

	auxetic_model = mdb.Model(name=model_name)

	auxetic_model.setValues(noPartsInputFile=OFF)

	# Material creation

	import material

	# Scaffold material is Polycaprolactone (PCL)

	cell_material = auxetic_model.Material(name=material_name)

	cell_material.Density(table=((1.145 * 10 ** -12,),))  # Density - Units: [10^15 kg/m^3]

	cell_material.Elastic(table=((0.1, 0.3),))  # Elastic props. (Young's modulus, Poisson's ratio)

	cell_material.Plastic(table=((0.012, 0.0), (0.0145, 0.25), (0.017, 0.5), (0.0195, 1),))

	# ----------------------------------------------------------------
	# Part creation

	import sketch
	import part

	# -----------------------
	# Basic Part (auxetic cell)

	part_sketch = auxetic_model.ConstrainedSketch(name='Part sketch', sheetSize=2000)

	part_sketch.Spline(points=((0.0, 0.0), (b, a), (0.0, 2 * a)))
	part_sketch.Spline(points=((0.0, 2 * a), (- b, 3 * a), (0.0, 4 * a)))

	part_sketch.Spline(points=((0.0, 0.0), (a, - b), (2 * a, 0.0)))
	part_sketch.Spline(points=((2 * a, 0.0), (3 * a, b), (4 * a, 0.0)))

	part_sketch.Line(point1=(0.0, y_size), point2=(0.0, y_size + frame_length))

	part_sketch.Line(point1=(x_size, 0.0), point2=(x_size + frame_length, 0.0))

	g = part_sketch.geometry

	part_sketch.linearPattern(geomList=(g[2], g[3]), vertexList=(),
							  number1=x_rep + 1, spacing1=x_spacing, angle1=0.0,
							  number2=y_rep, spacing2=y_spacing, angle2=90.0)

	part_sketch.linearPattern(geomList=(g[4], g[5]), vertexList=(),
							  number1=x_rep, spacing1=x_spacing, angle1=0.0,
							  number2=y_rep + 1, spacing2=y_spacing, angle2=90.0)

	part_sketch.linearPattern(geomList=(g[6],), vertexList=(),
							  number1=x_rep + 1, spacing1=x_spacing, angle1=0.0,
							  number2=1, spacing2=y_spacing, angle2=90.0)

	part_sketch.linearPattern(geomList=(g[7],), vertexList=(),
							  number1=1, spacing1=x_spacing, angle1=0.0,
							  number2=y_rep + 1, spacing2=y_spacing, angle2=90.0)

	part = auxetic_model.Part(name=part_name, dimensionality=THREE_D, type=DEFORMABLE_BODY)
	part.BaseWire(sketch=part_sketch)

	# -----------------------------------------------------------------
	# Assembly creation

	import assembly

	model_assembly = auxetic_model.rootAssembly

	model_assembly.Instance(name=instance_name, part=part, dependent=OFF)

	model_assembly.LinearInstancePattern(instanceList=(instance_name,),
										 direction1=(1.0, 0.0, 0.0), direction2=(0.0, 0.0, 1.0),
										 number1=1, number2=z_rep, spacing1=1.0, spacing2=z_spacing)

	model_assembly.InstanceFromBooleanMerge(name=merged_part_name, instances=model_assembly.instances.values(),
											originalInstances=DELETE, domain=GEOMETRY)

	model_assembly.features.changeKey(fromName=merged_part_name + '-1', toName=merged_part_instance_name)

	# -----------------------------------------------------------------
	# Section creation and assignment

	import section
	import regionToolset

	auxetic_model.CircularProfile(name='circular_profile', r=diameter / 2)

	auxetic_model.BeamSection(name=section_name, integration=DURING_ANALYSIS, poissonRatio=0.3,
							  profile='circular_profile', material=material_name)

	merged_part = auxetic_model.parts[merged_part_name]

	merged_region = regionToolset.Region(edges=merged_part.edges)

	merged_part.SectionAssignment(region=merged_region, sectionName=section_name)

	merged_part.assignBeamSectionOrientation(region=merged_region, method=N1_COSINES, n1=(0.0, 0.0, -1.0))

	# -----------------------------------------------------------------
	# Mesh

	import mesh

	merged_part.seedPart(size=elem_size, deviationFactor=0.1, minSizeFactor=0.8)

	elem_type = mesh.ElemType(elemCode=B31, elemLibrary=STANDARD)

	merged_part.generateMesh()

	merged_part.setElementType(regions=(merged_part.edges,), elemTypes=(elem_type,))

	# -----------------------------------------------------------------
	# Step creation

	import step

	auxetic_model.ExplicitDynamicsStep(name=step_name, previous='Initial', nlgeom=ON, timePeriod=step_time, maxIncrement=0.00012)

	# -----------------------------------------------------------------
	# Sets definition

	all_nodes = merged_part.nodes

	fix_nodes = []

	left_nodes = []
	bottom_nodes = []
	right_nodes = []
	top_nodes = []

	x_coord_list, y_coord_list = [i * x_spacing for i in range(x_rep + 1)], \
								 [j * y_spacing for j in range(y_rep + 1)]

	x_coord_list.append(x_size + frame_length)
	y_coord_list.append(y_size + frame_length)

	rows, columns = len(y_coord_list), len(x_coord_list)

	model_constraints = [[{'ref_node': [], 'node_region': []} for _ in range(columns)] for _ in range(rows)]

	tol = 0.001 * diameter

	for n in all_nodes:
		xcoord = n.coordinates[0] if n.coordinates[0] < - tol or n.coordinates[0] > tol else 0.0
		ycoord = n.coordinates[1] if n.coordinates[1] < - tol or n.coordinates[1] > tol else 0.0
		zcoord = n.coordinates[2] if n.coordinates[2] < - tol or n.coordinates[2] > tol else 0.0

		if xcoord in x_coord_list and ycoord in y_coord_list:
			if xcoord != x_coord_list[-1] or ycoord != y_coord_list[-1]:
				i = x_coord_list.index(xcoord)
				j = y_coord_list.index(ycoord)
				if -0.01 < zcoord < 0.01:
					model_constraints[j][i]['ref_node'].append(n)
				else:
					model_constraints[j][i]['node_region'].append(n)

		if xcoord < g_offset and ycoord < g_offset:
			fix_nodes.append(n)
		if xmin_left < xcoord < xmax_left and ymax_bottom < ycoord < ymax_top - frame_length:
			left_nodes.append(n)
		if ymin_bottom < ycoord < ymax_bottom and xmax_left < xcoord < xmax_right - frame_length:
			bottom_nodes.append(n)
		if xmin_right < xcoord < xmax_right and ycoord < ymin_top:
			right_nodes.append(n)
		if ymin_top < ycoord < ymax_top and xcoord < xmin_right:
			top_nodes.append(n)

	import interaction

	for j, row in enumerate(model_constraints):
		for i, constraint in enumerate(row):
			if j != len(model_constraints) - 1 or i != len(row) - 1:
				name = 'constraint' + str(i) + str(j)

				mesh_ref_node = mesh.MeshNodeArray(constraint['ref_node'])
				set_ref_node_name = name + 'ref node'
				merged_part.Set(nodes=mesh_ref_node, name=set_ref_node_name)
				set_ref_node = auxetic_model.rootAssembly.instances[merged_part_instance_name].sets[set_ref_node_name]

				mesh_node_region = mesh.MeshNodeArray(constraint['node_region'])
				set_node_region_name = name + 'node_region'
				merged_part.Set(nodes=mesh_node_region, name=set_node_region_name)
				set_node_region = auxetic_model.rootAssembly.instances[merged_part_instance_name].sets[
					set_node_region_name]

				# auxetic_model.Coupling(name=name, surface=set_node_region, controlPoint=set_ref_node,
				#                        influenceRadius=WHOLE_SURFACE, couplingType=KINEMATIC)
				#                          ur1=OFF, ur2=OFF, ur3=OFF)

				auxetic_model.RigidBody(name=name, refPointRegion=set_ref_node, tieRegion=set_node_region)


	mesh_fix_nodes = mesh.MeshNodeArray(fix_nodes)
	merged_part.Set(nodes=mesh_fix_nodes, name=set_fix_nodes_name)

	mesh_left_nodes = mesh.MeshNodeArray(left_nodes)
	merged_part.Set(nodes=mesh_left_nodes, name=set_left_nodes_name)

	mesh_bottom_nodes = mesh.MeshNodeArray(bottom_nodes)
	merged_part.Set(nodes=mesh_bottom_nodes, name=set_bottom_nodes_name)

	mesh_right_nodes = mesh.MeshNodeArray(right_nodes)
	merged_part.Set(nodes=mesh_right_nodes, name=set_right_nodes_name)

	mesh_top_nodes = mesh.MeshNodeArray(top_nodes)
	merged_part.Set(nodes=mesh_top_nodes, name=set_top_nodes_name)

	set_fix_nodes = auxetic_model.rootAssembly.instances[merged_part_instance_name].sets[set_fix_nodes_name]
	set_left_nodes = auxetic_model.rootAssembly.instances[merged_part_instance_name].sets[set_left_nodes_name]
	set_bottom_nodes = auxetic_model.rootAssembly.instances[merged_part_instance_name].sets[set_bottom_nodes_name]
	set_right_nodes = auxetic_model.rootAssembly.instances[merged_part_instance_name].sets[set_right_nodes_name]
	set_top_nodes = auxetic_model.rootAssembly.instances[merged_part_instance_name].sets[set_top_nodes_name]

	# -----------------------------------------------------------------
	# Boundary conditions and loads

	vel_x = displacement_x / step_time
	vel_y = displacement_y / step_time

	# FIX NODES BC
	auxetic_model.EncastreBC(name=boundary_condition_fix_nodes_name, createStepName=step_name, region=set_fix_nodes)

	# BOTTOM BC
	auxetic_model.YsymmBC(name=boundary_condition_bottom_name, createStepName=step_name, region=set_bottom_nodes)

	# TOP BC
	auxetic_model.VelocityBC(name=boundary_condition_top_name, createStepName=step_name,
							 region=set_top_nodes, v1=0.0, v2=vel_y, v3=0.0)

	# LEFT BC
	auxetic_model.XsymmBC(name=boundary_condition_left_name, createStepName=step_name, region=set_left_nodes)

	# RIGHT BC
	auxetic_model.VelocityBC(name=boundary_condition_right_name, createStepName=step_name,
							 region=set_right_nodes, v1=vel_x, v2=0.0, v3=0.0)

	# -----------------------------------------------------------------
	# History Output

	auxetic_model.HistoryOutputRequest(name=left_rf_output_name, createStepName=step_name,
									   variables=('RF1',), timeInterval=timeInterv, region=set_left_nodes)
	auxetic_model.HistoryOutputRequest(name=left_u_output_name, createStepName=step_name,
									   variables=('U1',), timeInterval=timeInterv, region=set_left_nodes)
	auxetic_model.HistoryOutputRequest(name=bottom_rf_output_name, createStepName=step_name,
									   variables=('RF2',), timeInterval=timeInterv, region=set_bottom_nodes)
	auxetic_model.HistoryOutputRequest(name=bottom_u_output_name, createStepName=step_name,
									   variables=('U2',), timeInterval=timeInterv, region=set_bottom_nodes)
	auxetic_model.HistoryOutputRequest(name=right_rf_output_name, createStepName=step_name,
									   variables=('RF1',), timeInterval=timeInterv, region=set_right_nodes)
	auxetic_model.HistoryOutputRequest(name=right_u_output_name, createStepName=step_name,
									   variables=('U1',), timeInterval=timeInterv, region=set_right_nodes)
	auxetic_model.HistoryOutputRequest(name=top_rf_output_name, createStepName=step_name,
									   variables=('RF2',), timeInterval=timeInterv, region=set_top_nodes)
	auxetic_model.HistoryOutputRequest(name=top_u_output_name, createStepName=step_name,
									   variables=('U2',), timeInterval=timeInterv, region=set_top_nodes)

	# -----------------------------------------------------------------
	# Job creation

	mdb.Job(name=job_name, model=model_name, description='', type=ANALYSIS, atTime=None,
			waitMinutes=0, waitHours=0, queue=None, memory=90, memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True,
			explicitPrecision=DOUBLE, nodalOutputPrecision=SINGLE, parallelizationMethodExplicit=DOMAIN,
			numDomains=16, echoPrint=OFF, modelPrint=OFF, contactPrint=OFF, historyPrint=OFF,
			userSubroutine='', scratch='', multiprocessingMode=DEFAULT, numCpus=4)

	mdb.jobs[job_name].writeInput(consistencyChecking=OFF)

	# -----------------------------------------------------------------


def stri(a, b, diameter, x_rep, y_rep, z_rep, id):
	"""
				Creates an auxetic model with S_TRIANGULAR geometry design written to .inp file.

				Args:
					- a (float):
					- b (float):
					- diameter (float):
					- x_rep (int):
					- y_rep (int):
					- z_rep (int):
	"""

	# ------------------ GLOBAL VARIABLES ----------------------------

	# -----------------------
	# GENERAL VARIABLE NAMES:
	# -----------------------

	model_name = 'auxetic_model'
	part_name = 'auxetic cell'
	material_name = 'PCL'
	section_name = 'beam_section'
	instance_name = 'assembly_instance'
	merged_part_name = 'merged_part'
	merged_part_instance_name = 'merged_part_instance'
	step_name = 'loading_step'
	set_fix_nodes_name = 'fix_nodes'
	set_left_nodes_name = 'left_nodes'
	set_bottom_nodes_name = 'bottom_nodes'
	set_right_nodes_name = 'right_nodes'
	set_top_nodes_name = 'top_nodes'
	boundary_condition_fix_nodes_name = 'fix_nodes_bc'
	boundary_condition_bottom_name = 'bottom_bc'
	boundary_condition_top_name = 'top_bc'
	boundary_condition_left_name = 'left_bc'
	boundary_condition_right_name = 'right_bc'
	left_rf_output_name = 'left_RF_output'
	left_u_output_name = 'left_U_output'
	bottom_rf_output_name = 'bottom_RF_output'
	bottom_u_output_name = 'bottom_U_output'
	right_rf_output_name = 'right_RF_output'
	right_u_output_name = 'right_U_output'
	top_rf_output_name = 'top_RF_output'
	top_u_output_name = 'top_U_output'
	job_name = 'stri_' + str(id)

	# ------------------
	# AUXILIAR VARIABLES:
	# ------------------

	elem_size = 10 * diameter  # global size of elements

	g_offset = 0.01  # small margin to avoid rounding issues

	step_time = 20
	timeInterv = 0.1

	x_spacing = 4 * a
	y_spacing = 4 * a * sin(pi / 3)
	z_spacing = diameter

	x_size = x_spacing * x_rep
	y_size = y_spacing * y_rep

	frame_length = 10 * a

	displacement_x = 3 * x_rep * sqrt(a ** 2 + b ** 2)
	displacement_y = 3 * y_rep * sqrt(a ** 2 + b ** 2)

	# -----------------------
	# BOUNDARY SETS CONDITIONS:
	# -----------------------

	xmin_left = - x_spacing / 2 - g_offset
	xmax_left = - x_spacing / 2 + g_offset
	ymin_bottom = - g_offset
	ymax_bottom = + g_offset
	xmin_right = x_size - x_spacing + frame_length - g_offset
	xmax_right = x_size - x_spacing + frame_length + g_offset
	ymin_top = y_size + frame_length - g_offset
	ymax_top = y_size + frame_length + g_offset

	# ----------------------------------------------------------------
	# START MODEL GENERATION:
	# ----------------------------------------------------------------

	# This line is required to make the ABAQUS viewport display nothing

	session.viewports['Viewport: 1'].setValues(displayedObject=None)

	# Model creation
	# By default, ABAQUS creates a model named Model-1.

	auxetic_model = mdb.Model(name=model_name)

	auxetic_model.setValues(noPartsInputFile=OFF)

	# Material creation

	import material

	# Scaffold material is Polycaprolactone (PCL)

	cell_material = auxetic_model.Material(name=material_name)

	cell_material.Density(table=((1.145 * 10 ** -12,),))  # Density - Units: [10^15 kg/m^3]

	cell_material.Elastic(table=((0.1, 0.3),))  # Elastic props. (Young's modulus, Poisson's ratio)

	cell_material.Plastic(table=((0.012, 0.0), (0.0145, 0.25), (0.017, 0.5), (0.0195, 1),))

	# ----------------------------------------------------------------
	# Part creation

	import sketch
	import part

	# -----------------------
	# Basic Part (auxetic cell)

	part_sketch = auxetic_model.ConstrainedSketch(name='Part sketch', sheetSize=2000)

	part_sketch.Spline(points=((0.0, 0.0), (a, - b), (2 * a, 0.0)))
	part_sketch.Spline(points=((2 * a, 0.0), (3 * a, b), (4 * a, 0.0)))

	g = part_sketch.geometry

	part_sketch.copyRotate(centerPoint=(0.0, 0.0), angle=60.0, objectList=(g[2], g[3]))
	part_sketch.copyRotate(centerPoint=(4 * a, 0.0), angle=- 60.0, objectList=(g[2], g[3]))

	part_sketch.radialPattern(geomList=(g[2], g[3], g[4], g[5], g[6], g[7]), vertexList=(),
							  number=6, totalAngle=360.0, centerPoint=(x_spacing / 2, y_spacing))

	part_sketch.Line(point1=(x_size - x_spacing, 0.0), point2=(x_size - x_spacing + frame_length, 0.0))
	part_sketch.Line(point1=(x_size - x_spacing / 2, y_spacing),
					 point2=(x_size - x_spacing + frame_length, y_spacing))

	if y_rep % 2 != 0:

		part_sketch.Line(point1=(- 2 * a, y_size), point2=(- 2 * a, y_size + frame_length))

		part_sketch.linearPattern(geomList=(g[38], g[39]), vertexList=(),
								  number1=1, spacing1=x_spacing, angle1=0.0,
								  number2=y_rep / 2 + 1, spacing2=2 * y_spacing, angle2=90.0)

		part_sketch.linearPattern(geomList=(g[40],), vertexList=(),
								  number1=x_rep + 1, spacing1=x_spacing, angle1=0.0,
								  number2=1, spacing2=y_spacing, angle2=90.0)

		part_sketch.linearPattern(geomList=(g[4], g[5], g[6], g[7], g[8], g[9], g[10], g[11], g[12], g[13], g[16],
											g[17], g[30], g[31], g[32], g[33], g[34], g[35], g[36], g[37]),
								  vertexList=(),
								  number1=x_rep - 1, spacing1=x_spacing, angle1=0.0,
								  number2=2, spacing2=y_size - y_spacing, angle2=90.0)

	else:

		part_sketch.Line(point1=(0.0, y_size), point2=(0.0, y_size + frame_length))

		part_sketch.linearPattern(geomList=(g[38],), vertexList=(),
								  number1=1, spacing1=x_spacing, angle1=0.0,
								  number2=y_rep / 2 + 1, spacing2=2 * y_spacing, angle2=90.0)

		part_sketch.linearPattern(geomList=(g[39],), vertexList=(),
								  number1=1, spacing1=x_spacing, angle1=0.0,
								  number2=y_rep / 2, spacing2=2 * y_spacing, angle2=90.0)

		part_sketch.linearPattern(geomList=(g[40],), vertexList=(),
								  number1=x_rep, spacing1=x_spacing, angle1=0.0,
								  number2=1, spacing2=y_spacing, angle2=90.0)

	part_sketch.linearPattern(geomList=(g[2], g[3], g[4], g[5], g[6], g[7], g[8], g[9], g[10], g[11], g[12], g[13],
										g[14], g[15], g[16], g[17], g[18], g[19], g[20], g[21], g[22], g[23], g[24],
										g[25], g[26], g[27], g[28], g[29], g[30], g[31], g[32], g[33], g[34], g[35],
										g[36], g[37]), vertexList=(),
							  number1=x_rep - 1, spacing1=x_spacing, angle1=0.0,
							  number2=y_rep / 2, spacing2=2 * y_spacing, angle2=90.0)

	part = auxetic_model.Part(name=part_name, dimensionality=THREE_D, type=DEFORMABLE_BODY)
	part.BaseWire(sketch=part_sketch)

	# -----------------------------------------------------------------
	# Assembly creation

	import assembly

	model_assembly = auxetic_model.rootAssembly

	model_assembly.Instance(name=instance_name, part=part, dependent=OFF)

	model_assembly.LinearInstancePattern(instanceList=(instance_name,),
										 direction1=(1.0, 0.0, 0.0), direction2=(0.0, 0.0, 1.0),
										 number1=1, number2=z_rep, spacing1=1.0, spacing2=z_spacing)

	model_assembly.InstanceFromBooleanMerge(name=merged_part_name, instances=model_assembly.instances.values(),
											originalInstances=DELETE, domain=GEOMETRY)

	model_assembly.features.changeKey(fromName=merged_part_name + '-1', toName=merged_part_instance_name)

	# -----------------------------------------------------------------
	# Section creation and assignment

	import section
	import regionToolset

	auxetic_model.CircularProfile(name='circular_profile', r=diameter / 2)

	auxetic_model.BeamSection(name=section_name, integration=DURING_ANALYSIS, poissonRatio=0.3,
							  profile='circular_profile', material=material_name)

	merged_part = auxetic_model.parts[merged_part_name]

	merged_region = regionToolset.Region(edges=merged_part.edges)

	merged_part.SectionAssignment(region=merged_region, sectionName=section_name)

	merged_part.assignBeamSectionOrientation(region=merged_region, method=N1_COSINES, n1=(0.0, 0.0, -1.0))

	# -----------------------------------------------------------------
	# Mesh

	import mesh

	merged_part.seedPart(size=elem_size, deviationFactor=0.1, minSizeFactor=0.8)

	elem_type = mesh.ElemType(elemCode=B31, elemLibrary=STANDARD)

	merged_part.generateMesh()

	merged_part.setElementType(regions=(merged_part.edges,), elemTypes=(elem_type,))

	# -----------------------------------------------------------------
	# Step creation

	import step

	auxetic_model.ExplicitDynamicsStep(name=step_name, previous='Initial', nlgeom=ON, timePeriod=step_time, maxIncrement=0.00012)

	# -----------------------------------------------------------------
	# Sets definition

	all_nodes = merged_part.nodes

	fix_nodes = []

	left_nodes = []
	bottom_nodes = []
	right_nodes = []
	top_nodes = []

	x_coord_list_short, y_coord_list_short = [round(i * x_spacing, 1) for i in range(x_rep)],\
											 [round(j * 2 * y_spacing, 1) for j in range(int(y_rep / 2) + 1)]

	x_coord_list_long, y_coord_list_long = [round((i - 0.5) * x_spacing, 1) for i in range(x_rep + 1)],\
										   [round((2 * j + 1) * y_spacing, 1) for j in range(int((y_rep + 1) / 2))]

	x_coord_list_short.append(round(x_size - x_spacing + frame_length, 1))
	x_coord_list_long.append(round(x_size - x_spacing + frame_length, 1))

	if y_rep % 2 == 0:
		y_coord_list_short.append(round(y_size + frame_length, 1))
	else:
		y_coord_list_long.append(round(y_size + frame_length, 1))

	rows_short, columns_short = len(y_coord_list_short), len(x_coord_list_short)
	rows_long, columns_long = len(y_coord_list_long), len(x_coord_list_long)

	model_constraints_short = [[{'ref_node': [], 'node_region': []} for _ in range(columns_short)] for _ in
							   range(rows_short)]
	model_constraints_long = [[{'ref_node': [], 'node_region': []} for _ in range(columns_long)] for _ in
							  range(rows_long)]

	tol = 0.01

	for n in all_nodes:
		xcoord = n.coordinates[0] if n.coordinates[0] < - tol or n.coordinates[0] > tol else 0.0
		ycoord = n.coordinates[1] if n.coordinates[1] < - tol or n.coordinates[1] > tol else 0.0
		zcoord = n.coordinates[2] if n.coordinates[2] < - tol or n.coordinates[2] > tol else 0.0

		if y_rep % 2 != 0:
			if round(xcoord, 1) in x_coord_list_short and round(ycoord, 1) in y_coord_list_short:
				i = x_coord_list_short.index(round(xcoord, 1))
				j = y_coord_list_short.index(round(ycoord, 1))
				if -0.01 < zcoord < 0.01:
					model_constraints_short[j][i]['ref_node'].append(n)
				else:
					model_constraints_short[j][i]['node_region'].append(n)

			if round(xcoord, 1) in x_coord_list_long and round(ycoord, 1) in y_coord_list_long:
				if round(xcoord, 1) != x_coord_list_long[-1] or round(ycoord, 1) != y_coord_list_long[-1]:
					i = x_coord_list_long.index(round(xcoord, 1))
					j = y_coord_list_long.index(round(ycoord, 1))
					if -0.01 < zcoord < 0.01:
						model_constraints_long[j][i]['ref_node'].append(n)
					else:
						model_constraints_long[j][i]['node_region'].append(n)

		if y_rep % 2 == 0:
			if round(xcoord, 1) in x_coord_list_short and round(ycoord, 1) in y_coord_list_short:
				if round(xcoord, 1) != x_coord_list_long[-1] or round(ycoord, 1) != y_coord_list_long[-1]:
					i = x_coord_list_short.index(round(xcoord, 1))
					j = y_coord_list_short.index(round(ycoord, 1))
					if -0.01 < zcoord < 0.01:
						model_constraints_short[j][i]['ref_node'].append(n)
					else:
						model_constraints_short[j][i]['node_region'].append(n)

			if round(xcoord, 1) in x_coord_list_long and round(ycoord, 1) in y_coord_list_long:
				i = x_coord_list_long.index(round(xcoord, 1))
				j = y_coord_list_long.index(round(ycoord, 1))
				if -0.01 < zcoord < 0.01:
					model_constraints_long[j][i]['ref_node'].append(n)
				else:
					model_constraints_long[j][i]['node_region'].append(n)

		if xcoord < g_offset and ycoord < g_offset:
			fix_nodes.append(n)
		if xmin_left < xcoord < xmax_left and ymax_bottom < ycoord < ymax_top - frame_length:
			left_nodes.append(n)
		if ymin_bottom < ycoord < ymax_bottom and xmax_left < xcoord < xmax_right - frame_length:
			for i in range(1, x_rep):
				x_bottom = x_spacing * i
				if abs(x_bottom - xcoord) < g_offset:
					bottom_nodes.append(n)
		if xmin_right < xcoord < xmax_right and ycoord < ymin_top:
			right_nodes.append(n)
		if ymin_top < ycoord < ymax_top and xcoord < xmin_right:
			top_nodes.append(n)

	import interaction

	if y_rep % 2 != 0:

		for j, row in enumerate(model_constraints_short):
			for i, constraint in enumerate(row):
				# if j != len(model_constraints_short) - 1 or i != len(row) - 1:
				name = 'constraint_short' + str(i) + str(j)

				mesh_ref_node = mesh.MeshNodeArray(constraint['ref_node'])
				set_ref_node_name = name + 'ref node'
				merged_part.Set(nodes=mesh_ref_node, name=set_ref_node_name)
				set_ref_node = auxetic_model.rootAssembly.instances[merged_part_instance_name].sets[set_ref_node_name]

				mesh_node_region = mesh.MeshNodeArray(constraint['node_region'])
				set_node_region_name = name + 'node_region'
				merged_part.Set(nodes=mesh_node_region, name=set_node_region_name)
				set_node_region = auxetic_model.rootAssembly.instances[merged_part_instance_name].sets[
					set_node_region_name]

				auxetic_model.RigidBody(name=name, refPointRegion=set_ref_node, tieRegion=set_node_region)

		for j, row in enumerate(model_constraints_long):
			for i, constraint in enumerate(row):
				if j != len(model_constraints_long) - 1 or i != len(row) - 1:
					name = 'constraint_long' + str(i) + str(j)

					mesh_ref_node = mesh.MeshNodeArray(constraint['ref_node'])
					set_ref_node_name = name + 'ref node'
					merged_part.Set(nodes=mesh_ref_node, name=set_ref_node_name)
					set_ref_node = auxetic_model.rootAssembly.instances[merged_part_instance_name].sets[set_ref_node_name]

					mesh_node_region = mesh.MeshNodeArray(constraint['node_region'])
					set_node_region_name = name + 'node_region'
					merged_part.Set(nodes=mesh_node_region, name=set_node_region_name)
					set_node_region = auxetic_model.rootAssembly.instances[merged_part_instance_name].sets[
						set_node_region_name]

					auxetic_model.RigidBody(name=name, refPointRegion=set_ref_node, tieRegion=set_node_region)

	if y_rep % 2 == 0:

		for j, row in enumerate(model_constraints_short):
			for i, constraint in enumerate(row):
				if j != len(model_constraints_short) - 1 or i != len(row) - 1:
					name = 'constraint_short' + str(i) + str(j)

					mesh_ref_node = mesh.MeshNodeArray(constraint['ref_node'])
					set_ref_node_name = name + 'ref node'
					merged_part.Set(nodes=mesh_ref_node, name=set_ref_node_name)
					set_ref_node = auxetic_model.rootAssembly.instances[merged_part_instance_name].sets[set_ref_node_name]

					mesh_node_region = mesh.MeshNodeArray(constraint['node_region'])
					set_node_region_name = name + 'node_region'
					merged_part.Set(nodes=mesh_node_region, name=set_node_region_name)
					set_node_region = auxetic_model.rootAssembly.instances[merged_part_instance_name].sets[
						set_node_region_name]

					auxetic_model.RigidBody(name=name, refPointRegion=set_ref_node, tieRegion=set_node_region)

		for j, row in enumerate(model_constraints_long):
			for i, constraint in enumerate(row):
				# if j != len(model_constraints_long) - 1 or i != len(row) - 1:
				name = 'constraint_long' + str(i) + str(j)

				mesh_ref_node = mesh.MeshNodeArray(constraint['ref_node'])
				set_ref_node_name = name + 'ref node'
				merged_part.Set(nodes=mesh_ref_node, name=set_ref_node_name)
				set_ref_node = auxetic_model.rootAssembly.instances[merged_part_instance_name].sets[
					set_ref_node_name]

				mesh_node_region = mesh.MeshNodeArray(constraint['node_region'])
				set_node_region_name = name + 'node_region'
				merged_part.Set(nodes=mesh_node_region, name=set_node_region_name)
				set_node_region = auxetic_model.rootAssembly.instances[merged_part_instance_name].sets[
					set_node_region_name]

				auxetic_model.RigidBody(name=name, refPointRegion=set_ref_node, tieRegion=set_node_region)

	mesh_fix_nodes = mesh.MeshNodeArray(fix_nodes)
	merged_part.Set(nodes=mesh_fix_nodes, name=set_fix_nodes_name)

	mesh_left_nodes = mesh.MeshNodeArray(left_nodes)
	merged_part.Set(nodes=mesh_left_nodes, name=set_left_nodes_name)

	mesh_bottom_nodes = mesh.MeshNodeArray(bottom_nodes)
	merged_part.Set(nodes=mesh_bottom_nodes, name=set_bottom_nodes_name)

	mesh_right_nodes = mesh.MeshNodeArray(right_nodes)
	merged_part.Set(nodes=mesh_right_nodes, name=set_right_nodes_name)

	mesh_top_nodes = mesh.MeshNodeArray(top_nodes)
	merged_part.Set(nodes=mesh_top_nodes, name=set_top_nodes_name)

	set_fix_nodes = auxetic_model.rootAssembly.instances[merged_part_instance_name].sets[set_fix_nodes_name]
	set_left_nodes = auxetic_model.rootAssembly.instances[merged_part_instance_name].sets[set_left_nodes_name]
	set_bottom_nodes = auxetic_model.rootAssembly.instances[merged_part_instance_name].sets[set_bottom_nodes_name]
	set_right_nodes = auxetic_model.rootAssembly.instances[merged_part_instance_name].sets[set_right_nodes_name]
	set_top_nodes = auxetic_model.rootAssembly.instances[merged_part_instance_name].sets[set_top_nodes_name]

	# -----------------------------------------------------------------
	# Boundary conditions and loads

	vel_x = displacement_x / step_time
	vel_y = displacement_y / step_time

	# FIX NODES BC
	auxetic_model.EncastreBC(name=boundary_condition_fix_nodes_name, createStepName=step_name, region=set_fix_nodes)

	# BOTTOM BC
	auxetic_model.YsymmBC(name=boundary_condition_bottom_name, createStepName=step_name, region=set_bottom_nodes)

	# TOP BC
	auxetic_model.VelocityBC(name=boundary_condition_top_name, createStepName=step_name,
							 region=set_top_nodes, v1=0.0, v2=vel_y, v3=0.0)

	# LEFT BC
	auxetic_model.XsymmBC(name=boundary_condition_left_name, createStepName=step_name, region=set_left_nodes)

	# RIGHT BC
	auxetic_model.VelocityBC(name=boundary_condition_right_name, createStepName=step_name,
							 region=set_right_nodes, v1=vel_x, v2=0.0, v3=0.0)

	# -----------------------------------------------------------------
	# History Output

	auxetic_model.HistoryOutputRequest(name=left_rf_output_name, createStepName=step_name,
									   variables=('RF1',), timeInterval=timeInterv, region=set_left_nodes)
	auxetic_model.HistoryOutputRequest(name=left_u_output_name, createStepName=step_name,
									   variables=('U1',), timeInterval=timeInterv, region=set_left_nodes)
	auxetic_model.HistoryOutputRequest(name=bottom_rf_output_name, createStepName=step_name,
									   variables=('RF2',), timeInterval=timeInterv, region=set_bottom_nodes)
	auxetic_model.HistoryOutputRequest(name=bottom_u_output_name, createStepName=step_name,
									   variables=('U2',), timeInterval=timeInterv, region=set_bottom_nodes)
	auxetic_model.HistoryOutputRequest(name=right_rf_output_name, createStepName=step_name,
									   variables=('RF1',), timeInterval=timeInterv, region=set_right_nodes)
	auxetic_model.HistoryOutputRequest(name=right_u_output_name, createStepName=step_name,
									   variables=('U1',), timeInterval=timeInterv, region=set_right_nodes)
	auxetic_model.HistoryOutputRequest(name=top_rf_output_name, createStepName=step_name,
									   variables=('RF2',), timeInterval=timeInterv, region=set_top_nodes)
	auxetic_model.HistoryOutputRequest(name=top_u_output_name, createStepName=step_name,
									   variables=('U2',), timeInterval=timeInterv, region=set_top_nodes)

	# -----------------------------------------------------------------
	# Job creation

	mdb.Job(name=job_name, model=model_name, description='', type=ANALYSIS, atTime=None,
			waitMinutes=0, waitHours=0, queue=None, memory=90, memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True,
			explicitPrecision=DOUBLE, nodalOutputPrecision=SINGLE, parallelizationMethodExplicit=DOMAIN,
			numDomains=16, echoPrint=OFF, modelPrint=OFF, contactPrint=OFF, historyPrint=OFF,
			userSubroutine='', scratch='', multiprocessingMode=DEFAULT, numCpus=4)

	mdb.jobs[job_name].writeInput(consistencyChecking=OFF)

	# -----------------------------------------------------------------


def hcell(a, b, diameter, x_rep, y_rep, z_rep, id):
	"""
		Creates an auxetic model with H_CELL geometry design written to .inp file.

				Args:
					- a (float):
					- b (float):
					- diameter (float):
					- x_rep (int):
					- y_rep (int):
					- z_rep (int):
	"""

	# ------------------ VARIABLES ----------------------------

	# -----------------------
	# VARIABLE NAMES:
	# -----------------------

	model_name = 'auxetic_model'
	part_name = 'basic part'
	material_name = 'PCL'
	section_name = 'beam_section'
	instance_name = 'basic_instance'
	merged_part_name = 'merged_part'
	merged_part_instance_name = 'merged_part_instance'
	step_name = 'loading_step'
	set_fix_nodes_name = 'fix_nodes'
	set_left_nodes_name = 'left_nodes'
	set_bottom_nodes_name = 'bottom_nodes'
	set_right_nodes_name = 'right_nodes'
	set_top_nodes_name = 'top_nodes'
	boundary_condition_fix_nodes_name = 'fix_nodes_bc'
	boundary_condition_bottom_name = 'bottom_bc'
	boundary_condition_top_name = 'top_bc'
	boundary_condition_left_name = 'left_bc'
	boundary_condition_right_name = 'right_bc'
	left_rf_output_name = 'left_RF_output'
	left_u_output_name = 'left_U_output'
	bottom_rf_output_name = 'bottom_RF_output'
	bottom_u_output_name = 'bottom_U_output'
	right_rf_output_name = 'right_RF_output'
	right_u_output_name = 'right_U_output'
	top_rf_output_name = 'top_RF_output'
	top_u_output_name = 'top_U_output'
	job_name = 'hcell_' + str(id)

	# ------------------
	# AUXILIAR VARIABLES:
	# ------------------

	elem_size = 10 * diameter  # global size of elements

	g_offset = 0.1  # small margin to avoid rounding issues

	step_time = 20
	timeInterv = 0.1

	x_spacing = 4 * a + 2 * b
	y_spacing = 4 * a + 2 * b
	z_spacing = diameter

	x_size = 2 * x_rep * (2 * a + b)
	y_size = 4 * a * y_rep + b * (2 * y_rep - 1)

	displacement_x = x_rep * 4 * a
	displacement_y = y_rep * 4 * a

	# -----------------------
	# BOUNDARY SETS CONDITIONS:
	# -----------------------

	xmin_left = - b - g_offset
	xmax_left = - b + g_offset
	ymin_bottom = - b - g_offset
	ymax_bottom = - b + g_offset
	xmin_right = x_size - g_offset
	xmax_right = x_size + g_offset
	ymin_top = y_size + b - g_offset
	ymax_top = y_size + b + g_offset

	# ----------------------------------------------------------------
	# START MODEL GENERATION:
	# ----------------------------------------------------------------

	# This line is required to make the ABAQUS viewport display nothing

	session.viewports['Viewport: 1'].setValues(displayedObject=None)

	# Model creation
	# By default, ABAQUS creates a model named Model-1.

	auxetic_model = mdb.Model(name=model_name)

	auxetic_model.setValues(noPartsInputFile=OFF)

	# Material creation

	import material

	# Scaffold material is Polycaprolactone (PCL)

	cell_material = auxetic_model.Material(name=material_name)

	cell_material.Density(table=((1.145 * 10 ** -12,),))  # Density - Units: [10^15 kg/m^3]

	cell_material.Elastic(table=((0.1, 0.3),))  # Elastic props. (Young's modulus, Poisson's ratio)

	cell_material.Plastic(table=((0.012, 0.0), (0.0145, 0.25), (0.017, 0.5), (0.0195, 1),))

	# ----------------------------------------------------------------
	# Part creation

	import sketch
	import part

	# -----------------------
	# Basic Part: hcell

	part_sketch = auxetic_model.ConstrainedSketch(name='Part sketch', sheetSize=2000)

	part_sketch.Spline(points=((0, 0), (0.2 * a, 0.8 * a), (a, a), (a + 0.8 * a, a + 0.2 * a), (2 * a, 2 * a)))
	part_sketch.Spline(points=((0, 2 * a), (0.8 * a, 2 * a - 0.2 * a), (a, a), (a + 0.2 * a, 0.2 * a), (2 * a, 0)))

	part_sketch.Spline(points=((2 * a, 2 * a + b),
							   (2 * a - 0.2 * a, 2 * a + b + 0.8 * a),
							   (a, 2 * a + b + a),
							   (0.2 * a, 2 * a + b + a + 0.2 * a),
							   (0, 4 * a + b)))
	part_sketch.Spline(points=((0, 2 * a + b),
							   (0.8 * a, 2 * a + b + 0.2 * a),
							   (a, 2 * a + b + a),
							   (a + 0.2 * a, 2 * a + b + a + 0.8 * a),
							   (2 * a, 4 * a + b)))

	part_sketch.Spline(points=((2 * a + b, 0),
							   (2 * a + b + 0.8 * a, 0.2 * a),
							   (2 * a + b + a, a),
							   (2 * a + b + a + 0.2 * a, a + 0.8 * a),
							   (4 * a + b, 2 * a)))
	part_sketch.Spline(points=((4 * a + b, 0),
							   (4 * a + b - 0.2 * a, 0.8 * a),
							   (2 * a + b + a, a),
							   (2 * a + b + 0.2 * a, a + 0.2 * a),
							   (2 * a + b, 2 * a)))

	part_sketch.Spline(points=((2 * a + b, 4 * a + b),
							   (2 * a + b + 0.8 * a, 4 * a + b - 0.2 * a),
							   (3 * a + b, 3 * a + b),
							   (3 * a + b + 0.2 * a, 3 * a + b - 0.8 * a),
							   (4 * a + b, 2 * a + b)))
	part_sketch.Spline(points=((2 * a + b, 2 * a + b),
							   (2 * a + b + 0.2 * a, 2 * a + b + 0.8 * a),
							   (3 * a + b, 3 * a + b),
							   (3 * a + b + 0.8 * a, 3 * a + b + 0.2 * a),
							   (4 * a + b, 4 * a + b)))

	part_sketch.Line(point1=(- b, 2 * a), point2=(0, 2 * a))
	part_sketch.Line(point1=(- b, 2 * a + b), point2=(0, 2 * a + b))

	part_sketch.Line(point1=(2 * a, 0), point2=(2 * a + b, 0))
	part_sketch.Line(point1=(2 * a, 4 * a + b), point2=(2 * a + b, 4 * a + b))

	part_sketch.Line(point1=(2 * a, 2 * a), point2=(2 * a, 2 * a + b))
	part_sketch.Line(point1=(2 * a + b, 2 * a), point2=(2 * a + b, 2 * a + b))

	part_sketch.Line(point1=(0, 4 * a + b), point2=(0, 4 * a + 2 * b))
	part_sketch.Line(point1=(4 * a + b, 4 * a + b), point2=(4 * a + b, 4 * a + 2 * b))

	part_sketch.Line(point1=(0, 0), point2=(0, - b))
	part_sketch.Line(point1=(4 * a + b, 0), point2=(4 * a + b, - b))

	g = part_sketch.geometry

	part_sketch.linearPattern(geomList=(g[2], g[3], g[4], g[5], g[6], g[7], g[8], g[9], g[12], g[13], g[14], g[15]),
							  vertexList=(),
							  number1=x_rep, spacing1=x_spacing, angle1=0.0,
							  number2=y_rep, spacing2=y_spacing, angle2=90.0)

	part_sketch.linearPattern(geomList=(g[10], g[11]), vertexList=(),
							  number1=x_rep + 1, spacing1=x_spacing, angle1=0.0,
							  number2=y_rep, spacing2=y_spacing, angle2=90.0)

	part_sketch.linearPattern(geomList=(g[16], g[17]), vertexList=(),
							  number1=x_rep, spacing1=x_spacing, angle1=0.0,
							  number2=y_rep - 1, spacing2=y_spacing, angle2=90.0)

	part_sketch.linearPattern(geomList=(g[18], g[19]), vertexList=(),
							  number1=x_rep, spacing1=x_spacing, angle1=0.0,
							  number2=2, spacing2=y_size + b, angle2=90.0)

	part = auxetic_model.Part(name=part_name, dimensionality=THREE_D, type=DEFORMABLE_BODY)
	part.BaseWire(sketch=part_sketch)

	# -----------------------------------------------------------------
	# Assembly creation

	import assembly

	model_assembly = auxetic_model.rootAssembly

	model_assembly.Instance(name=instance_name, part=part, dependent=OFF)

	model_assembly.LinearInstancePattern(instanceList=(instance_name,),
										 direction1=(1.0, 0.0, 0.0), direction2=(0.0, 0.0, 1.0),
										 number1=1, number2=z_rep, spacing1=1.0, spacing2=z_spacing)

	model_assembly.InstanceFromBooleanMerge(name=merged_part_name, instances=model_assembly.instances.values(),
											originalInstances=DELETE, domain=GEOMETRY)

	model_assembly.features.changeKey(fromName=merged_part_name + '-1', toName=merged_part_instance_name)

	# -----------------------------------------------------------------
	# Section creation and assignment

	import section
	import regionToolset

	auxetic_model.CircularProfile(name='circular_profile', r=diameter / 2)

	auxetic_model.BeamSection(name=section_name, integration=DURING_ANALYSIS, poissonRatio=0.3,
							  profile='circular_profile', material=material_name)

	merged_part = auxetic_model.parts[merged_part_name]

	merged_region = regionToolset.Region(edges=merged_part.edges)

	merged_part.SectionAssignment(region=merged_region, sectionName=section_name)

	merged_part.assignBeamSectionOrientation(region=merged_region, method=N1_COSINES, n1=(0.0, 0.0, -1.0))

	# -----------------------------------------------------------------
	# Mesh

	import mesh

	merged_part.seedPart(size=elem_size, deviationFactor=0.1, minSizeFactor=0.8)

	elem_type = mesh.ElemType(elemCode=B31, elemLibrary=STANDARD)

	merged_part.generateMesh()

	merged_part.setElementType(regions=(merged_part.edges,), elemTypes=(elem_type,))

	# -----------------------------------------------------------------
	# Step creation

	import step

	auxetic_model.ExplicitDynamicsStep(name=step_name, previous='Initial', nlgeom=ON, timePeriod=step_time, maxIncrement=0.00012)

	# -----------------------------------------------------------------
	# Sets definition

	all_nodes = merged_part.nodes

	fix_nodes = []

	left_nodes = []
	bottom_nodes = []
	right_nodes = []
	top_nodes = []

	for n in all_nodes:
		xcoord = n.coordinates[0]
		ycoord = n.coordinates[1]
		if xcoord < g_offset and ymin_bottom < ycoord < ymax_bottom:
			fix_nodes.append(n)
		if xmin_left < xcoord < xmax_left and ymax_bottom < ycoord < ymax_top:
			left_nodes.append(n)
		if ymin_bottom < ycoord < ymax_bottom and g_offset < xcoord < xmax_right:
			bottom_nodes.append(n)
		if xmin_right < xcoord < xmax_right and ycoord < ymin_top:
			right_nodes.append(n)
		if ymin_top < ycoord < ymax_top and xcoord < xmin_right:
			top_nodes.append(n)

	mesh_fix_nodes = mesh.MeshNodeArray(fix_nodes)
	merged_part.Set(nodes=mesh_fix_nodes, name=set_fix_nodes_name)

	mesh_left_nodes = mesh.MeshNodeArray(left_nodes)
	merged_part.Set(nodes=mesh_left_nodes, name=set_left_nodes_name)

	mesh_bottom_nodes = mesh.MeshNodeArray(bottom_nodes)
	merged_part.Set(nodes=mesh_bottom_nodes, name=set_bottom_nodes_name)

	mesh_right_nodes = mesh.MeshNodeArray(right_nodes)
	merged_part.Set(nodes=mesh_right_nodes, name=set_right_nodes_name)

	mesh_top_nodes = mesh.MeshNodeArray(top_nodes)
	merged_part.Set(nodes=mesh_top_nodes, name=set_top_nodes_name)

	set_fix_nodes = auxetic_model.rootAssembly.instances[merged_part_instance_name].sets[set_fix_nodes_name]
	set_left_nodes = auxetic_model.rootAssembly.instances[merged_part_instance_name].sets[set_left_nodes_name]
	set_bottom_nodes = auxetic_model.rootAssembly.instances[merged_part_instance_name].sets[set_bottom_nodes_name]
	set_right_nodes = auxetic_model.rootAssembly.instances[merged_part_instance_name].sets[set_right_nodes_name]
	set_top_nodes = auxetic_model.rootAssembly.instances[merged_part_instance_name].sets[set_top_nodes_name]

	# -----------------------------------------------------------------
	# Boundary conditions and loads

	vel_x = displacement_x / step_time
	vel_y = displacement_y / step_time

	# FIX NODES BC
	auxetic_model.EncastreBC(name=boundary_condition_fix_nodes_name, createStepName=step_name, region=set_fix_nodes)

	# BOTTOM BC
	auxetic_model.YsymmBC(name=boundary_condition_bottom_name, createStepName=step_name, region=set_bottom_nodes)

	# TOP BC
	auxetic_model.VelocityBC(name=boundary_condition_top_name, createStepName=step_name,
							 region=set_top_nodes, v1=0.0, v2=vel_y, v3=0.0)

	# LEFT BC
	auxetic_model.XsymmBC(name=boundary_condition_left_name, createStepName=step_name, region=set_left_nodes)

	# RIGHT BC
	auxetic_model.VelocityBC(name=boundary_condition_right_name, createStepName=step_name,
							 region=set_right_nodes, v1=vel_x, v2=0.0, v3=0.0)

	# -----------------------------------------------------------------
	# History Output

	auxetic_model.HistoryOutputRequest(name=left_rf_output_name, createStepName=step_name,
									   variables=('RF1',), timeInterval=timeInterv, region=set_left_nodes)
	auxetic_model.HistoryOutputRequest(name=left_u_output_name, createStepName=step_name,
									   variables=('U1',), timeInterval=timeInterv, region=set_left_nodes)
	auxetic_model.HistoryOutputRequest(name=bottom_rf_output_name, createStepName=step_name,
									   variables=('RF2',), timeInterval=timeInterv, region=set_bottom_nodes)
	auxetic_model.HistoryOutputRequest(name=bottom_u_output_name, createStepName=step_name,
									   variables=('U2',), timeInterval=timeInterv, region=set_bottom_nodes)
	auxetic_model.HistoryOutputRequest(name=right_rf_output_name, createStepName=step_name,
									   variables=('RF1',), timeInterval=timeInterv, region=set_right_nodes)
	auxetic_model.HistoryOutputRequest(name=right_u_output_name, createStepName=step_name,
									   variables=('U1',), timeInterval=timeInterv, region=set_right_nodes)
	auxetic_model.HistoryOutputRequest(name=top_rf_output_name, createStepName=step_name,
									   variables=('RF2',), timeInterval=timeInterv, region=set_top_nodes)
	auxetic_model.HistoryOutputRequest(name=top_u_output_name, createStepName=step_name,
									   variables=('U2',), timeInterval=timeInterv, region=set_top_nodes)

	# -----------------------------------------------------------------
	# Job creation

	mdb.Job(name=job_name, model=model_name, description='', type=ANALYSIS, atTime=None,
			waitMinutes=0, waitHours=0, queue=None, memory=90, memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True,
			explicitPrecision=DOUBLE, nodalOutputPrecision=SINGLE, parallelizationMethodExplicit=DOMAIN,
			numDomains=16, echoPrint=OFF, modelPrint=OFF, contactPrint=OFF, historyPrint=OFF,
			userSubroutine='', scratch='', multiprocessingMode=DEFAULT, numCpus=4)

	mdb.jobs[job_name].writeInput(consistencyChecking=OFF)

	# -----------------------------------------------------------------
