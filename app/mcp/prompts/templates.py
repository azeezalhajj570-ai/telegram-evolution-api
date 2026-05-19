from mcp.server.fastmcp import FastMCP


def register_prompts(mcp: FastMCP):
    @mcp.prompt(
        name="compose_message",
        description="Help compose a Telegram message for a specific recipient and context",
    )
    async def compose_message(recipient: str, context: str = "", tone: str = "casual") -> list[dict]:
        tone_guide = {
            "formal": "Use formal language, proper greetings, and professional tone.",
            "casual": "Use conversational language, be friendly and approachable.",
            "urgent": "Get straight to the point, convey importance clearly.",
        }.get(tone, "Use conversational language.")

        prompt = f"You are drafting a Telegram message to {recipient}.\n\n"
        if context:
            prompt += f"Context: {context}\n\n"
        prompt += f"Tone: {tone_guide}\n\n"
        prompt += "Draft the message now:"
        return [{"role": "user", "content": prompt}]

    @mcp.prompt(
        name="summarize_chat",
        description="Summarize recent activity in a Telegram chat",
    )
    async def summarize_chat(chat_id: int, hours: int = 24) -> list[dict]:
        prompt = (
            f"Please summarize the recent activity in Telegram chat {chat_id} "
            f"over the last {hours} hours.\n\n"
            "Focus on:\n"
            "- Key discussion topics\n"
            "- Important messages or announcements\n"
            "- Decisions made or action items\n"
            "- Overall sentiment and activity level"
        )
        return [{"role": "user", "content": prompt}]

    @mcp.prompt(
        name="draft_reply",
        description="Draft a reply to a specific message in a Telegram chat",
    )
    async def draft_reply(chat_id: int, message_id: int) -> list[dict]:
        prompt = (
            f"Draft a reply to message {message_id} in Telegram chat {chat_id}.\n\n"
            "First, analyze the message:\n"
            "- What is the sender's intent?\n"
            "- What is the appropriate response?\n\n"
            "Then draft a contextual reply."
        )
        return [{"role": "user", "content": prompt}]
