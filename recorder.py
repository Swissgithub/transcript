# recorder.py
import pyaudio
import wave
import threading

class AudioRecorder:
    def __init__(self, output_path, chunk=1024, format=pyaudio.paInt16, channels=1, rate=16000):
        self.output_path = output_path
        self.chunk = chunk
        self.format = format
        self.channels = channels
        self.rate = rate
        self.is_recording = False
        self.frames = []
        self.thread = None
        self.p = pyaudio.PyAudio()

    def start_recording(self):
        if not self.is_recording:
            self.is_recording = True
            self.frames = []
            self.thread = threading.Thread(target=self.record)
            self.thread.start()

    def record(self):
        stream = self.p.open(format=self.format,
                             channels=self.channels,
                             rate=self.rate,
                             input=True,
                             frames_per_buffer=self.chunk)
        while self.is_recording:
            data = stream.read(self.chunk, exception_on_overflow=False)
            self.frames.append(data)
        stream.stop_stream()
        stream.close()

    def stop_recording(self):
        if self.is_recording:
            self.is_recording = False
            self.thread.join()
            self.save_recording()

    def save_recording(self):
        wf = wave.open(self.output_path, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.p.get_sample_size(self.format))
        wf.setframerate(self.rate)
        wf.writeframes(b''.join(self.frames))
        wf.close()

    def terminate(self):
        self.p.terminate()
