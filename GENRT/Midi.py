# NOTE THAT CHANNEL 9 IN MIDO IS REALLY CHANNEL 10!!! (FOR PERCUSSION)

from mido import MidiFile, MidiTrack

class MidiUtils:
    def get_midi_file(type):
        midi_file = MidiFile(type=type)
        #print(f"Midi file length right after creation {midi_file.length}")
        start_tracks = MidiTracks()

        #Hack to avoid track concatenating error:
        MidiTracks.primary_chord_tracks = [MidiTrack(), MidiTrack(), MidiTrack()]
        MidiTracks.secondary_chord_tracks = [MidiTrack(), MidiTrack(), MidiTrack()]
        MidiTracks.primary_melody_track = MidiTrack()
        MidiTracks.secondary_melody_track = MidiTrack()
        MidiTracks.primary_bass_track = MidiTrack()
        MidiTracks.secondary_bass_track = MidiTrack()
        MidiTracks.percussion_tracks = [MidiTrack(), MidiTrack(), MidiTrack()]


        #Original
        midi_file.tracks.extend(MidiTracks.primary_chord_tracks)
        midi_file.tracks.extend(MidiTracks.secondary_chord_tracks)
        midi_file.tracks.append(MidiTracks.primary_melody_track)
        midi_file.tracks.append(MidiTracks.secondary_melody_track)
        midi_file.tracks.append(MidiTracks.primary_bass_track)
        midi_file.tracks.append(MidiTracks.secondary_bass_track)
        midi_file.tracks.extend(MidiTracks.percussion_tracks)
        

        #Attempt at creating the tracks each time
        """
        midi_file.tracks.extend([MidiTrack(), MidiTrack(), MidiTrack()])
        midi_file.tracks.extend([MidiTrack(), MidiTrack(), MidiTrack()])
        midi_file.tracks.append(MidiTrack())
        midi_file.tracks.append(MidiTrack())
        midi_file.tracks.append(MidiTrack())
        midi_file.tracks.append(MidiTrack())
        midi_file.tracks.extend([MidiTrack(), MidiTrack(), MidiTrack()])
        """
        """
        #Attempt at new class each time
        start_tracks = MidiTracks()
        midi_file.tracks.extend(start_tracks.primary_chord_tracks)
        midi_file.tracks.extend(start_tracks.secondary_chord_tracks)
        midi_file.tracks.append(start_tracks.primary_melody_track)
        midi_file.tracks.append(start_tracks.secondary_melody_track)
        midi_file.tracks.append(start_tracks.primary_bass_track)
        midi_file.tracks.append(start_tracks.secondary_bass_track)
        midi_file.tracks.extend(start_tracks.percussion_tracks)
        print(f"Midi file length right after track addition: {midi_file.length}")
        """


        return midi_file


class MidiChannels:
    primary_chord_channel = 0
    secondary_chord_channel = 1
    primary_melody_channel = 2
    secondary_melody_channel = 3
    primary_bass_channel = 4
    secondary_bass_channel = 5
    percussion_channel = 9

class MidiTracks:
    #Original
    
    primary_chord_tracks = [MidiTrack(), MidiTrack(), MidiTrack()]
    secondary_chord_tracks = [MidiTrack(), MidiTrack(), MidiTrack()]
    primary_melody_track = MidiTrack()
    secondary_melody_track = MidiTrack()
    primary_bass_track = MidiTrack()
    secondary_bass_track = MidiTrack()
    percussion_tracks = [MidiTrack(), MidiTrack(), MidiTrack()]

        


    """
    def __init__(self):
        self.primary_chord_tracks = [MidiTrack(), MidiTrack(), MidiTrack()]
        self.secondary_chord_tracks = [MidiTrack(), MidiTrack(), MidiTrack()]
        self.primary_melody_track = MidiTrack()
        self.secondary_melody_track = MidiTrack()
        self.primary_bass_track = MidiTrack()
        self.secondary_bass_track = MidiTrack()
        self.percussion_tracks = [MidiTrack(), MidiTrack(), MidiTrack()]

    """