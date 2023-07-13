import numpy as np
import pandas as pd
import pytest

from qolmat.imputations import imputers_pytorch
from qolmat.utils.exceptions import PyTorchExtraNotInstalled

# from __future__ import annotations

try:
    import torch as nn
except ModuleNotFoundError:
    raise PyTorchExtraNotInstalled

df_incomplete = pd.DataFrame(
    {
        "col1": [np.nan, 15, np.nan, 23, 33],
        "col2": [69, 76, 74, 80, 78],
        "col3": [174, 166, 182, 177, np.nan],
        "col4": [9, 12, 11, 12, 8],
        "col5": [93, 75, np.nan, 12, np.nan],
    }
)


@pytest.mark.parametrize("df", [df_incomplete])
def test_ImputerRegressorPyTorch_fit_transform(df: pd.DataFrame) -> None:
    nn.manual_seed(42)
    if nn.cuda.is_available():
        nn.cuda.manual_seed(42)
    estimator = imputers_pytorch.build_mlp_example(input_dim=2, list_num_neurons=[64, 32])
    imputer = imputers_pytorch.ImputerRegressorPyTorch(
        estimator=estimator, handler_nan="column", epochs=10
    )

    result = imputer.fit_transform(df)
    expected = pd.DataFrame(
        {
            "col1": [2.031, 15.0, 2.132, 23.0, 33.0],
            "col2": [69.0, 76.0, 74.0, 80.0, 78.0],
            "col3": [174.0, 166.0, 182.0, 177.0, 9.258],
            "col4": [9.0, 12.0, 11.0, 12.0, 8.0],
            "col5": [93.0, 75.0, 13.417, 12.0, 14.076],
        }
    )
    np.testing.assert_allclose(result, expected, atol=1e-3)


@pytest.mark.parametrize("df", [df_incomplete])
def test_imputers_pytorch_Autoencoder(df: pd.DataFrame) -> None:
    nn.manual_seed(42)
    if nn.cuda.is_available():
        nn.cuda.manual_seed(42)
    input = df.values.shape[1]
    latent = 4
    encoder, decoder = imputers_pytorch.build_autoencoder_example(
        input_dim=input,
        latent_dim=latent,
        output_dim=input,
        list_num_neurons=[4 * latent, 2 * latent],
    )
    autoencoder = imputers_pytorch.Autoencoder(encoder, decoder, epochs=10)
    result = autoencoder.imputation_data(df=df, mask=df.isna(), lamb=0.01, iterations=5)
    expected = pd.DataFrame(
        {
            "col1": [23.681, 15.0, 23.678, 23.0, 33.0],
            "col2": [69.0, 76.0, 74.0, 80.0, 78.0],
            "col3": [174.0, 166.0, 182.0, 177.0, 176.319],
            "col4": [9.0, 12.0, 11.0, 12.0, 8.0],
            "col5": [93.0, 75.0, 60.509, 12.0, 60.243],
        }
    )
    np.testing.assert_allclose(result, expected, atol=1e-3)
