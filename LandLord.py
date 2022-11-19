'''
By Draxx182
Credits go to HeartlessSeph for his pointers and code
SutandoTsukai181 for his Binary Reader and
Retraso for some of his base code
'''
#Imports
import math
import json
import sys
import os
import shutil
import time
from pathlib import Path
from collections import defaultdict
from binary_reader import BinaryReader

#Dicts
headerDict = dict()
stringDict = dict()
gmtDict = dict()
mepDict = dict()
pointerDict = dict()
#Reference
moveIDDictNew = {1:"Hitbox Audio(?)",2:"Audio",3:"Follow Up Lock",4:"Control Lock",5:"Hitbox",6:"Pickup(?)",10:"Sync 1 Damage",11:"Invincibility",12:"Bullet Effect",13:"Dropdown(?)",15:"Camera Shake",16:"Controller Shake",18:"Camera",20:"Lock-on",26:"Hyper Armor Control",28:"Charge Attack Property",29:"Heat Control",30:"Heat Gain(?)"}
moveIDDictOld = {1:"Character Audio", 2: "Audio", 3:"Follow Up Lock",4:"Control Lock", 5:"Hitbox",17:"Recovery",18:"Camera Shake",30:"Hyper Armor Control"}
moveTableDict = {"StartFrame":16,"EndFrame":16,"Modifier":8,"Unk 1":8,"Unk 2":8,"Property Type ID":1,"Unk Value":32}
hitboxDictNew = {"Location1":1,"Location2":1,"Hit Effect":16,"Hit Strength":8,"Hit Location":8,"Flags":16,"Damage":8,"Heat":8,"Hit Value":32}
hitboxDictOld = {"Location1":1,"Location2":1,"Flags":116,"Damage":8,"Heat":8}

def tree(): #Makes a tree :troll:
    def the_tree():
        return defaultdict(the_tree)
    return the_tree()

#Tree Dicts
moveDict = tree()
actionDict = tree()

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
    input("Press ENTER to exit... ")
else:
    propertyPath = sys.argv[1]
    if(propertyPath.endswith("string.bin")):
        file = open(propertyPath, 'rb')
        rd = BinaryReader(file.read())
        rd.set_endian(True)
        new_path = Path(propertyPath[:-18])

        #--Important Variables--
        numOfStrings = rd.read_uint16()
        rd.read_uint16()
        pointerToPointers = rd.read_uint32()

        rd.seek(pointerToPointers)
        pointerList = []
        for string in range(numOfStrings):
            pointerList.append(rd.read_uint32())
        for index, pointer in enumerate(pointerList):
            rd.seek(pointer)
            stringDict["String "+str(index)] = rd.read_str()

        export_json(new_path, "dispose_string", stringDict) #Exports dispose_string
        file.close()
    elif (propertyPath.endswith(".cas")):
        file = open(propertyPath, 'rb')
        rd = BinaryReader(file.read())
        rd.set_endian(True)
        new_path = Path(os.path.dirname(propertyPath))
        nameOfFile = os.path.basename(os.path.normpath(propertyPath))
        nameOfFile = nameOfFile[:-4]
        
        #--Header--
        actionDict["FileHeader"]["Magic"] = rd.read_str(4)
        actionDict["FileHeader"]["Endianess"] = rd.read_uint16()
        actionDict["FileHeader"]["Unk1"] = rd.read_uint16()
        actionDict["FileHeader"]["File Version"] = rd.read_uint32()
        actionDict["FileHeader"]["Unk2"] = rd.read_uint32()

        #--Effects Strings--
        effectDict = tree()
        actionDict["Main Table"]
        effectsIncrement = 0
        while True:
            effectsIncrement += 1
            string = rd.read_str()
            effectDict[effectsIncrement]["String"] = string

            fillerByte = rd.read_uint8()
            rd.seek(rd.pos()-1) #Reads next byte to see if it's a CC or Y byte
            if (fillerByte == 255 or fillerByte == 204):
                break

        while True: #Skips all CC or Y bytes
            nullByte = rd.read_uint8()
            rd.seek(rd.pos()-1) #Reads next byte to see if it's a CC or Y byte
            if (nullByte == 255 or nullByte == 204):
                rd.read_uint8()
            else:
                break

        #--Battle Strings--
        battleIncrement = 0
        while True:
            string = rd.read_str()
            actionDict["Battle Table"]["String "+str(battleIncrement)] = string
            battleIncrement += 1
            fillerByte = rd.read_uint8()
            rd.seek(rd.pos()-1) #Reads next byte to see if it's a CC or Y byte
            if (fillerByte == 255 or fillerByte == 204):
                break
        btlNames = list(actionDict["Battle Table"].values())

        while True: #Skips all CC/Y bytes
            nullByte = rd.read_uint8()
            rd.seek(rd.pos()-1) #Reads next byte to see if it's a CC or Y byte
            if (nullByte == 255 or nullByte == 204):
                rd.read_uint8()
            else:
                break
        
        #--Effects Data--
        effectsIncrement = 0
        for effect in effectDict:
            effectsIncrement += 1
            effectDict[effectsIncrement]["Unk"] = rd.read_uint16() 

        #--Move Table--
        moveIncrement = 0
        while True: #Reads all move strings
            moveDict["Move Table"][moveIncrement]["Move String"] = rd.read_str()
            moveIncrement += 1
            fillerByte = rd.read_uint8()
            rd.seek(rd.pos()-1)
            if (fillerByte == 255 or fillerByte == 204):
                break
        while True: #Skips all CC/Y bytes
            nullByte = rd.read_uint8()
            rd.seek(rd.pos()-1)
            if (nullByte == 255 or nullByte == 204):
                rd.read_uint8()
            else:
                break

        moveName = list(moveDict["Move Table"][0].values())
        for move in range(moveIncrement): #Searches through dictionary to point at a certain string
            moveName = list(moveDict["Move Table"][move].values())
            try:
                btlString = rd.read_uint16()
                moveDict["Move Table"][move]["Battle String"] = btlNames[btlString]
            except:
                break
        
        dataIncrement = 0
        for effect in range(len(effectDict)):
            effectString = effectDict[effect+1]["String"]
            effect1Unk = effectDict[effect+1]["Unk"]
            newMoveIncrement = 0
            if (dataIncrement == effect1Unk):
                actionDict["Main Table"][effectString] = None
            while dataIncrement < effect1Unk:
                moveString = moveDict["Move Table"][dataIncrement]["Move String"]
                battleString = moveDict["Move Table"][dataIncrement]["Battle String"]
                actionDict["Main Table"][effectString][newMoveIncrement][battleString] = moveString
                newMoveIncrement += 1
                dataIncrement += 1
        export_json(new_path, nameOfFile, actionDict) #Exports actionset.cas
        file.close()
    elif (propertyPath.endswith(".json")):
        file = open(propertyPath, 'rb')
        actionDict = json.loads(file.read())
        wr = BinaryReader(file.read())
        wr.set_endian(True)

        #--Header--
        actionDict = list(actionDict.values())
        headerDict = list(actionDict[0].values())
        wr.write_str(headerDict[0])
        wr.write_uint16(headerDict[1])
        wr.write_uint16(headerDict[2])
        wr.write_uint32(headerDict[3])
        wr.write_uint32(headerDict[4])

        #--Effects Strings--
        effectDict = list(actionDict[1].keys())
        for item in effectDict:
            wr.write_str(item, null=True)
            '''
            writeEffect = list(item.values())
            for effect in writeEffect:
                wr.write_str(list(effect.values())[0], null=True) #Writes string to bin
            '''
        wr.write_uint8(255) #String table always nulled by 255 byte
        ccByte = wr.pos() % 2
        if (ccByte != 0): #Checks to see if bytes already aligned, else writes CC byte
            for item in range(2-ccByte):
                wr.write_uint8(255)

        #--Battle Strings--
        btlDict = list(actionDict[2].values())
        btlName = dict()
        for index, value in enumerate(btlDict):
            btlName[value] = index
            wr.write_str(value, null=True) #Writes string to bin
        wr.write_uint8(255) #String table always nulled by 255 byte
        ccByte = wr.pos() % 2
        if (ccByte != 0): #Checks to see if bytes already aligned, else writes CC byte
            for item in range(2-ccByte):
                wr.write_uint8(255)
        eDataPointer = wr.pos()

        #--Effects Data Placeholder--
        for value in range(len(effectDict)):
            wr.write_uint16(0)

        #--Move Strings--
        moveDict = list(actionDict[1].values())
        moveSets = list()
        dataIncrement = 0
        for value in moveDict:
            if (value is None):
                moveSets.append(dataIncrement)
                continue
            writeEffect = list(value.values())
            for effect in writeEffect:
                wr.write_str(list(effect.values())[0], null=True) #Writes string to bin
                dataIncrement += 1
            moveSets.append(dataIncrement)
        wr.write_uint8(255) #String table always nulled by 255 byte
        ccByte = wr.pos() % 2
        if (ccByte != 0): #Checks to see if bytes already aligned, else writes FF byte
            for item in range(2-ccByte):
                wr.write_uint8(255)
        mDataPointer = wr.pos()
        wr.seek(eDataPointer)

        
        #--Effects Data--
        effectDict = list(actionDict[1].values())
        for value in moveSets:
            wr.write_uint16(value)
        wr.seek(mDataPointer)

        #--Move Data--
        for value in moveDict:
            if (value is None):
                continue
            valueList = list(value.values())
            for move in valueList:
                btlString = list(move.keys())[0]
                wr.write_uint16(btlName[btlString])

        if propertyPath.endswith('.json'): #Cuts .json out of file_path
            new_path = propertyPath[:-5]
            with open(new_path+" new.cas", 'wb') as f:
                f.write(wr.buffer())
        else:
            with open(propertyPath+".cas", 'wb') as f:
                f.write(wr.buffer())
            new_path = propertyPath
        file.close()
    elif (propertyPath.endswith(".bin")):
        #Asks which game the user is on
        print("Which Property.bin Game are you exporting from?")
        print("Y5/0/K1/FOTNS/Ishin: 0")
        print("Yakuza 3: 1")
        print("Yakuza 4: 2")
        gameType = input("Please enter a valid Game type: ")
        gameTypeInt = int(gameType)
        if gameTypeInt > 2: #Kinda copied this code from Seph, sorry.
            print("An incorrect option was entered. Please restart the program and try again.")
            input("Press ENTER to exit... ")
            sys.exit()

        file = open(propertyPath, 'rb')
        rd = BinaryReader(file.read())
        rd.set_endian(True)
        propertyFolder = write_dir(propertyPath, ' folder')
        direct = write_dir(propertyFolder, '//Table Data')

        #Number of blocks in each table, plus it's starting pointers.
        if (gameTypeInt == 0):
            rd.seek(40, whence=2)
            hitboxDict = hitboxDictNew
            gameTypeString = "Yakuza 5-K1 Old Engine Property.bin"
        elif (gameTypeInt == 1 or gameTypeInt == 2):
            rd.seek(28, whence=2)
            hitboxDict = hitboxDictOld
            gameTypeString = "Yakuza 3/4 Old Engine Property.bin"
        moveBlocks = rd.read_uint32(3) #Num of moveblocks, pointer to name table, pointer to data table
        gmtBlocks = rd.read_uint32(2) #Num of GMT files, pointer to start of GMT table
        mepBlocks = rd.read_uint32(2) #Num of MEP files, pointer to start of MEP table
        if (gameTypeInt == 0):
            unkBlocks = rd.read_uint32(3) #Num of Unk Files, pointer to start of Unk GMT table, pointer to start of Unk blocks
        rd.seek(0)

        #--Header--
        rd.read_bytes(6)
        headerDict["Unk"] = rd.read_uint16()
        headerDict["File Version"] = rd.read_uint32()
        headerDict["Game Type"] = gameTypeString
        export_json(propertyFolder, "PropertyHeader", headerDict) #Yes I have a function to create a json, shush
        rd.read_uint32()
        print("Property Header successfully exported")

        #--String Data--
        stringSet = 0 #Checker to see position
        stringNum = 0 #Incrementing number to name string
        while stringSet < moveBlocks[1]-2:
            try:
                stringNum += 1
                stringDict[stringNum] = rd.read_str()
                stringSet = rd.pos() #Updates string position
            except:
                stringSet = moveBlocks[1]
        export_json(direct, "String Data", stringDict) #Exports GMT Table
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
        if (gameTypeInt == 0):
            moveIDDict = moveIDDictNew
        else:
            moveIDDict = moveIDDictOld
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
                if (gameTypeInt == 0):
                    moveDict[moveName]["Move Data"]["MEP Table ID"] = mepList[mepIndex]
                else: #For some reason the last move block will have an invalid MEP ID
                    try:
                        moveDict[moveName]["Move Data"]["MEP Table ID"] = mepList[mepIndex+1]
                    except:
                        moveDict[moveName]["Move Data"]["MEP Table ID"] = ""
            else:
                moveDict[moveName]["Move Data"]["MEP Table ID"] = ""
            #Pointers, recalculated on repack.
            if (gameTypeInt == 0):
                sizeOfMove = rd.read_uint32() #Size of the structure (Contains main data table)
                rd.read_uint32() #Pointer to move properties start (Not needed for exporting)
                sizeOfMove = int((sizeOfMove - 4)/4) #Makes sure it has the correct amount.
            else: #For Yakuza 3/4 for now.
                rd.read_uint32() #Pointer to move properties start (Not needed for exporting)
                sizeOfMove = rd.read_uint32() #Size of the structure (Contains main data table)
                sizeOfMove = int((sizeOfMove - 16)/2) #Makes sure it has the correct amount.

            if (gameTypeInt == 0):
                gmtCounter = 1
                for tUnk in range(sizeOfMove):
                    stay = rd.pos()
                    unk = rd.read_float()
                    if (19 < len(str(unk)) or math.isnan(unk)): #Checks to see if it's a float or invalid
                        rd.seek(stay)
                        unk = rd.read_int32()
                        if (unk != -1): #Checks if not a number
                            try: #Checks if it's a GMT Table Index
                                if (tUnk == 4):
                                    moveDict[moveName]["Move Data"]["GMT Table ID"] = gmtList[unk]
                                else:
                                    moveDict[moveName]["Move Data"]["Additonal GMT "+str(gmtCounter)] = gmtList[unk]
                                    gmtCounter += 1
                            except: #If not, make it a normal uint
                                rd.seek(stay)
                                unk = rd.read_uint32()
                                moveDict[moveName]["Move Data"]["Unk "+str(tUnk+1)] = unk
                        else: 
                            moveDict[moveName]["Move Data"]["GMT Table ID"] = ""
                    else: #If just a float, write it.
                        moveDict[moveName]["Move Data"]["Unk "+str(tUnk+1)] = unk
            elif (gameTypeInt == 1 or gameTypeInt == 2):
                for tUnk in range(sizeOfMove):
                    if (tUnk == 4): #Checks if GMT Table ID
                        gmtIndex = rd.read_int16()
                        if (gmtIndex != -1):
                            moveDict[moveName]["Move Data"]["GMT Table ID"] = gmtList[gmtIndex]
                        else:
                            moveDict[moveName]["Move Data"]["GMT Table ID"] = ""
                    else: #If not, label as unk
                        moveDict[moveName]["Move Data"]["Unk "+str(tUnk+1)] = rd.read_uint16()

            #Move Properties
            moveBlocksProperty = rd.pos() #Start of the properties table
            if (gameTypeInt == 0):
                moveDict[moveName]["Move Properties"]["Property Unk"] = rd.read_uint16()
                numOfProperties = rd.read_uint16()
            elif (gameTypeInt == 1 or gameTypeInt == 2):
                moveDict[moveName]["Move Properties"]["Filler Property Unk"] = 0
                numOfProperties = rd.read_uint32()
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
                        if (gameTypeInt == 0): #Newer games
                            moveDict[moveName]["Move Properties"]["Properties Table"][id]["Audio"]["Voice Que"] = "0x{:04x}".format(rd.read_int16())[2:]#I stole this from Ret
                            moveDict[moveName]["Move Properties"]["Properties Table"][id]["Audio"]["Sound Container ID"] = rd.read_int16() 
                            for unk in range(8):
                                moveDict[moveName]["Move Properties"]["Properties Table"][id]["Audio"]["Unk "+str(unk)] = rd.read_int16()
                        elif (gameTypeInt == 1):
                            for unk in range(6):
                                moveDict[moveName]["Move Properties"]["Properties Table"][id]["Audio"]["Unk "+str(unk)] = rd.read_int16()
                        elif (gameTypeInt == 2): #Yakuza 4
                            for unk in range(10):
                                moveDict[moveName]["Move Properties"]["Properties Table"][id]["Audio"]["Unk "+str(unk)] = rd.read_int16()
                        rd.seek(propertiesTablePos)
                    elif (propertyIDType == 2): #Audio Property | ID 2
                        rd.seek(propertiesPointer + moveBlocksProperty)
                        if (gameTypeInt == 0): #Newer games/Yakuza 4
                            moveDict[moveName]["Move Properties"]["Properties Table"][id]["Audio"]["Voice Que"] = "0x{:04x}".format(rd.read_int16())[2:]#I stole this from Ret
                            moveDict[moveName]["Move Properties"]["Properties Table"][id]["Audio"]["Sound Container ID"] = rd.read_int16() 
                            for unk in range(8):
                                moveDict[moveName]["Move Properties"]["Properties Table"][id]["Audio"]["Unk "+str(unk)] = rd.read_int16() 
                        elif (gameTypeInt == 1):
                            for unk in range(6):
                                moveDict[moveName]["Move Properties"]["Properties Table"][id]["Audio"]["Unk "+str(unk)] = rd.read_int16()
                        elif (gameTypeInt == 2): #Yakuza 4
                            for unk in range(10):
                                moveDict[moveName]["Move Properties"]["Properties Table"][id]["Audio"]["Unk "+str(unk)] = rd.read_int16()
                        rd.seek(propertiesTablePos)
                    elif (propertyIDType == 5): #Hitbox | ID 5
                        rd.seek(propertiesPointer + moveBlocksProperty)
                        #Guesses which property it is, assigns appropriate location
                        hitboxStr = "Hitbox"
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
                            elif (value == 0):
                                moveDict[moveName]["Move Properties"]["Properties Table"][id][hitboxStr][key] = 1
                            elif (value == 116):
                                moveDict[moveName]["Move Properties"]["Properties Table"][id][hitboxStr][key] = "0x{:04x}".format(rd.read_uint16())[2:]
                        rd.seek(propertiesTablePos)
        export_json(direct, "Move Block Data", moveDict) #Exports Move Table
        print("Move Block Data successfully exported")

        if (gameTypeInt == 0):
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
    else:
        propertyTable = os.path.join(propertyPath +'//Table Data') #Path to table data folder
        #Binary Reader
        wr = BinaryReader()
        wr.set_endian(True)
    
        #--Header--
        headerDict = import_json(propertyPath, "PropertyHeader")
        wr.write_uint32(1128353874)
        wr.write_uint16(513)
        headerDict = list(headerDict.values())
        wr.write_uint16(headerDict[0])
        wr.write_uint32(headerDict[1])
        filesize = wr.pos() #Takes us back to the writer's filesize pos
        wr.write_uint32(0) #Placeholder for filesize

        try:
            if (headerDict[2] == "Yakuza 3/4 Old Engine Property.bin"):
                gameTypeInt = 1
                hitboxDict = hitboxDictOld
            else:
                gameTypeInt = 0
                hitboxDict = hitboxDictNew
        except:
            gameTypeInt = 0
            hitboxDict = hitboxDictNew

        #--String Table--
        stringDict = import_json(propertyTable, "String Data")
        for value in stringDict.values():
            pointerDict[value] = wr.pos() #Switches string to key, then writes adds pointer location
            wr.write_str(value, null=True) #Writes string to bin
        ccByte = wr.pos() % 4
        for item in range(4-ccByte):
            wr.write_uint8(204)
        print("String Data successfully repacked")

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
        print("GMT Block Data successfully repacked")

        #--MEP Table--
        mepDict = import_json(propertyTable, "MEP Block Data")
        mepBlocks = [len(mepDict), wr.pos()] #MEP table size, position at start of MEP table
        mepName = dict()
        for index, value in enumerate(mepDict.values()): #Finds index of mepDict, then writes appropriate pointer.
            mepName[value] = index
            mep = pointerDict[value]
            wr.write_uint32(mep)
        print("MEP Block Data successfully repacked")

        if (gameTypeInt == 0):
            #--Unk Pointer Table--
            unkDict = import_json(propertyTable, "Unk Block Data")
            unkBlocks = [len(unkDict), wr.pos(), 0] #Unk table size, position at start of Unk table
            unkName = list(unkDict.values()) #Gets the names from the Unk Dict
            for value in unkDict.values(): #Finds index of unkDict, then writes appropriate pointer.
                unk = pointerDict[value]
                wr.write_uint32(unk)
            print("Unk Block Data successfully repacked")

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
            print("Unk-Data Blocks successfully repacked")

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
                if (gameTypeInt == 0):
                   wr.write_int32(mepIndex)
                else:
                   wr.write_int32(mepIndex-1)

            if (gameTypeInt == 0):
                sizeOfMove = (len(moveData) - 1) * 4 #Calculates how big a table is from the length of the move data
                wr.write_uint32(sizeOfMove) 
                tilPointer = sizeOfMove + 12 #Pointer will always be 12 more than size of table
                wr.write_uint32(tilPointer)
            elif (gameTypeInt == 1):
                sizeOfMove = (len(moveData) + 6) * 2 #Calculates how big a table is from the length of the move data
                tilPointer = sizeOfMove - 12 #Pointer will always be 12 less than size of table
                wr.write_uint32(tilPointer)
                wr.write_uint32(sizeOfMove) 

            for index2, value in enumerate(moveData[2::]):
                if (gameTypeInt == 0):
                    if (isinstance(value, str)):
                        if (value == ""):
                            wr.write_int32(-1)
                        else:
                            gmtIndex = int(gmtName[value])
                            wr.write_int32(gmtIndex)
                    elif (isinstance(value, int)):
                        wr.write_uint32(value)
                    else:
                        wr.write_float(value)
                elif (gameTypeInt == 1): #Spaghetti code, go fuck yourself
                    if (index2 == 4):
                        if (value == ""):
                            wr.write_int16(-1)
                        else:
                            gmtIndex = int(gmtName[value])
                            wr.write_int16(gmtIndex)
                    else:
                        wr.write_uint16(value)

            #Move Properties
            moveBlocksProperty = wr.pos() #Start of the properties table
            try:
                moveStruct2 = list(moveTable[1].values()) #Dicts inside the properties table
                numOfProperties = len(moveStruct2)
            except:
                numOfProperties = 0
            if (gameTypeInt == 0):
                wr.write_uint16(moveTable[0]) #Table Unk
                wr.write_uint16(numOfProperties) #Number of properties.
            elif (gameTypeInt == 1):
                wr.write_uint32(numOfProperties) #Number of properties.
            propertiesPointer = []
            propertyIDType = []
            if (numOfProperties > 0):
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
                        elif (value == 2):
                            wr.write_uint8(moveProperties[index3])

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
                    if (id == 2 or id == 1): #Audio and Hitbox Audio
                        for index, unk in enumerate(moveIDs):
                            if (gameTypeInt == 0):
                                if (index == 0):
                                    if (unk == "-001"):
                                        wr.write_int16(-1)
                                        continue
                                    hex_str = unk
                                    hex_int = int(hex_str, 16)
                                    wr.write_int16(hex_int)
                                else:
                                    wr.write_int16(unk)
                            else:
                                wr.write_int16(unk)
                        idPosition = wr.pos()
                        wr.seek(propertiesPointer[index4])
                        wr.write_uint32(pointerPosition)
                        wr.seek(idPosition)
                    elif (id == 5): #Hitbox
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
                            elif (value == 0):
                                continue
                            elif (value == 116):
                                hex_str = moveIDs[indexHit]
                                hex_int = int(hex_str, 16)
                                wr.write_uint16(hex_int)
                        idPosition = wr.pos() 
                        wr.seek(propertiesPointer[index4])
                        wr.write_uint32(pointerPosition)
                        wr.seek(idPosition)

        #--Move Data Pointers--
        moveBlocks[2] = wr.pos()
        for pointer in moveDataPointers:
            wr.write_uint32(pointer)
        print("Move Block Data successfully repacked")

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
        if (gameTypeInt == 0):
            #Unk block pointers
            wr.write_uint32(unkBlocks[0])
            wr.write_uint32(unkBlocks[1])
            wr.write_uint32(unkBlocks[2])
        #Filesize
        wr.seek(filesize)
        wr.write_uint32(wr.size())
        print("File successfully repacked")

        if propertyPath.endswith('folder'): #Cuts folder out of file_path
            new_path = propertyPath[:-11]
            with open(new_path+" new.bin", 'wb') as f:
                f.write(wr.buffer())
        else:
            with open(propertyPath+".bin", 'wb') as f:
                f.write(wr.buffer())
            new_path = propertyPath
