import random
import copy
import os
import pandas as pd
from enum import Enum
import numpy as np
from datetime import datetime
import metricCalculation as metCalc
import musicGeneration as musGen
import matplotlib.pyplot as plt
import seaborn as sns; sns.set_theme()
from music21 import *
import musicTracks as mt

MAX_PER_CELL = 2

d = duration.Duration(2.0)
CMAJ = chord.Chord(["E4","C4","G4"], duration = d)



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
        if(value_a<=b[1]):
            a_index=counter
            a_loc_found= True
            break
        counter+=1
    
    counter = 0
    for b in buckets_b:
        if(value_b<=b[1]):
            b_index=counter
            b_loc_found= True
            break
        counter+=1
    
    if(a_loc_found and b_loc_found):
        return a_index, b_index

    else:
        print(f"ERROR: Track does not fit in grid for met value: {value_a},{value_b}")
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
def mutate_nro_sequence(nro_sequence, max_length, mut_chance):
    for i, cnro in enumerate(nro_sequence):
        if(random.uniform(0,1)<mut_chance):
            nro_sequence[i] = musGen.generate_random_compound_nro(max_length)
    return nro_sequence

def crossover_nro_sequence(seq1, seq2):
    crosspoint = random.randint(0, len(seq1))

    child1 = seq1[:crosspoint]+seq2[crosspoint:]
    child2 = seq2[:crosspoint]+seq1[crosspoint:]

    return child1, child2
        
def calc_fitness_based_on_key_confidence(track):
    return track.stream.analyze('key').correlationCoefficient

def calc_track_fitness(track):
    contains_duplicates = False
    prev_chord = None
    for chord in track.chord_seq:
        if chord == prev_chord:
            contains_duplicates = True
        prev_chord = chord

    if contains_duplicates:
        return 0
    else:
        return calc_fitness_based_on_key_confidence(track)

def add_track_to_grid(map, new_track, buckets_a, buckets_b):
    position = get_location_for_track(new_track.metric_a, new_track.metric_b, buckets_a, buckets_b)

    if(len(map[position])>MAX_PER_CELL):
        cached_comp_index = -1
        worst_fitness_found = 1
        for index, t in enumerate(map[position]):
            fitness = calc_track_fitness(t)
            if(fitness<worst_fitness_found):
                worst_fitness_found = fitness
                cached_comp_index = index
        
        new_track_fitness= calc_track_fitness(new_track)
        if(new_track_fitness>worst_fitness_found):
            #print(f"Removing track with fitness {worst_fitness_found} with track with fitness {new_track_fitness}")
            del map[position][cached_comp_index]
            map[position].append(new_track)
    else:
        map[position].append(new_track)
    
    return map


def generate_starting_population(size, track_length, metric_a, metric_b, max_cnro_length):
    start_pop = []
    for i in range(size):
        rand_nro_seq = musGen.generate_random_compound_nro_sequence(track_length, max_cnro_length)
        start_pop.append(mt.musicTrack(chord.Chord(musGen.generate_random_admissable_chord(60,72), duration = d), rand_nro_seq, metric_a, metric_b))

    
    return start_pop


def evaluate_map(map, a_size, b_size, print_file = False, output_file_name= ""):
    filled_cells = 0
    total_pop = 0
    total_max_cell_fitness = 0
    total_fit_cells = 0

    max_fit_matrix = np.zeros((a_size,b_size))

    for key in map:
        x=map[key]
        max_cell_fitness = 0
        if(len(x)>0):
            filled_cells+=1

            for track in x:
                fitness = calc_track_fitness(track)
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
        
    
    return max_fit_matrix, total_pop, filled_cells, average_grid_fitness

def generate_songs_from_map(map, output_folder, buckets_a, buckets_b, fit_only= True):
    
    for k in map:
        if(len(map[k])>0):
            loc_path = output_folder+"/"+str(k)+"/"
            os.makedirs(loc_path)
            counter = 1
            with open(loc_path+"/CellStats.txt", 'w') as f:
                f.write(f"MetricA Range: {buckets_a[k[0]]}\n")
                f.write(f"MetricB Range: {buckets_b[k[1]]}\n")

                for track in map[k]:
                    
                    #final_chord =  track.chord_seq[-1]
                    fitness = calc_track_fitness(track)
                    if fitness == 1 or not fit_only:
                        s = musGen.chord_seq_to_stream(track.chord_seq)
                        musGen.save_stream_to_midi(s, f"{loc_path}Track{str(counter)}.mid")

                        
                        with open(f"{loc_path}/Track{str(counter)}.txt", 'w') as t:
                            t.write(f"Track fitness: {fitness}\n")
                            t.write(f"Track Metric A Val: {track.metric_a}\n")
                            t.write(f"Track Metric B Val: {track.metric_b}\n")
                            #print(f"Metric b val: {track.metric_b}")
                            #print(f"CNRO Seq: {track.cnro_seq}")
                            t.write(f"Track Mode: {metCalc.MusicModes(track.metric_a).name}\n")

                            t.write(f"Track Is Complete (CNRO Sequence Admissible): {track.is_complete_track}\n")
                        
                            
                            t.write(f"Music Mode Info:\n")
                            ays = s.analyze('key')
                            t.write(f"Track Predicted Key: {ays}\n")
                            t.write(f"Predicted key correlation coefficient: {ays.correlationCoefficient}")


                            t.write(f"\nChord List:\n")
                            for c in track.chord_seq:
                                t.write(f"{str(c)}\n")
                                #for n in c.notes:
                                    #t.write(n)
                                
                            t.write(f"\nCompound NRO List:\n")
                            for i, cn in enumerate(track.cnro_seq):
                                t.write(f"CNRO {i}\n")
                                for nro in cn:
                                    t.write(f"{str(nro)}\n")
                    
                    f.write(f"Track{str(counter)} with fitness: {fitness}\n")

                    counter+=1
            

def get_buckets_for_metric(metric):
    if metric== metCalc.metric_type.Avg_NRO_Shift:
        return  generate_buckets(1, 5, 10)
    elif metric == metCalc.metric_type.Major_Minor_ChordRatio:
        return generate_buckets(0,1,10)
    elif metric == metCalc.metric_type.Track_Mood:
        return generate_buckets(0.5,7.5,7)

def map_elites_run(iteration_count, run_name, track_length, metric_a, metric_b, mut_chance, cross_chance, fit_only_generated, max_cnro_length):
    
    
    output_folder = f"{os.getcwd()}/output_folder/{run_name}/"

    if not os.path.exists(output_folder):
        # If it doesn't exist, create it
        os.makedirs(output_folder)

    
    mood_names = []
    if(metric_a == metCalc.metric_type.Track_Mood):
        for m in metCalc.MusicModes:
            mood_names.append(m.name)


    start_pop = generate_starting_population(500, track_length, metric_a, metric_b, max_cnro_length)
    
    a_buckets= get_buckets_for_metric(metric_a)
    b_buckets= get_buckets_for_metric(metric_b)

    
    map = generate_grid(len(a_buckets), len(b_buckets))

    
    with open(output_folder+"/Run_Config.txt", 'w') as f:
        f.write(f"Loop count: {iteration_count}\n\n")
        f.write(f"Track Length: {track_length}\n\n")
        f.write(f"MetricA: {metric_a}\n")
        f.write(f"MetricB: {metric_b}\n")
        f.write(f"MetricA buckets: {a_buckets}\n")
        f.write(f"MetricB buckets: {b_buckets}\n\n")
        f.write(f"Mutation Rate: {mut_chance}\n")
        f.write(f"Crossover Rate: {cross_chance}\n")

    
    for track in start_pop:
        add_track_to_grid(map, track, a_buckets, b_buckets)

    #print(map)
    map_stats_over_time = []


    print("Starting pop map details:")
    max_fit_matrix, start_map_pop, start_filled, start_avg_fit = evaluate_map(map, len(a_buckets), len(b_buckets))

    map_stats_over_time.append([0, start_map_pop, start_filled, start_avg_fit])

    for i in range(0, iteration_count):
        track1 = select_random_track_from_grid(map)
        track2 = select_random_track_from_grid(map)
        rand_comp_cnro_seq1 = track1.get_cnro_seq()
        rand_comp_cnro_seq2 = track2.get_cnro_seq()
        #print(f"Premutation selected seq: {rand_comp_cnro_seq1}")

        mut_cnro_seq1 = mutate_nro_sequence(rand_comp_cnro_seq1, max_cnro_length, mut_chance)
        
        mut_cnro_seq2 = mutate_nro_sequence(rand_comp_cnro_seq2, max_cnro_length, mut_chance)

        if(random.uniform(0,1)<cross_chance):
            mut_cnro_seq1, mut_cnro_seq2 = crossover_nro_sequence(mut_cnro_seq1, mut_cnro_seq2)
        
        new_track1 = mt.musicTrack(track1.start_chord, mut_cnro_seq1, metric_a, metric_b)
        new_track2 = mt.musicTrack(track2.start_chord, mut_cnro_seq2, metric_a, metric_b)

        add_track_to_grid(map,new_track1, a_buckets, b_buckets)
        add_track_to_grid(map,new_track2, a_buckets, b_buckets)

        if(i%100==0):
            print("Map at loop " + str(i))
            max_fit_matrix, map_pop, filled, avg_fit  = evaluate_map(map, len(a_buckets), len(b_buckets))
            map_stats_over_time.append([i,map_pop, filled, avg_fit])
        
        if(i%5000 ==0):
            if(metric_a == metCalc.metric_type.Track_Mood):
                generate_map_heatmap(max_fit_matrix,a_buckets,b_buckets, f"Loop {i} Heatmap", f"{output_folder}/Loop {i} Heatmap.png", mood_names)
            else:
                generate_map_heatmap(max_fit_matrix,a_buckets,b_buckets, f"Loop {i} Heatmap", f"{output_folder}/Loop {i} Heatmap.png")
    
    
    print("Final map details:")
    max_fit_matrix, final_map_pop, final_filled, final_avg_fit = evaluate_map(map, len(a_buckets), len(b_buckets), True, output_folder+"/FinalMapData.txt")
    map_stats_over_time.append([iteration_count,final_map_pop, final_filled, final_avg_fit])

    stats_df = pd.DataFrame(map_stats_over_time, columns = ['Loop Count','Population', 'Filled Cells', 'Avg Fitness'])

    stats_df.to_csv(output_folder+"/RunStats.csv")

    print(stats_df.head)

    print(max_fit_matrix)

    pd.DataFrame(max_fit_matrix).to_csv(output_folder+"/FitMatrix.csv")

    if(metric_a == metCalc.metric_type.Track_Mood):

        generate_map_heatmap(max_fit_matrix,a_buckets,b_buckets, "Final Fitness Heatmap", output_folder+"/FinalHeatMap.png", mood_names)
    else:
        generate_map_heatmap(max_fit_matrix,a_buckets,b_buckets, "Final Fitness Heatmap", output_folder+"/FinalHeatMap.png")

    generate_songs_from_map(map, output_folder, a_buckets, b_buckets, fit_only_generated)

def generate_map_heatmap(fit_matrix, buckets_a, buckets_b, plot_title, file_name, col_names_a= [], row_names_b= []):

    if(len(col_names_a)==0):
        for bucket in buckets_a:
            col_names_a.append(f"{round(bucket[0],2)} to {round(bucket[1],2)}")

    if(len(row_names_b)==0):
        for bucket in buckets_b:
            row_names_b.append(f"{round(bucket[0],2)} to {round(bucket[1],2)}")

    df_cm = pd.DataFrame(fit_matrix, index = col_names_a,
                    columns = row_names_b)
    
    ax = sns.heatmap(df_cm, vmin=0, vmax=1, annot=False)
    plt.title(plot_title)
    #plt.show()

    fig = ax.get_figure()
    fig.savefig(file_name,dpi=300, bbox_inches="tight") 
    
    plt.close()
    return

if __name__ == "__main__":
    print("Start")
    overall_start_time = datetime.now()

    map_elites_run(100, "Test-NoNROClass", 20, metCalc.metric_type.Track_Mood,metCalc.metric_type.Avg_NRO_Shift,  .2, .5, False, 5)

    #".2.5-5kFinalRunV2-NewSig"
    runtime_seconds=  datetime.now () -overall_start_time
    runtime_minutes = runtime_seconds/60
    print("Total Runtime: " + str(runtime_minutes) + " minutes")



