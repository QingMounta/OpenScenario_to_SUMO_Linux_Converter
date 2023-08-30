import xml.etree.ElementTree as ET
import os
import logging
import copy


# Load the OpenSCENARIO file
file_path = "../resources/myresources/OSC-ALKS-scenarios/Scenarios/ALKS_Scenario_4_2_3_CrossingPedestrian_TEMPLATE.xosc"
# file_path = "../resources/myresources/SampleScenarios/575d7e80-10e8-4f39-84b3-ddb52fbf6089.xosc"
# file_path = "../resources/myresources/Circle/circle.xosc"
tree = ET.parse(file_path)
root = tree.getroot()


catalogs = tree.find("CatalogLocations")
# print(catalogs)
# print(list(catalogs))
if list(catalogs) != []:
    # catalog_types = ["Vehicle",
    #                 "Controller",
    #                 "Pedestrian",
    #                 "MiscObject",
    #                 "Environment",
    #                 "Maneuver",
    #                 "Trajectory",
    #                 "Route"]
    catalog_types = ["Vehicle",
                    "Pedestrian"]
    catalogs_dict = {}
    for catalog_type in catalog_types:
        catalog = catalogs.find(catalog_type + "Catalog")
        
        if catalog is None:
            continue

        catalog_path = catalog.find("Directory").attrib.get('path') + "/" + catalog_type + "Catalog.xosc"




        if not os.path.isabs(catalog_path) and "xosc" in file_path:
            catalog_path = os.path.dirname(os.path.abspath(file_path)) + "/" + catalog_path


        if not os.path.isfile(catalog_path):
            logging.basicConfig()
            logger = logging.getLogger("[OpenScenarioConfiguration]")
            logger.warning("The %s path for the %s Catalog is invalid", catalog_path, catalog_type)
        else:
            xml_tree = ET.parse(catalog_path)
            # self._validate_openscenario_catalog_configuration(xml_tree)
            catalog = xml_tree.find("Catalog")
            catalog_name = catalog.attrib.get("name")

            
            catalogs_dict[catalog_name] = {}
            for entry in catalog:
                catalogs_dict[catalog_name][entry.attrib.get("name")] = {}

                if catalog_type == "Vehicle":
                    Infos_categorie = entry.attrib.get("vehicleCategory")
                    catalogs_dict[catalog_name][entry.attrib.get("name")]["vehicleCategory"] = Infos_categorie
                    for item in entry:
                        if item.tag == "Performance":
                            Infos_speed = item.attrib.get("maxSpeed")
                            Infos_acc = item.attrib.get("maxAcceleration")
                            Infos_dec = item.attrib.get("maxDeceleration")
                            catalogs_dict[catalog_name][entry.attrib.get("name")]["maxSpeed"] = Infos_speed
                            catalogs_dict[catalog_name][entry.attrib.get("name")]["maxAcceleration"] = Infos_acc
                            catalogs_dict[catalog_name][entry.attrib.get("name")]["maxDeceleration"] = Infos_dec
                        if item.tag == "BoundingBox":
                            BB_Dimension = item.find("Dimensions")
                            length = BB_Dimension.attrib.get("length")
                            catalogs_dict[catalog_name][entry.attrib.get("name")]["length"] = length

                    
                elif catalog_type == "Pedestrian":
                    Infos_categorie = entry.attrib.get("pedestrianCategory")
                    Infos_mass = entry.attrib.get("mass")
                    catalogs_dict[catalog_name][entry.attrib.get("name")]["pedestrianCategory"] = Infos_categorie
                    catalogs_dict[catalog_name][entry.attrib.get("name")]["mass"] = Infos_mass
                    for item in entry:
                        if item.tag == "BoundingBox":
                            BB_Dimension = item.find("Dimensions")
                            length = BB_Dimension.attrib.get("length")
                            catalogs_dict[catalog_name][entry.attrib.get("name")]["length"] = length


                
                print("The catalog name '",catalog_name,"' with the item name of '", entry.attrib.get("name"), "' has the following infos: ", catalogs_dict[catalog_name][entry.attrib.get("name")])

catalogs = tree.find("CatalogLocations")    

if list(catalogs) != []:
    xml_string = {}
    i = 0
    for entity in tree.iter("Entities"):
        for obj in entity.iter("ScenarioObject"):
            ScenarioObject_name = obj.attrib.get("name")
            
            for catalog_reference in obj.iter("CatalogReference"):
                catalog_name = str(catalog_reference.attrib.get("catalogName"))
                entry_name = str(catalog_reference.attrib.get("entryName"))
                # print("catalog name:",catalog_name," with entry name:",entry_name)
                if catalog_name in catalogs_dict:
                    
                    Info = catalogs_dict[catalog_name][entry_name]
                    Info["ID"] = ScenarioObject_name
                    print("The ScenarioObject_name: '",ScenarioObject_name,"' from catalog name: '",catalog_name,"' with entry name: '",entry_name,"' has following infos:",Info)
                    if catalog_name == "VehicleCatalog":
                        xml_string[str(i)] = f'''    <vType accel="{Info["maxAcceleration"]}" decel="{Info["maxDeceleration"]}" id="{Info["ID"]}" length="{Info["length"]}" maxSpeed="{Info["maxSpeed"]}" sigma="0.0" guiShape="passenger" />'''
                    elif catalog_name == "PedestrianCatalog":
                        xml_string[str(i)] = f'''    <vType id="{Info["ID"]}" length="{Info["length"]}"  sigma="0.0"/>'''

                 
                    i += 1

else:
    xml_string = {}
    i = 0
    for entity in tree.iter("Entities"):
        
        for obj in entity.iter("ScenarioObject"):
            ScenarioObject_name = obj.attrib.get("name")
            
            Vehicle = obj.find("Vehicle")
            # print(Vehicle)
            Info = {}
            Info["ID"] = ScenarioObject_name
            Info["vehicleCategory"] = Vehicle.attrib.get("vehicleCategory")
            performance = Vehicle.find("Performance")
            Info["maxSpeed"] = performance.attrib.get("maxSpeed")
            Info["maxAcceleration"] = performance.attrib.get("maxAcceleration")
            Info["maxDeceleration"] = performance.attrib.get("maxDeceleration")
            BoundingBox = Vehicle.find("BoundingBox")
            BB_Dimension = BoundingBox.find("Dimensions")
            Info["length"] = BB_Dimension.attrib.get("length")

            print("The ScenarioObject_name: '",ScenarioObject_name,"' directly has following infos: ",Info)

            xml_string[str(i)] = f'''    <vType accel="{Info["maxAcceleration"]}" decel="{Info["maxDeceleration"]}" id="{Info["ID"]}" length="{Info["length"]}" maxSpeed="{Info["maxSpeed"]}" sigma="0.0" guiShape="passenger" />'''
            i += 1

# 将XML字符串写入xxx.rou.xml文件
with open('xxx.rou.xml', 'w') as file:
    file.write('''<routes>''')
    i = 0
    for items in xml_string:
        file.write('''\n''')
        file.write(xml_string[str(i)])
        i += 1
    file.write('''\n''')
    file.write('''</routes>''')



