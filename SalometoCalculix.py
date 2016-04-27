# -*- coding: utf-8 -*-
# Mesh with Salome and export to Calculix
# Author: Gomez Lucio
# Version: 0.1 (27/04/2016)

#/****************************************************************************
# THIS PROGRAM IS FREE SOFTWARE; YOU CAN REDISTRIBUTE IT AND/OR MODIFY
# IT UNDER THE TERMS OF THE GNU LESSER GENERAL PUBLIC LICENSE 
# AS PUBLISHED BY THE FREE SOFTWARE FOUNDATION; 
#  
# THIS PROGRAM IS DISTRIBUTED IN THE HOPE THAT IT WILL BE USEFUL, BUT
# WITHOUT ANY WARRANTY; WITHOUT EVEN THE IMPLIED WARRANTY OF
# MERCHANTABILITY OR FITNESS FOR A PARTICULAR PURPOSE. SEE THE GNU
# LESSER GENERAL PUBLIC LICENSE FOR MORE DETAILS.
#
# YOU SHOULD HAVE RECEIVED A COPY OF THE GNU GENERAL PUBLIC LICENSE
# ALONG WITH THIS PROGRAM; IF NOT, WRITE TO THE FREE SOFTWARE FOUNDATION, INC,
# 51 Franklin St, Fifth Floor, Boston, MA 02110-1301, USA
#*****************************************************************************/

# CONFIGURATION - EDIT THE FOLLOWING LINE TO MATCH YOUR UNICAL BINARY

unical_bin = '/home/user/unical/unical' # example for Linux
#unical_bin = "C:\\Daten\\unical\\unical.exe" # example for Windows


# Configuration the optional option to poen results in cgx
cgx_bin = '/home/user/Calculix/cgx_2.9 ' # CGX binary exapmle for Linux

# END CONFIGURATION

import salome
import subprocess
import sys
import tempfile
import  SMESH, SALOMEDS
from PyQt4 import QtGui,QtCore
from salome.smesh import smeshBuilder
from platform import system


def findSelectedMeshes():
    meshes=list()
    smesh = smeshBuilder.New(salome.myStudy)
    nrSelected=salome.sg.SelectedCount()
    
    foundMesh=False
    for i in range(nrSelected):
        selected=salome.sg.getSelected(i)
        selobjID=salome.myStudy.FindObjectID(selected)
        selobj=selobjID.GetObject()
        if selobj.__class__ ==SMESH._objref_SMESH_Mesh:
            mName=selobjID.GetName().replace(" ","_")
            foundMesh=True
            mesh=smesh.Mesh(selobj)
            meshes.append(mesh)
    if not foundMesh:
        QtGui.QMessageBox.critical(None,'Error',"You have to select a mesh object and then run this script.",QtGui.QMessageBox.Abort)
        return None
    else:
        return meshes


def proceed():
    meshes=findSelectedMeshes()
    try:
        if not meshes == None:
            for mesh in meshes:
                if not mesh == None:
                    temp_file = tempfile.mkstemp(suffix='.unv')[1]
                    mesh.ExportUNV(temp_file)
        file_inp = le_inp_file.text()            
        command = unical_bin + ' ' + temp_file + ' ' + file_inp
        print command
        output = subprocess.check_output([command, '-1'], shell=True, stderr=subprocess.STDOUT,)
        QtGui.QMessageBox.information(None,'successful result','The mesh has been exported successfully in ' + file_inp,QtGui.QMessageBox.Ok)
    except:
        QtGui.QMessageBox.critical(None,'Error',"Unexpected error in Salome to Calculix Script: {}".format(sys.exc_info()[0]),QtGui.QMessageBox.Abort)    
    if rb_cgx.isChecked():
        open_CGX()
    if rb_delet_e_f.isChecked():
        delete_edges_and_faces_mesh()
    #hide()

def hide():
    dialog.hide()              
    
def meshFile():
    PageName = QtGui.QFileDialog.getSaveFileName(QtGui.qApp.activeWindow(),'Select inp file result ',"Result.inp",filter ="inp (*.inp *.)")
    le_inp_file.setText(str(PageName))
    
def open_CGX():
    command_cgx = cgx_bin + '-c ' + le_inp_file.text()
    try:
        process = QtCore.QProcess()
        process.startDetached('xterm -e ' + command_cgx)
    except:
        QtGui.QMessageBox.critical(None,'Error',"Unexpected error in CGX process to open the result",QtGui.QMessageBox.Abort)
    
def name_mesh():
    meshes=findSelectedMeshes()
    if not meshes == None:
        for mesh in meshes:
            if not mesh == None:
                mName=mesh.GetName()
                le_selectMesh.setText(mName)
                
def delete_edges_and_faces_mesh():
    meshes=findSelectedMeshes()
    if not meshes == None:
        for mesh in meshes:
            if not mesh == None:
                Group_1 = mesh.CreateEmptyGroup(SMESH.FACE, 'Group_1' )
                nbAdd = Group_1.AddFrom( mesh.GetMesh() )
                Group_2 = mesh.CreateEmptyGroup( SMESH.EDGE, 'Group_2' )
                nbAdd = Group_2.AddFrom( mesh.GetMesh() )
                mesh.RemoveGroupWithContents(Group_1)
                mesh.RemoveGroupWithContents(Group_2)


if salome.sg.hasDesktop():
  salome.sg.updateObjBrowser(1)
   
    
##### GUI APLIACTION #####
dialog = QtGui.QDialog()
dialog.resize(600,200)
dialog.setWindowTitle("Salome to Calculix")
layout = QtGui.QGridLayout(dialog)
l_inp_file   = QtGui.QLabel("inp file result:")
le_inp_file   = QtGui.QLineEdit()
pb_inp_file = QtGui.QPushButton()
pb_inp_file.setText("inp file result")
l_selectMesh = QtGui.QLabel("Selected Mesh:")
le_selectMesh = QtGui.QLineEdit()
le_selectMesh.setEnabled(False)
pb_sel_mesh = QtGui.QPushButton()
pb_sel_mesh.setText("Select Mesh")
name_mesh()
            
okbox = QtGui.QDialogButtonBox(dialog)
okbox.setOrientation(QtCore.Qt.Horizontal)
okbox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
l_options   = QtGui.QLabel("Aditional options:")
rb_cgx = QtGui.QCheckBox("Open the result with CGX at the end")
rb_delet_e_f = QtGui.QCheckBox("Delete delete edges and faces in selected mesh")
rb_cgx.setChecked(False)
layout.addWidget(l_selectMesh,1,0)
layout.addWidget(le_selectMesh,2,0)
layout.addWidget(pb_sel_mesh,2,1)
layout.addWidget(l_inp_file,3,0)
layout.addWidget(le_inp_file,4,0)
layout.addWidget(pb_inp_file,4,1)
layout.addWidget(l_options,5,0)
layout.addWidget(rb_cgx,6,0)
layout.addWidget(rb_delet_e_f,7,0)
layout.addWidget(okbox,8,0)
pb_sel_mesh.clicked.connect(name_mesh)
pb_inp_file.clicked.connect(meshFile)
QtCore.QObject.connect(okbox, QtCore.SIGNAL("accepted()"), proceed)
QtCore.QObject.connect(okbox, QtCore.SIGNAL("rejected()"), hide) 
QtCore.QMetaObject.connectSlotsByName(dialog)
dialog.show()