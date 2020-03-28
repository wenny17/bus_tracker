import json

import pytest


@pytest.mark.parametrize("data, expected_response", [
    (
        "just string",
        {"errors": ["Requires valid JSON"], "msgType": "Errors"}
    ),
    (
        json.dumps({"wrong key": "value"}),
        {"errors": ["Requires msgType specified"], "msgType": "Errors"}
    )
])
async def test_harmful_client(client_stream, data, expected_response):
    _ = await client_stream.get_message()
    await client_stream.send_message(data)
    response = json.loads(await client_stream.get_message())
    assert response == expected_response
