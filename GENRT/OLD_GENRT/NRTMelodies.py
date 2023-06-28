from mido import Message
from Rhythms import *
from OLD_GENRT.Chords import *
from OLD_GENRT.Midi import *
import random


class NRTMelodySpec:
    def __init__(self, instrument_num, fixed_key, rhythm_string, start_volume,
                 end_volume, is_voice_leading, chord_splits_allowed, note_length,
                 episode_overlap_chords):
        self.instrument_num = instrument_num
        self.fixed_key = fixed_key
        self.rhythm_string = rhythm_string
        self.start_volume = start_volume
        self.end_volume = end_volume
        self.is_voice_leading = is_voice_leading
        self.chord_splits_allowed = chord_splits_allowed
        self.note_length = note_length
        self.episode_overlap_chords = episode_overlap_chords


class NRTMelodyNote:
    def __init__(self, note_ind, note_num, start_tick, cutoff_tick, duration_ticks, num_splits):
        self.note_ind = note_ind
        self.note_num = note_num
        self.start_tick = start_tick
        self.cutoff_tick = cutoff_tick
        self.duration_ticks = duration_ticks
        self.num_splits = num_splits

    def add_to_track(self, volume, primary_prop):
        primary_volume = int(volume * primary_prop)
        secondary_volume = int(volume * (1 - primary_prop))
        pad_ticks = self.duration_ticks - self.cutoff_tick
        MidiTracks.primary_melody_track.append(Message(type='note_on', channel=MidiChannels.primary_melody_channel, note=self.note_num, velocity=primary_volume, time=0))
        MidiTracks.primary_melody_track.append(Message(type='note_off', channel=MidiChannels.primary_melody_channel, note=self.note_num, velocity=primary_volume, time=self.cutoff_tick))
        MidiTracks.secondary_melody_track.append(Message(type='note_on', channel=MidiChannels.secondary_melody_channel, note=self.note_num, velocity=secondary_volume, time=0))
        MidiTracks.secondary_melody_track.append(Message(type='note_off', channel=MidiChannels.secondary_melody_channel, note=self.note_num, velocity=secondary_volume, time=self.cutoff_tick))
        if pad_ticks > 0:
            MidiTracks.primary_melody_track.append(Message(type='note_on', channel=MidiChannels.primary_melody_channel, note=self.note_num, velocity=0, time=0))
            MidiTracks.primary_melody_track.append(Message(type='note_off', channel=MidiChannels.primary_melody_channel, note=self.note_num, velocity=0, time=pad_ticks))
            MidiTracks.secondary_melody_track.append(Message(type='note_on', channel=MidiChannels.secondary_melody_channel, note=self.note_num, velocity=0, time=0))
            MidiTracks.secondary_melody_track.append(Message(type='note_off', channel=MidiChannels.secondary_melody_channel, note=self.note_num, velocity=0, time=pad_ticks))


class NRTMelody:
    def __init__(self, spec):
        self.spec = spec
        self.notes = []
        self.note_triples = []
        self.bar_notes = {}

    def first_stage_calculate_notes(self, chord_sequence, previous_episode):
        if self.spec.is_voice_leading:
            self.first_stage_generate_voice_leading_melody(chord_sequence, previous_episode)
        else:
            for ind, chord in enumerate(chord_sequence.chords):
                rhythm = Rhythm(self.spec.rhythm_string, chord.duration_ticks)
                bnotes = []
                for nind, rnote in enumerate(rhythm.rhythm_notes):
                    note_num = chord.notes[rnote.note_id - 1] + 12
                    mnote = NRTMelodyNote(nind, note_num, rnote.start_tick, rnote.cutoff_tick, rnote.duration_ticks, 1)
                    bnotes.append(mnote)
                    self.notes.append(mnote)
                self.bar_notes[ind] = bnotes

    def second_stage_calculate_notes(self, chord_sequence, previous_episode, next_episode):
        if self.spec.is_voice_leading:
            self.second_stage_generate_voice_leading_melody(chord_sequence, previous_episode, next_episode)

    def set_midi_instruments(self, next_spec):
        MidiTracks.primary_melody_track.append(Message('program_change', channel=MidiChannels.primary_melody_channel, program=self.spec.instrument_num, time=0))
        if next_spec is not None:
            MidiTracks.secondary_melody_track.append(Message('program_change', channel=MidiChannels.secondary_melody_channel, program=next_spec.melody_spec.instrument_num, time=0))

    def add_music(self):
        bar_nums = list(self.bar_notes.keys())
        bar_nums.sort()
        volume_add = (self.spec.end_volume - self.spec.start_volume)/(len(self.notes) - 1)
        volume = self.spec.start_volume
        overlap_start_bar = len(bar_nums) - self.spec.episode_overlap_chords + 1
        for bar_num in bar_nums:
            start_prop = None
            end_prop = None
            if self.spec.episode_overlap_chords > 0:
                prop_add = 1/self.spec.episode_overlap_chords
                if bar_num >= overlap_start_bar - 1:
                    start_prop = (bar_num - overlap_start_bar + 1) * prop_add
                    end_prop = start_prop + prop_add

            notes = self.bar_notes[bar_num]
            for ind, note in enumerate(notes):
                primary_prop = 1
                if start_prop is not None:
                    frac = ind/(len(notes) - 1) if len(notes) > 1 else 0
                    primary_prop = 1 - ((start_prop * (1-frac)) + (end_prop * frac))
                if note.note_ind == 0 and note.start_tick > 0:
                    MidiChannels.primary_melody_track.append(Message(type='note_on', channel=MidiChannels.primary_melody_channel, note=60, velocity=0, time=0))
                    MidiChannels.primary_melody_track.append(Message(type='note_off', channel=MidiChannels.primary_melody_channel, note=60, velocity=0, time=note.start_tick))
                    MidiChannels.secondary_melody_track.append(Message(type='note_on', channel=MidiChannels.secondary_melody_channel, note=60, velocity=0, time=0))
                    MidiChannels.secondary_melody_track.append(Message(type='note_off', channel=MidiChannels.secondary_melody_channel, note=60, velocity=0, time=note.start_tick))
                note.add_to_track(int(round(volume)), primary_prop)
                volume += volume_add

    def first_stage_generate_voice_leading_melody(self, chord_sequence, previous_episode):
        if previous_episode is not None and previous_episode.spec.chord_sequence_spec.end_event is not None:
            if previous_episode.spec.chord_sequence_spec.end_event.change_fixed_key is True:
                self.spec.fixed_key = previous_episode.chord_sequence.chords[-1].get_key_signature()
        for ind, chord in enumerate(chord_sequence.chords):
            a, b, c = chord.notes
            a += 12; b += 12; c += 12
            triples = [[a, b, c], [a, c, b], [b, a, c], [b, c, a], [c, a, b], [c, b, a]]
            if ind == 0 and previous_episode is None:
                triple = random.choice(triples)
                self.note_triples.append(triple)
            else:
                if ind == 0 and previous_episode is not None:
                    join_to_note = previous_episode.melody.note_triples[-1][-1]
                else:
                    join_to_note = self.note_triples[-1][-1]
                quins = []
                for a, b, c in triples:
                    dist = abs(join_to_note - a)
                    travel = abs(b - a) + abs(c - b)
                    quins.append([dist, travel, a, b, c])
                quins.sort()
                d, t, a, b, c = quins[0]
                self.note_triples.append((a, b, c))

    def second_stage_generate_voice_leading_melody(self, chord_sequence, previous_episode, next_episode):
        for ind, chord in enumerate(chord_sequence.chords):
            t = self.note_triples[ind]
            notes_for_chord = [t[0]]
            fixed_key = self.spec.fixed_key
            if chord.is_event_chord:
                fixed_key = chord.get_key_signature()
            target_note = t[1]
            next_note = self.get_next_note(fixed_key, t[0], t[1])
            pos = 1
            while next_note is not None:
                notes_for_chord.append(next_note)
                next_note = self.get_next_note(fixed_key, notes_for_chord[-1], target_note)
                if next_note is None:
                    pos += 1
                    if pos <= 2:
                        target_note = t[pos]
                    elif pos == 3 and ind < len(self.note_triples) - 1:
                        target_note = self.note_triples[ind + 1][0]
                    elif pos == 3 and next_episode is not None and ind == (len(self.note_triples) - 1):
                        target_note = next_episode.melody.note_triples[0][0]
                    next_note = self.get_next_note(fixed_key, notes_for_chord[-1], target_note)

            if ind < len(chord_sequence.chords) - 1 and notes_for_chord[-1] == self.note_triples[ind + 1][0]:
                notes_for_chord.pop(-1)
            if ind == len(chord_sequence.chords) - 1 and next_episode is not None:
                if notes_for_chord[-1] == next_episode.melody.note_triples[0][0]:
                    notes_for_chord.pop(-1)
            note_ticks = int(round(chord.duration_ticks/len(notes_for_chord)))
            start_tick = 0
            bnotes = []
            for nind, n in enumerate(notes_for_chord):
                note = NRTMelodyNote(nind, n, start_tick, note_ticks, note_ticks, 1)
                self.notes.append(note)
                bnotes.append(note)
                start_tick += note_ticks
            self.bar_notes[ind] = bnotes
            self.quantize_notes(chord, bnotes)

    def get_next_note(self, fixed_key, current_note, target_note):
        if current_note == target_note:
            return None
        if fixed_key is not None:
            return fixed_key.next_note_in_direction(current_note, target_note)
        else:
            if abs(current_note - target_note) <= 2:
                return None
            elif current_note < target_note:
                return current_note + 2
            else:
                return current_note - 2

    def quantize_notes(self, chord, notes):
        chord_letters = chord.get_note_letters()
        num_splits = 0
        for split in self.spec.chord_splits_allowed:
            if split >= len(notes):
                num_splits = split
                break
        total = 0
        split_duration_ticks = chord.duration_ticks//num_splits
        for ind, note in enumerate(notes):
            n = note.duration_ticks
            note.duration_ticks = split_duration_ticks
            note.cutoff_tick = int(split_duration_ticks * self.spec.note_length)
            note.start_tick = (ind * split_duration_ticks)
            note.num_splits = 1
            total += split_duration_ticks
        while total + split_duration_ticks <= chord.duration_ticks:
            note = random.choice(notes)
            letter = note_letters[(note.note_num + 3) % 12]
            if letter in chord_letters:
                note.duration_ticks += split_duration_ticks
                note.cutoff_tick = int(note.duration_ticks * self.spec.note_length)
                note.num_splits += 1
                ind = notes.index(note)
                for i in range(ind + 1, len(notes)):
                    notes[i].start_tick += split_duration_ticks
                total += split_duration_ticks
        diff = chord.duration_ticks - total
        note = random.choice(notes)
        note.duration_ticks += diff
        note.cutoff_tick = int(note.duration_ticks * self.spec.note_length)
        ind = notes.index(note)
        for i in range(ind + 1, len(notes)):
            notes[i].start_tick += split_duration_ticks
