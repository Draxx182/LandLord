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
moveIDDict = {1:"Hitbox Audio(?)",2:"Audio",3:"Follow Up Lock",4:"Control Lock",5:"Hitbox",6:"Pickup(?)",10:"Sync 1 Damage",11:"Invincibility",12:"Bullet Effect",13:"Dropdown(?)",15:"Camera Shake",16:"Controller Shake",18:"Camera",20:"Lock-on",26:"Hyper Armor Control",28:"Charge Attack Property",29:"Heat Control",30:"Heat Gain(?)"}
moveTableDict = {"StartFrame":16,"EndFrame":16,"Modifier":8,"Unk 1":8,"Unk 2":8,"Property Type ID":1,"Unk Value":32}
hitboxDict = {"Location1":1,"Location2":1,"Unk 1":16,"Unk 2":8,"Unk 3":8,"Flags":16,"Damage":8,"Heat":8,"Unk 4":32}

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
            stringDict[stringNum] = rd.read_str()
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
            moveDict[moveName]["Move Data"]["Unk 0"] = rd.read_uint32()
            mepIndex = rd.read_int32()
            if (mepIndex != -1):
                moveDict[moveName]["Move Data"]["MEP Table ID"] = mepList[mepIndex]
            else:
                moveDict[moveName]["Move Data"]["MEP Table ID"] = ""
            #Pointers, recalculated on repack.
            sizeOfMove = rd.read_uint32() #Size of the structure (Contains main data table)
            rd.read_uint32() #Pointer to move properties start (Not needed for exporting)
            sizeOfMove = int((sizeOfMove - 4)/4) #Makes sure it has the correct amount.

            for tUnk in range(sizeOfMove):
                if (tUnk == 4): #Checks if GMT Table ID
                    gmtIndex = rd.read_int32()
                    if (gmtIndex != -1):
                        moveDict[moveName]["Move Data"]["GMT Table ID"] = gmtList[gmtIndex]
                    else:
                        moveDict[moveName]["Move Data"]["GMT Table ID"] = ""
                else: #If not, label as unk
                    moveDict[moveName]["Move Data"]["Unk "+str(tUnk+1)] = rd.read_uint32()

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
                        id = ("Property "+str(property+1)+"| Type ID "+str(propertyIDType)+" = "+moveIDDictV[idIndex])
                    else:
                        id = ("Property "+str(property+1)+"| Type ID "+str(propertyIDType))

                    #Reads the basic data of a property in a move
                    for key in moveTableDict:
                        value = moveTableDict[key]
                        if (value == 32):
                            moveDict[moveName]["Move Properties"]["Properties Table"][id]["Property Data"][key] = rd.read_uint32()
                        elif (value == 16):
                            moveDict[moveName]["Move Properties"]["Properties Table"][id]["Property Data"][key] = rd.read_uint16()
                        elif (value == 8):
                            moveDict[moveName]["Move Properties"]["Properties Table"][id]["Property Data"][key] = rd.read_uint8()
                        elif (value == 1):
                            rd.read_uint8()
                            moveDict[moveName]["Move Properties"]["Properties Table"][id]["Property Data"][key] = propertyIDType
                    propertiesPointer = rd.read_uint32() #Pointer to where property id tables start at
                    propertiesTablePos = rd.pos()

                    #Checks the PropertyID to see if it's a special ID
                    if (propertyIDType == 1): #Unknown Property | ID 1
                        rd.seek(propertiesPointer + moveBlocksProperty)
                        for unk in range(10):
                            moveDict[moveName]["Move Properties"]["Properties Table"][id]["Unknown Property"]["Unk "+str(unk)] = rd.read_uint16()
                        rd.seek(propertiesTablePos)
                    elif (propertyIDType == 2): #Audio Property | ID 2
                        rd.seek(propertiesPointer + moveBlocksProperty)
                        for unk in range(10):
                            moveDict[moveName]["Move Properties"]["Properties Table"][id]["Audio"]["Unk "+str(unk)] = rd.read_uint16() 
                        rd.seek(propertiesTablePos)
                    elif (propertyIDType == 5 or propertyIDType == 18): #Hitbox or Camera Property | ID 5 or 18
                        rd.seek(propertiesPointer + moveBlocksProperty)
                        #Guesses which property it is, assigns appropriate location
                        if (propertyIDType == 5):
                            hitboxStr = "Hitbox"
                        elif (propertyIDType == 18): #dumb.png
                            hitboxStr = "Camera"
                        for key in hitboxDict:
                            value = hitboxDict[key]
                            if (value == 32):
                                moveDict[moveName]["Move Properties"]["Properties Table"][id][hitboxStr][key] = rd.read_uint32()
                            elif (value == 16):
                                moveDict[moveName]["Move Properties"]["Properties Table"][id][hitboxStr][key] = rd.read_uint16()
                            elif (value == 8):
                                moveDict[moveName]["Move Properties"]["Properties Table"][id][hitboxStr][key] = rd.read_uint8()
                            elif (value == 1): #Hitbox string location
                                moveDict[moveName]["Move Properties"]["Properties Table"][id][hitboxStr][hitboxStr+key] = rd.read_uint16()
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
        tableList = []
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
            rd.seek(unknown2)

            rd.seek(locOfU)
            dataDict[str(uDAT)+" Data Block"]["Name"] = dataName
            dataDict[str(uDAT)+" Data Block"]["Number of Tables"] = numOfU
            dataDict[str(uDAT)+" Data Block"]["Unk 1"] = unknown1
            #Loops through unk pointer blocks
            for u in range(numOfU):
                pointOfU = rd.read_uint32() #Pointer to table
                if (u == 0):
                    tableList.append(pointOfU)
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
        wr.write_uint8(204)

        #--Move Name Table--
        moveDict = import_json(propertyTable, "Move Block Data")
        moveBlocks = [len(moveDict), wr.pos(), 0] #Move table size, position of start of name table, placeholder for start of data table
        moveList = list(moveDict.items()) #Puts Dict in a list
        #Searches through every move block
        for key in moveDict:
            move = pointerDict[key]
            wr.write_uint32(move)

        #--GMT Table--
        gmtDict = import_json(propertyTable, "GMT Block Data")
        gmtBlocks = [len(gmtDict), wr.pos()] #GMT table size, position at start of GMT table
        gmtName = dict()
        for index, value in enumerate(gmtDict.values()): #Finds index of gmtDict, then writes appropriate pointer.
            gmtName[value] = index
            gmt = pointerDict[value]
            wr.write_uint32(gmt)

        #--MEP Table--
        mepDict = import_json(propertyTable, "MEP Block Data")
        mepBlocks = [len(mepDict), wr.pos()] #MEP table size, position at start of MEP table
        mepName = dict()
        for index, value in enumerate(mepDict.values()): #Finds index of mepDict, then writes appropriate pointer.
            mepName[value] = index
            mep = pointerDict[value]
            wr.write_uint32(mep)

        #--Unk Pointer Table--
        unkDict = import_json(propertyTable, "Unk Block Data")
        unkBlocks = [len(unkDict), wr.pos(), 0] #Unk table size, position at start of Unk table
        unkName = list(unkDict.values()) #Gets the names from the Unk Dict
        for value in unkDict.values(): #Finds index of unkDict, then writes appropriate pointer.
            unk = pointerDict[value]
            wr.write_uint32(unk)

        #--Unk Data Table--
        dataDict = import_json(propertyTable, "Unk-Data Blocks")
        dataList = list(dataDict.items()) #List of the Data Dict
        dataPointers = [] #Pointer for each data table made
        startTable = []
        namePointers = []
        nameDict = dict()

        for data in range(unkBlocks[0]): #Note: This part of code is REALLY messy since I had to jump around a lot
            dataOfList = list(dataList[data][1].values()) #Data of the ordereddict inside
            numOfTables = dataOfList[1]
            tablePointers = [] #Pointers of data of tables

            #Loops through how many tables there are
            for table in range(numOfTables):
                tableOfData = list(dataOfList[table+3].values()) #Gets data of each table ordereddict

                tableIndex = pointerDict[tableOfData[0]] #Finds index of the table name in pointers
                if (table == 0 and data != 0):
                    tablePointers.append(wr.pos())
                else:
                    tablePointers.append(wr.pos())
                    wr.write_uint32(tableIndex) #Writes Table Name
                    wr.write_uint32(tableOfData[1]) #Writes unk value
            #Writes the pointers of the tables at the end
            pointerToStart = wr.pos()
            for index, point in enumerate(tablePointers):
                if (index == 0 and data != 0):
                    wr.write_uint32(point-8)
                else:
                    wr.write_uint32(point)
            #Write the rest of the data
            dataPointers.append(wr.pos())
            if (data == 0):
                finalPointer1 = wr.pos()
            wr.write_uint32(numOfTables) #Writes number of tables to bin
            wr.write_uint32(pointerToStart) #Writes the start of the unk tables
            if (data == unkBlocks[0]-1): 
                break
            else:
                dataIndex = pointerDict[dataOfList[0]]
            wr.write_uint32(dataIndex) #Writes pointer of the name
            wr.write_uint32(dataOfList[2])

        #--Unk Name Table--
        unkBlocks[2] = wr.pos()
        for name in range(unkBlocks[0]):
            wr.write_uint32(dataPointers[name])

        #--Move Data Table--
        moveDataPointers = []
        for index1, move in enumerate(moveDict):
            moveStruct1 = list(moveList[index1][1].values())
            moveData = list(moveStruct1[0].values())
            moveTable = list(moveStruct1[1].values())
        
            moveDataPointers.append(wr.pos())
            #Move Data, imports from dict.
            wr.write_uint32(moveData[0]) #First unk
            if (moveData[1] == ""):
                wr.write_int32(-1)
            else: #Writes MEP Table ID
                mepIndex = int(mepName[moveData[1]])
                wr.write_int32(mepIndex)

            sizeOfMove = (len(moveData) - 1) * 4 #Calculates how big a table is from the length of the move data
            wr.write_uint32(sizeOfMove) 
            tilPointer = sizeOfMove + 12 #Pointer will always be 12 more than size of table
            wr.write_uint32(tilPointer)

            for index2, value in enumerate(moveData[2::]):
                if (index2 == 4):
                    if (value == ""):
                        wr.write_int32(-1)
                    else:
                        gmtIndex = int(gmtName[value])
                        wr.write_int32(gmtIndex)
                else:
                    wr.write_uint32(value)

            #Move Properties
            moveBlocksProperty = wr.pos() #Start of the properties table
            wr.write_uint16(moveTable[0]) #Table Unk
            numOfProperties = moveTable[1]
            wr.write_uint16(numOfProperties)
            propertiesPointer = []
            propertyIDType = []
            if (numOfProperties > 0):
                moveStruct2 = list(moveTable[2].values()) #Dicts inside the properties table
                for property in range(numOfProperties):
                    moveStruct3 = list(moveStruct2[property].values()) #Every property, including it's data.
                    moveProperties = list(moveStruct3[0].values())

                    for index3, value in enumerate(moveTableDict.values()):
                        if (value == 32):
                            wr.write_uint32(moveProperties[index3])
                        elif (value == 16):
                            wr.write_uint16(moveProperties[index3])
                        elif (value == 8):
                            wr.write_uint8(moveProperties[index3])
                        elif (value == 1): #Property ID Type
                            propertyIDType.append(moveProperties[index3])
                            wr.write_uint8(propertyIDType[property])

                    propertiesPointer.append(wr.pos()) #Where the pointer is
                    wr.write_uint32(0) #Placeholder for the table pointer
                for index4, id in enumerate(propertyIDType):
                    try: #Tests to see if there is a dropdown menu
                        moveStruct3 = list(moveStruct2[index4].values()) #Every property, including it's data.
                        moveIDs = list(moveStruct3[1].values())
                    except: #If not, then skips to next move property.
                        pass
                    pointerStart = wr.pos()
                    pointerPosition = pointerStart - moveBlocksProperty
                    if (id == 1): #Hitbox Audio
                        for unk in moveIDs:
                            wr.write_uint16(unk)
                        idPosition = wr.pos() 
                        wr.seek(propertiesPointer[index4])
                        wr.write_uint32(pointerPosition) #Writes how far the pointer is
                        wr.seek(idPosition)
                    elif (id == 2): #Audio
                        for unk in moveIDs:
                            wr.write_uint16(unk)
                        idPosition = wr.pos()
                        wr.seek(propertiesPointer[index4])
                        wr.write_uint32(pointerPosition)
                        wr.seek(idPosition)
                    elif (id == 5 or id == 18): #Hitbox/Camera
                        for indexHit, key in enumerate(hitboxDict):
                            value = hitboxDict[key]
                            if (value == 32):
                                wr.write_uint32(moveIDs[indexHit])
                            elif (value == 16):
                                wr.write_uint16(moveIDs[indexHit])
                            elif (value == 8):
                                wr.write_uint8(moveIDs[indexHit])
                            elif (value == 1): #Hitboxlocations
                                wr.write_uint16(moveIDs[indexHit])
                        idPosition = wr.pos() 
                        wr.seek(propertiesPointer[index4])
                        wr.write_uint32(pointerPosition)
                        wr.seek(idPosition)

        #--Move Data Pointers--
        moveBlocks[2] = wr.pos()
        for pointer in moveDataPointers:
            wr.write_uint32(pointer)

        #--Final Pointers-- I promise I'll polish this in later revisions
        #Move block pointers
        wr.write_uint32(moveBlocks[0])
        wr.write_uint32(moveBlocks[1])
        wr.write_uint32(moveBlocks[2])
        #Gmt block pointers
        wr.write_uint32(gmtBlocks[0])
        wr.write_uint32(gmtBlocks[1])
        #Mep block pointers
        wr.write_uint32(mepBlocks[0])
        wr.write_uint32(mepBlocks[1])
        #Unk block pointers
        wr.write_uint32(unkBlocks[0])
        wr.write_uint32(unkBlocks[1])
        wr.write_uint32(unkBlocks[2])
        #Filesize
        wr.seek(filesize)
        wr.write_uint32(wr.size())

        if propertyPath.endswith('folder'): #Cuts folder out of file_path
            new_path = propertyPath[:-11]
        with open(new_path+" new.bin", 'wb') as f:
            f.write(wr.buffer())
        print("My program took", time.time() - start_time, "to run")
