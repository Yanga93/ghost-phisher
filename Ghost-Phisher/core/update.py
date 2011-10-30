import os
import time
import shutil
import thread
import urllib2

from gui import update_ui
from PyQt4 import QtGui,QtCore

class update_class(QtGui.QDialog,update_ui.Ui_Dialog):
    def __init__(self):
        QtGui.QDialog.__init__(self)
        self.setupUi(self)
        self.retranslateUi(self)
        self.current_version = 1.2
        self.new_version = float()

        self.connect(self.upgrade_button,QtCore.SIGNAL("clicked()"),self.update_installer)
        self.connect(self,QtCore.SIGNAL("download failed"),self.update_timeout_message)
        self.connect(self,QtCore.SIGNAL("finished downloading"),self.finished_download)
        self.connect(self,QtCore.SIGNAL('file downloaded'),self.downloading)
        self.connect(self,QtCore.SIGNAL("restart application"),self.restart_application)


    def display_update_version(self):
        self.update_display_label.setText("Version %s Available"%(self.new_version))


    def percentage(self,current,total):
        float_point = float(current)/float(total)
        calculation = int(float_point * 100)
        percent = str(calculation) + '%'
        return(percent)


    def restart_application(self):
        self.progress_label.setText('<font color=red>Please Restart Application</font>')


    def finished_download(self):
        self.progress_label.setText('<font color=green>Finished Downloading</font>')


    def downloading(self):
        self.progress_label.setText('<font color=green>%s Complete</font>'%(self.percentage(self.files_downloaded,self.file_total)))


    def update_timeout_message(self):
        self.progress_label.setText("<font color=red>Network timeout</font>")


    def update_error(self):
        svn_failure_message = str()
        svn_failure = self.svn_access.stderr
        self.svn_failure_message = svn_failure.read()
        if self.svn_failure_message:
            self.progress_label.setText("<font color=red>Update Failed:" + self.svn_failure_message + "</font>")


    def update_installer(self):
        thread.start_new_thread(self.update_launcher,())


    def update_launcher(self):
        ''' Downloads and installs update files
        '''
        self.file_total = int()
        self.files_downloaded = int()

        ghost_directory = os.getcwd()
        forbidden_files = ['Settings','Ghost-Phisher-Database']

        update_directory = '/tmp/Ghost-Phisher/'

        svn_path = 'http://ghost-phisher.googlecode.com/svn/Ghost-Phisher'

        try:
            online_response_check = urllib2.urlopen('http://ghost-phisher.googlecode.com/svn/Ghost-Phisher/UPDATE')
            online_response = online_response_check.read()

            online_files = re.compile('total_files = \d+',re.IGNORECASE)

            for online_file_total in online_response.splitlines():
                if re.match(online_files,online_file_total):
                    self.file_total = int(online_file_total.split()[2])

            if os.path.exists(update_directory):
                shutil.rmtree(update_directory)

            self.svn_access = subprocess.Popen('cd /tmp/ \n svn checkout ' + svn_path,\
                    shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,stdin=subprocess.PIPE)
            svn_update = self.svn_access.stdout
            thread.start_new_thread(self.update_error,())

            while True:
                response = svn_update.readline()
                if len(response) > 0:
                    self.files_downloaded += 1
                    self.emit(QtCore.SIGNAL('file downloaded'))

                if str('revision') in str(response):
                    self.emit(QtCore.SIGNAL("finished downloading"))

                    for old_file in os.listdir(os.getcwd()):
                        if os.path.isfile(os.getcwd() + os.sep + old_file) and old_file not in  forbidden_files:
                            os.remove(os.getcwd() + os.sep + old_file)

                    for old_directory in os.listdir(os.getcwd()):
                        if os.path.isdir(os.getcwd() + os.sep + old_directory) and old_directory not in  forbidden_files:
                            shutil.rmtree(os.getcwd() + os.sep + old_directory)

                    for update_file in os.listdir(update_directory):        # Copy New update files to working directory
                        if os.path.isfile(update_directory + update_file):
                            shutil.copyfile(update_directory + update_file,os.getcwd() + os.sep + update_file)
                        else:
                            shutil.copytree(update_directory + update_file,os.getcwd() + os.sep + update_file)

                    time.sleep(5)
                    self.emit(QtCore.SIGNAL("restart application"))
                    break
                if len(self.svn_failure_message) > 2:
                    self.emit(QtCore.SIGNAL("download failed"))
                    break

        except(urllib2.URLError,urllib2.HTTPError):
            self.emit(QtCore.SIGNAL("download failed"))


    #
    # Update checker Thread
    #
    def update_initializtion_check(self):
        print("called")
        while True:
            try:
                online_response_thread = urllib2.urlopen('http://ghost-phisher.googlecode.com/svn/Ghost-Phisher/UPDATE')
                online_response_string = ''
                online_response = online_response_thread.read()

                online_version = re.compile('version = \d+\.?\d+',re.IGNORECASE)

                for version_iterate in online_response.splitlines():
                    if re.match(online_version,version_iterate):
                        online_response_string += version_iterate

                update_version_number = float(online_response_string.split()[2])

                if float(self.current_version) != update_version_number:
                    self.emit(QtCore.SIGNAL("new update available"))
                    print("here")
                    self.new_version = update_version_number
                    break

                if float(self.current_version) == update_version_number:
                    break

            except Exception:
                time.sleep(9)








