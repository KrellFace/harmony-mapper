from music21 import * 
import random
import os
from enum import Enum
import mapElites as me
import metricCalculation as metCalc

note_letters = ['A','B','C','D','E','F','G']


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


def generate_random_admissable_chord(min_midi_root, max_midi_root):
    notes = []
    root_note = random.randint(min_midi_root, max_midi_root+1)
    
    if random.random() >0.5:
        notes.extend([root_note, root_note+4, root_note+7])
    else:
        notes.extend([root_note, root_note+3, root_note+7])
    return notes



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

        numeric_form = convert_music21chord_to_numeric(input_chord)
        new_numeric_chord = []
        for i, n in enumerate(numeric_form):
            new_numeric_chord.append(n+nro_shift[i])
        #print(f"Premapped chord: {chord.Chord(new_numeric_chord)}")
        remapped_notes = map_numeric_chord_to_root(new_numeric_chord)
        d = duration.Duration(2.0)
        input_chord = chord.Chord(remapped_notes, duration=d)
        #print(f"Postmapped chord: {input_chord}")

        #print(f"New Intermediary Chord: {chord.Chord(notes)} from nro {nro}")

    
    return input_chord, succeeded

def generate_random_compound_nro(max_cnro_length, classic_only = True):
    all_nros = ['R', 'P', 'L', 'N', 'S', 'M']
    c_nro_length = random.randint(1, max_cnro_length)
    nro_letters = []
    for j in range(c_nro_length):
        nro_letters.append(random.choice(all_nros))
    return nro_letters

def generate_random_compound_nro_sequence(count, max_cnro_length):

    output_c_nros = []

    for i in range(count):
        output_c_nros.append(generate_random_compound_nro(max_cnro_length))
    return output_c_nros



def generate_chord_seq_from_cnro_list(start_chord, c_nro_list):
    chord_list = []
    chord_list.append(start_chord)
    success = True

    #print(start_chord)

    for cnro in c_nro_list:
        nextchord, success = apply_compoundnro_to_chord(chord_list[-1], cnro)
        if(success):
            #print(f"Generated: {next_n_chord}")
            chord_list.append(nextchord)
        else:
            #print("CNRO Sequence inadmissable - discarding")
            success = False
            break
    
    return chord_list, success

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


if __name__ == "__main__":

   ""

