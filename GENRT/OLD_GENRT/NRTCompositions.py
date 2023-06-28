from NRTChordSequences import *
from NRTMelodies import *
from NRTBasslines import *
from NRTPercussion import *
from OLD_GENRT.Midi import *

class NRTComposition:

    def __init__(self, episode_specs = [], episodes=[]):
        #Original method to generate a composition stochastically based on specs
        if(len(episodes)==0):
            self.episodes = []
            self.episode_specs = episode_specs
            self.chords_on = True
            self.melody_on = True
            self.bassline_on = True
            self.percussion_on = True
            previous_episode = None
            episode_start_time_ms = 0

            for ind, episode_spec in enumerate(episode_specs):
                episode = NRTEpisode(episode_spec)
                self.episodes.append(episode)
                episode.first_stage_calculate_music(previous_episode, episode_start_time_ms)
                episode_start_time_ms += episode.chord_sequence.sequence_duration_ms
                previous_episode = episode

            previous_episode = None
            for ind, episode in enumerate(self.episodes):
                next_episode = None if ind >= len(self.episodes) - 1 else self.episodes[ind + 1]
                episode.second_stage_calculate_music(previous_episode, next_episode)
                previous_episode = episode
        #New method to generate directly from premade episodes
        else:
            self.episodes = episodes
            self.episode_specs = episode_specs
            self.chords_on = True
            self.melody_on = True
            self.bassline_on = True
            self.percussion_on = True


    def __str__(self):
        s = ""
        line = "======================================================="
        for num, episode in enumerate(self.episodes):
            dets = ""
            if episode.spec.chord_sequence_spec.fixed_key is not None:
                dets += "fixed:" + episode.spec.chord_sequence_spec.fixed_key.__str__()
            if episode.spec.chord_sequence_spec.focal_note is not None:
                dets += " focal:" + f"{episode.spec.chord_sequence_spec.focal_note}"
            s += f"{line} Episode {num + 1} {dets} {line}\n"
            for ind, l in enumerate(f"{episode.chord_sequence}".split("\n")):
                melody_string = ""
                tot_m_ticks = 0
                for note in episode.melody.bar_notes[ind]:
                    letter = note_letters[(note.note_num + 3) % 12]
                    splits = ""
                    for i in range(1, note.num_splits):
                        splits += "-"
                    melody_string += f"{letter}{splits} "
                    tot_m_ticks += note.duration_ticks
                s += l + f"    {melody_string.strip().ljust(35)} ({tot_m_ticks} ticks)" + "\n"
        return s

    def save_song(self, file_name):
        midi_file = MidiUtils.get_midi_file(type=1)

        #print(f"Midifile length after instantiation:{midi_file.length}")
        #midi_file = MidiFile(1)
        for ind, episode in enumerate(self.episodes):
            next_episode = None if ind == len(self.episodes) - 1 else self.episodes[ind + 1]
            episode.add_music_to_midi(next_episode, self.chords_on, self.melody_on, self.bassline_on, self.percussion_on)
        midi_file.save(file_name)
        #print(f"Midifile length after tracks adding:{midi_file.length}")
        #midi_file.close()


class NRTEpisodeSpec:
    def __init__(self, chord_sequence_spec, melody_spec, bassline_spec, percussion_spec):
        self.chord_sequence_spec = chord_sequence_spec
        self.melody_spec = melody_spec
        self.bassline_spec = bassline_spec
        self.percussion_spec = percussion_spec

class NRTEpisode:

    def __init__(self, spec=[], chord_seq=None, dur_ms = 1000):
        
        if(chord_seq==None):
            #Original method, generating an episode from a spec
            self.chord_sequence = None
            self.melody = None
            self.bassline = None
            self.percussion = None
            self.spec = spec
            self.duration_ms = 1000
        #Generate directly from a chord sequence
        else:
            self.chord_sequence = chord_seq
            self.melody = None
            self.bassline = None
            self.percussion = None
            self.spec = None
            self.duration_ms = dur_ms

    def __str__(self):
        return f"{self.chord_sequence}"

    def first_stage_calculate_music(self, previous_episode, start_timestamp):
        self.chord_sequence = NRTChordSequence(self.spec.chord_sequence_spec)
        self.chord_sequence.calculate_chords(previous_episode, start_timestamp)
        self.melody = NRTMelody(self.spec.melody_spec)
        self.melody.first_stage_calculate_notes(self.chord_sequence, previous_episode)
        self.bassline = NRTBassline(self.spec.bassline_spec)
        self.bassline.calculate_notes(self.chord_sequence, previous_episode)
        self.percussion = NRTPercussion(self.spec.percussion_spec)
        self.percussion.calculate_notes(self.chord_sequence, previous_episode)

    def second_stage_calculate_music(self, previous_episode, next_episode):
        self.melody.second_stage_calculate_notes(self.chord_sequence, previous_episode, next_episode)

    def add_music_to_midi(self, next_episode, chords_on, melody_on, bassline_on, percussion_on):
        next_spec = None if next_episode is None else next_episode.spec
        if chords_on:
            self.chord_sequence.set_midi_instruments(next_spec)
            self.chord_sequence.add_music()
        if melody_on:
            self.melody.set_midi_instruments(next_spec)
            self.melody.add_music()
        if bassline_on:
            self.bassline.set_midi_instrument(next_spec)
            self.bassline.add_music()
        if percussion_on:
            self.percussion.add_music()