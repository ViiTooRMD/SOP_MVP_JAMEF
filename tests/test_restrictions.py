import pytest

from app.models.restriction import Restriction


def test_restriction_accepts_valid_rate():
    restriction = Restriction(client_id="cliente-a", reduction_rate=0.2)
    assert restriction.reduction_rate == 0.2


@pytest.mark.parametrize("rate", [-0.01, 1.01])
def test_restriction_rejects_invalid_rate(rate):
    with pytest.raises(ValueError):
        Restriction(client_id="cliente-a", reduction_rate=rate)
