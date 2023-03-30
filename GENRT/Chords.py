from mido import Message
from Midi import *

note_letters = ["a", "a#", "b", "c", "c#", "d", "d#", "e", "f", "f#", "g", "g#"]
major_scale_positions = [0, 2, 4, 5, 7, 9, 11]
minor_scale_positions = [0, 2, 3, 5, 7, 8, 10]


class KeySignature:

    def __init__(self, note_letter, major_or_minor):
        self.note_letter = note_letter
        self.major_or_minor = major_or_minor
        if self.major_or_minor == "maj":
            self.scale_positions = major_scale_positions
        if self.major_or_minor == "min":
            self.scale_positions = minor_scale_positions
        self.scale_letters = []
        start_ind = note_letters.index(self.note_letter)
        for pos in self.scale_positions:
            ind = (start_ind + pos) % 12
            self.scale_letters.append(note_letters[ind])

    def __str__(self):
        return self.note_letter + self.major_or_minor

    def is_in_key(self, chord):
        chord_letters = chord.get_note_letters()
        for letter in chord_letters:
            if letter not in self.scale_letters:
                return False
        return True

    def next_note_in_direction(self, current_note, target_note):
        if current_note == target_note:
            return None
        addon = 1 if target_note > current_note else -1
        note = current_note
        is_ok = False
        while note != target_note and is_ok is False:
            note += addon
            letter = note_letters[(note + 3) % 12]
            if letter in self.scale_letters:
                is_ok = True
        return note



class Trichord:

    def __init__(self, notes):
        self.notes = notes
        self.duration_ticks = 0
        self.is_event_chord = False
        self.timestamp_ms = 0

    def __str__(self):
        #        return f"{self.notes[0]},{self.notes[1]},{self.notes[2]}"
        s = ""
        for letter in self.get_note_letters():
            s += f"{letter},"
        addon = ""
        if self.is_major():
            addon = "(maj)"
        elif self.is_minor():
            addon = "(min)"
        return s[:-1] + addon

    def get_key_signature(self):
        a, b, c = self.mapped_to_majmin_base()
        letter = note_letters[(a + 3) % 12]
        majmin = "maj" if self.is_major() else "min"
        return KeySignature(letter, majmin)

    def is_major(self):
        a, b, c = self.mapped_to_mid_octave()
        for t1, t2, t3 in [[a, b, c], [c - 12, a, b], [b - 12, c - 12, a]]:
            if t2 - t1 == 4 and t3 - t2 == 3:
                return True
        return False

    def is_minor(self):
        a, b, c = self.mapped_to_mid_octave()
        for t1, t2, t3 in [[a, b, c], [c - 12, a, b], [b - 12, c - 12, a]]:
            if t2 - t1 == 3 and t3 - t2 == 4:
                return True
        return False

    def mapped_to_majmin_base(self):
        a, b, c = self.mapped_to_mid_octave()
        mapped_notes = []
        for t1, t2, t3 in [[a, b, c], [c - 12, a, b], [b - 12, c - 12, a]]:
            if t2 - t1 == 3 and t3 - t2 == 4:
                mapped_notes = [t1, t2, t3]
                break
            if t2 - t1 == 4 and t3 - t2 == 3:
                mapped_notes = [t1, t2, t3]
                break
        return mapped_notes

    def get_note_letters(self):
        letters = []
        for note in self.notes:
            letters.append(note_letters[(note + 3) % 12])
        return letters

    def apply_nro(self, nro):
        notes = []
        for ind, operator in enumerate(nro.operators):
            notes.append(self.notes[ind] + operator)
        output_trichord = Trichord(notes)
        return output_trichord

    def apply_compound_nro(self, compound_nro, map_to_majmin=False):
        output_trichord = Trichord(self.notes)
        if map_to_majmin:
            output_trichord.notes = output_trichord.mapped_to_majmin_base()
        for nro in compound_nro.nros:
            output_trichord = output_trichord.apply_nro(nro)
            if map_to_majmin:
                output_trichord.notes = output_trichord.mapped_to_majmin_base()
        return output_trichord

    def is_admissable(self):
        a, b, c = self.notes

        # Must be a trichord with three distinct note categories
        l1, l2, l3 = self.get_note_letters()
        if l1 == l2 or l1 == l3 or l2 == l3:
            return False

        # Must not have two notes apart by only a semitone
        ind1 = note_letters.index(l1)
        ind2 = note_letters.index(l2)
        ind3 = note_letters.index(l3)
        if abs(ind1 - ind2) <= 1 or abs(ind1 - ind3) <= 1 or abs(ind2 - ind3) <= 1:
            return False

        if abs(ind1 - ind2) >= 12 or abs(ind1 - ind3) >= 12 or abs(ind2 - ind3) >= 12:
            return False

        return True

    def map_to_focal_note(self, focal_note):
        min_dist = 1000000
        mapped_chord = []
        for note in self.notes:
            min_dist = 10000
            try_note = note + (12 * 5)
            mapped_note = note
            while try_note > 0:
                dist = abs(focal_note - try_note)
                if dist < min_dist:
                    mapped_note = try_note
                    min_dist = dist
                try_note -= 12
            mapped_chord.append(mapped_note)
        mapped_chord.sort()
        self.notes = mapped_chord

    def mapped_to_mid_octave(self):
        mapped_chord = []
        for note in self.notes:
            try_note = note + (12 * 5)
            mapped_note = note
            while try_note > 0:
                if try_note >= 60 and try_note < 72:
                    mapped_note = try_note
                try_note -= 12
            mapped_chord.append(mapped_note)
        mapped_chord.sort()
        return mapped_chord

    def add_to_tracks(self, volume, start_primary_prop, end_primary_prop):
        for track_num, note in enumerate(self.notes):
            primary_track = MidiTracks.primary_chord_tracks[track_num]
            secondary_track = MidiTracks.secondary_chord_tracks[track_num]
            num_rnotes = len(self.rhythm.rhythm_notes)
            start_primary_volume = volume * start_primary_prop
            start_secondary_volume = volume * (1 - start_primary_prop)
            end_primary_volume = volume * end_primary_prop
            end_secondary_volume = volume * (1 - end_primary_prop)
            primary_volume_addon = 0 if num_rnotes == 1 else (end_primary_volume - start_primary_volume)/(num_rnotes - 1)
            secondary_volume_addon = 0 if num_rnotes == 1 else (end_secondary_volume - start_secondary_volume)/(num_rnotes - 1)
            for ind, rnote in enumerate(self.rhythm.rhythm_notes):
                primary_volume = int(round(start_primary_volume + (primary_volume_addon * ind)))
                secondary_volume = int(round(start_secondary_volume + (secondary_volume_addon * ind)))
                if ind == 0 and rnote.start_tick > 0:
                    primary_track.append(Message(type='note_on', channel=MidiChannels.primary_chord_channel, note=note, velocity=0, time=0))
                    primary_track.append(Message(type='note_on', channel=MidiChannels.primary_chord_channel, note=note, velocity=0, time=rnote.start_tick))
                    secondary_track.append(Message(type='note_on', channel=MidiChannels.secondary_chord_channel, note=note, velocity=0, time=0))
                    secondary_track.append(Message(type='note_on', channel=MidiChannels.secondary_chord_channel, note=note, velocity=0, time=rnote.start_tick))
                primary_track.append(Message(type='note_on', channel=MidiChannels.primary_chord_channel, note=note, velocity=primary_volume, time=0))
                primary_track.append(Message(type='note_off', channel=MidiChannels.primary_chord_channel, note=note, velocity=primary_volume, time=rnote.cutoff_tick))
                secondary_track.append(Message(type='note_on', channel=MidiChannels.secondary_chord_channel, note=note, velocity=secondary_volume, time=0))
                secondary_track.append(Message(type='note_off', channel=MidiChannels.secondary_chord_channel, note=note, velocity=secondary_volume, time=rnote.cutoff_tick))
                pad_ticks = rnote.duration_ticks - rnote.cutoff_tick
                if pad_ticks > 0:
                    primary_track.append(Message(type='note_on', channel=MidiChannels.primary_chord_channel, note=60, velocity=0, time=0))
                    primary_track.append(Message(type='note_off', channel=MidiChannels.primary_chord_channel, note=60, velocity=0, time=pad_ticks))
                    secondary_track.append(Message(type='note_on', channel=MidiChannels.secondary_chord_channel, note=60, velocity=0, time=0))
                    secondary_track.append(Message(type='note_off', channel=MidiChannels.secondary_chord_channel, note=60, velocity=0, time=pad_ticks))
