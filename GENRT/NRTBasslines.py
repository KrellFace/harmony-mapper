from mido import Message
from Rhythms import *
from Midi import *

class NRTBasslineSpec:
    def __init__(self, instrument_num, rhythm_string, start_volume, end_volume, episode_overlap_chords):
        self.instrument_num = instrument_num
        self.rhythm_string = rhythm_string
        self.start_volume = start_volume
        self.end_volume = end_volume
        self.episode_overlap_chords = episode_overlap_chords


class NRTBassNote:
    def __init__(self, note_ind, note_num, start_tick, cutoff_tick, duration_ticks):
        self.note_num = note_num
        self.note_ind = note_ind
        self.start_tick = start_tick
        self.cutoff_tick = cutoff_tick
        self.duration_ticks = duration_ticks

    def add_to_track(self, volume, primary_prop):
        primary_volume = int(volume * primary_prop)
        secondary_volume = int(volume * (1 - primary_prop))
        pad_ticks = self.duration_ticks - self.cutoff_tick
        MidiTracks.primary_bass_track.append(Message(type='note_on', channel=MidiChannels.primary_bass_channel, note=self.note_num, velocity=primary_volume, time=0))
        MidiTracks.primary_bass_track.append(Message(type='note_off', channel=MidiChannels.primary_bass_channel, note=self.note_num, velocity=primary_volume, time=self.cutoff_tick))
        MidiTracks.secondary_bass_track.append(Message(type='note_on', channel=MidiChannels.secondary_bass_channel, note=self.note_num, velocity=secondary_volume, time=0))
        MidiTracks.secondary_bass_track.append(Message(type='note_off', channel=MidiChannels.secondary_bass_channel, note=self.note_num, velocity=secondary_volume, time=self.cutoff_tick))
        if pad_ticks > 0:
            MidiTracks.primary_bass_track.append(Message(type='note_on', channel=MidiChannels.primary_bass_channel, note=self.note_num, velocity=0, time=0))
            MidiTracks.primary_bass_track.append(Message(type='note_off', channel=MidiChannels.primary_bass_channel, note=self.note_num, velocity=0, time=pad_ticks))
            MidiTracks.secondary_bass_track.append(Message(type='note_on', channel=MidiChannels.secondary_bass_channel, note=self.note_num, velocity=0, time=0))
            MidiTracks.secondary_bass_track.append(Message(type='note_off', channel=MidiChannels.secondary_bass_channel, note=self.note_num, velocity=0, time=pad_ticks))


class NRTBassline:
    def __init__(self, spec):
        self.spec = spec
        self.notes = []
        self.bar_notes = {}

    def calculate_notes(self, chord_sequence, previous_episode):
        for ind, chord in enumerate(chord_sequence.chords):
            rhythm = Rhythm(self.spec.rhythm_string, chord.duration_ticks)
            bnotes = []
            for nind, rnote in enumerate(rhythm.rhythm_notes):
                note_num = chord.notes[rnote.note_id - 1] - 12
                bnote = NRTBassNote(nind, note_num, rnote.start_tick, rnote.cutoff_tick, rnote.duration_ticks)
                self.notes.append(bnote)
                bnotes.append(bnote)
            self.bar_notes[ind] = bnotes

    def set_midi_instrument(self, next_spec):
        MidiTracks.primary_bass_track.append(Message('program_change', channel=MidiChannels.primary_bass_channel, program=self.spec.instrument_num, time=0))
        if next_spec is not None:
            MidiTracks.secondary_bass_track.append(Message('program_change', channel=MidiChannels.secondary_bass_channel, program=next_spec.bassline_spec.instrument_num, time=0))

    def add_music(self):
        bar_nums = list(self.bar_notes.keys())
        bar_nums.sort()
        overlap_start_bar = len(bar_nums) - self.spec.episode_overlap_chords + 1
        volume_add = (self.spec.end_volume - self.spec.start_volume)/(len(self.notes) - 1)
        volume = self.spec.start_volume
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
                    MidiTracks.primary_bass_track.append(Message(type='note_on', channel=MidiChannels.primary_bass_channel, note=60, velocity=0, time=0))
                    MidiTracks.primary_bass_track.append(Message(type='note_off', channel=MidiChannels.primary_bass_channel, note=60, velocity=0, time=note.start_tick))
                    MidiTracks.secondary_bass_track.append(Message(type='note_on', channel=MidiChannels.secondary_bass_channel, note=60, velocity=0, time=0))
                    MidiTracks.secondary_bass_track.append(Message(type='note_off', channel=MidiChannels.secondary_bass_channel, note=60, velocity=0, time=note.start_tick))
                note.add_to_track(int(round(volume)), primary_prop)
                volume += volume_add
