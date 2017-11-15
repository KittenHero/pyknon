from pyknon.MidiFile import MIDIFile
from pyknon.music import Note, NoteSeq, Rest
import collections


class MidiError(Exception):
    pass



class Midi(object):
    def __init__(self, number_tracks=1, tempo=60, instrument=0, channel=None, track_name=None):
        """Creates a Midi object with specified properties

        Arguments:
        number_tracks   (int)
        tempo           (int or Iterable)   BPM of the each track
        instrument      (int or Iterable)   Instrument of each track
        channel         (int or Iterable)   MIDI channel of each track
        track_name      (Iterable)          Name of each Track
        """

        # transform args
        def iterify(item, iterified=lambda item: [item]*number_tracks):
            return item if isinstance(item, collections.Iterable) else iterified(item)
        tempo = iterify(tempo)
        instrument = iterify(instrument)
        channel = range(number_tracks) if channel is None else iterify(channel)
        track_name = (f'Track {i}' for i in range(number_tracks)) if track_name is None else track_name

        # create MIDI File object
        self.number_tracks = number_tracks
        self.midi_data = MIDIFile(number_tracks)

        for track, (name, _tempo, _channel, instr) in enumerate(zip(track_name, tempo, channel, instrument)):
            self.midi_data.addTrackName(track, 0, name)
            self.midi_data.addTempo(track, 0, _tempo)
            self.midi_data.addProgramChange(track, _channel, 0, instr)

    def seq_chords(self, seqlist, track=0, time=0, channel=None):
        '''Adds a series of chords to a track at the specified time and channel

        Arguments:
        seqlist     (List of NoteSeq and Rest)
        track       (int)
        time        (float)                     start time of the chord sequence
        channel     (int)
        '''
        if not (0 <= track < self.number_tracks):
            raise MidiError(f"Invalid track number {track}")

        _channel = channel if channel is not None else track

        for item in seqlist:
            if isinstance(item, NoteSeq):
                for note in item:
                    self.midi_data.addNote(track, _channel, note.midi_number, time, note.dur, note.volume)
                time += min(note.dur for note in item)
            elif isinstance(item, Rest):
                time += item.midi_dur
            else:
                raise MidiError(f"Expected a sequence of NoteSeq but found {seqlist} containing {item}")
        return time

    def seq_notes(self, noteseq, track=0, time=0, channel=None):
        '''Adds a melody to a track at the specified time and channel

        Arguments:
        noteseq     (Note seq or List of Notes)
        track       (int)
        time        (float)                     start time of the chord sequence
        channel     (int)
        '''
        if not (0 <= track < self.number_tracks):
            raise MidiError(f"Invalid track number {track}")

        _channel = channel if channel is not None else track

        for note in noteseq:
            if isinstance(note, Note):
                self.midi_data.addNote(track, _channel, note.midi_number, time, note.midi_dur, note.volume)
            time += note.midi_dur

        return time

    def change_tuning(self, track, tunings, real_time=False, tuning_program=0):
        self.midi_data.changeNoteTuning(track, tunings, realTime=real_time, tuningProgam=tuning_program)

    def write(self, filename):
        if isinstance(filename, str):
            with open(filename, 'wb') as midifile:
                self.midi_data.writeFile(midifile)
        else:
            self.midi_data.writeFile(filename)
