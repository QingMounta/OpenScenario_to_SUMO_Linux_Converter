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

Before you start, make sure you have the following prerequisites ready.

- **Operating System:** Windows
- **Python Version:** The project requires Python. It has been tested on versions '3.10' and '3.11'. Make sure you have Python installed.
- **SUMO Version:** The project utilizes SUMO version 1.18.0. Follow the [official SUMO installation guide](https://sumo.dlr.de/docs/Installing/index.html) to install it.
- **Required Python Packages:** Make sure to have the following Python packages installed:

    - numpy==1.25.2
    - openpyxl==3.1.2
    - pandas==2.0.3
    - pip==23.0.1
    - sumolib==1.16.0
    - traci==1.16.0
    - imageio==2.31.2
    - pillow==10.0.0


  
For the best experience, we strongly recommend using the Anaconda Python distribution.

# Installation
[(Back to top)](#table-of-contents)

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/your-repo.git
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
   
5. The generating results including the static map, settings of each participants, and the detailed trajectories of each participants are stored in the folder ./SUMOtest/outputfolder_xxx, xxx is the file name of .xosc file:
   (To Do): list the resulting files and short explain


# Unity Connection

1. Change the Offset according to the offset information generated in infos4unity.txt 
2. Change the name of the ego participant GameObject as "Ego"
3. Use the model generated in the folder xxx (To Do)



# License

[(Back to top)](#table-of-contents)




[Esmini](https://github.com/esmini/esmini.git)
[Detailed User guide](https://esmini.github.io)


