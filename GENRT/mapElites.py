import random
import NROs as nros
import random
import copy
import os
from NRTCompositions import *
from NRTChordSequences import *
from NROs import *
from Chords import *
import numpy as np
import metricExtraction

MAX_PER_CELL = 3



START_CHORD = Trichord([48, 52, 55])
TARGET_FINAL_CHORD = Trichord([48, 52, 55])


event1 = NRTEvent(AntagonismCNRO, 52000, True)


fixed_key = KeySignature("c", "maj")
focal_note = 48
chord_instrument_num = 48 # harp
chord_instrument_num2 = 48 # harpsichord
melody_instrument_num = 42  # blown bottle
melody_instrument_num2 = 42
bass_instrument_num = 39 # synth bass
bass_instrument_num2 = 42
cmaj = KeySignature("c", "maj")

TEST_CHORD_SPEC = NRTChordSequenceSpec(instrument_num=chord_instrument_num,
                                           start_chord=START_CHORD,
                                           rhythm_string="1:1/1:1/1",
                                           target_episode_duration=10000,
                                           start_target_chord_duration=4000,
                                           end_target_chord_duration=2000,
                                           start_volume=50,
                                           end_volume=50,
                                           min_cnro_length=1,
                                           max_cnro_length=2,
                                           focal_note=focal_note,
                                           fixed_key=None,
                                           is_classic=True,
                                           end_event=event1,
                                           episode_overlap_chords=0)



melody_spec = NRTMelodySpec(instrument_num=melody_instrument_num2,
                                     rhythm_string="1:1/1:1/1",
                                     fixed_key=cmaj,
                                     start_volume=50,
                                     end_volume=127,
                                     is_voice_leading=True,
                                     chord_splits_allowed=[1, 2, 4, 8, 16],
                                     note_length=1,
                                     episode_overlap_chords=3)

bass_spec = NRTBasslineSpec(instrument_num=bass_instrument_num,
                                     rhythm_string="1:1/1:1/1",
                                     start_volume=50,
                                     end_volume=127,
                                     episode_overlap_chords=3)

drum_rstring = "1:1/8,1:4/8,1:5/8"
highhat_rstring = "1:1/8,1:2/8,1:3/8,1:4/8,1:5/8,1:6/8,1:7/8,1:8/8"
cymbal_rstring = "1:6/8,1:7/8"

percussion_spec = NRTPercussionSpec(instrument_nums=[35, 59, 51],
                                             rhythm_strings=[drum_rstring, highhat_rstring, cymbal_rstring],
                                             start_volumes=[0, 0, 0],
                                             end_volumes=[0, 0, 0])




def generate_buckets(minval, maxval, bucketcount):
    buckets = []

    increment_size = (maxval-minval)/bucketcount

    b1 = minval
    b2 = minval+increment_size

    for i in range(bucketcount):
        buckets.append([b1, b2])
        b1+=increment_size
        b2+=increment_size
    
    return buckets


def generate_grid(dim1_size, dim2_size):
    map = dict()
    for i in range(dim1_size):
        for j in range(dim2_size):
            map[(i,j)]=[]
    
    return map


def get_location_for_track(value_a, value_b, buckets_a, buckets_b):
    a_index=0,
    b_index=0  
    
    a_loc_found = False
    b_loc_found = False

    counter = 0
    for b in buckets_a:
        if(value_a<b[1]):
            a_index=counter
            a_loc_found= True
            break
        counter+=1
    
    counter = 0
    for b in buckets_b:
        if(value_b<b[1]):
            b_index=counter
            b_loc_found= True
            break
        counter+=1
    
    if(a_loc_found and b_loc_found):
        return a_index, b_index

    else:
        print("ERROR: Track does not fit in grid")
        return 0,0
    
def select_random_track_from_grid(grid):
    found = False
    rand_track = None
    while not found:
        rand_loc = random.randint(0, len(grid)-1)
        key = list(grid)[rand_loc]
        if(len(grid[key])>0):
            rand_track = grid[key][random.randint(0, len(grid[key])-1)]
            found = True
    return rand_track


#Replace an NRO in a sequence with a random one
def mutate_nro_sequence(nro_sequence):
    random_nro = generate_random_compound_nro()
    nro_sequence[random.randrange(len(nro_sequence))] = random_nro
    return nro_sequence


def generate_random_compound_nro(maxlength = 3):
    nro_count = random.randrange(1,maxlength+1)
    nro_sequence = []
    all_nros = nros.get_all_nros()
    for i in range(nro_count):
        nro_sequence.append(all_nros[random.randrange(len(all_nros))])
    return nros.CompoundNRO(nro_sequence)

def generate_chord_list_for_new_nros(original_chordlist, new_nro_seq):
    new_chordlist = []
    #First chord always the same
    new_chordlist.append(original_chordlist[0])

    for i in range(1,len(new_nro_seq)):
        new_chordlist.append(original_chordlist[i-1].apply_compound_nro(new_nro_seq[i]))

        #print("Prev chord: " + str(original_chordseq[i-1]))
        #print("New chord: " + str(new_chordseq[i-1]))
    
    return new_chordlist

def calc_fitness_based_on_final_chord(final_chord, target_chord):
    actual_note_sum = np.sum(final_chord.notes)
    target_note_sum = np.sum(target_chord.notes)
    return abs(actual_note_sum-target_note_sum)

def add_track_to_grid(map, metric_a, metric_b, buckets_a, buckets_b, new_composition, target_chord):
    position = get_location_for_track(metric_a, metric_b, buckets_a, buckets_b)

    if(len(map[position])>MAX_PER_CELL):
        cached_comp_index = -1
        worst_fitness_found = 0
        for index, composition in enumerate(map[position]):
            final_chord =  composition.episodes[-1].chord_sequence.chords[-1]
            fitness = calc_fitness_based_on_final_chord(final_chord, target_chord)
            if(fitness>worst_fitness_found):
                worst_fitness_found = fitness
                cached_comp_index = index
        
        new_track_final_chord =  new_composition.episodes[-1].chord_sequence.chords[-1]
        new_track_fitness = calc_fitness_based_on_final_chord(new_track_final_chord, target_chord)
        if(new_track_fitness<worst_fitness_found):
            del map[position][cached_comp_index]
            map[position].append(new_composition)
    else:
        map[position].append(new_composition)
    
    return map

def mutate_composition(comp):

    #Extract pre mutated values
    extracted_episode = comp.episodes[0]
    extracted_chordseq = extracted_episode.chord_sequence
    extracted_duration = extracted_episode.duration_ms
    extracted_compound_nro_list = extracted_chordseq.compound_nros

    """
    print("Pre_mutation compound NROs")
    for nro in extracted_compound_nro_list:
        print(nro)
    #print(extracted_episode.chord_sequence.compound_nros)
    """


    #Generate mutation
    mutated_nros = mutate_nro_sequence(extracted_compound_nro_list)

    """
    print("Post mutation compound NROs")
    for nro in mutated_nros:
        print(nro)
    """

    #Generate new composition from mutated NRO list
    mutated_chord_list = generate_chord_list_for_new_nros(extracted_chordseq.chords, mutated_nros)
    mutated_chord_sequence = NRTChordSequence(extracted_chordseq.spec, mutated_chord_list, extracted_duration, extracted_chordseq.tick_durations, mutated_nros)
    mutated_episode = NRTEpisode(chord_seq= mutated_chord_sequence, dur_ms = extracted_duration)

    mutated_comp = NRTComposition( episodes = [mutated_episode])
    mutated_comp.melody_on = False
    mutated_comp.bassline_on = False
    mutated_comp.percussion_on = False

    return  mutated_comp

def generate_starting_population(size, spec):
    start_pop = []
    for i in range(size):
        print("Loop: " + str(i))
        comp_spec  = copy.deepcopy(spec)
        episode_spec = NRTEpisodeSpec(spec, melody_spec, bass_spec, percussion_spec)
        composition = NRTComposition(episode_specs = [episode_spec])
        #composition.chords_on = False
        composition.melody_on = False
        composition.bassline_on = False
        composition.percussion_on = False

        #nro_length = len(composition.episodes[0].chord_sequence.compound_nros)
        #print(f"Generated Track Compound nro length: {nro_length}")

        start_pop.append(composition)
    
    return start_pop

def evaluate_map(map):
    filled_cells = 0
    total_pop = 0

    for x in map.values():
        if(len(x)>0):
            filled_cells+=1
        total_pop+=len(x)
    
    print(f"Filled cells: {filled_cells} and total pop: {total_pop}")

def generate_songs_from_map(map, output_folder, fit_only= True):
    outpath = 'output_folder/'+output_folder+"/"
    if not os.path.exists(outpath):
        os.makedirs(outpath)
    
    for k in map:
        if(len(map[k])>0):
            loc_path = outpath+"/"+str(k)+"/"
            os.makedirs(loc_path)
            counter = 1
            for comp in map[k]:
                
                final_chord =  comp.episodes[-1].chord_sequence.chords[-1]
                fitness = calc_fitness_based_on_final_chord(final_chord, TARGET_FINAL_CHORD)
                if fitness == 0 or not fit_only:
                    comp.save_song(f"{loc_path}Track{str(counter)}.mid")

    

if __name__ == "__main__":

    test_start_pop = generate_starting_population(10, TEST_CHORD_SPEC)

    #for c in test_start_pop:
        #print("NroShift: " + str(metricExtraction.calc_average_nro_shift(c)))
        #print("MinManChordRatio: " + str(metricExtraction.calc_majorchord_ratio(c)))
    
    map = generate_grid(10,10)

    ns_buckets = generate_buckets(0, 3, 10)
    mm_buckets = generate_buckets(0,1,10)

    
    for c in test_start_pop:
        add_track_to_grid(map,metricExtraction.calc_average_nro_shift(c), metricExtraction.calc_majorchord_ratio(c), ns_buckets, mm_buckets, c,  TARGET_FINAL_CHORD)

    #print(map)

    print("Starting pop map details:")
    evaluate_map(map)

    for i in range(0, 10000):
        rand_comp = select_random_track_from_grid(map)
        mutated_comp = mutate_composition(rand_comp)
        add_track_to_grid(map,metricExtraction.calc_average_nro_shift(mutated_comp), metricExtraction.calc_majorchord_ratio(mutated_comp), ns_buckets, mm_buckets,mutated_comp,  TARGET_FINAL_CHORD)
    
    
    print("Final map details:")
    evaluate_map(map)

    generate_songs_from_map(map, "TestRun2", False)





"""
buckets_a_test = generate_buckets(10, 110, 2)
buckets_b_test = generate_buckets(1, 2, 2)

print(buckets_a_test)
print(buckets_b_test)

pos_test = get_location_for_track(60.1, 1.51, buckets_a_test,buckets_b_test )

print(pos_test)



map_test = generate_grid(2,2)

print(map_test)

map_test[(1,1)].append(69)
map_test[(0,1)].append(666)
map_test[(1,1)].append(1234)

print(map_test)

rand_val = select_random_track_from_grid(map_test)
print(rand_val)
"""