# salomeToCalculix

A python script that outputs a Salome mesh to Calculix using unical converter for Bernhardi, Aug 2011

To run: 
* First configure the unical binary in the configuration line inside of salomeToCalculix.py
* You can get the binary code unical compiling the source as indicated in the instructions on unical1_b.c which it is a modified version of unical2 provided by rafal brzegowy

To compile whit gcc:

gcc -o2 -static -o unical unical1_b.c

* Then select the mesh you wish to export and go to file->load script and run salomeToCalculix.py
* Read unical c code for more information

# Optional

* You can configure CGX binary location inside of salomeToCalculix.py and launch cgx after the mesh convert

# Previews

Nodes and Faces:

![ScreenShot](SalomeToCalculix2.png)


Elements:

![ScreenShot](SalomeToCalculix3.png)


# Videos
Old Youtube Video version: https://www.youtube.com/watch?v=yxqawAr1H3s

# Know Problems
* No report unical converter shown
* Not work whit multiple meshes

# To Do
* Add a report unical in the gui