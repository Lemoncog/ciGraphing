import json
import random
import jsonpickle
#{"deletions": 0, "insertions": 0, "revisionHash": "", "author": "", "filesChanged": 0, "date": ""}

def calculateTotalCommits(commits, key):
	total = 0

	for commit in commits:

		count = commit[key]

		##ASSUMING 500+ is a library thats been added##
		##TODO - NEEDS MARKING SPECIALLY##
		if count < 1000:
			total += count

	return total

class CommitAverage:
	def __init__(self, averageInsertions, averageDeletes, averageFilesChanged):
		self.averageInsertions = averageInsertions
		self.averageDeletes = averageDeletes
		self.averageFilesChanged = averageFilesChanged

	def toJSON():
		return self.__dict__

class HoverOn:
	def __init__(self, title, subtitle, description):
		self.title = title
		self.subtitle = subtitle
		self.description = description

	def toJSON(self):
		return self.__dict__

class Circle:
	def __init__(self, y, scl, color):
		self.y = y
		self.scl = scl
		self.color = color

	def toJSON(self):
		return self.__dict__

class GraphPoint:
	def __init__(self, commitNo, author, circle, hoverOn):
		self.commitNo = commitNo
		self.author = author
		self.circle = circle
		self.hoverOn = hoverOn

	def toJSON(self):
		return { "commitNo" : self.commitNo, "circle" : self.circle.toJSON(), "hoverOn" : self.hoverOn.toJSON() }

def expertAverage():
	return CommitAverage(0, 0, 0)

def groupAverage(root):

	commits = root["commits"]

	print "commit.count {}".format(len(commits))

	commitCount = len(commits);
	totalInsertionAmount = calculateTotalCommits(commits, "insertions")
	totalDeleteAmount = calculateTotalCommits(commits, "deletions")
	totalFilesChanged = calculateTotalCommits(commits, "filesChanged")


	averageInsertions = totalInsertionAmount/commitCount;
	averageDeletes = totalDeleteAmount/commitCount;
	averageFilesChanged = totalFilesChanged/commitCount;

	print 'Commit Count: {}, totalInsertionAmount {}, average {}'.format(commitCount, totalInsertionAmount, averageInsertions)
	print 'Commit Count: {}, totalDeleteAmount {}, average {}'.format(commitCount, averageDeletes, averageDeletes)
	print 'Commit Count: {}, totalFilesChanged {}, average {}'.format(commitCount, averageFilesChanged, averageFilesChanged)

	# TODO check time since last commit (commit often, in small chunks)
	# For each commit, create graph data
	return CommitAverage(averageInsertions, averageDeletes, averageFilesChanged)

def findMax(commits):
	max = 0
	isSpike = False

	for commit in commits:
		commitHealth = commit["insertions"] + commit["deletions"] + commit["filesChanged"]

		if commitHealth > 500:
			isSpike = True

		if commitHealth > max and isSpike != True:
			max = commitHealth

	return max

colorMap = { }

def randomHexColor():
	r = lambda: random.randint(0,255)
	return ('#%02X%02X%02X' % (r(),r(),r()))

def colorFor(author):
	hexcolor = colorMap.get(author)

	if hexcolor is None:
		hexcolor = randomHexColor()
		colorMap[author] = hexcolor

	return hexcolor

def buildGraphData(root):

	commits = root["commits"]
	commitNo = 0

	maxCommit = findMax(commits)
	isSpike = False

	graphData = []

	for commit in commits:
		mergedHealth = commit["insertions"] + commit["deletions"] + commit["filesChanged"]
		author = commit["author"]
		date = commit["date"]
		description = commit["message"]

		commitHealth = 1-(float(mergedHealth)/float(maxCommit))# * 10.0
		commitNo+=1

		graphPoint = GraphPoint(commitNo, author, Circle(commitHealth, commitHealth, colorFor(author)), HoverOn(author, date, description))

		print "mergedHealth {} maxCommit {} commit health {}".format(mergedHealth, maxCommit, commitHealth)

		print graphPoint.toJSON()

		graphData.append(graphPoint.toJSON())

		#jsonGraphPoint = jsonpickle.encode(graphPoint)
		#print jsonGraphPoint
	with open('data/graphData.json', 'w') as outfile:
 		json.dump(graphData, outfile)


file=open("data/commitLog.json",'r')

rootJSON = json.load(file)

commitAverages = expertAverage()

buildGraphData(rootJSON);