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
from pathlib import Path
from collections import OrderedDict
from collections import defaultdict
from binary_reader import BinaryReader

#Dicts
headerDict = OrderedDict()
importDict = OrderedDict()
stringDict = OrderedDict()

def tree(): #Makes a tree :troll:
    def the_tree():
        return defaultdict(the_tree)
    return the_tree()

#Tree Dicts
moveDict = tree()

def make_idstring(id, property): #Returns a string based on the PropertyIDType
    if (id == 1):
        return("Property "+str(property+1)+"| Type ID "+str(id)+" = Unknown Property")
    elif (id == 2):
        return("Property "+str(property+1)+"| Type ID "+str(id)+" = Audio")
    elif (id == 3):
        return("Property "+str(property+1)+"| Type ID "+str(id)+" = Follow Up Lock")
    elif (id == 4):
        return("Property "+str(property+1)+"| Type ID "+str(id)+" = Control Lock")
    elif (id == 5):
        return("Property "+str(property+1)+"| Type ID "+str(id)+" = Hitbox")
    elif (id == 18):
        return("Property "+str(property+1)+"| Type ID "+str(id)+" = Camera")
    else:
        return("Property "+str(property+1)+"| Type ID "+str(id))

def write_dir(file_path, name): #Writes a new directory to another directory
    foldName = os.path.join(str(file_path)+name)
    folder = Path(foldName)
    folder.mkdir(exist_ok=True)
    return(folder)

def export_json(target_path, filename, data): #Writes a json to a certain directory
    jsonFile = json.dumps(data, ensure_ascii=False, indent=2)
    jsonPath = target_path / (filename+ '.json')
    jsonPath.write_text(jsonFile)

def import_json(target_path): #Goes through a directory, then loads json info into OrderedDict
    folder = os.listdir(target_path)
    #Get paths of all the jsons in a directory
    all_json_files = [os.path.join(target_path, f) for f in folder if os.path.isfile(os.path.join(target_path, f)) and f.endswith(".json")]

    #Iterate over json paths to load json data into a dict
    for file_path in all_json_files:
        with open(file_path) as input_file:
            json_array = json.loads(input_file.read(), object_pairs_hook=OrderedDict)
            return(json_array)

def toExport(file_path): #Exports property.bin into directory and according jsons
    file = open(file_path, 'rb')
    rd = BinaryReader(file.read())
    wr = BinaryReader()
    rd.set_endian(True)
    wr.set_endian(True)
    direct = write_dir(propertyFolder, '\\Table Data')

    #Number of blocks in each table, plus it's starting pointers.
    rd.seek(40, whence=2)
    endingOf = rd.pos()
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

    #--Move Blocks--
    moveBlocksName = moveBlocks[1] #Name Table
    moveBlocksData = moveBlocks[2] #Data Table

    #Goes through every move block and makes a json
    for move in range(moveBlocks[0]):
        #Looks for the name of the move, plus pointer
        rd.seek(moveBlocksName)
        moveNamePointer = rd.read_uint32()
        moveBlocksName = rd.pos()
        rd.seek(moveNamePointer)
        moveName = rd.read_str()
        stringDict["String "+str(move)] =  moveName
        
        #Looks for the data of the move, plus pointer
        rd.seek(moveBlocksData)
        moveData = rd.read_uint32()
        moveBlocksData = rd.pos()
        rd.seek(moveData)

        #Goes to the data of move.
        for unk in range(15): #Checks to see the 16 bit data and 8 bit data of a move
            if (unk == 1): 
                moveDict[moveName]["Move Data"]["MEP Table ID"] = rd.read_int32()
            elif (unk == 4):
                moveDict[moveName]["Move Data"]["Unk "+str(unk)+"p1"] = rd.read_uint16()
                moveDict[moveName]["Move Data"]["Unk "+str(unk)+"p2"] = rd.read_uint16()
            elif (unk == 5):
                moveDict[moveName]["Move Data"]["Unk "+str(unk)+" Bitfield"] = rd.read_uint32()
            elif (unk == 8):
                moveDict[moveName]["Move Data"]["GMT Table ID"] = rd.read_int32()
            elif (unk == 11):
                moveDict[moveName]["Move Data"]["Unk "+str(unk)+"p1"] = rd.read_uint16()
                moveDict[moveName]["Move Data"]["Unk "+str(unk)+"p2"] = rd.read_uint16()
            elif (unk == 12):
                moveDict[moveName]["Move Data"]["Ubyte Unk 1"] = rd.read_uint8()
                moveDict[moveName]["Move Data"]["Unk "+str(unk)] = rd.read_uint16()
                moveDict[moveName]["Move Data"]["Ubyte Unk 2"] = rd.read_uint8()
            else:
                moveDict[moveName]["Move Data"]["Unk "+str(unk)] = rd.read_uint32()

        #Move Properties
        moveBlocksProperty = rd.pos() #Start of the properties table
        moveDict[moveName]["Move Properties"]["Property Unk"] = rd.read_uint16()
        numOfProperties = rd.read_uint16()
        moveDict[moveName]["Move Properties"]["Number of Properties"] = numOfProperties
        if (numOfProperties > 0):
            for property in range(numOfProperties): #I know, this is not pretty coding. DM if you have a way to make this bite-sized
                #Will polish things later. Gets Property ID Before scanning, basically.
                pointerStart = rd.pos()
                rd.read_bytes(6)
                rd.read_uint8() #Stupid
                propertyIDType = rd.read_uint8()
                rd.seek(pointerStart)

                id = make_idstring(propertyIDType, property) #Yes, I made a function to give back an ID string

                #Reads the basic data of a property in a move
                moveDict[moveName]["Move Properties"]["Properties Table"][id]["Property Data"]["StartFrame"] = rd.read_uint16()
                moveDict[moveName]["Move Properties"]["Properties Table"][id]["Property Data"]["EndFrame"] = rd.read_uint16()
                moveDict[moveName]["Move Properties"]["Properties Table"][id]["Property Data"]["Modifier"] = rd.read_uint8()
                moveDict[moveName]["Move Properties"]["Properties Table"][id]["Property Data"]["Unk 1"] = rd.read_uint8()
                moveDict[moveName]["Move Properties"]["Properties Table"][id]["Property Data"]["Unk 2"] = rd.read_uint8()

                rd.read_uint8() #Be not afraid
                moveDict[moveName]["Move Properties"]["Properties Table"][id]["Property Data"]["Property Type ID"] = propertyIDType
                moveDict[moveName]["Move Properties"]["Properties Table"][id]["Property Data"]["Unk Value"] = rd.read_uint32()
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
                        moveDict[moveName]["Move Properties"]["Properties Table"][id]["Audio"]["Unk "+str(unk)] = rd.read_uint16() #Is your figure less than greek?
                    rd.seek(propertiesTablePos)
                elif (propertyIDType == 5 or 18): #Hitbox or Camera Property | ID 5 or 18
                    rd.seek(propertiesPointer + moveBlocksProperty)
                    #Guesses which property it is, assigns appropriate location
                    if (propertyIDType == 5):
                        hitboxStr = "Hitbox"
                    else: #dumb.png
                        hitboxStr = "Audio"
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
                else:
                    rd.seek(propertiesTablePos)
    export_json(direct, "Move Block Data", moveDict) #Exports Move Table

    #--GMT Table--
    gmtDict = OrderedDict()
    gmtBlocksTable = gmtBlocks[1]
    #Goes through every GMT block and makes a json
    for gmt in range(gmtBlocks[0]):
        rd.seek(gmtBlocksTable)
        gmtBlocksName = rd.read_uint32() #Gives back the pointer location for the name
        gmtBlocksTable = rd.pos() #Records position of current GMT Block

        rd.seek(gmtBlocksName)
        gmtName = rd.read_str()
        stringDict["String "+str(gmt)] =  gmtName
        gmtDict["GMT Block "+str(gmt)] = gmtName
    export_json(direct, "GMT Block Data", gmtDict) #Exports GMT Table

    #--MEP Table--
    mepDict = OrderedDict()
    mepBlocksTable = mepBlocks[1]
    #Goes through every MEP block and makes a json
    for mep in range(mepBlocks[0]):
        rd.seek(mepBlocksTable)
        mepBlocksName = rd.read_uint32() #Gives back the pointer location for the name
        mepBlocksTable = rd.pos() #Records position of current MEP Block

        rd.seek(mepBlocksName)
        mepName = rd.read_str()
        stringDict["String "+str(mep)] =  mepName
        mepDict["MEP Block "+str(mep)] = mepName
    endOf = rd.pos()
    export_json(direct, "MEP Block Data", mepDict) #Exports MEP Table

    #Random Data idk
    #If you're asking where the Unk and Data table are, screw you im not doing that yet.
    read_til_end = endingOf - endOf
    reading = rd.read_bytes(read_til_end)
    writing = wr.write_bytes(reading)
    with open(str(direct)+"\\Unknown Data.bin", "w") as f:
        f.write(str(wr.buffer()))

    #--String Table--
    inverse_dict = OrderedDict((v,k) for k,v in stringDict.items()) #Inverses dict :troll:
    inversed_dict = OrderedDict((v,k) for k,v in inverse_dict.items()) #Inverses dict again :doubletroll:
    #Basically removes duplicates from string table, it's also retarded that I have to do that.
    export_json(direct, "String Data", inversed_dict) #Exports string table

    file.close() #Closes file path

def toImport(file_path): #Ignore this part for now
    wr = BinaryReader()
    wr.set_endian(True)
    importDict = import_json(file_path)
    importList = list(importDict.values())
    if file_path.endswith('folder'):
        file_path = file_path[:-11]
    propertyBin = os.path.join(file_path + ' new')

    wr.write_uint32(importList[0])
    wr.write_uint16(importList[1])
    wr.write_uint16(importList[2])
    wr.write_uint32(importList[3])
    wr.write_uint32(0)

    with open(propertyBin+".bin", 'wb') as f:
        f.write(wr.buffer())
    
#Checks to make sure argument is set, then either imports a directory or exports property.bin
if (len(sys.argv) <= 1):
    print('Drag and drop property.bin from the motion files to LandLord for it to work.')
else:
    propertyPath = sys.argv[1]
    if (propertyPath.endswith(".bin")):
        propertyFolder = write_dir(propertyPath, ' folder')
        toExport(propertyPath)
    else:
        toImport(propertyPath)