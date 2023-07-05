from music21 import * 
import random
import os
from enum import Enum
import NROs
import mapElites as me
import metricCalculation as metCalc

note_letters = ['A','B','C','D','E','F','G']


run_name = "TestFold"

def generate_random_note(min_octave, max_octave):

    octave = str(random.randint(min_octave, max_octave+1))

    sharp = ''
    if random.random() >0.5:
        sharp = '#'

    letter = note_letters[random.randint(0,len(note_letters)-1)]

    return note.Note(f"{letter}{sharp}{octave}")

def generate_random_trichord(min_octave, max_octave):
    n1 = generate_random_note(min_octave,max_octave)
    n2 = generate_random_note(min_octave,max_octave)
    n3 = generate_random_note(min_octave,max_octave)
    return chord.Chord([n1, n2, n3])



def generate_random_track(min_octave, max_octave, chord_count):

    s = stream.Stream()
    for i in range(chord_count):
        s.append(generate_random_trichord(min_octave, max_octave))

    return s

def chord_seq_to_stream(chord_seq):
    
    s = stream.Stream()
    for chord in chord_seq:
        s.append(chord)
    return s

def save_stream_to_midi(stream, file_path):
    mf = midi.translate.streamToMidiFile(stream)
    mf.open(file_path, 'wb')
    mf.write()
    mf.close()

def get_key_and_confidence_from_stream(s):
    return s.analyze('key')


def convert_music21chord_to_numeric(chord):
    midi_pitch_numbers = []
    for note in chord.notes:
        midi_pitch_numbers.append(note.pitch.midi)
    return midi_pitch_numbers

def get_classic_nro_from_letter_and_mode(letter, mode):
    if letter == 'R' and mode == 'Major':
        return [0, 0, 2]
    elif letter == 'R' and mode == 'Minor':
        return [-2, 0, 0]
    elif letter == 'P' and mode == 'Major':
        return [0, -1, 0]
    elif letter == 'P' and mode == 'Minor':
        return [0, 1, 0]
    elif letter == 'L' and mode == 'Major':
        return [-1, 0, 0]
    elif letter == 'L' and mode == 'Minor':
        return [0, 0, 1]
    elif letter == 'N' and mode == 'Major':
        return [0, 1, 1]
    elif letter == 'N' and mode == 'Minor':
        return [-1, 1, 0]
    elif letter == 'M' and mode == 'Major':
        return [-2, -2, 0]
    elif letter == 'M' and mode == 'Minor':
        return [0, 2, 2]
    elif letter == 'S' and mode == 'Major':
        return [1, 0, 1]
    elif letter == 'S' and mode == 'Minor':
        return [-1, 0, -1]
    else:
        print("Faulty request for NRO made")
        return 


"""
def apply_nro_to_numeric_chord(n_chord, nro):
    notes = []
    for ind, operator in enumerate(nro.operators):
        notes.append(n_chord[ind] + operator)
    #remapped_notes = remap_numeric_chord(notes)
    #print(f"Premapping notes: {chord.Chord(notes)}")
    remapped_notes = map_numeric_chord_to_root(notes)
    #print(f"Root chord notes: {chord.Chord(remapped_notes)}")
    return remapped_notes
"""

def apply_compoundnro_to_chord(input_chord, cnro):
    #notes = n_chord
    succeeded = True
    
    for nro in cnro:
        #print(input_chord)
        nro_shift = None
        if(input_chord.isMajorTriad()):
            nro_shift = get_classic_nro_from_letter_and_mode(nro, 'Major')
        else:
            nro_shift = get_classic_nro_from_letter_and_mode(nro, 'Minor')
        
        #print(F"Retrieved nroshift: {nro_shift}, for letter {nro} and mode {input_chord.isMajorTriad()}")

        #new_chord = apply_letter_nro_to_chord(input_chord, nro)
        #numeric_form = convert_music21chord_to_numeric(new_chord)
        numeric_form = convert_music21chord_to_numeric(input_chord)
        #print(input_chord)
        #print(numeric_form)
        new_numeric_chord = []
        for i, n in enumerate(numeric_form):
            new_numeric_chord.append(n+nro_shift[i])
        #print(f"Premapped chord: {chord.Chord(new_numeric_chord)}")
        remapped_notes = map_numeric_chord_to_root(new_numeric_chord)
        d = duration.Duration(2.0)
        input_chord = chord.Chord(remapped_notes, duration=d)
        #print(f"Postmapped chord: {input_chord}")

        """
        if(len(notes)==0):
            #print("Chord could not be mapped to root. Discarding")
            succeeded= False
            break
        """

        #print(f"New Intermediary Chord: {chord.Chord(notes)} from nro {nro}")

    
    return input_chord, succeeded

"""
def apply_letter_nro_to_chord(c, letter):
    print(c)
    print(c.isMajorTriad())
    new_chord = None
    if letter == 'R':
        new_chord=  analysis.neoRiemannian.R(c)
    elif letter == 'P':
        new_chord=   analysis.neoRiemannian.P(c)
    elif letter == 'L':
        new_chord=   analysis.neoRiemannian.L(c)
    elif letter == 'N':
        new_chord=   analysis.neoRiemannian.N(c)
    elif letter == 'S':
        new_chord=   analysis.neoRiemannian.S(c)
    return new_chord
"""
    
def generate_random_compound_nro(max_cnro_length, classic_only = True):
    """
    all_nros = []
    if(not classic_only):
        all_nros = NROs.get_all_nros()
    else:
        all_nros = NROs.classic_nros

    c_nro_length = random.randint(1, max_cnro_length)
    nros = []
    for j in range(c_nro_length):
        nros.append(random.choice(all_nros))
    return nros
    """
    all_nros = ['R', 'P', 'L', 'N', 'S', 'M']
    c_nro_length = random.randint(1, max_cnro_length)
    nro_letters = []
    for j in range(c_nro_length):
        nro_letters.append(random.choice(all_nros))
    return nro_letters

"""
def get_final_chord_from_cnro_seq(start_chord, cnroseq):
    return generate_chord_seq_from_cnro_list(start_chord,cnroseq)[-1]
"""
    
def generate_random_compound_nro_sequence(count, max_cnro_length):

    output_c_nros = []

    for i in range(count):
        output_c_nros.append(generate_random_compound_nro(max_cnro_length))
        """
        c_nro_length = random.randint(0, max_cro_length+1)
        nros = []
        for j in range(c_nro_length):
            nros.append(random.choice(all_nros))
        output_c_nros.append(NROs.CompoundNRO(nros))
        """
    return output_c_nros



def generate_chord_seq_from_cnro_list(start_chord, c_nro_list):
    chord_list = []
    chord_list.append(start_chord)
    success = True

    #print(start_chord)

    for cnro in c_nro_list:
        #print(f"Applying CNRO to {chord_list[-1]}")
        #prev_n_chord = convert_music21chord_to_numeric(chord_list[-1])
        #print(f"Applying CNRO to {prev_n_chord}")
        #next_n_chord, success = apply_compoundnro_to_chord(prev_n_chord, cnro)
        #print(chord_list[-1])
        nextchord, success = apply_compoundnro_to_chord(chord_list[-1], cnro)
        if(success):
            #print(f"Generated: {next_n_chord}")
            chord_list.append(nextchord)
        else:
            #print("CNRO Sequence inadmissable - discarding")
            success = False
            break
    
    return chord_list, success

"""
def map_numericchord_to_mid_octave(numeric_chord):
    mapped_chord = []
    for note in numeric_chord:
        try_note = note + (12 * 5)
        mapped_note = note
        while try_note > 0:
            if try_note >= 60 and try_note < 72:
                mapped_note = try_note
            try_note -= 12
        mapped_chord.append(mapped_note)
    mapped_chord.sort()
    return mapped_chord
"""

def map_numeric_chord_to_root(numeric_chord):
    #mid_octave_ver = map_numericchord_to_mid_octave(numeric_chord)

    #print(f"Premapped notes: {numeric_chord}")

    scale_pos = []
    for n in numeric_chord:
        scale_pos.append(n%12)
    
    min_val = min(scale_pos)

    root_pos = []
    for n in scale_pos:
        root_pos.append(n-min_val)
    
    #If the root chord form bridges an octave, it can be in the form 5, 8, 0(12) or 5, 9, 0(12)
    
    maj1 =  all(item in root_pos for item in [0,4,7])
    maj2 =  all(item in root_pos for item in [5,9,0])
    maj3 =  all(item in root_pos for item in [8,0,3])
    min1 =  all(item in root_pos for item in [0,3,7])
    min2 =  all(item in root_pos for item in [5,8,0])
    min3 =  all(item in root_pos for item in [9,0,4])

    root_form_notes = []
    if(maj1 or maj2 or maj3 or min1 or min2 or min3):
        if(maj1):
            root_form_notes.append(numeric_chord[root_pos.index(0)])
            root_form_notes.append(numeric_chord[root_pos.index(4)])
            root_form_notes.append(numeric_chord[root_pos.index(7)])
        elif(maj2):
            root_form_notes.append(numeric_chord[root_pos.index(5)])
            root_form_notes.append(numeric_chord[root_pos.index(9)])
            root_form_notes.append(numeric_chord[root_pos.index(0)])
        elif(maj3):
            root_form_notes.append(numeric_chord[root_pos.index(8)])
            root_form_notes.append(numeric_chord[root_pos.index(0)])
            root_form_notes.append(numeric_chord[root_pos.index(3)])
        elif(min1):
            root_form_notes.append(numeric_chord[root_pos.index(0)])
            root_form_notes.append(numeric_chord[root_pos.index(3)])
            root_form_notes.append(numeric_chord[root_pos.index(7)])
        elif(min2):
            root_form_notes.append(numeric_chord[root_pos.index(5)])
            root_form_notes.append(numeric_chord[root_pos.index(8)])
            root_form_notes.append(numeric_chord[root_pos.index(0)])
        elif(min3):
            root_form_notes.append(numeric_chord[root_pos.index(9)])
            root_form_notes.append(numeric_chord[root_pos.index(0)])
            root_form_notes.append(numeric_chord[root_pos.index(4)])
    
    return root_form_notes
    """
    a, b, c = mid_octave_ver
    mapped_notes = []
    for t1, t2, t3 in [[a, b, c], [c - 12, a, b], [b - 12, c - 12, a]]:
        if t2 - t1 == 3 and t3 - t2 == 4:
            mapped_notes = [t1, t2, t3]
            break
        if t2 - t1 == 4 and t3 - t2 == 3:
            mapped_notes = [t1, t2, t3]
            break
    return mapped_notes
    """

"""
def remap_numeric_chord(numeric_chord):

    #print(f"Resorting numeric chord: {numeric_chord}")
    ident_dict = dict()
    for i, note in enumerate(numeric_chord):
        pos_indentifier = (note+4)%12
        #ident_dict[pos_indentifier] = i
        ident_dict[i] = pos_indentifier
    
    #print(f"Ident dict: {ident_dict}")
    key_list = list(ident_dict.keys())
    val_list = list(ident_dict.values())

    #sorted_keys = sorted(ident_dict)
    sorted_values = sorted(val_list)
    output_numeric_chord = []

    #print(f"Ident dict sorted values: {sorted_keys}")
    #print(f"Ident dict sorted values: {sorted_values}")

    for val in sorted_values:
        #output_numeric_chord.append(numeric_chord[ident_dict[val]])
        output_numeric_chord.append(numeric_chord[key_list[val_list.index(val)]])
    #print(f"Final sorted chord: {output_numeric_chord}")
    
    return output_numeric_chord
"""

if __name__ == "__main__":

    #Generate a random track starting at C Major
    c_maj = chord.Chord(["C2","E4","G6"])
    print(c_maj)
    
    cnro_seq = generate_random_compound_nro_sequence(10, 1)
    chord_seq, success = generate_chord_seq_from_cnro_list(c_maj, cnro_seq)

    #Print the chords
    print("Chords in track:")
    for c in chord_seq:
        sorted = c.sortDiatonicAscending()
        print(sorted)
        print(sorted.notes)

    #Print the NROs
    
    print("CNROs in track:")
    for i, cn in enumerate(cnro_seq):
        print(f"CNRO {i}")
        for nro in cn:
            print(nro)
    

    #Generate track and analyse
    track = chord_seq_to_stream(chord_seq)
    ays = track.analyze('key')
    letter = ays.tonicPitchNameWithCase
    key_signature = ays.asKey(tonic=letter)

    #Print track info
    print(f"Track Key:{ays}")
    print(f"Track Key String Raw:{str(ays)[0:2]}")
    key_str = list(str(track.analyze('key'))[0:2].replace('-','b'))
    if key_str[0].islower():
        key_str[0] = key_str[0].upper()
    print(key_str[1])
    if key_str[1] == ' ':
        del key_str[1]
    print(f"Track Key String Revised:{key_str}")
    
    print(f"Correlation Coefficient:{ays.correlationCoefficient}")
    print(f"Tonal Certainty:{ays.tonalCertainty()}")
    print(f"Alt Interpretations:{ays.alternateInterpretations[0:4]}")
    
    print(f"Key tonic: {ays.tonicPitchNameWithCase}")
    print(f"Mode: {key_signature}")
    print(f"Mode Only: {key_signature.mode}")

    #print(metCalc.calc_mode_ford_chordlist_revised(chord_seq))

    #me.calc_fitness_based_on_final_chord(chord_seq[-1],c_maj)

    #track.show('midi')

    """
    f= generate_random_note(3,5)
    print(f)
    f.show('midi')
    """

    """
    c = generate_random_trichord(1,6)
    print(c)
    c.show('midi')
    """

    """
    c = generate_random_trichord(1,6)
    print(c)
    print(convert_music21chord_to_numeric(c))
    c.show('midi')
    """

    """
    s = generate_random_track(3,5, 20)
    print(s)
    s.show('midi')
    
    details = get_key_and_confidence_from_stream(s)
    print(details)
    print(details.correlationCoefficient)
    print(details.mode)


    output_folder = f"{os.getcwd()}/{run_name}/"

    if not os.path.exists(output_folder):
        # If it doesn't exist, create it
        os.makedirs(output_folder)

    save_stream_to_midi(s, output_folder+"TestTrack.mid")
    """