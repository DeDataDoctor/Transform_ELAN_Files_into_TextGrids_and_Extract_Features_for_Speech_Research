#this script will extract basic annotations in long format from every textgrid in a directory
#WARNING: Make sure all the sound files and textgrids have matching names AND are in the same directory. Also no spaces are allowed in the naming format. These are limitations of Praat.

#This part creates a Sound strings list from your directory and and prepares this stringlist for a loop function
Create Strings as file list... Sound DirectoryPathToWavFiles\*.wav #add the path to the directory that contains the wav files you want to extract features from.
selectObject: "Strings Sound"
n_wavs = Get number of strings

#opens all sound files so that I can later use them
for n from 1 to n_wavs
	select Strings Sound
	name_soundfile$ = Get string... 'n'
	Read from file... DirectoryPathToWavFiles\'name_soundfile$' #add the path to the directory that contains the wav files you want to extract features from.
endfor

#this part creates a TextGrid strings list from your directory and and prepares this stringlist for a loop function
Create Strings as file list... TextGrid DirectoryPathToTextGridFiles\*.Textgrid #add the path to the directory that contains the TextGrid files you want to extract features from.
selectObject: "Strings TextGrid"
n_grids = Get number of strings

#this writes the header of the file and starts a new line
writeInfoLine: "textgridfile", tab$, "interval_label_T1", tab$, "interval_label_T2", tab$, "interval_label_T3", tab$, "interval_label_T4", tab$, "interval_start",
... tab$, "interval_end", tab$, 
... "interval_mean_pitch", tab$, "interval_standard_dev_pitch", tab$, "0.05quantile_pitch", tab$, "0.95quantile_pitch", tab$, "voicedness", tab$,
... "interval_mean_intensity", tab$, "interval_standard_dev_intensity", tab$, "0.05quantile_intensity", tab$, "0.95quantile_intensity" 


#start of looping through files and opening them using praat
for i from 1 to n_grids
	select Strings TextGrid
	name_file$ = Get string... 'i'
	Read from file... DirectoryPathToTextGridFiles\'name_file$' #add the path to the directory that contains the TextGrid files you want to extract features from.
	name_object$ = selected$("TextGrid")
	select TextGrid 'name_object$'
	identifier$ = name_object$
	num = Get number of intervals: 1
	#select sound object using the identifier and create a pitch and intensity object
	select Sound 'identifier$'
	To Pitch: 0, 75, 600
	select Sound 'identifier$'
	To Intensity: 100, 0, "yes"

	#This loop itterates through a specific tier that you specified in num and extracts interval information to append this to the file.
	#we reselect the textgrid again for each loop since we select another object in the following if statement
	for m from 1 to num 
		select TextGrid 'name_object$'
		interval_label_T1$ = Get label of interval: 1, m
		interval_label_T2$ = Get label of interval: 2, m
		interval_label_T3$ = Get label of interval: 3, m
		interval_label_T4$ = Get label of interval: 4, m
    		interval_start = Get start time of interval: 1, m
		interval_end = Get end time of interval: 1, m	
		#This if statement catches all the intervals that are equal to your specified labels
		if ((interval_label_T1$ = "laugh") or (interval_label_T1$ = "speech-laugh"))
			#appends all extracted information from textgrid object but does not start a new line, also the fixed function lets you control how many decimals will be in the output.
			appendInfo: name_object$, tab$, interval_label_T1$, tab$, interval_label_T2$, tab$, interval_label_T3$, tab$, interval_label_T4$, tab$, fixed$ (interval_start, 3), tab$, fixed$ (interval_end, 3)
			select TextGrid 'name_object$'
			#select the earlier created pitch object and extract values in the following lined, then append the info
			select Pitch 'identifier$'
			mean_pitch = Get mean: interval_start, interval_end, "Hertz"
			standard_dev_pitch = Get standard deviation: interval_start, interval_end, "Hertz"
			min_pitch = Get quantile: interval_start, interval_end, 0.05, "Hertz"
			max_pitch = Get quantile: interval_start, interval_end, 0.95, "Hertz"
			nr_voicedframes = Count voiced frames
			nr_totalframes = Get number of frames
			voicedness = nr_voicedframes/nr_totalframes
			appendInfo: tab$, fixed$ (mean_pitch, 3), tab$, fixed$ (standard_dev_pitch, 3), tab$, fixed$ (min_pitch, 3), tab$, fixed$ (max_pitch, 3), tab$, fixed$ (voicedness, 3)
			#select the earlier created intensity object and extract values in the following lined, then append the info
			select Intensity 'identifier$'
			mean_intensity = Get mean: interval_start, interval_end, "energy"
			standard_dev_intensity = Get standard deviation: interval_start, interval_end
			min_intensity = Get quantile: interval_start, interval_end, 0.05
			max_intensity = Get quantile: interval_start, interval_end, 0.95
			appendInfo: tab$, fixed$ (mean_intensity, 3), tab$, fixed$ (standard_dev_intensity, 3), tab$, fixed$ (min_intensity, 3), tab$, fixed$ (max_intensity, 3) #the second argument, the integer 3 indicates the number of decimals.
			appendInfo: newline$
		endif
	endfor
	#this line would be useful if you wanted to do some kind of action with every textgrid in your directory and store it in a new directory.
	#Save as text file: "YourPath\'name_file$'"
endfor

#saves the info window output in a txt, this txt is stored in the same directory as this script is stored.
appendFile ("Filename.txt", info$ ())

#clear the info window because otherwise old info might get appended with the new info
clearinfo
