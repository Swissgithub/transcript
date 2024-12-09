import pyaudio
import wave
import threading
import logging

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
            try:
                # Tentative d'ouverture du flux audio
                stream = self.p.open(format=self.format,
                                     channels=self.channels,
                                     rate=self.rate,
                                     input=True,
                                     frames_per_buffer=self.chunk)
                stream.close()  # Fermer immédiatement après vérification
                self.is_recording = True
                self.frames = []
                self.thread = threading.Thread(target=self.record)
                self.thread.start()
                logging.info("Recording started successfully.")
            except Exception as e:
                logging.error(f"Failed to start recording: {e}")
                return False
        return True

    def record(self):
        try:
            stream = self.p.open(format=self.format,
                                 channels=self.channels,
                                 rate=self.rate,
                                 input=True,
                                 frames_per_buffer=self.chunk)
            logging.info("Audio stream opened successfully.")
            while self.is_recording:
                data = stream.read(self.chunk, exception_on_overflow=False)
                self.frames.append(data)
            stream.stop_stream()
            stream.close()
            logging.info("Audio stream closed successfully.")
        except Exception as e:
            logging.error(f"Failed to open audio stream: {e}")

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
