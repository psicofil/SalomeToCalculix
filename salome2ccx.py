# -*- coding: utf-8 -*-


"""
    © Gomez Lucio, April 2016 - original code
    © Ihor Mirzov, August 2019 - refactoring and improvements
    Distributed under GNU General Public License v3.0

    Exports Salome mesh to Calculix INP format.
    Run from Salome Mesh module with File->Load Script... (Ctrl+T)
"""


import os, sys, subprocess, tempfile, inspect, shutil
import salome, SMESH, SALOMEDS
from salome.smesh import smeshBuilder
from platform import system
try:
    from PyQt4 import QtGui, QtCore, uic
    from PyQt4.QtGui import *
    from PyQt4.QtCore import *
except:
    from PyQt5 import QtCore, QtGui, uic
    from PyQt5.QtWidgets import *


# Path to CGX binary (exapmle for Linux)
cgx_bin = '/usr/local/bin/cgx'


class Dialog(QDialog):


    def __init__(self):
        current_script = inspect.getfile(inspect.currentframe()) # full path to this script
        self.script_dir = os.path.dirname(current_script) # path to directory with this script 

        # Create dialog window
        super(Dialog, self).__init__()

        # Load form for GUI
        gui_form_file = os.path.join(self.script_dir, 'salome2ccx.ui')
        uic.loadUi(gui_form_file, self)

        self.meshes = []

        # Actions
        self.pb_sel_mesh.clicked.connect(self.select_meshes)
        self.pb_output_folder.clicked.connect(self.output_folder)
        self.okbox.button(QDialogButtonBox.Reset).clicked.connect(self.reset)
        self.okbox.rejected.connect(lambda: self.reject()) # close window
        self.okbox.accepted.connect(self.convert)


    # Clear selected mesh list
    def reset(self):
        self.le_selectMesh.setText('')
        self.meshes = []
        self.le_output_folder.setText('')


    # Select folder to put conversion results to
    def output_folder(self):
        INP_dir = QFileDialog.getExistingDirectory(self,
                        'Select output folder', self.script_dir,
                        QFileDialog.ShowDirsOnly)
        self.le_output_folder.setText(INP_dir)


    # Open CGX to view conversion result
    def open_CGX(self, inp_full_path):
        try:
            command_cgx = cgx_bin + ' -c ' + inp_full_path
            QtCore.QProcess().startDetached(command_cgx)
        except:
            QMessageBox.critical(None,
                'Abort!',
                'Can\'t open result with CGX.',
                QMessageBox.Abort)


    #  Perform conversion
    def convert(self):
        success = True

        #  If meshes are chosen
        if len(self.meshes):

            # Chosen output folder 
            output_folder = self.le_output_folder.text()
            if os.path.isdir(output_folder):

                # Path to chosen converter's binary
                extension = ('.exe' if os.name=='nt' else '') # file extension in OS
                binary = os.path.join(self.script_dir, 'converters',
                    self.converter.currentText() + extension)

                # For each of selected meshes
                for mesh in self.meshes:

                    if self.rb_delet_e_f.isChecked():
                        self.delete_edges_and_faces(mesh)

                    # UNV file name is a mesh name
                    unv_file_name = mesh.GetName() # file name only
                    if unv_file_name.endswith('.unv'):
                        unv_file_name = unv_file_name[:-4]

                    # Export UNV file into TEMP folder: path can't be too long - Salome BUG
                    temp_folder = os.path.dirname(tempfile.mkstemp()[1])
                    unv_full_path = os.path.join(temp_folder, unv_file_name) # file name with path
                    mesh.ExportUNV(unv_full_path + '.unv')

                    try:

                        # Perform conversion
                        if 'unical3' in binary:
                            command = ' '.join([binary, unv_full_path]) # without extension
                            output = subprocess.check_output([command, '-1'],
                                shell=True, stderr=subprocess.STDOUT)
                        else: # unv2ccx
                            command = ' '.join([binary, unv_full_path + '.unv']) # with extension
                            output = subprocess.check_output(command,
                                shell=True, stderr=subprocess.STDOUT)

                        # Move result file from TEMP to output directory
                        inp_full_path = os.path.join(output_folder, unv_file_name) + '.inp'
                        shutil.move(unv_full_path + '.inp', inp_full_path)

                    except:
                        success = False
                        QMessageBox.critical(None,
                            'Error!',
                            'Can\'t convert ' + unv_file_name,
                            QMessageBox.Ok)

                    # Delete temp file
                    os.remove(unv_full_path + '.unv')

                    # For each mesh open CGX to view conversion result
                    if self.rb_cgx.isChecked():
                        self.open_CGX(inp_full_path)

                # Result message box
                if success:
                    QMessageBox.information(None,
                        'Ok!',
                        'Operation successfull!',
                        QMessageBox.Ok)

                    # Exit
                    self.accept()

            else:
                QMessageBox.warning(None,
                    'Warning!',
                    'Please, select output folder!',
                    QMessageBox.Ok)
        else:
            QMessageBox.warning(None,
                'Warning!',
                'Please, select meshes!',
                QMessageBox.Ok)


    # Delete_edges_and_faces from mesh
    # TODO Doesn't work!
    # def delete_edges_and_faces(self, mesh):
    #     Group_1 = mesh.CreateEmptyGroup(SMESH.FACE, 'Group_1' )
    #     nbAdd = Group_1.AddFrom( mesh.GetMesh() )
    #     Group_2 = mesh.CreateEmptyGroup( SMESH.EDGE, 'Group_2' )
    #     nbAdd = Group_2.AddFrom( mesh.GetMesh() )
    #     mesh.RemoveGroupWithContents(Group_1)
    #     mesh.RemoveGroupWithContents(Group_2)


    # Get list of selected meshes
    def select_meshes(self):
        smesh = smeshBuilder.New(salome.myStudy)

        # Get selected meshes
        selCount = salome.sg.SelectedCount() # total number of selected items
        for i in range(selCount):
            selected = salome.sg.getSelected(i)
            selobjID = salome.myStudy.FindObjectID(selected)
            selobj = selobjID.GetObject()
            mName = selobjID.GetName().replace(' ','_')
            try:
                mesh = smesh.Mesh(selobj)
                self.meshes.append(mesh)
                mesh_name = mesh.GetName()
                if not mesh_name in self.le_selectMesh.toPlainText():
                    self.le_selectMesh.append(mesh_name)
            except:
                selCount = 0
                break

        # Wrong selection or nothing selected
        if not selCount:
            QMessageBox.critical(None,
                'Abort!',
                'Please, select meshes in the Object Browser. Only meshes.',
                QMessageBox.Abort)


if __name__ == '__main__':

    if salome.sg.hasDesktop():
        salome.sg.updateObjBrowser(1)

    Dialog().show()
