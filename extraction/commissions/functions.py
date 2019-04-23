
def isFill(objet):
    if (objet != "\n" and
        objet != " \n" and
        objet != " " and
        objet != "\t\n"):
        return True
    else:
        return False

def conca(objet):
    i = 0
    lines = []
    taille = len(objet)
    while i < taille:
        if isFill(objet[i]):
            string = objet[i]
            if i + 1 < taille:
                i = i + 1
                while isFill(objet[i]):
                    string = string + " " + objet[i]
                    if i + 1 < taille:
                        i = i + 1
                    else:
                        break
                lines.append(string)
                del string
            else:
                i = i + 1
        else:
            i = i + 1
    return lines

def create_file(doc, SEANCE):
    with open('commission_'+ SEANCE +'.txt', 'w') as f:
        for i in range(0, len(doc)):
            if isFill(doc[i]):
                data = str(doc[i])
                data = ' '.join(data.split())
                data = data + '\n'
                f.write(data)
