# Define the contents of the .sumocfg file as a string
sumocfg_contents = """
<configuration>
    <input>
		<net-file value="simulation.net.xml"/>
		<route-files value="simulation.rou.xml"/>
	</input>
	<time>
		<begin value="0"/>
		<end value="10000"/>
		<step-length value="0.025"/>
	</time>
</configuration>
"""


# Define the new file name
name = input("Enter your scenario name: ")
net_file = "circle.net.xml"

# Replace the value using the replace() method
sumocfg_contents = sumocfg_contents.replace('simulation.net.xml', net_file)

# Display the updated string
print(sumocfg_contents)

# Specify the file path for the .sumocfg file
file_path = "simulation.sumocfg"

# Write the contents to the .sumocfg file
with open(file_path, "w") as file:
    file.write(sumocfg_contents)

print(f".sumocfg file written successfully at {file_path}")