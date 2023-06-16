import random
import NROs as nros
import random
import copy
import os
import pandas as pd
from NRTCompositions import *
from NRTChordSequences import *
from NROs import *
from Chords import *
import numpy as np
import metricExtraction as me
import matplotlib.pyplot as plt
import seaborn as sns; sns.set_theme()

MAX_PER_CELL = 3



START_CHORD = Trichord([48, 52, 55])
TARGET_FINAL_CHORD = Trichord([48, 52, 55])


event1 = NRTEvent(AntagonismCNRO, 52000, True)


fixed_key = KeySignature("C", "maj")
focal_note = 48
chord_instrument_num = 48 # harp
chord_instrument_num2 = 48 # harpsichord
melody_instrument_num = 42  # blown bottle
melody_instrument_num2 = 42
bass_instrument_num = 39 # synth bass
bass_instrument_num2 = 42
cmaj = KeySignature("C", "maj")

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

def crossover_nro_sequence(seq1, seq2):
    crosspoint = random.randint(0, len(seq1))

    child1 = seq1[:crosspoint]+seq2[crosspoint:]
    child2 = seq2[:crosspoint]+seq1[crosspoint:]

    return child1, child2


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
    
    diff = abs(actual_note_sum-target_note_sum)

    if diff!=0:
        return 1/diff
    else:
        return 1


def add_track_to_grid(map, metric_a, metric_b, buckets_a, buckets_b, new_composition, target_chord):
    position = get_location_for_track(metric_a, metric_b, buckets_a, buckets_b)

    if(len(map[position])>MAX_PER_CELL):
        cached_comp_index = -1
        worst_fitness_found = 1
        for index, composition in enumerate(map[position]):
            final_chord =  composition.episodes[-1].chord_sequence.chords[-1]
            fitness = calc_fitness_based_on_final_chord(final_chord, target_chord)
            if(fitness<worst_fitness_found):
                worst_fitness_found = fitness
                cached_comp_index = index
        
        new_track_final_chord =  new_composition.episodes[-1].chord_sequence.chords[-1]
        new_track_fitness = calc_fitness_based_on_final_chord(new_track_final_chord, target_chord)
        if(new_track_fitness>worst_fitness_found):
            #print(f"Removing track with fitness {worst_fitness_found} with track with fitness {new_track_fitness}")
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

    #Generate mutation
    mutated_nros = mutate_nro_sequence(extracted_compound_nro_list)

    #Generate new composition from mutated NRO list
    mutated_chord_list = generate_chord_list_for_new_nros(extracted_chordseq.chords, mutated_nros)
    mutated_chord_sequence = NRTChordSequence(extracted_chordseq.spec, mutated_chord_list, extracted_duration, extracted_chordseq.tick_durations, mutated_nros)
    mutated_episode = NRTEpisode(chord_seq= mutated_chord_sequence, dur_ms = extracted_duration)

    mutated_comp = NRTComposition( episodes = [mutated_episode])
    mutated_comp.melody_on = False
    mutated_comp.bassline_on = False
    mutated_comp.percussion_on = False

    return  mutated_comp

def crossover_compositions(comp1, comp2):
    extracted_episode_1 = comp1.episodes[0]
    extracted_chordseq_1 = extracted_episode_1.chord_sequence
    extracted_duration_1 = extracted_episode_1.duration_ms
    extracted_compound_nro_list_1 = extracted_chordseq_1.compound_nros

    extracted_episode_2 = comp2.episodes[0]
    extracted_chordseq_2 = extracted_episode_2.chord_sequence
    extracted_duration_2 = extracted_episode_2.duration_ms
    extracted_compound_nro_list_2 = extracted_chordseq_2.compound_nros

    chilseq_1, childseq_2 = crossover_nro_sequence(extracted_compound_nro_list_1, extracted_compound_nro_list_2)

    #Generate child 1
    child1_chord_list = generate_chord_list_for_new_nros(extracted_chordseq_1.chords, chilseq_1)
    child1_chord_sequence = NRTChordSequence(extracted_chordseq_1.spec, child1_chord_list, extracted_duration_1, extracted_chordseq_1.tick_durations, extracted_compound_nro_list_1)
    child1_episode = NRTEpisode(chord_seq= child1_chord_sequence, dur_ms = extracted_duration_1)
    child1_comp = NRTComposition( episodes = [child1_episode])
    child1_comp.melody_on = False
    child1_comp.bassline_on = False
    child1_comp.percussion_on = False

    
    #Generate child 2
    child2_chord_list = generate_chord_list_for_new_nros(extracted_chordseq_2.chords, childseq_2)
    child2_chord_sequence = NRTChordSequence(extracted_chordseq_2.spec, child1_chord_list, extracted_duration_2, extracted_chordseq_2.tick_durations, extracted_compound_nro_list_2)
    child2_episode = NRTEpisode(chord_seq= child2_chord_sequence, dur_ms = extracted_duration_2)
    child2_comp = NRTComposition( episodes = [child2_episode])
    child2_comp.melody_on = False
    child2_comp.bassline_on = False
    child2_comp.percussion_on = False

    return child1_comp, child2_comp


def generate_starting_population(size, spec):
    start_pop = []
    for i in range(size):
        #print("Loop: " + str(i))
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

def evaluate_map(map, target_chord, print_file = False, output_file_name= ""):
    filled_cells = 0
    total_pop = 0
    total_max_cell_fitness = 0
    total_fit_cells = 0

    max_fit_matrix = np.zeros((10,10))

    for key in map:
        x=map[key]
        max_cell_fitness = 0
        if(len(x)>0):
            filled_cells+=1

            for composition in x:
                final_chord =  composition.episodes[-1].chord_sequence.chords[-1]
                fitness = calc_fitness_based_on_final_chord(final_chord, target_chord)
                if(fitness>max_cell_fitness):
                    max_cell_fitness = fitness
        total_pop+=len(x)
        total_max_cell_fitness+=max_cell_fitness
        
        if(max_cell_fitness==1):
            total_fit_cells+=1
        
        max_fit_matrix[key[0],key[1]] = max_cell_fitness
    
    average_grid_fitness = total_max_cell_fitness/len(map)


    
    print(f"Filled cells: {filled_cells} and total pop: {total_pop} Average Grid Fitness: {average_grid_fitness} Total Fit Cells: {total_fit_cells}")

    if(print_file):
        with open(output_file_name, 'w') as f:
            f.write(f"Filled Cells: {filled_cells}\n")
            f.write(f"Total Pop: {total_pop}\n")
            f.write(f"Average Grid Fitness: {average_grid_fitness}\n")
            f.write(f"Total Fit Cells: {total_fit_cells}\n")
        
    
    return max_fit_matrix

def generate_songs_from_map(map, output_folder, buckets_a, buckets_b, fit_only= True):
    #outpath = 'output_folder/'+output_folder+"/"
    #if not os.path.exists(output_folder):
    #    os.makedirs(outpath)
    
    for k in map:
        if(len(map[k])>0):
            loc_path = output_folder+"/"+str(k)+"/"
            os.makedirs(loc_path)
            counter = 1
            with open(loc_path+"/CellStats.txt", 'w') as f:
                f.write(f"MetricA Range: {buckets_a[k[0]]}\n")
                f.write(f"MetricB Range: {buckets_b[k[1]]}\n")

                for comp in map[k]:
                    
                    final_chord =  comp.episodes[-1].chord_sequence.chords[-1]
                    fitness = calc_fitness_based_on_final_chord(final_chord, TARGET_FINAL_CHORD)
                    if fitness == 1 or not fit_only:
                        comp.save_song(f"{loc_path}Track{str(counter)}.mid")
                    counter+=1
                    
                    f.write(f"Track{str(counter)} with fitness: {fitness}\n")
            

#def generate_map_cell_stats(cell, output_file_name)

def get_buckets_for_metric(metric):
    if metric== me.metric_type.Avg_NRO_Shift:
        return  generate_buckets(0, 3, 10)
    elif metric == me.metric_type.Major_Minor_ChordRatio:
        return generate_buckets(0,1,10)
    elif metric == me.metric_type.Track_Mood:
        return generate_buckets(0,1,10)

def map_elites_run(iteration_count, output_folder, metric_a, metric_b, mut_chance, cross_chance, fit_only_generated):
        #Generate a random starting population

    if not os.path.exists(output_folder):
        # If it doesn't exist, create it
        os.makedirs(output_folder)


    test_start_pop = generate_starting_population(100, TEST_CHORD_SPEC)
    
    map = generate_grid(10,10)

    #ns_buckets = generate_buckets(0, 3, 10)
    #mm_buckets = generate_buckets(0,1,10)
    a_buckets= get_buckets_for_metric(metric_a)
    b_buckets= get_buckets_for_metric(metric_b)

    
    with open(output_folder+"/Run_Config.txt", 'w') as f:
        f.write(f"Loop count: {iteration_count}\n\n")
        f.write(f"MetricA: {metric_a}\n")
        f.write(f"MetricB: {metric_b}\n")
        f.write(f"MetricA buckets: {a_buckets}\n")
        f.write(f"MetricB buckets: {b_buckets}\n\n")
        f.write(f"Mutation Rate: {mut_chance}\n")
        f.write(f"Mutation Rate: {cross_chance}\n")


    
    for c in test_start_pop:
        add_track_to_grid(map,me.calc_average_nro_shift(c), me.calc_majorchord_ratio(c), a_buckets, b_buckets, c,  TARGET_FINAL_CHORD)

    #print(map)

    print("Starting pop map details:")
    max_fit_matrix = evaluate_map(map, TARGET_FINAL_CHORD)

    
    generate_map_heatmap(max_fit_matrix, a_buckets,b_buckets, "Initial Pop Heatmap", output_folder+"/InitialPopHeatmap.png")

    for i in range(0, iteration_count):
        rand_comp_1 = select_random_track_from_grid(map)
        rand_comp_2 = select_random_track_from_grid(map)

        if(random.uniform(0,1)<mut_chance):
            rand_comp_1 = mutate_composition(rand_comp_1)
        
        if(random.uniform(0,1)<mut_chance):
            rand_comp_2 = mutate_composition(rand_comp_1)

        if(random.uniform(0,1)<cross_chance):
            #print(f"Pre crossover chord sequence: {rand_comp_1.episodes[0].chord_sequence.chords} ")
            rand_comp_1, rand_comp_2 = crossover_compositions(rand_comp_1, rand_comp_2)
            #print(f"Post crossover chord sequence: {rand_comp_1.episodes[0].chord_sequence.chords} ")

        add_track_to_grid(map,me.get_metric_value_for_metric(rand_comp_1, metric_a), me.get_metric_value_for_metric(rand_comp_1, metric_b), a_buckets, b_buckets, rand_comp_1,  TARGET_FINAL_CHORD)
        add_track_to_grid(map,me.get_metric_value_for_metric(rand_comp_2, metric_a), me.get_metric_value_for_metric(rand_comp_2, metric_b), a_buckets, b_buckets, rand_comp_2,  TARGET_FINAL_CHORD)


        if(i%1000==0):
            print("Map at loop " + str(i))
            evaluate_map(map, TARGET_FINAL_CHORD)
    
    
    print("Final map details:")
    max_fit_matrix = evaluate_map(map, TARGET_FINAL_CHORD, True, output_folder+"/FinalMapData.txt")

    print(max_fit_matrix)
    
    generate_map_heatmap(max_fit_matrix,a_buckets,b_buckets, "Final Fitness Heatmap", output_folder+"/FinalHeatMap.png")

    generate_songs_from_map(map, output_folder, a_buckets, b_buckets, fit_only_generated)

def generate_map_heatmap(fit_matrix, buckets_a, buckets_b, plot_title, file_name):

    first_increm_a = []
    for bucket in buckets_a:
        first_increm_a.append(bucket[0])

    first_increm_b = []

    for bucket in buckets_b:
        first_increm_b.append(bucket[0])

    df_cm = pd.DataFrame(fit_matrix, index = first_increm_a,
                    columns = first_increm_b)
    
    ax = sns.heatmap(df_cm, vmin=0, vmax=1, annot=False)
    plt.title(plot_title)
    plt.show()

    #fig = hexplot.fig
    fig = ax.get_figure()
    fig.savefig(file_name) 
    
    #plt.savefig(file_name,dpi=300, bbox_inches="tight")
    plt.close()
    return

if __name__ == "__main__":
    print(f"Seaborn ver: {sns.__version__}")
    #"""
    comp_spec  = copy.deepcopy(TEST_CHORD_SPEC)
    episode_spec = NRTEpisodeSpec(comp_spec, melody_spec, bass_spec, percussion_spec)
    test_composition = NRTComposition(episode_specs = [episode_spec])
    #composition.chords_on = False
    test_composition.melody_on = False
    test_composition.bassline_on = False
    test_composition.percussion_on = False

    chord_list = test_composition.episodes[0].chord_sequence.chords

    print(chord_list)

    me.calc_mode_for_chordlist(test_composition)
    #"""

    #map_elites_run(1000, "HeatmapTestNew", me.metric_type.Avg_NRO_Shift, me.metric_type.Major_Minor_ChordRatio, 0.5, 0.5, True)



