import torch
import torchaudio

from  ml.audio.models.backbone.vggish import get_VGGish

waveform, sr = torchaudio.load('/zdata/projects/shared/datasets/AUDIOSET/balanced_eval_44100_1_pcm32le/007P6bFgRCU.wav')
model = get_VGGish()
out = model('/zdata/projects/shared/datasets/AUDIOSET/balanced_eval_44100_1_pcm32le/007P6bFgRCU.wav')
print(out)