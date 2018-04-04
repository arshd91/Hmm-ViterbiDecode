import sys
import time

tags = set()
observations = set()

def loadTrainData(filepath):
	#
	#	Load data from training corpus (POS-Tagged)
	#	The/DT third/JJ was/VBD being/VBG run/VBN by/IN the/DT head/NN of/IN an/DT investment/NN firm/NN ./.
	#
	#print("Loading training corpus...("+str(filepath)+")\n")
	with open(filepath) as trainFile:
		data = trainFile.read()
	return data

def prepareData(data):
	#
	#	Prepare corpus for training
	#	Split data into sentences
	#
	sentences = data.strip().split('\n')
	#sentences = ['$STRT#/q0 ' + str(s) + ' $END#/qF' for s in sentences ]
	sentences = ['$STRT#/q0 ' + str(s) + ' $END#/qF' for s in sentences ]
	return sentences

def learnTransitions(sentences):
	#
	#	Learn A, transition matrix from corpus
	#	
	#

	#Initialize dicts for total tag occurence count, tag1-to-tag2 transition
	tagCount = {}
	tagTransitionDict = {}
	global tags
	#Tokenize in words
	for s in sentences:
		#print(s)
		#input('...')
		wordTagPairs = s.split(' ')
		wTP_count = len(wordTagPairs)
		for k in range((wTP_count-1)):
			#print('\t'+ wordTagPairs[k] + ' ' + str(k))
			curr_wT = wordTagPairs[k]
			currTag = curr_wT.rsplit('/',1)[1]
			
			next_wT = wordTagPairs[k+1]
			nextTag = next_wT.rsplit('/',1)[1]

			tags.add(str(currTag))
			tags.add(str(nextTag))	
			tagCount[currTag] = tagCount.get(currTag,0) + 1
			tagTransitionDict[(currTag, nextTag)] = tagTransitionDict.get((currTag,nextTag),0) + 1

	#IF-DEBUG
	#for x in tagCount.keys():
		#print(str(x)+'\n')
	#for x in tagTransitionDict.keys():
	#	print(str(x)+'='+str(tagTransitionDict.get(x))+'\n')
	#print("Total Tags: " + str(len(tagCount.keys())))
	return tagCount,tagTransitionDict

def learnEmissions(sentences):
	#
	#	Learn A, transition matrix from corpus
	#	
	#

	#Initialize dicts for total tag occurence count, tag1-to-tag2 transition
	tagWordEmitDict = {}
	tagCount = {}
	global observations
	#Tokenize in words
	for s in sentences:
		#print(s)
		#input('...')
		wordTagPairs = s.split(' ')
		wTP_count = len(wordTagPairs)
		for k in range(1,wTP_count):
			#print('\t'+ wordTagPairs[k] + ' ' + str(k))
			curr_wT = wordTagPairs[k]
			currWord = curr_wT.rsplit('/',1)[0]
			currTag = curr_wT.rsplit('/',1)[1]

			observations.add(str(currWord))
			tagCount[currTag] = tagCount.get(currTag,0) + 1
			tagWordEmitDict[(currTag, currWord)] = tagWordEmitDict.get((currTag, currWord),0) + 1

	#IF-DEBUG
	#for x in tagWordEmitDict.keys():
		#print(str(x)+'='+str(tagWordEmitDict.get(x))+'/'+str(tagCount.get(x[0]))+'\n')
	return tagCount,tagWordEmitDict

def saveModelParams(tagCountA,transitionDict,tagCountB, tagWordEmitDict):
	ts = time.gmtime()
	model = ''
	model += 'HMM Model File - '+str(time.strftime("%Y-%m-%d %H:%M:%S", ts))
	model += '\n---Tags---\n'
	model += str(len(tags)) + '\n'
	for t in tags:
		model += t+'\n'		
	model = model.strip('\n')
	model += '\n---Observations---\n'
	model += str(len(observations)) + '\n'
	for o in observations:
		model += o +'\n'
	model = model.strip('\n')
	model += '\n---Transition Probablities---\n'
	transProbs = ''
	transProbsCount = 0
	for t in tags:
		denominator = tagCountA['q0']
		if denominator == 0:
			denominator = 1
		numerator = transitionDict.get(('q0',t),0)
		if numerator > 0:	
			transProbs += 'q0 ' + str(t) + ' ' + str(float(numerator/denominator)) + '\n'
			#transProbs += 'q0 ' + str(t) + ' ' + str(float(numerator)) + ' ' + str(denominator) + '\n'
			transProbsCount += 1
	for t1 in tags:
		if not str(t1) == 'q0':
			for t2 in tags:
				denominator = tagCountA.get(t1,0)
				if denominator == 0:
					denominator = 1
				numerator = transitionDict.get((t1,t2),0)
				if numerator > 0:	
					transProbs += str(t1) + ' ' + str(t2) + ' ' + str(float(numerator/denominator)) + '\n'
					#transProbs += str(t1) + ' ' + str(t2) + ' ' + str(float(numerator)) + ' ' + str(denominator) + '\n'	
					transProbsCount += 1
	model += str(transProbsCount) + '\n'
	model += transProbs
	model = model.strip('\n')
	model += '\n--Emission Probablities---\n'
	emissProbs = ''
	emissProbsCount = 0
	for t in tags:
		for o in observations:
			denominator = tagCountB.get(t,0)
			if denominator == 0:
				denominator = 1
			numerator = tagWordEmitDict.get((t,o),0)
			if numerator > 0:	
				emissProbs += str(t) + ' ' + str(o) + ' ' + str(float(tagWordEmitDict.get((t,o),0)/denominator)) + '\n'
				#emissProbs += str(t) + ' ' + str(o) + ' ' + str(float(tagWordEmitDict.get((t,o),0))) + ' ' + str(denominator) + '\n'
				emissProbsCount += 1
	model += str(emissProbsCount) + '\n'
	model += emissProbs
	model = model.strip('\n')
	with open("hmmmodel.txt", "w+") as f:
		f.write(model)

def main():
	trainFilePath = sys.argv[1]
	corpus = loadTrainData(trainFilePath)
	sentences = prepareData(corpus)	
	tagCountA,tagTransitionDict = learnTransitions(sentences)
	tagCountB,tagWordEmitDict = learnEmissions(sentences)
	#Check if both are same.
	#for x in tagCountA.keys():
		#print(str(x) +'-'+ str(tagCountA.get(x,0))+'-'+str(tagCountB.get(x,0)))
	#print(tagCountA.keys())
	saveModelParams(tagCountA,tagTransitionDict,tagCountB,tagWordEmitDict)
	
if __name__ == '__main__':
    main()