import pytest
import torch
import torchaudio

@pytest.fixture
def loaded_inp():
    waveform, sample_rate = torchaudio.load('../assets/test.wav')
    return waveform, sample_rate

@pytest.fixture
def wav_file():
    return '../assets/test.wav'