import argparse
import json
import os.path
import sys
import subprocess

#define some consts
json_file_name="extern.git.json"

git_clean_msg = b'nothing to commit, working directory clean'
git_detached_msg = '(detached from'

json_key_git_repo = "git_repo" # array name of the repositories
json_key_name = "name"  # str : repo name
json_key_path = "path"  # str : path to working directory
json_key_absolutely_path = "absolutely_path"  #int : 0--not a absolutely path, related with the current directory; 1--absolutely path
json_key_repo_url = "repo_url"  #str : git repository URL, for example: "https://github.com/cppformat/cppformat.git"
json_key_rev_hash = "rev_hash" #str : git commite hash,
json_key_ccmd_before_sync = "cmd_before_sync"  # str: some commands running before doing the sync
json_key_ccmd_after_sync = "cmd_after_sync" # str: some commands running after doing the sync
json_key_ccmd_before_update = "cmd_before_update" # str: some commands running before doing the update
json_key_ccmd_after_update = "cmd_after_update" # str: some commands running after doing the pdate

def egm_sync(working_dir, force) : 
	print("Sync the working directory based on the version defined in "+json_file_name)
	json_data = json.load(open(working_dir+json_file_name))
	print("The following repos will be over written :")
	for git_repo in json_data[json_key_git_repo] : 
		if 0==git_repo[json_key_absolutely_path] : 
			repo_path=working_dir+git_repo[json_key_path]
		else : 
			repo_path=git_repo[json_key_path]

		print("\t"+git_repo[json_key_name] + " : " + repo_path)
		if not os.path.isdir(repo_path) : 
			print("Error: <", git_repo[json_key_name], "> has a wrong path : ", repo_path)
			continue
		os.chdir(repo_path)
		git_output = subprocess.check_output(["git", "status"], stderr=subprocess.STDOUT)
		if -1 == git_output.find(git_clean_msg) and not force: 
			print("Error: <", git_repo[json_key_name], "> in path : ", repo_path, " not clean")
			print(git_output)
			continue
		#we do not do git clean so that untrack files will be kept in working directory
		git_output = subprocess.check_output(["git", "reset", "--hard", "HEAD"], stderr=subprocess.STDOUT)
		#find out the branch name
		git_branch = subprocess.check_output(["git", "branch", "--contain", git_repo[json_key_rev_hash]], stderr=subprocess.STDOUT)
		git_branch = git_branch.decode(sys.stdout.encoding)
		git_branch = git_branch.strip('\r\n *')
		if -1 !=git_branch.find(git_detached_msg) : 
			# it is a detached commit, directly check out the commit
			git_output = subprocess.check_output(["git", "checkout", git_repo[json_key_rev_hash]], stderr=subprocess.STDOUT)
		else :
			#this commit belong to a branch, switch to the branch first and reset it to the commit
			git_output = subprocess.check_output(["git", "checkout", git_branch], stderr=subprocess.STDOUT)
			git_output = subprocess.check_output(["git", "reset", "--hard", git_repo[json_key_rev_hash]], stderr=subprocess.STDOUT)

		

def egm_update(working_dir) : 
	print("Update the " + json_file_name +" according to the current version in working directory")


#parse command line arguments
parser = argparse.ArgumentParser(description='A utility to manage extern GIT repository based on a file named extern.git.json in current directory', formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('command', choices=['scan', 'sync'], help="\nscan -- scan the directory defined in extern.git.json file and update the content in the file; \nsync -- sync the working directory with the version defined in the extern.git.json file" )
parser.add_argument('-f', '--force', help="Force the operation even the working directories are not clean", action='store_true')
args=parser.parse_args()

#first of all, make sure we have git installed
rt = subprocess.call(["git", "--version"])
if rt!=0 :
	sys.exit("Error: Can not find GIT command")

os.chdir(os.path.dirname(__file__))
current_dir = os.getcwd() + '/'
print(current_dir)

#check if the extern.git.json file esixt
if not os.path.exists(current_dir + json_file_name) : 
	sys.exit("Error: Can not find file " + json_file_name + " in current directory")

#ok, start to do the real work
egm_sync(current_dir, args.force)

sys.exit("Done !!")
