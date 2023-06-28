import os
from NRTCompositions import *
from NRTChordSequences import *
from NROs import *
from OLD_GENRT.Chords import *
import old_metricExtraction 
import mapElites

from datetime import *
import seaborn as sns; sns.set_theme()
import matplotlib.pyplot as plt
import numpy as np
from random import randint


primary_chord_channels = [0, 1, 2]
secondary_chord_channels = [3, 4, 5]
primary_melody_channel = 6
secondary_melody_channel = 7
primary_bass_channel = 8
secondary_bass_track = 10
percussion_channel = 9

start_chord = Trichord([48, 52, 55])
fixed_key = KeySignature("C", "maj")
focal_note = 48
chord_instrument_num = 48 # harp
chord_instrument_num2 = 48 # harpsichord
melody_instrument_num = 42  # blown bottle
melody_instrument_num2 = 42
bass_instrument_num = 39 # synth bass
bass_instrument_num2 = 42
cmaj = KeySignature("C", "maj")

event1 = NRTEvent(AntagonismCNRO, 52000, True)
event2 = NRTEvent(HeroismCNRO, 60000)

episode1_chord_spec = NRTChordSequenceSpec(instrument_num=chord_instrument_num,
                                           start_chord=start_chord,
                                           rhythm_string="1:1/1:1/1",
                                           target_episode_duration=70000,
                                           start_target_chord_duration=4000,
                                           end_target_chord_duration=2000,
                                           start_volume=30,
                                           end_volume=80,
                                           min_cnro_length=1,
                                           max_cnro_length=2,
                                           focal_note=focal_note,
                                           fixed_key=None,
                                           is_classic=True,
                                           end_event=event1,
                                           episode_overlap_chords=0)

episode2_chord_spec = NRTChordSequenceSpec(instrument_num=chord_instrument_num,
                                           start_chord=start_chord,
                                           rhythm_string="1:1/1:1/1",
                                           target_episode_duration=20000,
                                           start_target_chord_duration=2000,
                                           end_target_chord_duration=4000,
                                           start_volume=80,
                                           end_volume=50,
                                           min_cnro_length=1,
                                           max_cnro_length=3,
                                           focal_note=focal_note,
                                           fixed_key=None,
                                           is_classic=False,
                                           end_event=event2,
                                           episode_overlap_chords=0)

episode1_melody_spec = NRTMelodySpec(instrument_num=melody_instrument_num2,
                                     rhythm_string="1:1/1:1/1",
                                     fixed_key=cmaj,
                                     start_volume=50,
                                     end_volume=127,
                                     is_voice_leading=True,
                                     chord_splits_allowed=[1, 2, 4, 8, 16],
                                     note_length=1,
                                     episode_overlap_chords=3)

episode2_melody_spec = NRTMelodySpec(instrument_num=melody_instrument_num,
                                     rhythm_string="1:2/4:1/16,1:3/4:1/16,1:4/4:1/16",
                                     fixed_key=None,
                                     start_volume=127,
                                     end_volume=50,
                                     is_voice_leading=True,
                                     chord_splits_allowed=[1, 2, 4, 8, 16],
                                     note_length=1,
                                     episode_overlap_chords=0)

episode1_bass_spec = NRTBasslineSpec(instrument_num=bass_instrument_num,
                                     rhythm_string="1:1/1:1/1",
                                     start_volume=50,
                                     end_volume=127,
                                     episode_overlap_chords=3)

episode2_bass_spec = NRTBasslineSpec(instrument_num=bass_instrument_num2,
                                     rhythm_string="1:1/1:1/1",
                                     start_volume=127,
                                     end_volume=50,
                                     episode_overlap_chords=3)

drum_rstring = "1:1/8,1:4/8,1:5/8"
highhat_rstring = "1:1/8,1:2/8,1:3/8,1:4/8,1:5/8,1:6/8,1:7/8,1:8/8"
cymbal_rstring = "1:6/8,1:7/8"

episode1_percussion_spec = NRTPercussionSpec(instrument_nums=[35, 59, 51],
                                             rhythm_strings=[drum_rstring, highhat_rstring, cymbal_rstring],
                                             start_volumes=[0, 0, 0],
                                             end_volumes=[0, 0, 0])

episode2_percussion_spec = NRTPercussionSpec(instrument_nums=[35, 59, 51],
                                             rhythm_strings=[drum_rstring, highhat_rstring, cymbal_rstring],
                                             start_volumes=[0, 0, 0],
                                             end_volumes=[0, 0, 0])


episode1_spec = NRTEpisodeSpec(episode1_chord_spec, episode1_melody_spec, episode1_bass_spec, episode1_percussion_spec)
episode2_spec = NRTEpisodeSpec(episode2_chord_spec, episode2_melody_spec, episode2_bass_spec, episode2_percussion_spec)
composition_a = NRTComposition(episode_specs = [episode1_spec])


nro_length = len(composition_a.episodes[0].chord_sequence.compound_nros)
print(f"Generated Track Compound nro length a : {nro_length}")

composition_b = NRTComposition(episode_specs = [episode1_spec])
nro_length = len(composition_b.episodes[0].chord_sequence.compound_nros)
print(f"Generated Track Compound nro length b : {nro_length}")
composition_c = NRTComposition(episode_specs = [episode1_spec])

nro_length = len(composition_c.episodes[0].chord_sequence.compound_nros)
print(f"Generated Track Compound nro length c : {nro_length}")
composition_d = NRTComposition(episode_specs = [episode1_spec])

nro_length = len(composition_d.episodes[0].chord_sequence.compound_nros)
print(f"Generated Track Compound nro length d: {nro_length}")


"""
#composition.chords_on = False
composition_a.melody_on = False
composition_a.bassline_on = False
composition_a.percussion_on = False

composition_a.save_song("output_tracks/ChordsOnly5.mid")

#avg_nro_shift = metricExtraction.calc_average_nro_shift(composition_a)

#print(f"Avg NRO shift: {avg_nro_shift}")

#Testing creating a track from a track
extracted_episode = composition_a.episodes[0]
extracted_specs = composition_a.episode_specs

extracted_chordseq = extracted_episode.chord_sequence
extracted_duration = extracted_episode.duration_ms

new_episode = NRTEpisode(chord_seq= extracted_chordseq, dur_ms = extracted_duration)
new_composition = NRTComposition( episodes = [new_episode])

new_composition.melody_on = False
new_composition.bassline_on = False
new_composition.percussion_on = False

new_composition.save_song("output_tracks/CopiedTrack5.mid")

print("Pre_mutation compound NROs")
for nro in extracted_episode.chord_sequence.compound_nros:
    print(nro)
#print(extracted_episode.chord_sequence.compound_nros)

mutated_seq = mapElites.mutate_nro_sequence(extracted_episode.chord_sequence.compound_nros)

print("Post mutation compound NROs")

for nro in mutated_seq:
    print(nro)
#print(mutated_seq)

print("Pre_mutation Extracted Chord sequence")
print(str(new_episode.chord_sequence))

mutated_chord_list = mapElites.generate_chord_list_for_new_nros(extracted_chordseq.chords, mutated_seq)

print(extracted_chordseq.tick_durations)


mutated_chord_sequence = NRTChordSequence(extracted_chordseq.spec, mutated_chord_list, extracted_duration, extracted_chordseq.tick_durations, mutated_seq)

mutated_episode = NRTEpisode(chord_seq= mutated_chord_sequence, dur_ms = extracted_duration)

print("Post_mutation Extracted Chord sequence")
print(str(mutated_episode.chord_sequence))


mutated_composition = NRTComposition( episodes = [mutated_episode])

mutated_composition.melody_on = False
mutated_composition.bassline_on = False
mutated_composition.percussion_on = False

mutated_composition.save_song("output_tracks/MutatedTrack5.mid")

track_fitness = mapElites.calc_fitness_based_on_final_chord(mutated_chord_list[-1],start_chord)

print("New track fitness: " + str(track_fitness))



#print(composition)

"""

"""
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
    ax.set_xlim(xmin=0.1)
    ax.set_ylim(ymin=0.4)
    ax.spines['left'].set_color("black")
    ax.spines['left'].set_linewidth(0.5)
    ax.spines['bottom'].set_color("black")
    ax.spines['bottom'].set_linewidth(0.5)
    ax.grid(color = "black", linestyle = "dashed", linewidth = 0.1)
    ax.set_facecolor((1.0, 1.0,1.0))

    #plt.show()
    
    plt.savefig(f"{outpath}{metric1_name},{metric2_name} ERA Scatterplot")
"""



#Testing multiple track generation and ERA visualisation


#run_name = "SepFuncTest1"
##track_count_to_generate = 1000
#out_folder = (f"output_tracks/{run_name}/")
#try: 
#    os.mkdir(out_folder) 
#except OSError as error: 
#    print(error) 

#episode1_spec = NRTEpisodeSpec(episode1_chord_spec, episode1_melody_spec, episode1_bass_spec, episode1_percussion_spec)
#episode2_spec = NRTEpisodeSpec(episode2_chord_spec, episode2_melody_spec, episode2_bass_spec, episode2_percussion_spec)

#metricExtraction.generate_and_visualise_songset(track_count_to_generate, [episode1_spec, episode2_spec], out_folder)



"""
majorratio_dict = dict()
bassdiff_dict = dict()
majorratios = list()
bassdiffs = list()
tracks_dict = dict()

for i in range(track_count_to_generate):
    #episode1_spec = NRTEpisodeSpec(episode1_chord_spec, episode1_melody_spec, episode1_bass_spec, episode1_percussion_spec)
    #episode2_spec = NRTEpisodeSpec(episode2_chord_spec, episode2_melody_spec, episode2_bass_spec, episode2_percussion_spec)
    composition = NRTComposition([episode1_spec, episode2_spec])

    tracks_dict[i] = composition

    #print(composition)

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

    majorratio_dict[i] = (tot_majorchords/tot_chords)
    majorratios.append(tot_majorchords/tot_chords)

    print(f"For track{i} a total of {tot_chords} chords were generated with {tot_majorchords} being major, giving a major ratio of {(tot_majorchords/tot_chords)}")

    #Extract average bass note shift
    tot_bassnotes = 0
    tot_bassshift = 0
    prev_note = 0

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

    tracks_dict[min_key].save_song(out_folder+"/MinMajorRatio.mid")
    tracks_dict[max_key].save_song(out_folder+"/MaxMajorRatio.mid")


    metricExtraction.basic_era_scatter("Major_Chord_Ratio", "Avg Bassnote Shift", majorratios, bassdiffs,out_folder)
"""


#os.system(f"fluidsynth --quiet --no-shell new_song.mid")


""" 

FOR SAVING MP3 FILES 
os.system(f"timidity --quiet new_song.mid -Ow -o new_song.ogg")
os.system(f"ffmpeg -y -i new_song.ogg -acodec libmp3lame -ab 64k -loglevel quiet -hide_banner new_song.mp3")

FOR PLAYING MP3 FILES
os.system(f"ffplay -nodisp -autoexit -loglevel -8 -hide_banner new_song.mp3")

midi_file = MidiFile(type=1)

for i in range(0, 100):
    track = MidiTrack()
    midi_file.tracks.append(track)
    track.append(Message('program_change', channel=1, program=1, time=0))
    track.append(Message(type='note_on', channel=1, note=20 + i, velocity=127, time=0))
    track.append(Message(type='note_off', channel=1, note=20 + i, velocity=127, time=1800))

midi_file.save("new_song.mid")
os.system(f"fluidsynth --quiet --no-shell new_song.mid")
"""
