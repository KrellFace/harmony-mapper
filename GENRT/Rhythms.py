class RhythmNote:
    def __init__(self, note_id, start_tick, cutoff_tick, duration_ticks):
        self.note_id = note_id
        self.start_tick = start_tick
        self.cutoff_tick = cutoff_tick
        self.duration_ticks = duration_ticks

    def __str__(self):
        return f"note {self.note_id} at {self.start_tick} for {self.duration_ticks} ticks, cutoff after {self.cutoff_tick} ticks"


class Rhythm:
    def __init__(self, rhythm_string, chord_duration_ticks):
        self.rhythm_notes = []
        self.start_pause = 0
        for part in rhythm_string.split(","):
            p = part.strip()
            ps = p.split(":")
            id_part = ps[0]
            note_id = int(id_part)
            start_part = ps[1]
            top = float(start_part.split("/")[0]) - 1
            bottom = float(start_part.split("/")[1])
            timefrac = top/bottom
            start_tick = int(round((timefrac * chord_duration_ticks)))
            cutoff_part = p.split(":")[2] if len(ps) == 3 else None
            cutoff_tick = None
            if cutoff_part != None:
                t = float(cutoff_part.split("/")[0])
                b = float(cutoff_part.split("/")[1])
                tf = t/b
                cutoff_tick = int(round((tf * chord_duration_ticks)))
            rhythm_note = RhythmNote(note_id, start_tick, cutoff_tick, None)
            self.rhythm_notes.append(rhythm_note)
        self.rhythm_notes.sort(key=lambda x: x.start_tick)
        for i, rnote in enumerate(self.rhythm_notes):
            if i < len(self.rhythm_notes) - 1:
                next_note = self.rhythm_notes[i + 1]
                rnote.duration_ticks = next_note.start_tick - rnote.start_tick
            else:
                rnote.duration_ticks = chord_duration_ticks - rnote.start_tick
            if rnote.cutoff_tick is None:
                rnote.cutoff_tick = rnote.duration_ticks
        self.start_pause = self.rhythm_notes[0].start_tick