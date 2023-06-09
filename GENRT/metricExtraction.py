
import matplotlib.pyplot as plt
from enum import Enum
from NRTCompositions import *

class ChordMode(Enum):
    LYDIAN = 1
    IONIAN = 2
    MIXOLYDIAN = 3
    DORIAN = 4
    AEOLIAN = 5
    PHRYGIAN = 6
    LOCRIAN = 7

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

    total_nro_shift = 0
    total_chords = 0

    comp_episodes = composition.episodes
    for ep in comp_episodes:
        compound_nros = ep.chord_sequence.compound_nros
        for c in compound_nros:
            #print(f"C:{c}")
            if(c!="None"):
                nro_sequence = c.nros
                total_chords+=1
                total_nro_shift+=len(nro_sequence)
                #print(nro_sequence)
    
    return total_nro_shift/total_chords

def calc_chord_mode():
    return


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