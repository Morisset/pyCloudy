#!/usr/bin/env python
import pyCloudy
import os
import subprocess

def run(command):
	try:
		proc = subprocess.Popen(command, shell=True)
		proc.communicate()    
		print('Done "{0}"'.format(command))
	except:
		pyCloudy.log_.warn('Failed to run "{0}"'.format(command), calling = 'make_documentation')

def run_doxygen(config_file):
    run("sed 's/PROJECT_NUMBER         = .*/PROJECT_NUMBER         = {1}/1' {0} > {0}.tmp".format(config_file, pyCloudy.__version__))
    run("mv -f {0}.tmp {0}".format(config_file))
    run("doxygen {0}".format(config_file))

def make_latex(dir_, manual_name):
    run("cd {0}; make".format(dir_))
    run("mv -f {0}/refman.pdf {1}".format(dir_, manual_name))

def create_zipfile(upload_dir, zip_name):
    run("cd {0}; zip -r --exclude=*.svn* {1}.zip .".format(upload_dir, zip_name))
    
if __name__ == '__main__':
    run_doxygen('doxygen_config_user.txt')
    create_zipfile('/tmp/pyCloudy_Manual/html', '$HOME/Dropbox/Python/pyCloudy/dist/pyCloudy_{0}_documentation'.format(pyCloudy.__version__))
    run("mv /tmp/pyCloudy_Manual/html pyCloudy/docs")
    #make_latex('/tmp/pyCloudy_Manual/latex/', 'dist/PyCloudy_{0}_documentation.pdf'.format(pyCloudy.__version__))

    #run_doxygen('doxygen_config_devel.txt')
    #create_zipfile('pyCloudy/pyCloudy_Manual_devel/html', '../../../dist/pyCloudy_{0}_documentation_devel'.format(pyCloudy.__version__))
    #make_latex('pyCloudy/pyCloudy_Manual_devel/latex/', 'dist/PyCloudy_{0}_documentation_devel.pdf'.format(pyCloudy.__version__))

    run('git commit -a -m "This is version {}."'.format(pyCloudy.__version__))
    run('git tag -a {0} -m "This is version {0}."'.format(pyCloudy.__version__))
    run('git push --follow-tags')
    run('python setup.py sdist upload')
    run('scp dist/pyCloudy-{0}.tar.gz taranis:public_html/pyCloudy'.format(pyCloudy.__version__))
    run('ssh taranis bin/pyCloudy_updates.py')
