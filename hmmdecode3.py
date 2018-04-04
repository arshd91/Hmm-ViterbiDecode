import sys
import math
tags = set()
observations = set()
transitionProbs = {}
emissionProbs = {}

def loadModelFile(filepath):
	#
	#	Load data from training corpus (POS-Tagged)
	#	The/DT third/JJ was/VBD being/VBG run/VBN by/IN the/DT head/NN of/IN an/DT investment/NN firm/NN ./.
	#
	#print("Loading model...("+str(filepath)+")\n")
	with open(filepath) as model:
		data = model.read()
	return data

def loadTestData(filepath):
	#
	#	Load data from training corpus (POS-Tagged)
	#	The/DT third/JJ was/VBD being/VBG run/VBN by/IN the/DT head/NN of/IN an/DT investment/NN firm/NN ./.
	#
	with open(filepath) as testData:
		data = testData.read()
	return data

def parseModelParams(modelRaw):
	global tags
	global observations
	lines = modelRaw.strip('').split('\n')
	lines = lines[2:]
	totalTags = int(lines[0])
	tagsList = lines[1:totalTags+1]
	for t in tagsList:
		tags.add(t)
	lines = lines[totalTags+1:]	
	#at '---Observations---'
	lines = lines [1:]
	#print(lines[0])
	totalObservations = int(lines[0])
	obsList = lines[1:totalObservations+1]
	for o in obsList:
		observations.add(o)
	lines = lines[totalObservations+1:]
	
	#at '---Transition Probabilities---'
	lines = lines [1:]
	#print(lines[0])
	transitionProbsCount = int(lines[0])
	transProbsList = lines[1:transitionProbsCount+1]

	for l in transProbsList:
		data = l.split(' ')
		t1 = data[0]
		t2 = data[1]
		p= float(data[2])
		transitionProbs[(t1,t2)] = float(p)
	
	lines = lines[transitionProbsCount+1:]
	#at '---Emisison Probabilities---'	
	lines = lines[1:]
	#print(lines[0])
	emissionProbsCount = int(lines[0])
	emissionProbsList = lines[1:emissionProbsCount+1]
	for l in emissionProbsList:
		data = l.split(' ')
		t1 = data[0]
		o = data[1]
		p = float(data[2])
		emissionProbs[(t1,o)] = float(p)

	lines = lines[emissionProbsCount+1:]
	#for t in transitionProbs.keys():
	#	print(t[0] + ',' + t[1] + '-' + str(transitionProbs[t]) + '\n')
	#print(tags)

	#if len(lines) == 0:
		# print("Successfully loaded hmmmodel...")
		# print("Trasition Probabilities Count:" + str(len(transitionProbs.keys())))
		# print("Emission Probabilities Count:" + str(len(emissionProbs.keys())))
		# print("Total Tags:" + str(len(tags)))
		# print("Total Observations:" + str(len(observations)))

def viterbi(sentence):
	viterbi = {}
	backtrack = {}
	epsilon = 0.000000000001
	obs_seq = sentence.strip().split(' ')
	#print(obs_seq)
	output = ''
	T = len(obs_seq)
	for q in tags:
		timestep = (q,'0')
		curr_trans = ('q0',q)
		curr_emiss = (q,obs_seq[0])
		w = float(emissionProbs.get(curr_emiss,1))
		#print(str(transitionProbs.get(curr_trans,0)))
		if w == 0:
			w = epsilon
			viterbi[timestep] = float('-inf')
		else:
			if (transitionProbs.get(curr_trans,0)==0):
					print(curr_trans)
			viterbi[timestep] = math.log(float(transitionProbs.get(curr_trans)))+math.log(w)
		backtrack[timestep] = 'q0'
	#for k in viterbi:
	#	print(str(viterbi[k]))
	#input('...')	
	for t in range(1,T):
		for q1 in sorted(tags):
			p = float('-inf')
			w_state = ''
			for q2 in sorted(tags):
			#key = q+','+str(t+1)
				#print(prob.get((q2,str(t-1)),1))
				#print(q2)
				#input('...')
				w = float(viterbi.get((q2,str(t-1)))) + math.log(float(transitionProbs.get((q2,q1))))
				if w>p:
					p = w
					w_state = q2
			pp = float(emissionProbs.get((q1,obs_seq[t]),1))
			if pp != 0:
				viterbi[(q1,str(t))] = p + math.log(pp)
			else:
				viterbi[(q1,str(t))] = float('-inf')
			backtrack[(q1,str(t))] = w_state
	#print(prob)
	#print(backtrack)
	opt_p = float('-inf')
	opt_state = ''
	for t in tags:
		#print key
		w = viterbi.get((t,str(T-1)),float('-inf'))
		if w>opt_p:
			opt_p = w
			opt_state = t
	ws = opt_state
	for i in range(T-1,-1,-1):
		ws = backtrack.get((ws,str(i)),())
		opt_state = str(ws) + ' /' + str(opt_state)
		#print(opt_state)
	output += ' '.join(map(lambda a,b:a+b,obs_seq,opt_state.split(' ')[1:]))
    #print states[::-1]
    #output += ' '.join(states[::-1])
	output += '\n'
	return output


def main():
	modelRaw = loadModelFile("hmmmodel.txt")
	parseModelParams(modelRaw)
	result = ''
	testData = loadTestData(sys.argv[1])
	for s in testData.split('\n'):
		#print(s)
		output = viterbi(s)
		result += output
	with open("hmmoutput.txt", "w+") as f:
		f.write(result)
	return

if __name__ == '__main__':
	main()