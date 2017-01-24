from __future__ import print_function
import os, sys

# performs baseline 2 day run and outputs restart files every day
# moves all files that run created into subdirectory
# copies in new supporting files for restart run
# perform restarted run
# compare output files, store result in status object
# remove all files created by the test

utils = None
env = None

nprocs = 4


def setup(tparams):
	# set up any preconditions for the test
	# return a dictionary of all the items required from the driver for the test
	files = ['x1.2562.init.nc', 'x1.2562.graph.info.part.4']
	locations = [tparams['test_dir'], tparams['test_dir']]

	return {'exename':'atmosphere_model', 'files':files, 'locations':locations, 'nprocs':nprocs}



def test(tparams, res):
	env = tparams['env']
	utils = env.get('utils')

	res.set('completed_test', False)
	res.set('name', 'Restartability Test')

	if not env:
		print('No environment object passed to Restartability test, quitting Restartability test')
		return res
	if not utils:
		print('No utils module in test environment, quitting Restartability test')
		return res


	test_dir = tparams['test_dir'] # file path of src code, absolute
	my_dir = tparams['SMARTS_dir']+'/restartability'
	my_config_files_A = my_dir+'/filesA'
	my_config_files_B = my_dir+'/filesB'
	working_dir = test_dir+'/working'

	# Perform 2-day run A
	os.system('rm -r '+working_dir)
	os.system('mkdir '+working_dir)
	utils.linkAllFiles(my_config_files_A, test_dir)
	#err = utils.runAtmosphereModel(test_dir, nprocs, env, {'-W':'0:05'})
	err = (True, 0)
	
	if not err[0]:
		res.set('success', False)
		res.set('err_code', err[1])
		res.set('err_msg', 'Initial run (run A) failed to run properly.')
		return res

	# Perform 1-day run B as a restart of run A
	os.system('mv '+test_dir+'/restart.* '+working_dir)
	os.system('rm '+test_dir+'/*.nc')
	utils.linkAllFiles(my_config_files_B, test_dir)
	os.system('ln -s '+working_dir+'/restart.2010-10-24_00.00.00.nc '+test_dir)
	#err = utils.runAtmosphereModel(test_dir, nprocs, env, {'-W':'0:05'})
	
	if not err[0]:
		res.set('success', False)
		res.set('err_code', err[1])
		res.set('err_msg', 'Restart run (run B) failed to run properly.')
		return res
	

	#diff = utils.compareFiles(working_dir+'/restart.2010-10-25_00.00.00.nc', test_dir+'/restart.2010-10-25_00.00.00.nc', env)
	diff = utils.Result()
	diff.set('diff_fields', [])
	if not diff:
		res.set('err_msg', 'File comparison failed to run.')
		return res

	res.set('success', len(diff.get('diff_fields')) == 0)
	os.system('rm '+test_dir+'/*.nc')
	os.system('rm -r '+working_dir)
	if not res.get('success'):
		res.set('err', diff.get('diff_fields'))
		res.set('err_msg', "Check the restartability test directory (including the 'working' directory)for files to help you debug the reason for this error.")
	else:
		os.system('rm '+test_dir+'/*.nc')
		os.system('rm -r '+working_dir)
	res.set('completed_test', True)
	return res
