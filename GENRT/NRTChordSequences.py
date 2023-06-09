import random
from NROs import *
from Chords import *
from Rhythms import *
from Midi import *


#The spec holds the requirements for generating a chord sequence 
class NRTChordSequenceSpec:
    def __init__(self, instrument_num=46,
                 start_chord=Trichord([60, 64, 67]), rhythm_string="1/4",
                 target_episode_duration=10000,
                 start_target_chord_duration=1000, end_target_chord_duration=1000,
                 start_volume=64, end_volume=64,
                 min_cnro_length=1, max_cnro_length=1,
                 focal_note=None, fixed_key=None,
                 is_classic=False, end_event=None,
                 episode_overlap_chords=0):
        self.instrument_num = instrument_num
        self.start_chord = start_chord
        self.rhythm_string = rhythm_string
        self.target_episode_duration = target_episode_duration
        self.start_target_chord_duration = start_target_chord_duration
        self.end_target_chord_duration = end_target_chord_duration
        self.start_volume = start_volume
        self.end_volume = end_volume
        self.min_cnro_length = min_cnro_length
        self.max_cnro_length = max_cnro_length
        self.focal_note = focal_note
        self.fixed_key = fixed_key
        self.is_classic = is_classic
        self.end_event = end_event
        self.episode_overlap_chords = episode_overlap_chords

class NRTChordSequence:

    def __init__(self, spec, chords = [], sequence_duration_ms = 0, tick_durations = [], compound_nros = [], start_time_stamp = 0):
        

        #print(f"Input Compound Nros: {len(compound_nros)}")
        #print(f"Input Chords: {len(chords)}")
        self.spec = spec
        self.chords = chords
        self.sequence_duration_ms = sequence_duration_ms
        self.tick_durations = tick_durations
        self.compound_nros = []
        #print(f"vs self nros {len(self.compound_nros)}")
        #print(f"vs self chords {len(self.chords)}")

        #Extra step when generating a chord sequence from a pregenerated chord list:
        if(len(chords)>0):
            #Hack to avoid each new track being longer and longer. 0 idea why it should matter, but an expanding list of compound nros was getting passed in
            self.compound_nros = compound_nros
            duration_addon = 0
            for ind, chord in enumerate(self.chords):
                chord.timestamp_ms = start_time_stamp + duration_addon
                chord.duration_ticks = self.tick_durations[ind]
                chord.rhythm = Rhythm(self.spec.rhythm_string, chord.duration_ticks)
                duration_addon += (chord.duration_ticks / 960) * 1000
            #print("Sequence right after generation")
            #print(self)

    def __str__(self):
        s = ""
        for i, chord in enumerate(self.chords):
            s += f"[{chord.timestamp_ms:.0f}ms]".ljust(15)
            nro = "" if self.compound_nros[i] is None else f"== {self.compound_nros[i]} ==>"
            s += nro.ljust(23)
            s += f"{chord}".ljust(17)
            s += f"{chord.notes[0]},{chord.notes[1]},{chord.notes[2]}".ljust(10)
            s += f"{chord.duration_ticks} ticks\n"
        return s.strip()

    def calculate_chords(self, previous_episode, start_timestamp):

        #Get the details from the previous episode, primarily its final chord to use as the start of this new episodes chords 
        if previous_episode is not None and previous_episode.spec.chord_sequence_spec.end_event is not None:
            if previous_episode.spec.chord_sequence_spec.end_event.change_fixed_key is True:
                last_chord = previous_episode.chord_sequence.chords[-1]
                self.spec.fixed_key = last_chord.get_key_signature()

        spec = self.spec

        start_chord_duration = spec.start_target_chord_duration
        target_final_chord_duration = spec.end_target_chord_duration
        takeoff = 0
        if spec.end_event is not None:
            target_episode_duration = spec.end_event.timestamp - start_timestamp
        else:
            target_episode_duration = spec.target_episode_duration
            takeoff = 1

        #So, what on earth is happening here
        #Must be to do with target lengths for a chord 
        #Also, clearly bugged, start chord duration is getting plused and minused 
        #Also, isnt muliplying both sides by 2 pretty redundant?

        #n appears to be the number of chords that will be generated 
        #Then x is the change that needs to happen between chords to reach the target length 

        n = int((2 * target_episode_duration - start_chord_duration + target_final_chord_duration) // (2 * start_chord_duration + target_final_chord_duration - start_chord_duration))
        x = (start_chord_duration - target_final_chord_duration) / n

        shortt = (n * start_chord_duration) - (x * (n - 1) * n) / 2
        diff = target_episode_duration - shortt
        addon = diff / n
        n -= takeoff

        #I think this is calculating the actual length of track
        for i in range(0, n + 1):
            ms_duration = (start_chord_duration - (i * x)) + addon
            #This seems clunky. Could we just * .96
            tick_duration = int(round((ms_duration / 1000) * 960))
            self.tick_durations.append(tick_duration)

        num_chords = n + 1
        must_make_maj_or_min = False
        #Dont generate the last two chords if we have a specified end event
        if spec.end_event is not None:
            num_chords -= 2
        elif next_episode is not None and next_episode.chord_sequence_spec.is_classic:
            num_chords -= 1
            must_make_maj_or_min = True
        
        #nro_count = self.compound_nros
        #print(f"Num chords requested: {num_chords} and current nro count: {nro_count}")

        inherited_chord = None
        if previous_episode is not None:
            inherited_chord = previous_episode.chord_sequence.chords[-1]
        else:
            self.chords = [self.spec.start_chord]
            self.compound_nros.append("None")

        #Generate random chords for specified length 
        while len(self.chords) < num_chords:
            self.apply_admissable_random_compound_nro(spec.min_cnro_length, spec.max_cnro_length, inherited_chord)
            inherited_chord = None

        #Not sure why we have to add a minor or major chord before adding the final end event 
        if spec.end_event is not None:
            self.apply_admissible_major_or_minor_compound_nro(spec.min_cnro_length, spec.max_cnro_length)
            self.add_emotional_cnro(spec.end_event.compound_nro)
        elif must_make_maj_or_min:
            self.apply_admissible_major_or_minor_compound_nro(spec.min_cnro_length, spec.max_cnro_length)

        duration_addon = 0
        for ind, chord in enumerate(self.chords):
            chord.timestamp_ms = start_timestamp + duration_addon
            chord.duration_ticks = self.tick_durations[ind]
            chord.rhythm = Rhythm(self.spec.rhythm_string, chord.duration_ticks)
            duration_addon += (chord.duration_ticks / 960) * 1000
        self.sequence_duration_ms = duration_addon

    #Going to rename this method from 'apply_admissible_major_or_minor_compound_nro' as that name is misleading
    #What is does is add annother chord as a bridge to a desired end event 
    #A chord which is forced to be either major or minor (I didnt know there were other types of chord? \_0_/)
    def apply_admissible_major_or_minor_compound_nro(self, min_compound_length, max_compound_length):
        self.apply_admissable_random_compound_nro(min_compound_length, max_compound_length, None, True)

    def apply_admissable_random_compound_nro(self, min_compound_length, max_compound_length,
                                             inherited_chord, requires_minor_or_major=False):
        compound_nro = None
        compound_length = random.randint(min_compound_length, max_compound_length)
        next_chord = None
        last_chord = inherited_chord if inherited_chord is not None else self.chords[-1]
        is_ok = False
        trials = 0
        while not is_ok:
            if self.spec.is_classic:
                last_chord = Trichord(last_chord.mapped_to_majmin_base())
            compound_nro = self.get_compound_nro(last_chord, compound_length)
            map_to_base = self.spec.is_classic
            next_chord = last_chord.apply_compound_nro(compound_nro, map_to_base)
            if self.spec.focal_note is not None:
                next_chord.map_to_focal_note(self.spec.focal_note)
            is_in_fixed_key = self.spec.fixed_key is None or self.spec.fixed_key.is_in_key(next_chord)
            is_ok = (next_chord.is_admissable() and is_in_fixed_key)
            #Error handling for generating the same chord in a row
            if next_chord.notes == last_chord.notes:
                is_ok = False
            if requires_minor_or_major and not next_chord.is_major() and not next_chord.is_minor():
                is_ok = False
            trials += 1
            if trials == 1000:
                trials = 0
                compound_length += 1
        next_chord.notes.sort()
        self.compound_nros.append(compound_nro)
        self.chords.append(next_chord)

    def get_compound_nro(self, last_chord, compound_length):
        compound_nro = CompoundNRO([])
        if self.spec.is_classic:
            nro_lists = get_classic_nro_lists()
            start_pos = 0 if last_chord.is_major() else 1
            for i in range(0, compound_length):
                ind = (start_pos + i) % 2
                nros = nro_lists[ind]
                nro = random.choice(nros)
                compound_nro.nros.append(nro)
        else:
            for i in range(0, compound_length):
                compound_nro.nros.append(random.choice(all_nros))
        return compound_nro

    def add_emotional_cnro(self, emotional_cnro):
        nro_lists = get_classic_nro_lists()
        pos = 0 if self.chords[-1].is_major() else 1
        nros_in_compound_nro = []
        for ind, letter in enumerate(emotional_cnro.nro_letters):
            nros = nro_lists[(pos + ind) % 2]
            for nro in nros:
                if nro.name == letter:
                    nros_in_compound_nro.append(nro)
        compound_nro = CompoundNRO(nros_in_compound_nro)
        last_chord = self.chords[-1]
        last_chord = Trichord(last_chord.mapped_to_majmin_base())
        next_chord = last_chord.apply_compound_nro(compound_nro, True)
        if self.spec.focal_note is not None:
            next_chord.map_to_focal_note(self.spec.focal_note)
        self.compound_nros.append(compound_nro)
        self.chords.append(next_chord)
        next_chord.is_event_chord = True

    def apply_compound_nro(self, compound_nro):
        self.compound_nros.append(compound_nro)
        new_chord = self.get_next_chord(compound_nro)
        self.chords.append(new_chord)

    def set_midi_instruments(self, next_spec):
        for track in MidiTracks.primary_chord_tracks:
            track.append(Message('program_change', channel=MidiChannels.primary_chord_channel, program=self.spec.instrument_num, time=0))
        if next_spec is not None:
            for track in MidiTracks.secondary_chord_tracks:
                track.append(Message('program_change', channel=MidiChannels.secondary_melody_channel, program=next_spec.chord_sequence_spec.instrument_num, time=0))

    def add_music(self):
        volume_add = (self.spec.end_volume - self.spec.start_volume)/(len(self.chords) - 1)
        volume = self.spec.start_volume
        overlap_start_bar = len(self.chords) - self.spec.episode_overlap_chords + 1
        for ind, chord in enumerate(self.chords):
            start_primary_prop = 1
            end_primary_prop = 1
            if self.spec.episode_overlap_chords > 0:
                prop_add = 1/self.spec.episode_overlap_chords
                if ind >= overlap_start_bar - 1:
                    start_primary_prop = 1 - ((ind - overlap_start_bar + 1) * prop_add)
                    end_primary_prop = start_primary_prop - prop_add
            chord.add_to_tracks(int(round(volume)), start_primary_prop, end_primary_prop)
            volume += volume_add
