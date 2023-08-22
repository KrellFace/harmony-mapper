
class NRTEvent:
    def __init__(self, compound_nro, timestamp, change_fixed_key=False):
        self.compound_nro = compound_nro
        self.timestamp = timestamp
        self.change_fixed_key = change_fixed_key


class NRO:
    def __init__(self, operators):
        self.operators = operators

    def __str__(self):
        s = f"{self.operators[0]},{self.operators[1]},{self.operators[2]}"
        if isinstance(self, ClassicNRO):
            s += f"({self.name})"
        return s

class ClassicNRO(NRO):
    def __init__(self, operators, name, major_or_minor):
        self.operators = operators
        self.name = name
        self.major_or_minor = major_or_minor


class CompoundNRO:
    def __init__(self, nros):
        self.nros = nros

    def __str__(self):
        s = f"{self.nros[0]}"
        operators = [0, 0, 0]
        id_string = ""
        for nro in self.nros:
            for j in range(0, 3):
                operators[j] += nro.operators[j]
            if isinstance(nro, ClassicNRO):
                id_string += nro.name
        if id_string == "":
            id_string = f"{len(self.nros)}"
        return f"{operators[0]},{operators[1]},{operators[2]}({id_string})"


#Just a standard compound NRO with a string tag 
class EmotionalCompoundNRO:
    def __init__(self, nro_letters, emotion):
        self.nro_letters = nro_letters
        self.emotion = emotion


Rmaj_NRO = ClassicNRO([0, 0, 2], "R", "maj")
Rmin_NRO = ClassicNRO([-2, 0, 0], "R", "min")
Pmaj_NRO = ClassicNRO([0, -1, 0], "P", "maj")
Pmin_NRO = ClassicNRO([0, 1, 0], "P", "min")
Lmaj_NRO = ClassicNRO([-1, 0, 0], "L", "maj")
Lmin_NRO = ClassicNRO([0, 0, 1], "L", "min")
Nmaj_NRO = ClassicNRO([0, 1, 1], "N", "maj")
Nmin_NRO = ClassicNRO([-1, -1, 0], "N", "min")
Mmaj_NRO = ClassicNRO([-2, -2, 0], "M", "maj")
Mmin_NRO = ClassicNRO([0, 2, 2], "M", "min")
Smaj_NRO = ClassicNRO([1, 0, 1], "S", "maj")
Smin_NRO = ClassicNRO([-1, 0, -1], "S", "min")


def get_classic_nro_lists():
    maj_nros = []
    min_nros = []
    for nro in classic_nros:
        if nro.major_or_minor == "maj":
            maj_nros.append(nro)
        else:
            min_nros.append(nro)
    return [maj_nros, min_nros]



#Generates all NROs in the form of combinations between -2 and 2, with -2 and 2
#i.e [-2, -2], [-2, -1] etc
def get_all_nros():
    #Moves being just numbers between -2 and 2 inclusive 
    moves = range(-2, 3)
    all_nros = [[]]
    #Loop through 0, 1 & 2
    for rep in range(0, 3):
        new_nros = []
        #So even though all_nros contains only an empty array on the first loop, that still counts as a thing to loop on

        #print(f"All_nros before loop {all_nros}")
        for nro in all_nros:
            for move in moves:
                new_nro = nro.copy()
                new_nro.append(move)
                new_nros.append(new_nro)
        all_nros = new_nros
    nro_objs = []
    for operators in all_nros:
        if operators != [0, 0, 0] and 0 in operators:
            nro_objs.append(NRO(operators))
    return nro_objs


all_nros = get_all_nros()

classic_nros = [Rmaj_NRO, Rmin_NRO, Pmaj_NRO, Pmin_NRO, Lmaj_NRO, Lmin_NRO,
                Nmaj_NRO, Nmin_NRO, Mmaj_NRO, Mmin_NRO, Smaj_NRO, Smin_NRO]

