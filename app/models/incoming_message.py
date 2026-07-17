import datetime as dt
from typing import Optional

from telethon import events


class IncomingMessage:
    """Domain model representing an incoming Telegram message"""
    
    def __init__(
        self,
        message_id: int,
        chat_id: int,
        chat_title: str,
        sender_id: int,
        sender_name: str,
        text: str,
        date: dt.datetime,
        has_media: bool,
        raw_event: events.NewMessage.Event
    ):
        self.message_id = message_id
        self.chat_id = chat_id
        self.chat_title = chat_title
        self.sender_id = sender_id
        self.sender_name = sender_name
        self.text = text
        self.date = date
        self.has_media = has_media
        self.raw_event = raw_event