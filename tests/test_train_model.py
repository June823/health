import os
from backend import train_model


def test_train_creates_model(tmp_path):
    out = tmp_path / "anomaly_model.pkl"
    # run training to save to a tmp file
    m = train_model.train(save_path=str(out), n_samples=300)
    assert m is not None
    assert os.path.exists(str(out))
