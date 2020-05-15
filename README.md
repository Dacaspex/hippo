# text-generator
Text generator based on samples with a given probability

# Usage
The program takes two arguments: the location of the task file, and the root directory of the audio
files.
```
python generate.py /path/to/task_file.json /path/to/audio_files
```

# Installation instructions
This section contains the installation instructions in order to run the program. I assume that 
you have Python (version 3 or higher) and pip installed. 

## ffmpeg
If you are working with non-`.wav` files (such as `.mp3`), you need to install additional tools, 
such as [ffmpeg](https://www.ffmpeg.org/). Check the [documentation of Pydub](https://github.com/jiaaro/pydub#dependencies) 
for more information.

### Windows
Make sure that ffmpeg is installed and that it is added to your PATH system environment variable. 
You can find a guide to install it on Windows [here](http://blog.gregzaal.com/how-to-install-ffmpeg-on-windows/).

**Note:** Sometimes a reboot of your system is required.  

## Dependencies
Upon up a python virtual environment and install the packages with the following command:
```
pip install -r requirements.txt
```
