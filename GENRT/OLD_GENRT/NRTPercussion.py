from mido import Message
from Rhythms import *
from OLD_GENRT.Midi import *

class NRTPercussionSpec:
    def __init__(self, instrument_nums, rhythm_strings, start_volumes, end_volumes):
        self.instrument_nums = instrument_nums
        self.rhythm_strings = rhythm_strings
        self.start_volumes = start_volumes
        self.end_volumes = end_volumes


class NRTPercussionNote:
    def __init__(self, note_ind, note_num, start_tick, cutoff_tick, duration_ticks):
        self.note_ind = note_ind
        self.note_num = note_num
        self.start_tick = start_tick
        self.cutoff_tick = cutoff_tick
        self.duration_ticks = duration_ticks

    def add_to_track(self, percussion_track, volume):
        pad_ticks = self.duration_ticks - self.cutoff_tick
        percussion_track.append(Message(type='note_on', channel=MidiChannels.percussion_channel, note=self.note_num, velocity=volume, time=0))
        percussion_track.append(Message(type='note_off', channel=MidiChannels.percussion_channel, note=self.note_num, velocity=volume, time=self.cutoff_tick))
        if pad_ticks > 0:
            percussion_track.append(Message(type='note_on', channel=MidiChannels.percussion_channel, note=self.note_num, velocity=0, time=0))
            percussion_track.append(Message(type='note_off', channel=MidiChannels.percussion_channel, note=self.note_num, velocity=0, time=pad_ticks))


class NRTPercussion:
    def __init__(self, spec):
        self.spec = spec
        self.note_lists = []

    def calculate_notes(self, chord_sequence, previous_episode):
        for ind, rstring in enumerate(self.spec.rhythm_strings):
            notes = []
            for cind, chord in enumerate(chord_sequence.chords):
                rhythm = Rhythm(rstring, chord.duration_ticks)
                for nind, rnote in enumerate(rhythm.rhythm_notes):
                    note_num = self.spec.instrument_nums[ind]
                    rnote = NRTPercussionNote(nind, note_num, rnote.start_tick, rnote.cutoff_tick, rnote.duration_ticks)
                    notes.append(rnote)
            self.note_lists.append(notes)

    def add_music(self):
        for ind, track in enumerate(MidiTracks.percussion_tracks):
            if ind < len(self.spec.instrument_nums):
                notes = self.note_lists[ind]
                volume_add = (self.spec.end_volumes[ind] - self.spec.start_volumes[ind]) / (len(notes) - 1)
                volume = self.spec.start_volumes[ind]
                for note in notes:
                    if note.note_ind == 0 and note.start_tick > 0:
                        track.append(Message(type='note_on', channel=MidiChannels.percussion_channel, note=60, velocity=0, time=0))
                        track.append(Message(type='note_off', channel=MidiChannels.percussion_channel, note=60, velocity=0, time=note.start_tick))
                    note.add_to_track(track, int(round(volume)))
                    volume += volume_add
