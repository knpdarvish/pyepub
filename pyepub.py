#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Epub Maker - notes: need blank field check!!!"""

import codecs
import unicodedata
import sys,os
import simplejson
import signal
from epub3_utils import *
from PySide import QtCore, QtGui

epubcheck_cmd = 'java -jar ~/Dropbox/epubcheck/epubcheck-3.0b5.jar '

def handleIntSignal(signum,frame):
#    '''Ask app to close if Ctrl+C is pressed.'''
    print "Ctrl+C handling?"
    QtGui.closeAllWindows()

global_cfg = {}
save_config_name = ""


def save_config(fname,g_cfg):
    if (os.path.isfile(fname)):
        print "found ",fname," now overwriting..."
    else:
        print "Creating config file\"",fname,"\""
    s = simplejson.dumps(g_cfg,sort_keys=True, indent= ' ')
    ss = '\n'.join([l.rstrip() for l in  s.splitlines()])
    PTMP = open(fname,"w")
    PTMP.write(ss)
    PTMP.close()

startup_text = """\
Welcome to Epub3 Creator.
this is the file format........
First char of line : Meaning .......
char     Paragraph type
TAB      indent 1st character
TAB+TAB  indent whole paragraph
{...}    Poem
{{..}}   same as poem for now......
u'—'     Poet
\.../    Pic
|..|..|  Table
<[0-9]>  heading type
<c>      Center line
*        Italic line?
+        Page break
†        Footnote
!...}    Farsi Poem
"""


def redir(fname):
    if (os.path.isfile(fname)):
        os.remove(fname)

    #so = open(fname,'w',0)
    #sys.stdout = codecs.getwriter('utf-8')(sys.stdout,'w')
    #os.dup2(so.fileno(), sys.stdout.fileno())
    #os.dup2(so.fileno(), sys.stderr.fileno())

class MainDialog(QtGui.QDialog):
    def __init__(self, parent=None):
        super(MainDialog, self).__init__(parent)

        fileInfo = QtCore.QFileInfo(' ')

        self.tabWidget = QtGui.QTabWidget()
        self.tabWidget.addTab(InfoTab(fileInfo), "Book")
        self.tabWidget.addTab(FileTab(fileInfo), "Files")
        self.tabWidget.addTab(OptionsTab(fileInfo), "Options")
        self.tabWidget.currentChanged.connect(self.tabChanged)
        self.mainLayout = QtGui.QVBoxLayout()

        self.errorMessageDialog = QtGui.QErrorMessage(self)

        pubButton = QtGui.QPushButton(self.tr("&Publish"))
        pubButton.setDefault(True)

        buttonBox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok 
                                           | QtGui.QDialogButtonBox.Cancel)

        buttonBox.addButton(pubButton, QtGui.QDialogButtonBox.ActionRole)

        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        pubButton.clicked.connect(self.publish)

        self.mainLayout.addWidget(self.tabWidget)
        self.mainLayout.addWidget(buttonBox)
        self.setLayout(self.mainLayout)

        self.setWindowTitle("Epub3 Config")

        self.tabValue = 0

    def publish(self):
        print "Trying to create book!"
        cfg_file = global_cfg['config'][2]['input']
	if (os.path.isfile(cfg_file)):
            md_to_xhtml(global_cfg['config'])
            cmd = epubcheck_cmd+global_cfg['config'][2]['output']
            sss = commands.getoutput(cmd)
            print sss
            print "done!"
            self.outputMessage()
        else:
            ms = "Required input file \""+cfg_file+"\" not found, please set correct file!!!"
            self.errorMessageDialog.showMessage(ms)
            

    def outputMessage(self):    
        s = utffile2str('pyepub.log')
        msgBox = QtGui.QMessageBox()
        msgBox.addButton("&OK", QtGui.QMessageBox.AcceptRole)
        msgBox.addButton("&Quit", QtGui.QMessageBox.RejectRole)
        text = "Done!"
        #hack to lengthen box
        spaces = ".........................."
        text += spaces + spaces + spaces
        text += spaces + spaces + spaces
        msgBox.setText(text)
        msgBox.setMinimumWidth(500)
        msgBox.setDetailedText(s)
        if msgBox.exec_() == QtGui.QMessageBox.AcceptRole:
            pass
        else:
            sys.exit(tabdialog.exec_())

    def tabChanged(self): 
        global save_config_name
        global global_cfg
        #print "current index =", self.tabWidget.currentIndex()
        #print "current widget =", self.tabWidget.tabText(self.tabWidget.currentIndex())
        #print global_cfg['config'][self.tabWidget.currentIndex()]
        if (save_config_name == ""): save_config_name = 'pyepub.cfg'
        print "tab changed",
        save_config(save_config_name,global_cfg)
        #if (self.tabWidget.currentIndex() == 1):            print self.tabWidget.currentWidget().cfg
        # Update Global Cfg on tab change (on for infotab right now)
        self.tabWidget.widget(self.tabValue).update()
        #self.tabWidget.currentWidget().refresh()
        self.tabValue = self.tabWidget.currentIndex()

class FileTab(QtGui.QWidget):
    global global_cfg

    def update(self):   pass

    def __init__(self, fileInfo, parent=None):
        super(FileTab, self).__init__(parent)

        frameStyle = QtGui.QFrame.Sunken | QtGui.QFrame.Panel

        self.cfg = global_cfg['config'][2]

        layout = QtGui.QGridLayout()
        layout.setColumnStretch(1, 1)
        layout.setColumnMinimumWidth(1, 250)

        num = 1
        offset = 0
        Wrap = 14

        for k in sorted(self.cfg.iterkeys()):
            s = k + "Label"
            self.s = QtGui.QLabel(k)
            self.s.setFrameStyle(frameStyle)
            sb = k + "Button"
            self.sb = QtGui.QPushButton(k)
            if (k != 'filemap'):
                self.sb.clicked.connect(self.setOpenFileName)
            se = k + "LineEdit"
            self.se = QtGui.QLineEdit()
            self.se.setText(str(self.cfg[k]))
            layout.addWidget(self.sb, num, offset)
            layout.addWidget(self.se, num, offset+1)
            num = num+1
            if (num == Wrap):
                offset = offset + 2
                num = 1


        self.native = QtGui.QCheckBox()
        self.native.setText("Use native file dialog.")
        self.native.setChecked(True)
        if sys.platform not in ("win32", "darwin"):      self.native.hide()
        self.setLayout(layout)
        self.setWindowTitle("Epub3 Config")

    def setOpenFileName(self):    
        #print "sender = ",self.sender(),self.sender().text()
        k = self.sender().text()
        options = QtGui.QFileDialog.Options()
        if not self.native.isChecked():
            options |= QtGui.QFileDialog.DontUseNativeDialog
        fileName, filtr = QtGui.QFileDialog.getOpenFileName(self,"files",self.cfg[k],
#                self.openFileNameLabel.text(),
                "All Files (*);;Text Files (*.txt)", "", options)
        if fileName:
            print "got ",fileName
            self.cfg[k] = fileName
            se = k + "Label"
            self.se.setText(fileName)
            #self.openFileNameLabel.setText(fileName)


class OptionsTab(QtGui.QWidget):
    global global_cfg

    def update(self):   pass

    def box_checked(self,state):
        find_use = re.compile("use_")
        sender = self.sender()
        k = sender.text()
        file_k = find_use.sub("",k)
        has_file = find_use.match(k)
        flist = self.cfg['filemap']
        if (state == QtCore.Qt.Checked):
            #print k, "checked box!!!"
            self.options[k] = "y"
        else:
            #print k, " unchecked box!!!"
            self.options[k] = ""
        if (has_file):
            if (state == QtCore.Qt.Checked):
                if file_k in flist:
                    pass
                    #print file_k, " already in filemap ",flist
                else:
                    flist = self.cfg['filemap']
                    #print "flist = ",flist
                    flist.append(file_k)
                    self.cfg['filemap'] = flist
                    #print "adding ",file_k, " to filemap ",self.cfg['filemap']
            else:
                if file_k in flist:
                    self.cfg['filemap'].remove(file_k)
                    #print "removing ",file_k, " from filemap ",self.cfg['filemap']
                else:
                    pass
                    #print file_k, " not in filemap ",self.cfg['filemap']
        #print self.options

    def line_edited(self,text):
        print "new text",text
        sender = self.sender()
        print type(sender)
        print sender.text()
        #print self.options

    def setenough_lines(self):
        i, ok = QtGui.QInputDialog.getInteger(self, "QInputDialog.getInteger()","Enough Lines:")
        if ok != '':
            self.enough_linesLabel.setText("%d" % i)
            self.options['enough_lines'] =  i
            
    def setlev_toc(self):
        i, ok = QtGui.QInputDialog.getInteger(self, "QInputDialog.getInteger()","Lev Toc:")
        if ok != '':
            self.lev_tocLabel.setText("%d" % i)
            self.options['lev_toc'] =  i
            
    def setlev_break(self):
        i, ok = QtGui.QInputDialog.getInteger(self, "QInputDialog.getInteger()","Lev Break:")
        if ok != '':
            self.lev_breakLabel.setText("%d" % i)
            self.options['lev_break'] =  i
            
    def __init__(self, fileInfo, parent=None):
        super(OptionsTab, self).__init__(parent)

        frameStyle = QtGui.QFrame.Sunken | QtGui.QFrame.Panel

        self.options = global_cfg['config'][1]
        self.cfg     = global_cfg['config'][2]

        layout = QtGui.QGridLayout()
        layout.setColumnStretch(1, 1)
        layout.setColumnMinimumWidth(1, 250)

        num = 1
        offset = 0
        Wrap = 14

        k = "enough_lines"
        self.enough_linesLabel = QtGui.QLabel(k)
        self.enough_linesLabel.setFrameStyle(frameStyle)
        self.enough_linesButton = QtGui.QPushButton(k)
        self.enough_linesButton.clicked.connect(self.setenough_lines)
        self.enough_linesLabel.setText(str(self.options[k]))
        layout.addWidget(self.enough_linesButton, num, offset)
        layout.addWidget(self.enough_linesLabel, num, offset+1)
        num = num+1
        k = "lev_toc"
        self.lev_tocLabel = QtGui.QLabel(k)
        self.lev_tocLabel.setFrameStyle(frameStyle)
        self.lev_tocButton = QtGui.QPushButton(k)
        self.lev_tocButton.clicked.connect(self.setlev_toc)
        self.lev_tocLabel.setText(str(self.options[k]))
        layout.addWidget(self.lev_tocButton, num, offset)
        layout.addWidget(self.lev_tocLabel, num, offset+1)
        num = num+1
        k = "lev_break"
        self.lev_breakLabel = QtGui.QLabel(k)
        self.lev_breakLabel.setFrameStyle(frameStyle)
        self.lev_breakButton = QtGui.QPushButton(k)
        self.lev_breakButton.clicked.connect(self.setlev_break)
        self.lev_breakLabel.setText(str(self.options[k]))
        layout.addWidget(self.lev_breakButton, num, offset)
        layout.addWidget(self.lev_breakLabel, num, offset+1)
        num = num+1
  
        for k in sorted(self.options.iterkeys()):
            try:
                #print k,self.options[k]
                n = int(self.options[k])
            except:
                self.k = QtGui.QCheckBox(k)
                self.setk = k+"_change"
                if (self.options[k] != ""): self.k.setChecked(True)
                layout.addWidget(self.k)
                self.k.stateChanged.connect(self.box_checked)

                

        #self.native = QtGui.QCheckBox()
        #self.native.setText("Use native file dialog.")
        #self.native.setChecked(True)
        #if sys.platform not in ("win32", "darwin"):      self.native.hide()
        self.setLayout(layout)
        self.setWindowTitle("Epub3 Config")

class InfoTab(QtGui.QWidget):
    global global_cfg

    def line_edited(self,text):
        self.update()
    #print "new text",text
    #    sender = self.sender()

    def update(self):
        global global_cfg
        #print "updating global_cfg for Infotab"
        self.attr = global_cfg['config'][0]
        for k in sorted(self.attr.iterkeys()):
            se = k + "LineEdit"
            #print se,' ',self.attr[k],' shown ',self.lines[se].text()
            global_cfg['config'][0][k] = self.lines[se].text()

    def __init__(self, fileInfo, parent=None):
        super(InfoTab, self).__init__(parent)

        frameStyle = QtGui.QFrame.Sunken | QtGui.QFrame.Panel

        self.openFilesPath = ''

        self.attr = global_cfg['config'][0]
        self.options = global_cfg['config'][1]
        self.cfg = global_cfg['config'][2]

        layout = QtGui.QGridLayout()
        layout.setColumnStretch(1, 1)
        layout.setColumnMinimumWidth(1, 250)


        num = 1
        offset = 0
        Wrap = 14
        #for k in sorted(self.attr, key=self.attr.get):
        self.lines = {}
        for k in sorted(self.attr.iterkeys()):
            #print "k = ",k," v = ",self.attr[k]
            s = k + "Label"
            self.s = QtGui.QLabel(k)
            se = k + "LineEdit"
            self.lines[se] = QtGui.QLineEdit()
            self.lines[se].setText(self.attr[k])
            self.lines[se].textChanged.connect(self.line_edited)
            #print self.lines[se].text()
            layout.addWidget(self.s, num, offset)
            layout.addWidget(self.lines[se], num, offset+1)
            num = num+1
            if (num == Wrap):
                offset = offset + 2
                num = 1

        #self.errorMessageDialog = QtGui.QErrorMessage(self)

        self.native = QtGui.QCheckBox()
        self.native.setText("Use native file dialog.")
        self.native.setChecked(True)
        if sys.platform not in ("win32", "darwin"):
            self.native.hide()

            
        self.setLayout(layout)
        self.setWindowTitle("Epub3 Creator")

    def setText(self):
        text, ok = QtGui.QInputDialog.getText(self, "Title",
                "User name:", QtGui.QLineEdit.Normal,
                QtCore.QDir.home().dirName())
        if ok and text != '':
            self.textLabel.setText(text)

    def setExistingDirectory(self):    
        options = QtGui.QFileDialog.DontResolveSymlinks | QtGui.QFileDialog.ShowDirsOnly
        directory = QtGui.QFileDialog.getExistingDirectory(self,
                "QFileDialog.getExistingDirectory()",
                self.directoryLabel.text(), options)
        if directory:
            self.directoryLabel.setText(directory)

class StartupTab(QtGui.QDialog):
    global global_cfg

    def update(self):   pass

    def __init__(self, fileInfo, parent=None):
        super(StartupTab, self).__init__(parent)

        frameStyle = QtGui.QFrame.Sunken | QtGui.QFrame.Panel

        self.openFilesPath = ''

        self.openCfgFileNameLabel = QtGui.QLabel()
        self.openCfgFileNameLabel.setFrameStyle(frameStyle)
        self.openCfgFileNameLabel.setText(fileInfo)

        self.openCfgFileNameButton = QtGui.QPushButton("Config File")

        self.openCfgFileNameButton.clicked.connect(self.setOpenCfgFileName)

        layout = QtGui.QGridLayout()
        layout.setColumnStretch(1, 1)
        layout.setColumnMinimumWidth(1, 250)

        num = 1
        layout.addWidget(self.openCfgFileNameButton, num, 0)
        layout.addWidget(self.openCfgFileNameLabel, num, 1)

        num = num+1
        self.InfoLabel = QtGui.QLabel(startup_text)
        self.InfoLabel.setFrameStyle(frameStyle)
        layout.addWidget(self.InfoLabel,num,0,1,2)
        num = num+1


        self.native = QtGui.QCheckBox()
        self.native.setText("Use native file dialog.")
        self.native.setChecked(True)
        if sys.platform not in ("win32", "darwin"):
            self.native.hide()

        buttonBox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject) #sys.exit())

        layout.addWidget(buttonBox)
            
        self.setLayout(layout)
        self.setWindowTitle("Epub3 Creator")

    def setOpenCfgFileName(self):    
        global save_config_name
        global global_cfg
        options = QtGui.QFileDialog.Options()
        if not self.native.isChecked():
            options |= QtGui.QFileDialog.DontUseNativeDialog
        fileName, filtr = QtGui.QFileDialog.getOpenFileName(self,
                "QFileDialog.getOpenFileNames()", self.openFilesPath,
                "Config Files (*.cfg);; All Files (*)", "", options)
        if fileName:
            path = os.path.dirname(fileName)
            if (path != ''):
                print "Changing Current Directory to ",path
                os.chdir(path)
            self.openCfgFileNameLabel.setText(fileName)
            save_config_name = fileName
            global_cfg = read_config(fileName)
            b_name = fname + ".bak"
            save_config(b_name,global_cfg)
            self.accept()

if __name__ == '__main__':
    #signal.signal(signal.SIGINT, handleIntSignal)
    if (len(sys.argv) > 1):
        fname = sys.argv[1]
        g_cfg = read_config(fname)
        b_name = fname + ".bak"
        save_config(b_name,g_cfg)
        path = os.path.dirname(fname)
        if (path != ''): os.chdir(path)
        md_to_xhtml(g_cfg['config'],'pyepub.log')
        s = utffile2str("pyepub.log")
        cmd = epubcheck_cmd+g_cfg['config'][2]['output']
        sss = commands.getoutput(cmd)
        find_error = re.compile("ERROR")
        print_out = False
        if find_error.search(sss): print_out = True
        if (print_out): print s.encode('utf-8')
        print sss
        sys.exit()
    else:
        fname = 'pyepub.cfg'
        global_cfg = read_config(fname)

    app = QtGui.QApplication(fname)

    if (os.path.isfile(fname)):
        iotab = StartupTab(fname)
    else:
        iotab = StartupTab('')

    res = iotab.exec_()


    if (res == 0): ##QtGui.QDialog.rejected):
        print "Exiting"
        sys.exit()
    else:
        redir("pyepub.log")


    tabdialog = MainDialog()
    res = tabdialog.exec_()   
    if (res == 0): ##QtGui.QDialog.rejected):
        print "Exiting without saving"
    else:
        print "Saving config then exiting "
        if (save_config_name == ""):  save_config_name = 'pyepub.cfg'
        save_config(save_config_name,global_cfg)

    sys.exit()
