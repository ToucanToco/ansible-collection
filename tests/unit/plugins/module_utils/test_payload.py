import pytest

from plugins.module_utils.payload import diff_attributes

@pytest.mark.parametrize("payload, compare, expected" , [
        pytest.param(
            {"subdomain": "tesst", "company_name": "ToucanToco"},
            {"subdomain": "tesst", "company_name": "ToucanToco"},
            {},
            id="No new attributes"),
        pytest.param(
            {"subdomain": "tesst", "company_name": "ToucanToco", "logo_url": "http://MySuperLogo.png"},
            {"subdomain": "tesst", "company_name": "ToucanToco", "logo_url": None},
            {"logo_url": "http://MySuperLogo.png"},
            id="One new attribute"),
        pytest.param(
            {"subdomain": "tesst", "company_name": "NewCompany"},
            {"subdomain": "tesst", "company_name": "ToucanToco"},
            {"company_name": "NewCompany"},
            id="One attribute to update"),
    ]
)
def test_diff_attributes(payload, compare, expected):
    res = diff_attributes(payload, compare)
    assert res == expected
