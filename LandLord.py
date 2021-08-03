'''
By Draxx182
Credits go to HeartlessSeph for his pointers and code
SutandoTsukai181 for his Binary Reader and
Retraso for some of his base code
'''
#Imports
import json
import sys
import os
import shutil
import time
from pathlib import Path
from collections import defaultdict
from binary_reader import BinaryReader
start_time = time.time()

#Dicts
headerDict = dict()
stringDict = dict()
gmtDict = dict()
mepDict = dict()
pointerDict = dict()
#Reference
moveDataDict = {"Unk 0": 32, "MEP Table ID": 1, "Unk 2": 32, "Unk 3": 32, "Unk 4p1": 16, "Unk 4p2": 16, "Unk 5 Bitfield": 32, "Unk 6": 32, "Unk 7": 32, "GMT Table ID": 2, "Unk 9": 32, "Unk 10": 32, "Unk 11p1": 16, "Unk 11p2": 16, "Ubyte Unk 1": 8, "Unk 12": 16, "Ubyte Unk 2": 8, "Unk 13": 32, "Unk 14": 32}
moveIDDict = {1:"Hitbox Audio(?)",2:"Audio",3:"Follow Up Lock",4:"Control Lock",5:"Hitbox",6:"Pickup(?)",10:"Sync 1 Damage",11:"Invincibility",12:"Bullet Effect",13:"Dropdown(?)",15:"Camera Shake",16:"Controller Shake",18:"Camera",20:"Lock-on",26:"Hyper Armor Control",28:"Charge Attack Property",29:"Heat Control",30:"Heat Gain(?)"}
moveTableDict = {"StartFrame":16,"EndFrame":16,"Modifier":8,"Unk 1":8,"Unk 2":8,"Property Type ID":1,"Unk Value":32}
moveTableDataDict = {}

def tree(): #Makes a tree :troll:
    def the_tree():
        return defaultdict(the_tree)
    return the_tree()

#Tree Dicts
moveDict = tree()

def write_dir(file_path, name): #Writes a new directory to another directory
    foldName = os.path.join(str(file_path)+name)
    folder = Path(foldName)
    folder.mkdir(exist_ok=True)
    return(folder)

def export_json(target_path, filename, data): #Writes a json to a certain directory
    jsonFile = json.dumps(data, ensure_ascii=False, indent=2)
    jsonPath = target_path / (filename+ '.json')
    jsonPath.write_text(jsonFile)

def import_json(target_path, name): #Goes through a directory, then loads json info into a dict
    import_file = os.path.join(target_path+("//"+name+".json"))
    with open(import_file) as input_file:
        json_array = json.loads(input_file.read())
        return(json_array)

#Checks to make sure argument is set, then either imports a directory or exports property.bin
if (len(sys.argv) <= 1):
    print('Drag and drop property.bin from the motion files to LandLord for it to work.')
else:
    propertyPath = sys.argv[1]
    if (propertyPath.endswith(".bin")):
        file = open(propertyPath, 'rb')
        rd = BinaryReader(file.read())
        wr = BinaryReader()
        rd.set_endian(True)
        wr.set_endian(True)
        propertyFolder = write_dir(propertyPath, ' folder')
        direct = write_dir(propertyFolder, '//Table Data')

        #Number of blocks in each table, plus it's starting pointers.
        rd.seek(40, whence=2)
        moveBlocks = rd.read_uint32(3) #Num of moveblocks, pointer to name table, pointer to data table
        gmtBlocks = rd.read_uint32(2) #Num of GMT files, pointer to start of GMT table
        mepBlocks = rd.read_uint32(2) #Num of MEP files, pointer to start of MEP table
        unkBlocks = rd.read_uint32(3) #Num of Unk Files, pointer to start of Unk GMT table, pointer to start of Unk blocks
        rd.seek(0)

        #--Header--
        rd.read_bytes(6)
        headerDict["Unk"] = rd.read_uint16()
        headerDict["File Version"] = rd.read_uint32()
        export_json(propertyFolder, "PropertyHeader", headerDict) #Yes I have a function to create a json, shush
        rd.read_uint32()
        print("Property Header successfully exported")

        #--String Data--
        stringSet = 0 #Checker to see position
        stringNum = 0 #Incrementing number to name string
        while stringSet < moveBlocks[1]-2:
            stringNum += 1
            stringDict["String "+str(stringNum)] = rd.read_str()
            stringSet = rd.pos() #Updates string position
        print("String Data successfully exported")

        #--GMT Table--
        gmtBlocksTable = gmtBlocks[1]
        #Goes through every GMT block and makes a json
        for gmt in range(gmtBlocks[0]):
            rd.seek(gmtBlocksTable)
            gmtBlocksName = rd.read_uint32() #Gives back the pointer location for the name
            gmtBlocksTable = rd.pos() #Records position of current GMT Block

            rd.seek(gmtBlocksName)
            gmtName = rd.read_str()
            gmtDict[gmt] = gmtName
        export_json(direct, "GMT Block Data", gmtDict) #Exports GMT Table
        gmtList = list(gmtDict.values())
        print("GMT Block Data successfully exported")
    
        #--MEP Table--
        mepBlocksTable = mepBlocks[1]
        #Goes through every MEP block and makes a json
        for mep in range(mepBlocks[0]):
            rd.seek(mepBlocksTable)
            mepBlocksName = rd.read_uint32() #Gives back the pointer location for the name
            mepBlocksTable = rd.pos() #Records position of current MEP Block

            rd.seek(mepBlocksName)
            mepName = rd.read_str()
            mepDict[mep] = mepName
        export_json(direct, "MEP Block Data", mepDict) #Exports MEP Table
        mepList = list(mepDict.values())
        print("MEP Block Data successfully exported")

        #--Move Blocks--
        moveBlocksName = moveBlocks[1] #Name Table
        moveBlocksData = moveBlocks[2] #Data Table
        moveIDDictV = list(moveIDDict.values())
        moveIDDictK = list(moveIDDict.keys())
        moveDataDictI = moveDataDict.items()
        moveTableDictI = moveTableDict.items()

        #Goes through every move block and makes a json
        for move in range(moveBlocks[0]):
            #Looks for the name of the move, plus pointer
            rd.seek(moveBlocksName)
            moveNamePointer = rd.read_uint32()
            moveBlocksName = rd.pos()
            rd.seek(moveNamePointer)
            moveName = rd.read_str()
        
            #Looks for the data of the move, plus pointer
            rd.seek(moveBlocksData)
            moveData = rd.read_uint32()
            moveBlocksData = rd.pos()
            rd.seek(moveData)

            #Goes to the data of move.
            for key, value in moveDataDictI:
                if (value == 32): #Reads 32 bytes if the value is 32
                    moveDict[moveName]["Move Data"][key] = rd.read_uint32()
                elif (value == 16): #Reads 16 bytes if the value is 16
                    moveDict[moveName]["Move Data"][key] = rd.read_uint16()
                elif (value == 8): #Reads 8 bytes if the value is 8
                    moveDict[moveName]["Move Data"][key] = rd.read_uint8()
                elif (value == 1): #MEP Table ID, finds string to write it to dict.
                    mepIndex = rd.read_int32()
                    if mepIndex in mepDict:
                        moveDict[moveName]["Move Data"][key] = mepList[mepIndex]
                    else:
                        moveDict[moveName]["Move Data"][key] = ""
                elif (value == 2): #GMT Table ID, finds string to write it to dict.
                    gmtIndex = rd.read_int32()
                    if gmtIndex in gmtDict:
                        moveDict[moveName]["Move Data"][key] = gmtList[gmtIndex]
                    else:
                        moveDict[moveName]["Move Data"][key] = ""

            #Move Properties
            moveBlocksProperty = rd.pos() #Start of the properties table
            moveDict[moveName]["Move Properties"]["Property Unk"] = rd.read_uint16()
            numOfProperties = rd.read_uint16()
            moveDict[moveName]["Move Properties"]["Number of Properties"] = numOfProperties
            if (numOfProperties > 0):
                for property in range(numOfProperties): #I know, this is not pretty coding. 
                    #Will polish things later. Gets Property ID Before scanning, basically.
                    pointerStart = rd.pos()
                    rd.read_bytes(6)
                    rd.read_uint8() #Stupid
                    propertyIDType = rd.read_uint8()
                    rd.seek(pointerStart)

                    if propertyIDType in moveIDDict: #Gets the correct string to assign to property.
                        idIndex = moveIDDictK.index(propertyIDType)
                        id = ("Property 1| Type ID "+str(propertyIDType)+" = "+moveIDDictV[idIndex])
                    else:
                        id = ("Property 1| Type ID "+str(propertyIDType))

                    #Reads the basic data of a property in a move
                    for key, value in moveTableDictI:
                        if (value == 32):
                            moveDict[moveName]["Move Properties"]["Properties Table"][id]["Property Data"][key] = rd.read_uint32()
                        elif (value == 16):
                            moveDict[moveName]["Move Properties"]["Properties Table"][id]["Property Data"][key] = rd.read_uint16()
                        elif (value == 8):
                            moveDict[moveName]["Move Properties"]["Properties Table"][id]["Property Data"][key] = rd.read_uint8()
                        elif (value == 1):
                            rd.read_uint8()
                            moveDict[moveName]["Move Properties"]["Properties Table"][id]["Property Data"]["StartFrame"] = propertyIDType
                    propertiesPointer = rd.read_uint32() #Pointer to where property id tables start at
                    propertiesTablePos = rd.pos()

                    #Checks the PropertyID to see if it's a special ID
                    if (propertyIDType == 1): #Unknown Property | ID 1
                        rd.seek(propertiesPointer + moveBlocksProperty)
                        for unk in range(11):
                            moveDict[moveName]["Move Properties"]["Properties Table"][id]["Unknown Property"]["Unk "+str(unk)] = rd.read_uint16()
                        rd.seek(propertiesTablePos)
                    elif (propertyIDType == 2): #Audio Property | ID 2
                        rd.seek(propertiesPointer + moveBlocksProperty)
                        for unk in range(11):
                            moveDict[moveName]["Move Properties"]["Properties Table"][id]["Audio"]["Unk "+str(unk)] = rd.read_uint16() 
                        rd.seek(propertiesTablePos)
                    elif (propertyIDType == 5 or propertyIDType == 18): #Hitbox or Camera Property | ID 5 or 18
                        rd.seek(propertiesPointer + moveBlocksProperty)
                        #Guesses which property it is, assigns appropriate location
                        if (propertyIDType == 5):
                            hitboxStr = "Hitbox"
                        elif (propertyIDType == 18): #dumb.png
                            hitboxStr = "Camera"
                        else:
                            pass
                        moveDict[moveName]["Move Properties"]["Properties Table"][id][hitboxStr][hitboxStr+"Location1"] = rd.read_uint16()
                        moveDict[moveName]["Move Properties"]["Properties Table"][id][hitboxStr][hitboxStr+"Location2"] = rd.read_uint16()
                        #The Unks of the Hitbox and Camera property are in the same place
                        moveDict[moveName]["Move Properties"]["Properties Table"][id][hitboxStr]["Unk 1"] = rd.read_uint16()
                        moveDict[moveName]["Move Properties"]["Properties Table"][id][hitboxStr]["Unk 2"] = rd.read_uint8()
                        moveDict[moveName]["Move Properties"]["Properties Table"][id][hitboxStr]["Unk 3"] = rd.read_uint8()
                        #And the modifiers of them too.
                        moveDict[moveName]["Move Properties"]["Properties Table"][id][hitboxStr]["Flags"] = rd.read_uint16()
                        moveDict[moveName]["Move Properties"]["Properties Table"][id][hitboxStr]["Damage"] = rd.read_uint8()
                        moveDict[moveName]["Move Properties"]["Properties Table"][id][hitboxStr]["Heat"] = rd.read_uint8()
                        moveDict[moveName]["Move Properties"]["Properties Table"][id][hitboxStr]["Unk 4"] = rd.read_uint32()
                        rd.seek(propertiesTablePos)
        export_json(direct, "Move Block Data", moveDict) #Exports Move Table
        print("Move Block Data successfully exported")

        #--Unknown Table--
        unkDict = dict()
        unkBlocksTable = unkBlocks[1]
        #Goes through every Unk GMT block and makes a json
        for uGMT in range(unkBlocks[0]):
            rd.seek(unkBlocksTable)
            unkBlocksName = rd.read_uint32()
            unkBlocksTable = rd.pos()

            rd.seek(unkBlocksName)
            unkName = rd.read_str()
            unkDict["Unk Block "+str(uGMT)] = unkName
        export_json(direct, "Unk Block Data", unkDict) #Exports Unk Table
        print("Unk Block Data successfully exported")

        #--Data of Unknown Table
        dataDict = tree()
        dataBlocksTable1 = unkBlocks[2]
        #I honestly don't know anymore. 
        for uDAT in range(unkBlocks[0]):
            rd.seek(dataBlocksTable1)
            dataBlocksName1 = rd.read_uint32() #Pointer to find the pointer of the name
            dataBlocksTable1 = rd.pos() #Don't question the above

            rd.seek(dataBlocksName1) #Going to find the actual name
            numOfU = rd.read_uint32() #How many unk pointers there are in this block
            locOfU = rd.read_uint32() #Points to location of unk pointer
            dataBlocksName2 = rd.read_uint32() #Finally, the name pointer
            dataBlocksTable2 = rd.pos()

            rd.seek(dataBlocksName2)
            dataName = rd.read_str() #Gets the name
            rd.seek(dataBlocksTable2)
            unknown1 = rd.read_uint32() #Unknown
            unknown2 = rd.read_uint32() #Unknown

            rd.seek(locOfU)
            dataDict[str(uDAT)+" Data Block"]["Name"] = dataName
            dataDict[str(uDAT)+" Data Block"]["Number of Tables"] = numOfU
            dataDict[str(uDAT)+" Data Block"]["Unknown Value 1"] = unknown1
            #Loops through unk pointer blocks
            for u in range(numOfU):
                pointOfU = rd.read_uint32() #Pointer to table
                dataBlocksTable3 = rd.pos()
                rd.seek(pointOfU)
                dataName2 = rd.read_uint32() #Name of the data table string
                unkVal = rd.read_uint32()

                rd.seek(dataName2)
                dataString = rd.read_str()
                rd.seek(dataBlocksTable3)
                dataDict[str(uDAT)+" Data Block"]["Table "+str(u)]["Table Name"] = dataString
                dataDict[str(uDAT)+" Data Block"]["Table "+str(u)]["Unk Value"] = unkVal
            export_json(direct, "Unk-Data Blocks", dataDict) #Exports Data Table
        print("Unk-Data Blocks successfully exported")
        file.close()
        print("My program took", time.time() - start_time, "to run")
    else:
        propertyTable = os.path.join(propertyPath +'//Table Data') #Path to table data folder
        #Binary Reader
        wr = BinaryReader()
        wr.set_endian(True)

        '''
        ('E_btlst_NSK_B15', 
        OrderedDict([('Move Data', 
        OrderedDict([('Unk 0', 16), ('MEP Table ID', -1), ('Unk 2', 48), ('Unk 3', 60), ('Unk 4p1', 5), ('Unk 4p2', 0), ('Unk 5 Bitfield', 16777472), ('Unk 6', 0), ('Unk 7', 0), ('GMT Table ID', 1103), ('Unk 9', 0), ('Unk 10', 0), ('Unk 11p1', 3), ('Unk 11p2', 0), ('Ubyte Unk 1', 1), ('Unk 12', 0), ('Ubyte Unk 2', 0), ('Unk 13', 0), ('Unk 14', 0)])), ('Move Properties', 
        OrderedDict([('Property Unk', 0), ('Number of Properties', 1), ('Properties Table', 
        OrderedDict([('Property 1| Type ID 2 = Audio', 
        OrderedDict([('Property Data', 
        OrderedDict([('StartFrame', 5), ('EndFrame', 5), ('Modifier', 0), ('Unk 1', 0), ('Unk 2', 0), ('Property Type ID', 2), ('Unk Value', 0)])), ('Audio', 
        OrderedDict([('Unk 0', 18111), ('Unk 1', 13), ('Unk 2', 65535), ('Unk 3', 65535), ('Unk 4', 65535), ('Unk 5', 65535), ('Unk 6', 65535), ('Unk 7', 65535), ('Unk 8', 65535), ('Unk 9', 65535), ('Unk 10', 4)]))]))]))]))]))])
        '''
    
        #--Header--
        headerDict = import_json(propertyPath, "PropertyHeader")
        wr.write_uint32(1128353874)
        wr.write_uint16(513)
        headerDict = list(headerDict.values())
        wr.write_uint16(headerDict[0])
        wr.write_uint32(headerDict[1])
        filesize = wr.pos() #Takes us back to the writer's filesize pos
        wr.write_uint32(0) #Placeholder for filesize

        #--String Table--
        stringDict = import_json(propertyTable, "String Data")
        for value in stringDict.values():
            pointerDict[value] = wr.pos() #Switches string to key, then writes adds pointer location
            wr.write_str(value, null=True) #Writes string to bin
        pointerName = dict()
        pointers = list(pointerDict.values())
        pointerNames = list(pointerDict.keys())
        wr.write_uint8(204)

        #--Move Name Table--
        moveDict = import_json(propertyTable, "Move Block Data")
        moveBlocks = [len(moveDict), wr.pos(), 0] #Move table size, position of start of name table, placeholder for start of data table
        moveList = list(moveDict.items()) #Puts Dict in a list
        #Searches through every move block
        for key in moveDict:
            moveIndex = pointerNames.index(key)
            wr.write_uint32(pointers[moveIndex])

        #--GMT Table--
        gmtDict = import_json(propertyTable, "GMT Block Data")
        gmtBlocks = [len(gmtDict), wr.pos()] #GMT table size, position at start of GMT table
        gmtName = dict()
        for key in gmtDict: #Finds index of gmtDict, then writes appropriate pointer.
            value = gmtDict[key]
            index = pointerNames.index(value)
            gmtName[value] = key
            wr.write_uint32(pointers[index])

        #--MEP Table--
        mepDict = import_json(propertyTable, "MEP Block Data")
        mepBlocks = [len(mepDict), wr.pos()] #MEP table size, position at start of MEP table
        mepName = dict()
        for key in gmtDict: #Finds index of mepDict, then writes appropriate pointer.
            value = mepDict[key]
            index = pointerNames.index(value)
            mepName[value] = key #Switches key and value
            wr.write_uint32(pointers[index])

        #--Unk Pointer Table--
        unkDict = import_json(propertyTable, "Unk Block Data")
        unkBlocks = [len(unkDict), wr.pos(), 0] #Unk table size, position at start of Unk table
        unkName = list(unkDict.values()) #Gets the names from the Unk Dict
        for value in gmtDict.values(): #Finds index of unkDict, then writes appropriate pointer.
            index = pointerNames.index(value)
            wr.write_uint32(pointers[index])

        #--Unk Data Table--
        dataDict = import_json(propertyTable, "Unk-Data Blocks")
        dataList = list(dataDict.items()) #List of the Data Dict
        dataPointers = [] #Pointer for each data table made

        for data in range(unkBlocks[0]): #Note: This part of code is REALLY messy since I had to jump around a lot
            dataOfList = list(dataList[data][1].values()) #Data of the ordereddict inside
            numOfTables = dataOfList[1]
            tablePointers = [] #Pointers of data of tables
            #Loops through how many tables there are
            for table in range(numOfTables):
                tableOfData = list(dataOfList[table+3].values()) #Gets data of each table ordereddict
                tablePointers.append(wr.pos())

                tableIndex = pointerNames.index(tableOfData[0]) #Finds index of the table name in pointers
                wr.write_uint32(pointers[tableIndex]) #Writes Table Name
                wr.write_uint32(tableOfData[1]) #Writes unk value
            #Writes the pointers of the tables at the end
            pointerToStart = wr.pos()
            for point in range(len(tablePointers)):
                wr.write_uint32(tablePointers[point])
            #Write the rest of the data
            dataPointers.append(wr.pos())
            wr.write_uint32(numOfTables) #Writes number of tables to bin
            wr.write_uint32(pointerToStart) #Writes the start of the unk tables
            startOfName = wr.pos() #Something to write the second unknown pointer with
            try: #For some reason there's an unk table with no name, which is also causing me a lot of trouble
                dataIndex = pointerNames.index(dataOfList[0]) #Finds index of the data name in pointers
            except:
                pass
            wr.write_uint32(pointers[dataIndex]) #Writes pointer of the name
            wr.write_uint32(dataOfList[2])
            wr.write_uint32(startOfName)

        #--Unk Name Table--
        unkBlocks[2] = wr.pos()
        for name in range(unkBlocks[0]):
            wr.write_uint32(dataPointers[name])

        #--Move Data Table--
        moveDataPointers = []
        moveDataDictI = moveDataDict.items()
        moveTableDictI = moveTableDict.items()
        for index1, move in enumerate(moveDict):
            moveStruct1 = list(moveList[index1][1].values())
            moveData = list(moveStruct1[0].values())
            moveTable = list(moveStruct1[1].values())
        
            moveDataPointers.append(wr.pos())
            #--Actual Move Data--
            for index2, (key, value) in enumerate(moveDataDictI):
                if (value == 32):
                    wr.write_uint32(moveData[index2])
                elif (value == 16):
                    wr.write_uint16(moveData[index2])
                elif (value == 8):
                    wr.write_uint8(moveData[index2])
                elif (value == 1): #MEP Table
                    if (moveData[index2] == ""):
                        wr.write_int32(-1)
                    else:
                        mepIndex = int(mepName[moveData[index2]])
                        print(mepIndex)
                        wr.write_int32(mepIndex)
                elif (value == 2): #GMT Table
                    if (moveData[index2] == ""):
                        wr.write_int32(-1)
                    else:
                        gmtIndex = int(gmtName[moveData[index2]])
                        print(gmtIndex)
                        wr.write_int32(gmtIndex)
            #--Table Move Data--
            moveBlocksProperty = wr.pos() #Start of the properties table
            wr.write_uint16(moveTable[0]) #Table Unk
            numOfProperties = moveTable[1]
            wr.write_uint16(numOfProperties)
            propertiesPointer = []
            propertyIDType = []

        if propertyPath.endswith('folder'): #Cuts folder out of file_path
            new_path = propertyPath[:-11]
        with open(new_path+" new.bin", 'wb') as f:
            f.write(wr.buffer())
        print("My program took", time.time() - start_time, "to run")
