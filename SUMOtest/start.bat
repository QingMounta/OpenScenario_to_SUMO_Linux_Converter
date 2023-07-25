@echo off
setlocal enabledelayedexpansion

REM Store the current folder in a variable
set "currentFolder=%CD%"

@REM REM Navigate back to the parent folder
@REM cd ..

@REM REM Run esmini command
@REM @REM bin\esmini --window 60 60 800 400 --osc resources\myresources\Circle\circle.xosc --fixed_timestep 0.025 --record sim.dat
@REM ..\bin\esmini --window 60 60 800 400 --osc ..\resources\myresources\Circle\circle.xosc --fixed_timestep 0.025 --csv_logger full_log.csv --collision

@REM REM Run dat2csv command
@REM bin\dat2csv sim.dat

@REM REM Navigate back to the previous folder
@REM cd "%currentFolder%"

REM Prompt the user to enter the opendrive file path (e.g., resources\myresources\Circle\circle.xodr)
set /p filepath=Enter the opendrive file path (e.g., resources\myresources\Circle): 

REM Prompt the user to enter the xosc filename (e.g., circle)
set /p filename=Enter the xosc filename (e.g., circle): 

REM Prompt the user to enter the xodr filename (e.g., circle)
set /p odrfilename=Enter the xodr filename (e.g., circle): 

REM Run esmini command
..\bin\esmini --window 60 60 800 400 --osc ..\%filepath%\%filename%.xosc --fixed_timestep 0.025 --record sim.dat
..\bin\dat2csv sim.dat
..\bin\esmini --window 60 60 800 400 --osc ..\%filepath%\%filename%.xosc --fixed_timestep 0.025 --csv_logger full_log.csv --collision

REM Create the output folder using the user-defined filename
mkdir "outputfolder_%filename%"

REM Run the netconvert command with the modified file path and filename
netconvert --opendrive "..\%filepath%\%odrfilename%.xodr" -o "outputfolder_%filename%\%filename%.net.xml"

REM Check if the netconvert command was successful
if !errorlevel! equ 0 (
    REM Create the contents of the .sumocfg file
    echo ^<configuration^> > "outputfolder_%filename%\simulation.sumocfg"
    echo     ^<input^> >> "outputfolder_%filename%\simulation.sumocfg"
    echo         ^<net-file value="%filename%.net.xml"/^> >> "outputfolder_%filename%\simulation.sumocfg"
    echo         ^<route-files value="%filename%.rou.xml"/^> >> "outputfolder_%filename%\simulation.sumocfg"
    echo     ^</input^> >> "outputfolder_%filename%\simulation.sumocfg"
    echo     ^<time^> >> "outputfolder_%filename%\simulation.sumocfg"
    echo         ^<begin value="0"/^> >> "outputfolder_%filename%\simulation.sumocfg"
    echo         ^<end value="10000"/^> >> "outputfolder_%filename%\simulation.sumocfg"
    @REM echo         ^<step-length value="0.025"/^> >> "outputfolder_%filename%\simulation.sumocfg"
    echo     ^</time^> >> "outputfolder_%filename%\simulation.sumocfg"
    echo ^</configuration^> >> "outputfolder_%filename%\simulation.sumocfg"

    REM Display success message
    echo outputfolder_%filename%\simulation.sumocfg file written successfully.

    REM Run the remaining commands with the modified filename
    python randomTrips.py -n "outputfolder_%filename%\%filename%.net.xml" -e 1 --allow-fringe
    move "trips.trips.xml" "outputfolder_%filename%\"
    duarouter --trip-files "outputfolder_%filename%\trips.trips.xml" --net-file "outputfolder_%filename%\%filename%.net.xml" --output-file "outputfolder_%filename%\result.rou.xml"
    python xml2csv.py "outputfolder_%filename%\result.rou.xml"
    copy "vehicleType.rou.xml" "outputfolder_%filename%\"
    move "outputfolder_%filename%\vehicleType.rou.xml" "outputfolder_%filename%\%filename%.rou.xml"
    move "full_log.csv" "outputfolder_%filename%\"
    move "sim.csv" "outputfolder_%filename%\"
    python TraciFile_copy.py "%filename%"
) else (
    REM Display an error message
    echo Failed to convert the file.

)
