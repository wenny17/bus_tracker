import json

import pytest


@pytest.mark.parametrize("data, expected_response", [
    (
        "just string",
        {"errors": ["Requires valid JSON"], "msgType": "Errors"}
    ),
    (
        json.dumps({"wrong key": "value"}),
        {"errors": ["Requires busId specified"], "msgType": "Errors"}
    )
])
async def test_harmful_client(bus_data_stream, data, expected_response):
    await bus_data_stream.send_message(data)
    response = json.loads(await bus_data_stream.get_message())
    assert response == expected_response
