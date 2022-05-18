#!/usr/bin/env python
import pyCloudy
import subprocess

def run(command):
	try:
		proc = subprocess.Popen(command, shell=True)
		proc.communicate()    
		print('Done "{0}"'.format(command))
	except:
		pyCloudy.log_.warn('Failed to run "{0}"'.format(command), calling = 'make_documentation')
    
if __name__ == '__main__':

    run('git commit -a -m "This is version {}."'.format(pyCloudy.__version__))
    run('git tag -a {0} -m "This is version {0}."'.format(pyCloudy.__version__))
    run('git push --follow-tags')

    
    run('python -m build --no-isolation')
    run('twine upload dist/pyCloudy-{*}'.format(version) 


    run('scp dist/pyCloudy-{0}.tar.gz taranis:public_html/pyCloudy'.format(pyCloudy.__version__))
    run('ssh taranis bin/pyCloudy_updates.py')
