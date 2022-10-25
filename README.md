# File Converter

## Run File Converter
* python converter.py 0 <- prints supported formats
* python converter.py 1 [path to input file] [file format]
* python converter.py 2 [path to input file] [file format] [path to output directory] [options string]

## Add Importer / Exporter

### Importer / Exporter Requirements
* implement [import_interface](interfaces/import_interface.py) / [export_interface](interfaces/export_interface.py)
* name the (main) class **Import** / **Export**
* name the file *XYZ*_import.py / *XYZ*_export.py
* place the file in the [importer package](importer) / [exporter package](exporter)

### Expected data dictionary format
* polygon: Amount of vertices per face (has to be consistent for the mesh)
* frames: Amount of frames
* vertices: List of float values where all 3 consecutive floats form a vector3
* connectivity: List of vertex IDs
* vertex-precision: Precision ID for the vertex positions (optional, default is FP32)
* blocks: List of dictionaries (optional)
  * name: Name of the data block
  * precision: Precision ID for the data block values
  * values: List of values with a type corresponding to the precision ID

## Communication with webserver

* Realised with console output
* Result is given as options string
  * Does not contain information values
  * Each line is one parameter

### Keywords
| Keyword | Position            | Usage                                | Additional information                                                             |
|---------|---------------------|--------------------------------------|------------------------------------------------------------------------------------|
| \#      | Start of parameter  | Following parameter is information   | No other keyword will be parsed after a # besides the semicolon                    |
| _       | Start of parameter  | Following parameter is a child entry | Must be same value type as parent. All child entries can be changed simultaneously |
| :       | Middle of parameter | Name / Value separator               |                                                                                    |
| bool    | After :             | Boolean value requested              |                                                                                    |
| int     | After :             | Int value requested                  |                                                                                    |
| float   | After :             | Float value requested                |                                                                                    |

### Examples
An example for a comment:
```
#This is a comment
```

An example for a bool input:
```
A bool input:bool
```

An example for a grouped bool input:  
```
The parent input:bool
_A child input:bool
_Another child input:bool
```