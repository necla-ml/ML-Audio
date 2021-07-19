import pytest

from fixtures import *

@pytest.fixture
def model():
    from ml.audio.models import VGGishModel
    model = VGGishModel(pretrained=True)
    return model

@pytest.mark.essential
def test_vggish(model, wav_file):
    out = model(wav_file)
    assert list(out.shape) == [10, 128]
    print(out.shape)