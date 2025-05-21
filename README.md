# MEW-FEM AuxeticDesigner

**MEW-FEM AuxeticDesigner** is a computational tool for the design and export of auxetic scaffolds intended for soft tissue engineering applications. The tool enables both **Melt Electrowriting (MEW) G-code** and **Finite Element Model (FEM, ABAQUS .inp format)** file generation, with support for:

- **Manual mode**: Direct user-defined auxetic geometries.
- **Predictive mode**: Inverse design based on a target effective stiffness.

---

## 🚀 Features

- ✏️ **Manual design mode**  
  Use this mode to define scaffold geometry directly by specifying values for each design parameter. There are two ways to generate scaffolds in "Manual Mode":
  - "Match by position": Each parameter must have the same number of values. The tool will generate individual scaffolds matching values across parameters by their index.
      - Generates individual scaffold configurations defined row by row.
  - "Generate all combinations": Provide at least one value per parameter. The tool will generate all possible combinations between the given values.
      - Useful for generating an entire design space in a single run.

- 🎯 **Predictive design mode**  
  Specify a target effective stiffness value, and the tool will return the best-fit geometry configuration for each auxetic design based on trained statistical models.

- 🧵 **MEW-compatible output**  
  Exports G-code files ready for melt electrowriting of fiber-based scaffolds.

- 🧩 **FEM-ready ABAQUS input files**  
  Automatically exports `.inp` files suitable for mechanical simulation and analysis.

- 🧬 **Auxetic scaffold types supported**
  - H-cell (HCELL)
  - S-regular (SREG)
  - S-inverted (SINV)
  - S-triangular (STRI)

---
