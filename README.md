# OpenScenario2SUMO_viaEsmini
Automatic traffic scenario conversion interface between OpenSCENARIO and the traffic simulator SUMO


# Table of contents


- [Installation](#installation)
- [Demo](#demo)
- [Build](#build)
- [License](#license)


# Installation

[(Back to top)](#table-of-contents)


1. Download latest release from [here](https://github.com/esmini/esmini/releases/latest)


2. Pick the demo package for Windows.  
Make sure the zip file is not blocked: Right click, click Properties, at bottom right check Unblock. For more info, see Blocked by Windows Defender SmartScreen.  
To install the package, just unzip it anywhere. A single subfolder named esmini-demo is created.  


4. Pick the package: esmini-(version) for Windows.   
On Windows, make sure the zip file is not blocked: Right click, click Properties, at bottom right check Unblock. For more info, see Blocked by Windows Defender SmartScreen.  
To install the package, just unzip it anywhere. A single subfolder named esmini-(version) is created. This is the root folder for esmini. No files are stored outside this folder structure and no system files or registry is modified in any way.  



# Demo

[(Back to top)](#table-of-contents)


Try to run one of the examples:  

go to folder esmini-demo/run/esmini  

double click on a .bat file, e.g. run_cut-in.bat or run it from a command line.  

You can also run the examples explicitly from a command line:  
```sh
./bin/esmini --window 60 60 800 400 --osc ./resources/xosc/cut-in.xosc
```


# Build esmini - quick guide
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

# License

[(Back to top)](#table-of-contents)


[Esmini](https://github.com/esmini/esmini.git)
[Detailed User guide](https://esmini.github.io)


