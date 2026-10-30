# Deltarune-IRL-Computer-Vision-Script
This script allows users to control the soul in Deltarune battles by moving around inside of a taped out box captured via a webcam. Check out this video to see it in action: https://youtu.be/N6Lds6FhcIY?si=Z6NTTAWfVyBTj50b

The following files are included in this repository:
Main.py: The main script that allows you to control the soul in real life
CameraChecker.py: A script that allows you to click on pixels from your camera feed and view their HSV values. This can be helpful for setting your own detection bounds.
Soul.STL: STL file for the Soul-shaped headband used in the video to aid with detection. I highly recommend using either a colored headband or baseball cap to help with detection.

Before running any files, run the following command in your terminal to install the necessary Python packages: python -m pip install opencv-python numpy dxcam pynput

I am by no means a software engineer and this was definitely vibecoded so try not to make fun of me too much for any mistakes!
Thank you so much for all the support on the video. Feel free to use or modify the code here however you like. I hope you all have as much fun with it as I did!
