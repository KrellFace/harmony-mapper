
import matplotlib.pyplot as plt
import re
from enum import Enum, auto
from NRTCompositions import *

#Used this page for lots of the mode calculation code
#https://www.mvanga.com/blog/basic-music-theory-in-200-lines-of-python
#[1] for a citation
major_mode_rotations = {
    'Ionian':     0,
    'Dorian':     1,
    'Phrygian':   2,
    'Lydian':     3,
    'Mixolydian': 4,
    'Aeolian':    5,
    'Locrian':    6,
}

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

class metric_type(Enum):
    Major_Minor_ChordRatio = auto()
    Avg_NRO_Shift = auto()
    Track_Mood = auto()


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


def calc_majorchord_ratio(composition):
    comp_episodes = composition.episodes


    tot_chords = 0
    tot_majorchords = 0
    for ep in comp_episodes:
        chord_seq = ep.chord_sequence.chords
        for chord in chord_seq:
            tot_chords+=1
            if(chord.is_major()):
                tot_majorchords+=1

    return (tot_majorchords/tot_chords)


def calc_average_nro_shift(composition):

    total_individual_nros = 0
    total_compoud_nros = 0

    comp_episodes = composition.episodes
    for ep in comp_episodes:
        compound_nros = ep.chord_sequence.compound_nros
        for c in compound_nros:
            #print(f"C:{c}")
            if(c!="None"):
                nro_sequence = c.nros
                total_compoud_nros+=1
                total_individual_nros+=len(nro_sequence)
                #print(nro_sequence)
    
    return total_individual_nros/total_compoud_nros

def check_if_trichord_in_scale(trichord, scale):



    chord_letters = trichord.get_note_letters()
    in_scale = True
    for letter in chord_letters:
        if(letter not in scale):
            in_scale = False

    #print(f"Checked if chord {trichord} was in scale {scale} and found {in_scale}")

    return in_scale

def calc_mode_for_chordlist(composition):

    chord_list = composition.episodes[0].chord_sequence.chords

    modes = generate_modes()

    mode_count = dict()
    for m in major_mode_rotations:
        mode_count[m]=0

    print(f"Chord list length: {len(chord_list)}")
    
    for chord in chord_list:
        print(f"Checking chord {chord}")
        for key in modes:
            #print(f"Checking key {key}")
            for mode_in_key in modes[key]:
                #print(f"Checking mode {mode_in_key}")
                if check_if_trichord_in_scale(chord, modes[key][mode_in_key]):
                    mode_count[mode_in_key]+=1
                    #print(f"Added to {mode_in_key}. New count: {mode_count[mode_in_key]}")
        print(f"Chord full processed. New dict: { mode_count}")
    
    most_frequent_mode = ""
    biggest_count = 0

    for mode in mode_count:
        print(f"Chord sequence has {mode_count[mode]} matching scales for  {mode} ")
        if(mode_count[mode]>biggest_count):
            biggest_count = mode_count[mode]
            most_frequent_mode = mode

    print(f"Chord sequence fits best with {most_frequent_mode} with {biggest_count} matching scales total")

    return most_frequent_mode

def get_metric_value_for_metric(composition, met_type):
    if met_type== metric_type.Avg_NRO_Shift:
        return calc_average_nro_shift(composition)
    elif met_type == metric_type.Major_Minor_ChordRatio:
        return calc_majorchord_ratio(composition)
    elif met_type == metric_type.Track_Mood:
        return calc_mode_for_chordlist(composition)



def basic_era_scatter(metric1_name, metric2_name, metric1_vals, metric2_vals, outpath):

    fig = plt.figure(figsize = (8,8))
    ax = fig.add_subplot(1,1,1) 
    
    ax.set_xlabel(metric1_name, fontsize = 35)
    ax.set_ylabel(metric2_name, fontsize = 35)
        
    title = f"{metric1_name}-{metric2_name} ERA Scatterplot"


    #Color each generators points differently if we are running for multiple alternatives
    colors = []

    for i in range(len(metric1_vals)):
        #Gen random colors
        #colors.append('#%06X' % randint(0, 0xFFFFFF))
        #All pink
        #colors.append([255/ 255.0, 205/ 255.0, 243/ 255.0])
        #All purple
        colors.append([129/ 255.0, 38/ 255.0, 192/ 255.0])

    ax.scatter(metric1_vals
                , metric2_vals
                , c = colors
                , alpha = 0.4
                , s = 20)
    #ax.set_xlim(xmin=0.1)
    #ax.set_ylim(ymin=0.4)
    ax.spines['left'].set_color("black")
    ax.spines['left'].set_linewidth(0.5)
    ax.spines['bottom'].set_color("black")
    ax.spines['bottom'].set_linewidth(0.5)
    ax.grid(color = "black", linestyle = "dashed", linewidth = 0.1)
    ax.set_facecolor((1.0, 1.0,1.0))

    #plt.show()
    
    plt.savefig(f"{outpath}{metric1_name},{metric2_name} ERA Scatterplot")


def generate_and_visualise_songset(track_count_to_generate, episode_specs, output_folder):

    majorratio_dict = dict()
    bassdiff_dict = dict()
    majorratios = list()
    bassdiffs = list()
    tracks_dict = dict()

    for i in range(track_count_to_generate):
        #episode1_spec = NRTEpisodeSpec(episode1_chord_spec, episode1_melody_spec, episode1_bass_spec, episode1_percussion_spec)
        #episode2_spec = NRTEpisodeSpec(episode2_chord_spec, episode2_melody_spec, episode2_bass_spec, episode2_percussion_spec)
        composition = NRTComposition(episode_specs)

        tracks_dict[i] = composition

        #print(composition)

        """
        episodes = composition.episodes
        #Extract average major chord ratio from melody
        tot_chords = 0
        tot_majorchords = 0
        for ep in episodes:
            chord_seq = ep.chord_sequence.chords
            for chord in chord_seq:
                tot_chords+=1
                if(chord.is_major()):
                    tot_majorchords+=1
        """
        ratio = calc_majorchord_ratio(composition)

        majorratio_dict[i] = ratio
        majorratios.append(ratio)

        #Extract average bass note shift
        tot_bassnotes = 0
        tot_bassshift = 0
        prev_note = 0

        episodes = composition.episodes

        for ep in episodes:
            notes_seq = ep.bassline.notes
            prev_note=notes_seq[0].note_num
            for note in notes_seq:
                #print(f"For track {i} bass note {note.note_num} found next")
                tot_bassnotes+=1
                tot_bassshift +=abs(prev_note-note.note_num)
                prev_note = note.note_num

        bassdiff_dict[i] = (tot_bassshift/tot_bassnotes)
        bassdiffs.append(tot_bassshift/tot_bassnotes)

        print(f"For track{i} a total of {tot_bassnotes} bass notes were generated with a total bass shift of {tot_bassshift} and average note shift between notes of {(tot_bassshift/tot_bassnotes)}")

    #Saving the most extreme tracks
    min_val = 999
    min_key = 0
    max_val = 0
    max_key = 0
    for key in majorratio_dict.keys():
        val = majorratio_dict[key]
        if(val<min_val):
            min_val = val
            min_key = key

        if(val>max_val):
            max_val = val
            max_key = key

    #print(f"Min Key, Max Key: {min_key}, {max_key}")

    tracks_dict[min_key].save_song(output_folder+"/MinMajorRatio.mid")
    tracks_dict[max_key].save_song(output_folder+"/MaxMajorRatio.mid")


    basic_era_scatter("Major_Chord_Ratio", "Avg Bassnote Shift", majorratios, bassdiffs,output_folder)





if __name__ == "__main__":

    modes = generate_modes()

    print(modes['C'])

