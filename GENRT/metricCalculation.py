
import matplotlib.pyplot as plt
import re
from enum import Enum, auto
import random
from music21 import * 
import musicGeneration as musGen

#Used this page for lots of the mode calculation code
#https://www.mvanga.com/blog/basic-music-theory-in-200-lines-of-python
#[1] for a citation

class MusicModes(Enum):
    ionian = 1
    dorian = 2
    phrygian = 3
    lydian = 4
    mixolydian = 5
    aeolian = 6
    locrian = 7

major_mode_rotations = {
    'ionian':     0,
    'dorian':     1,
    'phrygian':   2,
    'lydian':     3,
    'mixolydian': 4,
    'aeolian':    5,
    'locrian':    6,
}

class metric_type(Enum):
    Major_Minor_ChordRatio = auto()
    Avg_NRO_Shift = auto()
    Track_Mood = auto()

keys = [
    'B#',  'C', 'C#', 'Db', 'D', 'D#',  'Eb', 'E',  'Fb', 'E#',  'F',
    'F#', 'Gb', 'G', 'G#',  'Ab', 'A', 'A#',  'Bb', 'B',  'Cb',
]

alphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G']

#From [1]
intervals = [
    ['P1', 'd2'],  # Perfect unison   Diminished second
    ['m2', 'A1'],  # Minor second     Augmented unison
    ['M2', 'd3'],  # Major second     Diminished third
    ['m3', 'A2'],  # Minor third      Augmented second
    ['M3', 'd4'],  # Major third      Diminished fourth
    ['P4', 'A3'],  # Perfect fourth   Augmented third
    ['d5', 'A4'],  # Diminished fifth Augmented fourth
    ['P5', 'd6'],  # Perfect fifth    Diminished sixth
    ['m6', 'A5'],  # Minor sixth      Augmented fifth
    ['M6', 'd7'],  # Major sixth      Diminished seventh
    ['m7', 'A6'],  # Minor seventh    Augmented sixth
    ['M7', 'd8'],  # Major seventh    Diminished octave
    ['P8', 'A7'],  # Perfect octave   Augmented seventh
]

#From [1]
notes = [
    ['B#',  'C',  'Dbb'],
    ['B##', 'C#', 'Db'],
    ['C##', 'D',  'Ebb'],
    ['D#',  'Eb', 'Fbb'],
    ['D##', 'E',  'Fb'],
    ['E#',  'F',  'Gbb'],
    ['E##', 'F#', 'Gb'],
    ['F##', 'G',  'Abb'],
    ['G#',  'Ab'],
    ['G##', 'A',  'Bbb'],
    ['A#',  'Bb', 'Cbb'],
    ['A##', 'B',  'Cb'],
]

formulas = {
    # Scale formulas
    'scales': {
        # Major scale, its modes, and minor scale
        'major':              '1,2,3,4,5,6,7',
        'minor':              '1,2,b3,4,5,b6,b7',
        # Melodic minor and its modes
        'melodic_minor':      '1,2,b3,4,5,6,7',
        # Harmonic minor and its modes
        'harmonic_minor':     '1,2,b3,4,5,b6,7',
        # Blues scales
        'major_blues':        '1,2,b3,3,5,6',
        'minor_blues':        '1,b3,4,b5,5,b7',
        # Penatatonic scales
        'pentatonic_major':   '1,2,3,5,6',
        'pentatonic_minor':   '1,b3,4,5,b7',
        'pentatonic_blues':   '1,b3,4,b5,5,b7',
    },
    'chords': {
        # Major
        'major':              '1,3,5',
        'major_6':            '1,3,5,6',
        'major_6_9':          '1,3,5,6,9',
        'major_7':            '1,3,5,7',
        'major_9':            '1,3,5,7,9',
        'major_13':           '1,3,5,7,9,11,13',
        'major_7_#11':        '1,3,5,7,#11',
        # Minor
        'minor':              '1,b3,5',
        'minor_6':            '1,b3,5,6',
        'minor_6_9':          '1,b3,5,6,9',
        'minor_7':            '1,b3,5,b7',
        'minor_9':            '1,b3,5,b7,9',
        'minor_11':           '1,b3,5,b7,9,11',
        'minor_7_b5':         '1,b3,b5,b7',
        # Dominant
        'dominant_7':         '1,3,5,b7',
        'dominant_9':         '1,3,5,b7,9',
        'dominant_11':        '1,3,5,b7,9,11',
        'dominant_13':        '1,3,5,b7,9,11,13',
        'dominant_7_#11':     '1,3,5,b7,#11',
        # Diminished
        'diminished':         '1,b3,b5',
        'diminished_7':       '1,b3,b5,bb7',
        'diminished_7_half':  '1,b3,b5,b7',
        # Augmented
        'augmented':          '1,3,#5',
        # Suspended
        'sus2':               '1,2,5',
        'sus4':               '1,4,5',
        '7sus2':              '1,2,5,b7',
        '7sus4':              '1,4,5,b7',
    },
}

intervals_major = [
    [ '1', 'bb2'],
    ['b2',  '#1'],
    [ '2', 'bb3',   '9'],
    ['b3',  '#2'],
    [ '3',  'b4'],
    [ '4',  '#3',  '11'],
    ['b5',  '#4', '#11'],
    [ '5', 'bb6'],
    ['b6',  '#5'],
    [ '6', 'bb7',  '13'],
    ['b7',  '#6'],
    [ '7',  'b8'],
    [ '8',  '#7'],
]



#From [1]
def find_note_index(scale, search_note):
    ''' Given a scale, find the index of a particular note '''
    for index, note in enumerate(scale):
        # Deal with situations where we have a list of enharmonic
        # equivalents, as well as just a single note as and str.
        if type(note) == list:
            if search_note in note:
                return index
        elif type(note) == str:
            if search_note == note:
                return index
            

#From [1]
def rotate(scale, n):
    ''' Left-rotate a scale by n positions. '''
    return scale[n:] + scale[:n]

def mode(scale, degree):
    return rotate(scale, degree)

def make_formula(formula, labeled):
    '''
    Given a comma-separated interval formula, and a set of labeled
    notes in a key, return the notes of the formula.
    '''
    return [labeled[x] for x in formula.split(',')]

#From [1]
def chromatic(key):
    ''' Generate a chromatic scale in a given key. '''
    # Figure out how much to rotate the notes list by and return
    # the rotated version.
    num_rotations = find_note_index(notes, key)
    return rotate(notes, num_rotations)

def make_intervals(key, interval_type='standard'):
    # Our labeled set of notes mapping interval names to notes
    labels = {}

    # Step 1: Generate a chromatic scale in our desired key
    chromatic_scale = chromatic(key)

    # The alphabets starting at provided key
    alphabet_key = rotate(alphabet, find_note_index(alphabet, key[0]))

    intervs = intervals if interval_type == 'standard' else intervals_major
    # Iterate through all intervals (list of lists)
    for index, interval_list in enumerate(intervs):

        # Step 2: Find the notes to search through based on degree
        notes_to_search = chromatic_scale[index % len(chromatic_scale)]

        for interval_name in interval_list:
            # Get the interval degree
            if interval_type == 'standard':
                degree = int(interval_name[1]) - 1 # e.g. M3 --> 2, m7 --> 6
            elif interval_type == 'major':
                degree = int(re.sub('[b#]', '', interval_name)) - 1

            # Get the alphabet to look for
            alphabet_to_search = alphabet_key[degree % len(alphabet_key)]

            #print('Interval {}, degree {}: looking for alphabet {} in notes {}'.format(interval_name, degree, alphabet_to_search, notes_to_search))
            try:
                note = [x for x in notes_to_search if x[0] == alphabet_to_search][0]
            except:
                note = notes_to_search[0]

            labels[interval_name] = note

    return labels


#From [1]
def make_intervals_standard(key):
    # Our labeled set of notes mapping interval names to notes
    labels = {}
    
    # Step 1: Generate a chromatic scale in our desired key
    chromatic_scale = chromatic(key)
    
    # The alphabets starting at provided key's alphabet
    alphabet_key = rotate(alphabet, find_note_index(alphabet, key[0]))
    
    # Iterate through all intervals (list of lists)
    for index, interval_list in enumerate(intervals):
    
        # Step 2: Find the notes to search through based on degree
        notes_to_search = chromatic_scale[index % len(chromatic_scale)]
        
        for interval_name in interval_list:
            # Get the interval degree
            degree = int(interval_name[1]) - 1 # e.g. M3 --> 3, m7 --> 7
            
            # Get the alphabet to look for
            alphabet_to_search = alphabet_key[degree % len(alphabet_key)]
            
            try:
                note = [x for x in notes_to_search if x[0] == alphabet_to_search][0]
            except:
                note = notes_to_search[0]
            
            labels[interval_name] = note

    return labels


#From [1]
def generate_modes():
    modes = {}
    for key in keys:
        intervs = make_intervals(key, 'major')
        c_major_scale = make_formula(formulas['scales']['major'], intervs)
        for m in major_mode_rotations:
            v = mode(c_major_scale, major_mode_rotations[m])
            if v[0] not in modes:
                modes[v[0]] = {}
            modes[v[0]][m] = v
    
    return modes


def calc_majorchord_ratio(chord_seq):

    tot_chords = 0
    tot_majorchords = 0
    for chord in chord_seq:
        tot_chords+=1
        if(chord.isMajorTriad()):
            tot_majorchords+=1

    return (tot_majorchords/tot_chords)


def calc_average_nro_shift(cnro_list):

    total_individual_nros = 0
    total_compoud_nros = 0

    #print(f"Calcing NRO shift ond {cnro_list}")

    for c in cnro_list:
        #print(f"C:{c}")
        if(c!="None"):
            total_compoud_nros+=1
            total_individual_nros+=len(c)
            #print(nro_sequence)
    
    
    #print(f"Returning {total_individual_nros/total_compoud_nros}")
    
    return total_individual_nros/total_compoud_nros

def check_if_trichord_in_scale(trichord, scale):



    chord_letters = trichord.get_note_letters()
    in_scale = True
    for letter in chord_letters:
        if(letter not in scale):
            in_scale = False

    #print(f"Checked if chord {trichord} was in scale {scale} and found {in_scale}")

    return in_scale

def convert_music21_notename(note):        
    letter = list(str(note.name)[0:2].replace('-','b'))
    #print(f"Letter as list: {letter}")
    if(len(letter)>1):
        if letter[1] not in ('#','b'):
            del letter[1]
    letter = "".join(letter)
    return letter


def check_if_music21chord_in_scale(chord, scale):

    in_scale = True
    for note in chord.notes:
        #print(f"Raw note: {note}")
        #print(f"Letter as string: {str(note.name)}")
        """
        letter = list(str(note.name)[0:2].replace('-','b'))
        #print(f"Letter as list: {letter}")
        if(len(letter)>1):
            if letter[1] not in ('#','b'):
                del letter[1]
        letter = "".join(letter)
        """
        #print(f"Letter as revised string: {letter}")
        #print(f"Checking if note {letter} in scale {scale}")
        letter = convert_music21_notename(note)

        if(letter not in scale):
            in_scale = False

    #print(f"Checked if chord {chord} was in scale {scale} and found {in_scale}")

    return in_scale

"""
def get_signature_note_for_mode(key, mode):
    letters = ['A','B','C','D','E','F','G']
    split_key = list(key)
    key_index = letters.index(split_key[0])
    target_index = 0
    suffix = ''
    if mode == 'ionian':
        target_index = key_index+4
    if mode == 'lydian':
        target_index = key_index+4
        suffix = '#'
    if mode == 'mixolydian':
        target_index = key_index+7
        suffix = '-'
    if mode == 'aeolian':
        target_index = key_index+6
    if mode == 'dorian':
        target_index = key_index+6
        suffix = '#'
    if mode == 'phrygian':
        target_index = key_index+2
        suffix = '-'
    if mode == 'locrian':
        target_index = key_index+5
        suffix = '-'
    
    if target_index>= 7:
        target_index-=7
    
    return note.Note(''.join(str(e) for e in [letters[target_index], suffix]))

"""

"""
def calc_mode_for_chordlist(chord_seq):

    track = musGen.chord_seq_to_stream(chord_seq)

    ays = track.analyze('key')
    letter = ays.tonicPitchNameWithCase
    mode_name = ays.asKey(tonic=letter).mode
    return MusicModes[mode_name].value
"""

def calc_mode_for_chordlist_revised(chord_seq):
    track = musGen.chord_seq_to_stream(chord_seq)

    key_str = list(str(track.analyze('key'))[0:2].replace('-','b'))
    if key_str[0].islower():
        key_str[0] = key_str[0].upper()
    if key_str[1] == ' ':
        del key_str[1]
    
    key_str = "".join(key_str)

    modes = generate_modes()

    mode_count = dict()
    for m in major_mode_rotations:
        mode_count[m]=0

    for chord in chord_seq:
        #print(f"Checking chord {chord}")
        for mode_in_key in modes[key_str]:
            #print(f"Checking mode {mode_in_key} in key {key_str}")
            if check_if_music21chord_in_scale(chord, modes[key_str][mode_in_key]):
                mode_count[mode_in_key]+=1
                #print(f"Added to {mode_in_key}. New count: {mode_count[mode_in_key]}")
        #print(f"Chord full processed. New dict: { mode_count}\n\n")
    
    most_frequent_modes = []
    biggest_count = 0

    for mode in mode_count:
        #print(f"Chord sequence has {mode_count[mode]} matching scales for  {mode} ")
        if(mode_count[mode]>biggest_count):
            biggest_count = mode_count[mode]
            most_frequent_modes = [mode]
        elif(mode_count[mode]==biggest_count):
            most_frequent_modes.append(mode)

    #print(f"Chord sequence fits best with {most_frequent_mode} with {biggest_count} matching scales total")

    if(len(most_frequent_modes) == 1):
        
        return MusicModes[most_frequent_modes[0]].value
    #If no matching scales found, return Ionian for how (HACk)
    elif(biggest_count==0):
        return MusicModes['ionian'].value
    elif(len(most_frequent_modes)>0):
        #print(f"Tie breaker as most freq : {mode_count}")
        #print(f"Most freq modes : {most_frequent_modes}")
        max_sig_note_count = 0
        return_mode= None
        return_sig_note = None
        for mode in most_frequent_modes:
            count = 0
            signature_note = modes[key_str][mode][3]
            for chord in chord_seq:
                for note in chord.notes:
                    if signature_note == convert_music21_notename(note):
                        count+=1
            if(count>max_sig_note_count):
                return_mode = mode
                max_sig_note_count=count
                return_sig_note= signature_note
        
        #print(f"Returning mode {return_mode} as {max_sig_note_count} signature notes for key {key_str} ({return_sig_note}) found")
        #print(f"For chord list: ")
        #for c in chord_seq:
        #   print(c)

        if(max_sig_note_count>0):
            return MusicModes[return_mode].value
        #Return a random choice of matching modes if no signature note appears most
        else:
            return MusicModes[random.choice(most_frequent_modes)].value


    
    else:
        return -1

"""
def OLD_calc_mode_for_chordlist(composition):

    chord_list = composition.episodes[0].chord_sequence.chords

    modes = generate_modes()

    mode_count = dict()
    for m in major_mode_rotations:
        mode_count[m]=0

    print(f"Chord list length: {len(chord_list)}")
    
    for chord in chord_list:
        print(f"Checking chord {chord}")
        for key in modes:
            print(f"Checking key {key}")
            for mode_in_key in modes[key]:
                print(f"Checking mode {mode_in_key} in key {key}")
                if check_if_trichord_in_scale(chord, modes[key][mode_in_key]):
                    mode_count[mode_in_key]+=1
                    print(f"Added to {mode_in_key}. New count: {mode_count[mode_in_key]}")
        print(f"Chord full processed. New dict: { mode_count}\n\n")
    
    most_frequent_mode = ""
    biggest_count = 0

    for mode in mode_count:
        print(f"Chord sequence has {mode_count[mode]} matching scales for  {mode} ")
        if(mode_count[mode]>biggest_count):
            biggest_count = mode_count[mode]
            most_frequent_mode = mode

    print(f"Chord sequence fits best with {most_frequent_mode} with {biggest_count} matching scales total")

    return most_frequent_mode
"""

def get_metric_value_for_metric(track, met_type):
    if met_type== metric_type.Avg_NRO_Shift:
        return calc_average_nro_shift(track.cnro_seq)
    elif met_type == metric_type.Major_Minor_ChordRatio:
        return calc_majorchord_ratio(track.chord_seq)
    elif met_type == metric_type.Track_Mood:
        #return calc_mode_for_chordlist(track.chord_seq)
        return calc_mode_for_chordlist_revised(track.chord_seq)


if __name__ == "__main__":
    ""
