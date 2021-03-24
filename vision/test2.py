import mainvision
import os

print(mainvision.getDirectory())
mainvision.setDirectory(mainvision.getDirectory() + "/Resources/test_frames")

for filename in os.listdir(mainvision.getDirectory()):
    if filename.endswith(".jpg") or filename.endswith(".png"):
        print("\n")
        print("Next File: " + filename)
        mainvision.initialHSVsetup(filename)
    else:
        continue