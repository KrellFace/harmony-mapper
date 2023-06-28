from music21 import *

for t1, t2, t3 in [[1, 2, 3], [4 - 12, 5, 6], [7 - 12, 8 - 12, 9]]:
    print("Looping baby")
    print(f"{t1},{t2},{t3}")



class test_class:

    def test_func(self):
        num_rnotes = len(self.rhythm.rhythm_notes)
        print(f"Length of undeclared thing: {num_rnotes}")
    

#t = test_class()
#t.test_func()

test_empty = [[]]

for t in test_empty:
    print("Do I run?")


#What does // do

a = 59
b = 10

print(a//b)

bsharp = chord.Chord('B#')
c = chord.Chord('Cb')
print(bsharp)
print(c)
for i in bsharp.notes:
    print(i.pitch.midi)

for j in c.notes:
    print(j.pitch.midi)