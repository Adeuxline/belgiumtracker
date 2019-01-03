def traiterCR(fichier):
	""" premier traitement de forme afin d'obtenir un fichier "propre" sans lignes blanches """
	
	
	fichier_nouveau = fichier[0:5]
	lines = []

	with open(fichier, "r") as f:
		line = f.readlines()

	for char in line:
			if (char != "\n" and
			char != " \n" and
			char != "\t\n"):
				lines.append(char)

	with open(fichier_nouveau, "a") as f:
			for char in lines:
				f.write(char)
	
	with open(fichier_nouveau, "r") as f:
		chaine = f.readlines()
		
	return chaine

	
def obtenirNumero(vote):
	if vote > 9:
		numero = str(vote)
	else:
		numero = "0" + str(vote)
	return numero

	
def extractionNom(vote, chaine, oui, non, abs):

	titre = "Vote nominatif - Naamstemming: 0" + obtenirNumero(vote)
	i = 0
	
	for ligne in chaine:
		if ligne[0:34] == titre:
			if oui != 0:
				iOui = i+4
			else:
				iOui = i+3
			
			if non != 0:
				iNon = iOui+4
			else:
				iNon = iOui+3
				
			if abs != 0:
				iAbs = iNon+4
			else:
				iAbs = iNon+3
		
			nomOUI = chaine[iOui].split(", ")
			nomNON = chaine[iNon].split(", ")
			nomABS = chaine[iAbs].split(", ")
		i +=1
	
	return nomOUI, nomNON, nomABS
				
def extractionVote(chaine):
	"""¨Passage de la "liste" de ligne en revue pour relever tous les votes. Pour l'instant c'est juste visible avec les prints successifs, l'objectif est évidemment de créer les données proprement à la place. """
	i = 0
	voteTotal = 0
	voteDoublon = 0
	for ligne in chaine:
		if ligne[0:14] == "(Stemming/vote":
			try:
				ligneVote = chaine[i]
				try:
					nbVote = int(ligneVote[15:17])
				except ValueError:
					nbVote = int(ligneVote[15:16])
				ligneOui = chaine[i+2]
				nbOui = int(ligneOui[0:3])
				ligneNon = chaine[i+5]
				nbNon = int(ligneNon[0:3])
				ligneAbs = chaine[i+8]
				nbAbs = int(ligneAbs[0:3])
				lignetotal = chaine[i+11]
				nomOUI, nomNON, nomABS = extractionNom(nbVote, chaine, nbOui, nbNon, nbAbs)	
				nbTotal = int(lignetotal[0:3])
				voteTotal = voteTotal+1
				print("Vote n°", nbVote, "ayant reçu", nbOui, "OUI,", nbNon, "NON et", nbAbs, "abstention, pour un total de", nbTotal, "votes")
				print("Personnes ayant voté POUR : ", nomOUI)
				print("Personnes ayant voté CONTRE : ", nomNON)
				print("Personnes ayant voté ABSTENTION : ", nomABS)
			except ValueError:
				voteDoublon = voteDoublon+1
				print("Vote doublon du précédent.")
		i = i+1

def initif():
	fichier = 'exemple.txt'

	chaine = traiterCR(fichier)
	
	extractionVote(chaine)

initif()