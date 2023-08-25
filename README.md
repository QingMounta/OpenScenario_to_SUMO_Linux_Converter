# OpenScenario2SUMO_viaEsmini
Automatic traffic scenario conversion interface between OpenSCENARIO and the traffic simulator SUMO


# Table of contents

- [Prerequisites](#prerequisites)
- [Installation of Esmini](#installation-of-esmini)
- [Build Esmini](#build-esmini)
- [Main Usage](#main-usage)
- [Unity Connection](#unity-connection)
- [License](#license)
- [Converge to csv](#converge-to-csv)


# Prerequisites
[(Back to top)](#table-of-contents)

Before getting started, ensure you have the following prerequisites:


- Operating System: Windows
- Python: The project requires Python [tested versions: '3.10', '3.11']. Make sure you have Python installed.
- SUMO: The project utilizes SUMO [tested version: 17.0, 18.0]. Install SUMO by following the official instructions
  [link to SUMO installation guide](https://sumo.dlr.de/docs/Installing/index.html).
- Required Python packages:

The usage of the Anaconda Python distribution is strongly recommended.

# Installation
[(Back to top)](#table-of-contents)

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/your-repo.git
   ```


2. Installation of Esmini

   1. Download latest release from [here](https://github.com/esmini/esmini/releases/latest)


   2. Pick the package: esmini-(version) for Windows.   
   On Windows, make sure the zip file is not blocked: Right click, click Properties, at bottom right check Unblock. For more info, see Blocked by Windows Defender SmartScreen.  
   To install the package, just unzip it anywhere. A single subfolder named esmini-(version) is created. This is the root folder for esmini. No files are stored outside this folder structure and no system files or registry is modified in any way.  

3. Move the SUMO_test into the folder esmini-(version)



# Build Esmini
[(Back to top)](#table-of-contents)


Make sure you have a C++ compiler and CMake installed.  

On Windows Visual Studio is recommended (Community/free version is good enough for building esmini). Make sure to check the "C/C++" and "CMake" packages for installation, no more is needed.  

Now we’re ready to build esmini. From esmini-(version) root folder:  

```sh
mkdir build
cd build
cmake ..
cmake --build . --config Release --target install
```
The build process automatically downloads 3rd party library binaries and the complete 3D model package.  

After a successful build, the binaries will be copied into esmini-(version)/bin folder. Try from the command line:  
```sh
./bin/esmini --window 60 60 800 400 --osc ./resources/xosc/cut-in.xosc
```



# Main Usage
[(Back to top)](#table-of-contents)

1. Go to folder SUMOtest folder.
```
cd SUMOtest
```

2. Open start.bat file.
   
4. Follow the instructions in the terminal window.
   
6. The generating results are stored in the folder ./SUMOtest/outputfolder_xxx, xxx is the file name of .xosc file.


# Unity Connection

1. Change the Offset according to the offset information generated in infos4unity.txt 
2. Change the name of the ego participant as "Ego"
3. Use the model generated in the folder xxx (To Do)



# License

[(Back to top)](#table-of-contents)


# Converge to csv
[(Back to top)](#table-of-contents)

1. Simple Scenario recording   

Esmini can save a file that captures the state of all entities. This file can later be used either to replay (see Replay scenario) the scenario or converted for further analysis, e.g. in Excel..dat.csv  

To create a recording with regular timesteps:  
```sh
./bin/esmini --window 60 60 800 400 --osc ./resources/xosc/cut-in.xosc --fixed_timestep 0.05 --record sim.dat
```
To convert the .dat file into .csv, do either of:  
```sh
or./bin/dat2csv sim.dat
python ./scripts/dat2csv.py sim.dat
```
Only a subset of the .dat file information is extracted. To extract some more info, e.g. road coordinates, run: ./scripts/dat2csv --extended sim.dat  

2. CSV logger

To create a more complete csv logfile, compared to the content of the .dat file, activate the CSV_Logger:
```sh
./bin/esmini --window 60 60 800 400 --osc ./resources/xosc/cut-in.xosc --fixed_timestep 0.05 --csv_logger full_log.csv
```
full_log.csv will contain more detailed states for all scenario entities. To also include collision detection:
```sh
./bin/esmini --window 60 60 800 400 --osc ./resources/xosc/cut-in.xosc --fixed_timestep 0.05 --csv_logger full_log.csv --collision
```
All collisions (overlap) between entity bounding boxes will be registered in the column of each entity. It will contain the IDs of any entities overlapping at given frame.collision_ids

# Inspect OpenDRIVE geometry and road IDs
[(Back to top)](#table-of-contents)

Esmini odrplot is a small application that creates a track.csv file that can be plotted with another small Python script xodr.py:
```sh
./bin/odrplot ./resources/xodr/fabriksgatan.xodr
```
change the line 12 of ./EnvironmentSimulator/Applications/odrplot/xodr.py by 
```
with open('track.csv') as f:
```
run 
```sh
./EnvironmentSimulator/Applications/odrplot/xodr.py
```

[Esmini](https://github.com/esmini/esmini.git)
[Detailed User guide](https://esmini.github.io)


