GETeditor
=========

GETeditor is a python editor with real-time collaborative editting. There are a number of features including:

* Basic text editing (e.g., open, save, undo, redo, change font size, tab)
* Python code editing (i.e., syntax highlighting, running the file)
* Sharing a file and collaboratively edit the same file
* Permission management


##Requirement

The program requires python 2.7.3 and PySide 1.1.2.

##Installation
Clone the repository and run `python main.py` inside the directory.

##Instruction
The following is the step to start collaborative editting.

1. A host creates/open a file and configure the share setting in the upper right button. The password can be set here.
2. Clients can request for sharing by 'Request' button and type host's IP and port number.
3. The host can see all clients in 'Manage sharing' button. The host needs to create a group and add clients into the group. Then, the host can share the file through 'Share' button and choose the group to share.
