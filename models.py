from pydantic import BaseModel
from typing import Optional, Dict


class JellyfinWebhookEvent(BaseModel):
    NotificationType: str
    Name: str
    ServerId: str
    ServerName: str
    ServerVersion: str
    ServerUrl: str
    Timestamp: str
    UtcTimestamp: str


class ItemAddedEvent(JellyfinWebhookEvent):
    ItemId: str
    ItemName: str
    ItemType: str
    ItemPath: str
    RunTimeTicks: Optional[int] = None
    ProductionYear: Optional[int] = None
    Genres: Optional[list] = None
    Tags: Optional[list] = None
    Overview: Optional[str] = None
    ProviderIds: Optional[Dict[str, str]] = None
    ImageTags: Optional[Dict[str, str]] = None
    MediaSources: Optional[list] = None


class PlaybackStartEvent(JellyfinWebhookEvent):
    ItemId: str
    ItemName: str
    ItemType: str
    ItemPath: str
    RunTimeTicks: Optional[int] = None
    ProductionYear: Optional[int] = None
    Genres: Optional[list] = None
    Tags: Optional[list] = None
    Overview: Optional[str] = None
    ProviderIds: Optional[Dict[str, str]] = None
    ImageTags: Optional[Dict[str, str]] = None
    MediaSources: Optional[list] = None
    UserId: str
    UserName: str
    Client: str
    DeviceName: str
    DeviceId: str
    ApplicationVersion: str
    PlaybackPosition: Optional[int] = None

