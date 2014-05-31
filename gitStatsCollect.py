#!/usr/bin/python

import commands
import subprocess
import os
import re
import json

class Changes:
	def __init__(self, inserts, deletes, filename):
		self.inserts = 0 if inserts == "-" else int(inserts) 
		self.deletes = 0 if deletes == "-" else int(deletes)
		self.fileName = filename

class Commit:
	def __init__(self):
		self.log = []
		self.hash = ""
		self.author = ""
		self.date = ""
		self.changes = []

	def calculateTotals(self):
		insertTotal = 0;
		deleteTotal = 0;
		fileChanges = len(self.changes)

		for change in self.changes:
			insertTotal += change.inserts
			deleteTotal += change.deletes

		self.insertTotal = insertTotal
		self.deleteTotal = deleteTotal
		self.fileChanges = fileChanges


	def addCommitLog(self, log):
		self.log.append(log)

	def addChange(self, change):
		self.changes.append(change)

	def toJSON(self):
		return { "deletions": self.deleteTotal,
            	 "insertions": self.insertTotal,
            	 "revisionHash": self.hash,
            	  "filesChanged": self.fileChanges,
            	  "author" : self.author,
            	  "date" : self.date,
            	  "message" : '\n '.join(str(x) for x in self.log)
            	 }




gitComamnd = "git log -200 --numstat"

pr = subprocess.Popen( gitComamnd, cwd = os.path.dirname( './' ), shell = True, stdout = subprocess.PIPE, stderr = subprocess.PIPE )
(out, error) = pr.communicate()

print "Error : " + str(error) 
print "out : " + str(out)

output = str(out)

lines = output.split('\n')


inLogLines = False
commit = Commit()

commits = []

for line in lines:
	newCommitMatch = re.match("(commit \\w{40}\\b)", line)

	authorLine = re.match(r"(Author:)", line)
	dateLine = re.match(r"(Date: )", line)
	inCommitLine = re.search(r"([0-9]\t[0-9])|(-	-)", line)

	if newCommitMatch:
		print "newCommit"
		commit.calculateTotals()
		commits.append(commit.toJSON())

		commit = Commit()

		hash = re.split(r'\s+', line)[1]

		commit.hash = hash
	elif inCommitLine:
		print "commitLine"
		inLogLines = False

		splitChanges = re.split(r'\t', line)

		print splitChanges

		changes = Changes(splitChanges[0], splitChanges[1], splitChanges[2])

		commit.addChange(changes)
		commit.addCommitLog(line)

	elif dateLine:
		print "dateLine"
		date = re.split(r'(Date:\s+)', line)[2]

		print date

		commit.date = date
	elif authorLine:
		print "authorLine"

		author = re.split(r'(Author:\s+)', line)[2]

		print author

		commit.author = author
	elif inLogLines:
		print "logLine"

		commit.addCommitLog(line)
	else:
		print "----"

	if dateLine:
		inLogLines = True


#print(commits)

with open('data/commitLog.json', 'w') as outfile:
	json.dump({ 'commits' : commits}, outfile)
