
import mainvision
import os




#mainvision.initialHSVsetup("Resources/SoftRobotInitialTest.mp4")


print(mainvision.getDirectory())
mainvision.setDirectory(mainvision.getDirectory() + "/Resources/initialTest")

for filename in os.listdir(mainvision.getDirectory()):
    if filename.endswith(".jpg") or filename.endswith(".png"):
        print("\n")
        print("Next File: " + filename)
        mainvision.initialHSVsetup(filename)
    else:
        continue