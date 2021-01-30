# -*- coding: utf-8 -*-
"""
Created on Wed Jun 24 09:17:10 2020

@author: JansenM
"""

#IMPORTANT this is a improved version of "Export ELAN to Textgrid.py". It is intended to automatically convert all eaf. files into usable textgrids in a list of directories. I tried to code this so that we can make adjustments in the ELAN files themselves and just run this code to get new data. Assumptions that should be met for this code to work:
#All Elan Files that you want are in the directories or subdirectories that you provide.
#All Elan Files are identically named to one .wav file
#ALL Elan files have complete annotations (meaning that if tier 1 is annotated, the other tiers are also labeled)
#For each Elan File there is only one .wav file in the same directory.
#A major flaw of the pympi library is that when converting ELAN to TextGrid files it did end the file at the last annotation and not at the end of the ELAN file.
#We will now add a "end" annotation first, which should be located at the end and would be 1 sec long.

import pympi
import os
import shutil
from pydub import AudioSegment

#Some other libraries for working with textgrid/ELAN files, but in the end pympi worked best for our usecase.
#import parselmouth 
#import wave
#import contextlib

DirectoryDocument = "C:\\Users\\JansenM\\Documents\\Database AC 2020 complete\\Scripts for extracting data\\StudentDirectoryList.txt" #this is a list of all the directories from students, numbers seem random but are assignment keys we will use this list to go through the folders we are interested in. We chose to not automatically extract these folders, but to use a short list with folder names since it was only a short list and gives more manual control/can be changed depending on the needs. Another reason to do it this way is because this way we are more aware of choices.

#Here we define a set of lists that will be cleared each time we run the code, and which will be used in different steps along the document.
DirectoryList = [] #This is a list we create for all directories we want to search.
OriginalFileAndRootList = [] #This is a list of input ELAN files and their location we find in each of these directories.
GeneralRootList = [] #This is a list with just the root structure for each file.
GeneralFileNameList = [] #This is a list with just the file names but not the file extenstions. This can be useful later when naming new files.
GeneralRootAndFileList = [] #This is a list with just the file names and paths but not the file extenstions. This can be useful later when naming new files.
AudioFileList = [] #This is a list of audio files that are associated with the ELAN files. A requirement for my code is that the ELAN Files should be named exactly the same as there corresponding audio files (AND NOT THE OTHER WAY AROUND )since we want to prevent ELAN from getting confused when we open ELAN and ELAN searches for corresponding audio files.
AudioFileLengthList = [] #This is a list of the duration of audiofiles in miliseconds, notice that we converted these to integers and removed any length smaller then a milisecond. These were extracted using the AudioFilelist and Pydub. In our case we do not have to be more precise and it is debateable if python without specific math packages does a accurate representation on numbers after miliseconds.
TextGridFileList = [] #This list are the names and locations of the intended output converted textgrids.
File_Extension = ".eaf" #For this script we often choose .eaf since we want to convert and add to these files using the pympi library. However it can be changed especially if we do not wish to convert any ELAN files. #make sure to comment the section out that uses pympi in that case.



#read the file containing the directory names that need to be searched line by line
with open(DirectoryDocument) as f:
    for fn in f:
        DirectoryList.append(fn.strip()) #make sure to strip the whitespace and the newline characters

print(DirectoryList) #test, can be commented out


# searches for all files ending with ".eaf" in the directories (and subdirectories) that we specified in DirectoryList.
for nr in range(0,len(DirectoryList)):
    for root, dirs, files in os.walk("C:\\Users\\JansenM\\Documents\\Database AC 2020 complete\\%s" %(DirectoryList[nr])): #Make sure the root here is correct and adjust it when needed.
        for file in files:
            if file.endswith(File_Extension):
                OriginalFileAndRootList.append(os.path.join(root, file))
                GeneralRootList.append(root)
                GeneralFileNameList.append(file[:-4:])
                GeneralRootAndFileList.append(os.path.join(root, file[:-4:]))

#some checks you can activate, check if length stays the same and if name of files remains similar.
print(OriginalFileAndRootList[1]) 
print(len(OriginalFileAndRootList))
print(GeneralRootList[1]) #Check if all file locations and names make sense.
print(len(GeneralRootList)) #Check this number and make sure it is the same for the other lists, this way we know that we are not losing data during converting.
print(GeneralFileNameList[1]) 
print(len(GeneralFileNameList))
print(GeneralRootAndFileList[1]) 
print(len(GeneralRootAndFileList))

#Here we make some string adjustments and then create the audio and TextGrid file lists. One thing you have to be sure of when using this part of the code is that ELAN files have identical names with wav files. 
#This is convention but not always the case in every database. IMPORTANT: Change the name of the ELAN files and not the other way around if possible. Otherwise you might need to "relocate" audio files when opening the eaf file in ELAN.
for nr in range(0,len(GeneralRootAndFileList)):
    AudioFileList.append(GeneralRootAndFileList[nr]+".wav")
    TextGridFileList.append(GeneralRootAndFileList[nr]+".TextGrid")

#some checks you can activate, check if length stays the same and if name of files remains similar.
print(AudioFileList[1])
print(type(AudioFileList[1]))   
print(len(AudioFileList))
print(TextGridFileList[1])
print(type(TextGridFileList[1]))
print(len(TextGridFileList))

##Calculate duration in miliseconds for each audio file in the list. We use miliseconds since pympi assumes this as normal input.
for nr in range(0,len(AudioFileList)):
    audio = AudioSegment.from_file(AudioFileList[nr])
    AudioFileLengthList.append(int(audio.duration_seconds * 1000))
    
#Here is the final check if all files are still alligned.
print(AudioFileList[3])
print(type(AudioFileList[3]))
print(AudioFileLengthList[3])
print(type(AudioFileLengthList[3])) 
print(len(AudioFileLengthList))       
 
##iterate over each ELAN file and export to PRAAT format
for nr in range(0,len(OriginalFileAndRootList)): # nr stands for a number that is part of the itteraction through a string of filename strings in FileList  
    elanFile = pympi.Elan.Eaf(OriginalFileAndRootList[nr])
    elanFile.add_tier('Start_End', ling='default-lt', parent=None, locale=None, part=None, ann=None, language=None, tier_dict=None)
    elanFile.add_annotation('Start_End', 0, 1000, value='START', svg_ref=None)   # adds a annotation at the start of the file
    elanFile.add_annotation('Start_End', (AudioFileLengthList[nr] - 1000), AudioFileLengthList[nr], value='END', svg_ref=None)   # adds a annotation at the end of the file, IMPORTANT: extending the file here with one second, you can check in your own scenario what would be a better sollution.
    elanFile = elanFile.to_textgrid() #should transform object to TextGrid
    elanFile.to_file(TextGridFileList[nr], codec='utf-8', mode='normal')
   
#Itterate through all the TextGrids and Audio files and copy these to a new location.
for nr in range(0,len(TextGridFileList)): # nr stands for a number that is part of the itteraction through a string of filename strings in FileList  
    shutil.copyfile(AudioFileList[nr], "C:\\Users\\JansenM\\Documents\\Database AC 2020 complete\\Scripts for extracting data\\%s%s" %(GeneralFileNameList[nr], ".wav"))
    shutil.copyfile(TextGridFileList[nr], "C:\\Users\\JansenM\\Documents\\Database AC 2020 complete\\Scripts for extracting data\\%s%s" %(GeneralFileNameList[nr], ".TextGrid"))