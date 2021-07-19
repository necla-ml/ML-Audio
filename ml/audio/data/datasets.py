from pathlib import Path

import torch
import torchaudio
import torchaudio.transforms as AT
from torch.utils.data import Dataset

class WavetoLogMelSpecDataset(Dataset):
    """
    Wave in, log-mel spectrogram out
    """
    def __init__(self, cfg, transform):
        super().__init__()

        root_path = Path(cfg.root)
        assert root_path.exists(), f'Path: {cfg.root} does not exist'

        # initializations
        self.cfg = cfg
        self.files = sorted(root_path.glob('*.wav'))
        self.transform = transform

        self.to_melspecgram = AT.MelSpectrogram(
            sample_rate=cfg.sample_rate,
            n_fft=cfg.n_fft,
            win_length=cfg.win_length,
            hop_length=cfg.hop_length,
            center=cfg.center, # True
            pad_mode=cfg.pad_mode, # "reflect"
            power=cfg.power, # 2.0
            norm='slaney',
            onesided=True,
            n_mels=cfg.n_mels,
            mel_scale="htk",
        )

    def __len__(self):
        return len(self.files)

    def __getitem__(self, idx):
        # load single channel .wav audio
        wav, sr = torchaudio.load(str(self.files[idx]))

        # to single channel (n, sr) -> (1, sr)
        wav = wav.mean(dim=0, keepdim=True)

        assert wav.shape[0] == 1, f'Convert .wav files to single channel audio, {self.files[idx]} has {wav.shape[0]} channels.'

        # resample if needed
        if sr != self.cfg.sample_rate:
            wav = torchaudio.functional.resample(wav, sr, self.cfg.sample_rate)

        # to log mel spectrogram -> (1, n_mels, time)
        lms = (self.to_melspecgram(wav) + torch.finfo().eps).log()

        # transform (augment)
        if self.transform:
            lms = self.transform(lms)

        return lms