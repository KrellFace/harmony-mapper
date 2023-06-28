import musicGeneration as musGen
import metricCalculation as metCalc
import mapElites as me 

class musicTrack:

    def __init__(self, start_chord, cnro_seq, metric_a, metric_b):
        self.start_chord = start_chord
        self.cnro_seq = cnro_seq
        self.chord_seq, self.is_complete_track = musGen.generate_chord_seq_from_cnro_list(start_chord, cnro_seq)
        self.metric_a = metCalc.get_metric_value_for_metric(self, metric_a)
        self.metric_b = metCalc.get_metric_value_for_metric(self, metric_b)