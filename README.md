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
2. Pick the demo package for your platform (Windows, Linux or Mac). 
On Windows, make sure the zip file is not blocked: Right click, click Properties, at bottom right check Unblock. For more info, see Blocked by Windows Defender SmartScreen.
To install the package, just unzip it anywhere. A single subfolder named esmini-demo is created. 
3. Pick the package: esmini-(version) for your platform (Windows, Linux or Mac). 
On Windows, make sure the zip file is not blocked: Right click, click Properties, at bottom right check Unblock. For more info, see Blocked by Windows Defender SmartScreen.
To install the package, just unzip it anywhere. A single subfolder named esmini-(version) is created. This is the root folder for esmini. No files are stored outside this folder structure and no system files or registry is modified in any way.



# Demo

[(Back to top)](#table-of-contents)



# Build esmini - quick guide

Supported systems: Windows, Linux and Mac.

Make sure you have a C++ compiler and CMake installed.

On Windows Visual Studio is recommended (Community/free version is good enough for building esmini). Make sure to check the "Desktop development with C++" package for installation, no more is needed.

Now we’re ready to build esmini. From esmini root folder:

```sh
mkdir build
cd build
cmake ..
cmake --build . --config Release --target install
```
The build process automatically downloads 3rd party library binaries and the complete 3D model package.

After successful build, the binaries will be copied into esmini/bin folder. Try from command line:
```sh
./bin/esmini --window 60 60 800 400 --osc ./resources/xosc/cut-in.xosc
```

# License

[(Back to top)](#table-of-contents)

[Esmini](https://github.com/esmini/esmini.git)
[Detailed User guide](https://esmini.github.io)


