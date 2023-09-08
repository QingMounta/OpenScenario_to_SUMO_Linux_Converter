# OpenScenario2SUMO_Converter

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

Before you start, make sure you have the following prerequisites ready.

- **Operating System:** Windows
- **Python Version:** The project requires Python. It has been tested on versions '3.10' and '3.11'. Make sure you have Python installed.
- **SUMO Version:** The project utilizes SUMO version 1.18.0. Follow the [official SUMO installation guide](https://sumo.dlr.de/docs/Installing/index.html) to install it.
- **Required Python Packages:** Make sure to have the following Python packages installed: requirements.txt


  
For the best experience, we strongly recommend using the Anaconda Python distribution.

# Installation
[(Back to top)](#table-of-contents)

1. Clone the repository:

   ```bash
   git clone https://github.com/TianZheng095/OpenScenario2SUMO_Converter.git
   ```





# Conversion to SUMO
[(Back to top)](#table-of-contents)

1. Go to folder SUMOtest folder.
```
cd SUMOtest
```

2. Open start.bat file.
   
3. Follow the instructions in the terminal window.
   
4. The converted sumo simulation file is automatic opened, click "run" to start the simulation

5. If use unity for visualization or/and interaction, "run" unity after start the SUMO simulation
   
6. The generating results including the static map, settings of each participants, and the detailed trajectories of each participants are stored in the folder ./SUMOtest/outputfolder_xxx, xxx is the file name of .xosc file:  

  - `OpenSCENARIO_output.net.xml`: This file contains the static network data converted from the provided Opendrive file.

  - `OpenSCENARIO_output.rou.xml`: This file includes all the object definitions that appear in the given scenario.
  
  - `infos4unity.txt`: This file provides offset information for use with Unity.
  
  - `loggingData4SUMO.xlsx`: This file contains detailed trajectories for each object in the scenario in SUMO format.
  
  - `loggingTrajectoriesXOSC.xlsx`: This file contains detailed trajectories for each object in the scenario in OpenSCENARIO format.
  
  - `trips.trips.xml`: This file represents a random trip generated based on the static network (OpenSCENARIO_output.net.xml).
  
  - `result.rou.xml`: Corresponding route file to the trip file (`trips.trips.xml`).
  
  - `simulation.sumocfg`: SUMO configuration file.
  
  - `simulation_animation.gif`: Visualization of the given OpenSCENARIO file via Esmini.











# Unity Connection

[(Back to top)](#table-of-contents)

1. Change the Offset according to the offset information generated in infos4unity.txt 
2. Change the name of the ego participant GameObject as "Ego"
3. Use the model generated in the folder xxx (To Do)



# License

[(Back to top)](#table-of-contents)


If you use OpenScenario2SUMO for academic work, we highly encourage you to cite this repository.\
Please feel free to reach out to TUM Verkehrstechnik or the directly to the email tian.zheng@tum.de for any questions.


