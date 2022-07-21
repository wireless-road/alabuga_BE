from schlumberger.utils.utility import generate_unique_name
import logging

logger = logging.getLogger(__name__)


def test_new_user():
    res = generate_unique_name("Absolutt lakk & bilverksted as")
    assert res == "absolutt-lakk-bilverksted"

    res = generate_unique_name("fagerhøy")
    assert res == "fagerhoy"
