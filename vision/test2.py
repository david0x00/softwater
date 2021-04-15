import MoreMarkers
import os

print(MoreMarkers.getDirectory())
MoreMarkers.setDirectory(MoreMarkers.getDirectory() + "/Resources/initialTest")

for filename in os.listdir(MoreMarkers.getDirectory()):

    if filename.endswith(".jpg") or filename.endswith(".png"):

        print("\n")
        print("Next File: " + filename)
        MoreMarkers.markers(filename)
    else:
        continue


