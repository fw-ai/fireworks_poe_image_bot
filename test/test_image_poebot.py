from typing import List
from fireworks_poe_image_bot import (
    FireworksPoeImageServerBot,
)
from sse_starlette.sse import ServerSentEvent
from fastapi_poe.types import (
    QueryRequest,
    ProtocolMessage,
    PartialResponse,
    ErrorResponse,
)

import unittest

from fireworks.client.api import (
    ChatCompletionResponseStreamChoice,
    ChatCompletionStreamResponse,
    DeltaMessage,
)


class TestFWPoeImageBot(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.model = "accounts/fireworks/models/stable-diffusion-xl-1024-v1-0"
        self.environment = ""
        self.server_version = ""
        self.s3_bucket_name = "fireworks-public-poe-temp-images"
        self.bot = FireworksPoeImageServerBot(
            model=self.model,
            environment=self.environment,
            server_version=self.server_version,
            s3_bucket_name=self.s3_bucket_name,
        )

    async def _test_with_query(self, query: List[ProtocolMessage]):
        query_request = QueryRequest(
            version="",
            type="query",
            query=query,
            user_id="",
            conversation_id="",
            message_id="",
        )
        resp_fragments = []
        async for resp in self.bot.get_response(query_request):
            if isinstance(resp, ErrorResponse):
                self.fail(resp.text)
            elif isinstance(resp, PartialResponse):
                resp_fragments.append(resp.text)
            elif isinstance(resp, ServerSentEvent):
                assert resp.event == "done", resp.event
        return "".join(resp_fragments)

    async def test_empty_query(self):
        with self.assertRaisesRegex(AssertionError, "Empty query"):
            await self._test_with_query([])

    async def test_single_query(self):
        resp = await self._test_with_query(
            [
                ProtocolMessage(role="user", content="hello"),
            ]
        )
        # self.assertEqual(resp, "foo")
        self.assertIn("![image](https://", resp)

    async def test_single_req_response(self):
        resp = await self._test_with_query(
            [
                ProtocolMessage(role="user", content="hello"),
                ProtocolMessage(role="bot", content="foo"),
                ProtocolMessage(role="user", content="bar"),
            ]
        )
        self.assertEqual(resp, "foo")

    async def test_system_prompt(self):
        resp = await self._test_with_query(
            [
                ProtocolMessage(role="system", content="hello"),
                ProtocolMessage(role="user", content="foo"),
            ]
        )
        self.assertEqual(resp, "foo")

    async def test_system_prompt_req_response(self):
        resp = await self._test_with_query(
            [
                ProtocolMessage(role="system", content="hello"),
                ProtocolMessage(role="user", content="foo"),
                ProtocolMessage(role="bot", content="bar"),
                ProtocolMessage(role="user", content="baz"),
            ]
        )
        self.assertEqual(resp, "foo")

    async def test_no_initial_user_msg(self):
        resp = await self._test_with_query(
            [
                ProtocolMessage(role="bot", content="hello"),
                ProtocolMessage(role="user", content="foo"),
            ]
        )
        self.assertEqual(resp, "foo")

    async def test_duplicate_user_msgs(self):
        resp = await self._test_with_query(
            [
                ProtocolMessage(role="user", content="hello"),
                ProtocolMessage(role="user", content="foo"),
            ]
        )
        self.assertEqual(resp, "foo")

    async def test_duplicate_assistant_msgs(self):
        resp = await self._test_with_query(
            [
                ProtocolMessage(role="user", content="hello"),
                ProtocolMessage(role="bot", content="foo"),
                ProtocolMessage(role="bot", content="bar"),
            ]
        )
        self.assertEqual(resp, "foo")

    async def test_no_final_user_msg(self):
        resp = await self._test_with_query(
            [
                ProtocolMessage(role="user", content="hello"),
                ProtocolMessage(role="bot", content="foo"),
            ]
        )
        self.assertEqual(resp, "foo")


if __name__ == "__main__":
    unittest.main()
