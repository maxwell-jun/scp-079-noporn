# SCP-079-NOPORN - Auto delete NSFW media messages
# Copyright (C) 2019 SCP-079 <https://scp-079.org>
#
# This file is part of SCP-079-NOPORN.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import logging
from typing import Iterable, List, Optional, Union

from pyrogram import Chat, ChatMember, ChatPermissions, ChatPreview, Client, InlineKeyboardMarkup, Message
from pyrogram.api.functions.messages import GetStickerSet
from pyrogram.api.functions.users import GetFullUser
from pyrogram.api.types import InputPeerUser, InputPeerChannel, InputStickerSetShortName, StickerSet, UserFull
from pyrogram.api.types.messages import StickerSet as messages_StickerSet
from pyrogram.errors import ChannelInvalid, ChannelPrivate, FloodWait, PeerIdInvalid
from pyrogram.errors import UsernameInvalid, UsernameNotOccupied, UserNotParticipant

from .. import glovar
from .etc import delay, get_int, t2t, wait_flood

# Enable logging
logger = logging.getLogger(__name__)


def delete_messages(client: Client, cid: int, mids: Iterable[int]) -> Optional[bool]:
    # Delete some messages
    result = None
    try:
        mids = list(mids)
        mids_list = [mids[i:i + 100] for i in range(0, len(mids), 100)]
        for mids in mids_list:
            try:
                flood_wait = True
                while flood_wait:
                    flood_wait = False
                    try:
                        result = client.delete_messages(chat_id=cid, message_ids=mids)
                    except FloodWait as e:
                        flood_wait = True
                        wait_flood(e)
            except Exception as e:
                logger.warning(f"Delete message {mids} in {cid} for loop error: {e}", exc_info=True)
    except Exception as e:
        logger.warning(f"Delete messages in {cid} error: {e}", exc_info=True)

    return result


def download_media(client: Client, file_id: str, file_ref: str, file_path: str):
    # Download a media file
    result = None
    try:
        flood_wait = True
        while flood_wait:
            flood_wait = False
            try:
                result = client.download_media(message=file_id, file_ref=file_ref, file_name=file_path)
            except FloodWait as e:
                flood_wait = True
                wait_flood(e)
    except Exception as e:
        logger.warning(f"Download media {file_id} to {file_path} error: {e}", exc_info=True)

    return result


def get_admins(client: Client, cid: int) -> Optional[Union[bool, List[ChatMember]]]:
    # Get a group's admins
    result = None
    try:
        flood_wait = True
        while flood_wait:
            flood_wait = False
            try:
                result = client.get_chat_members(chat_id=cid, filter="administrators")
            except FloodWait as e:
                flood_wait = True
                wait_flood(e)
            except (PeerIdInvalid, ChannelInvalid, ChannelPrivate):
                return False
    except Exception as e:
        logger.warning(f"Get admins in {cid} error: {e}", exc_info=True)

    return result


def get_chat(client: Client, cid: Union[int, str]) -> Optional[Union[Chat, ChatPreview]]:
    # Get a chat
    result = None
    try:
        flood_wait = True
        while flood_wait:
            flood_wait = False
            try:
                result = client.get_chat(chat_id=cid)
            except FloodWait as e:
                flood_wait = True
                wait_flood(e)
    except Exception as e:
        logger.warning(f"Get chat {cid} error: {e}", exc_info=True)

    return result


def get_chat_member(client: Client, cid: int, uid: int) -> Optional[ChatMember]:
    # Get information about one member of a chat
    result = None
    try:
        flood_wait = True
        while flood_wait:
            flood_wait = False
            try:
                result = client.get_chat_member(chat_id=cid, user_id=uid)
            except FloodWait as e:
                flood_wait = True
                wait_flood(e)
            except UserNotParticipant:
                result = False
    except Exception as e:
        logger.warning(f"Get chat member {uid} in {cid} error: {e}", exc_info=True)

    return result


def get_group_info(client: Client, chat: Union[int, Chat], cache: bool = True) -> (str, str):
    # Get a group's name and link
    group_name = "Unknown Group"
    group_link = glovar.default_group_link
    try:
        if isinstance(chat, int):
            the_cache = glovar.chats.get(chat)
            if the_cache:
                chat = the_cache
            else:
                result = get_chat(client, chat)

                if cache and result:
                    glovar.chats[chat] = result

                chat = result

        if not chat:
            return group_name, group_link

        if chat.title:
            group_name = chat.title

        if chat.username:
            group_link = "https://t.me/" + chat.username
    except Exception as e:
        logger.info(f"Get group {chat} info error: {e}", exc_info=True)

    return group_name, group_link


def get_messages(client: Client, cid: int, mids: Iterable[int]) -> Optional[List[Message]]:
    # Get some messages
    result = None
    try:
        flood_wait = True
        while flood_wait:
            flood_wait = False
            try:
                result = client.get_messages(chat_id=cid, message_ids=mids)
            except FloodWait as e:
                flood_wait = True
                wait_flood(e)
    except Exception as e:
        logger.warning(f"Get messages {mids} in {cid} error: {e}", exc_info=True)

    return result


def get_sticker_title(client: Client, short_name: str, normal: bool = False) -> Optional[str]:
    # Get sticker set's title
    result = None
    try:
        sticker_set = InputStickerSetShortName(short_name=short_name)
        flood_wait = True
        while flood_wait:
            flood_wait = False
            try:
                the_set = client.send(GetStickerSet(stickerset=sticker_set))
                if isinstance(the_set, messages_StickerSet):
                    inner_set = the_set.set
                    if isinstance(inner_set, StickerSet):
                        result = t2t(inner_set.title, normal)
            except FloodWait as e:
                flood_wait = True
                wait_flood(e)
    except Exception as e:
        logger.warning(f"Get sticker {short_name} title error: {e}", exc_info=True)

    return result


def get_user_bio(client: Client, uid: int, normal: bool = False) -> Optional[str]:
    # Get user's bio
    result = None
    try:
        user_id = resolve_peer(client, uid)
        if not user_id:
            return None

        flood_wait = True
        while flood_wait:
            flood_wait = False
            try:
                user: UserFull = client.send(GetFullUser(id=user_id))
                if user and user.about:
                    result = t2t(user.about, normal)
            except FloodWait as e:
                flood_wait = True
                wait_flood(e)
    except Exception as e:
        logger.warning(f"Get user {uid} bio error: {e}", exc_info=True)

    return result


def kick_chat_member(client: Client, cid: int, uid: Union[int, str]) -> Optional[Union[bool, Message]]:
    # Kick a chat member in a group
    result = None
    try:
        flood_wait = True
        while flood_wait:
            flood_wait = False
            try:
                result = client.kick_chat_member(chat_id=cid, user_id=uid)
            except FloodWait as e:
                flood_wait = True
                wait_flood(e)
    except Exception as e:
        logger.warning(f"Kick chat member {uid} in {cid} error: {e}", exc_info=True)

    return result


def leave_chat(client: Client, cid: int) -> bool:
    # Leave a channel
    try:
        flood_wait = True
        while flood_wait:
            flood_wait = False
            try:
                client.leave_chat(chat_id=cid)
            except FloodWait as e:
                flood_wait = True
                wait_flood(e)

        return True
    except Exception as e:
        logger.warning(f"Leave chat {cid} error: {e}", exc_info=True)

    return False


def resolve_peer(client: Client, pid: Union[int, str]) -> Optional[Union[bool, InputPeerChannel, InputPeerUser]]:
    # Get an input peer by id
    result = None
    try:
        flood_wait = True
        while flood_wait:
            flood_wait = False
            try:
                result = client.resolve_peer(pid)
            except FloodWait as e:
                flood_wait = True
                wait_flood(e)
            except (PeerIdInvalid, UsernameInvalid, UsernameNotOccupied):
                return False
    except Exception as e:
        logger.warning(f"Resolve peer {pid} error: {e}", exc_info=True)

    return result


def resolve_username(client: Client, username: str, cache: bool = True) -> (str, int):
    # Resolve peer by username
    peer_type = ""
    peer_id = 0
    try:
        username = username.strip("@")
        if not username:
            return "", 0

        result = glovar.usernames.get(username)
        if result and cache:
            return result["peer_type"], result["peer_id"]

        result = resolve_peer(client, username)
        if result:
            if isinstance(result, InputPeerChannel):
                peer_type = "channel"
                peer_id = result.channel_id
                peer_id = get_int(f"-100{peer_id}")
            elif isinstance(result, InputPeerUser):
                peer_type = "user"
                peer_id = result.user_id

        glovar.usernames[username] = {
            "peer_type": peer_type,
            "peer_id": peer_id
        }
    except Exception as e:
        logger.warning(f"Resolve username {username} error: {e}", exc_info=True)

    return peer_type, peer_id


def restrict_chat_member(client: Client, cid: int, uid: int, permissions: ChatPermissions,
                         until_date: int = 0) -> Optional[Chat]:
    # Restrict a user in a supergroup
    result = None
    try:
        flood_wait = True
        while flood_wait:
            flood_wait = False
            try:
                result = client.restrict_chat_member(
                    chat_id=cid,
                    user_id=uid,
                    permissions=permissions,
                    until_date=until_date
                )
            except FloodWait as e:
                flood_wait = True
                wait_flood(e)
    except Exception as e:
        logger.warning(f"Restrict chat member {uid} in {cid} error: {e}", exc_info=True)

    return result


def send_document(client: Client, cid: int, document: str, file_ref: str = None, caption: str = "", mid: int = None,
                  markup: InlineKeyboardMarkup = None) -> Optional[Union[bool, Message]]:
    # Send a document to a chat
    result = None
    try:
        flood_wait = True
        while flood_wait:
            flood_wait = False
            try:
                result = client.send_document(
                    chat_id=cid,
                    document=document,
                    file_ref=file_ref,
                    caption=caption,
                    parse_mode="html",
                    reply_to_message_id=mid,
                    reply_markup=markup
                )
            except FloodWait as e:
                flood_wait = True
                wait_flood(e)
            except (PeerIdInvalid, ChannelInvalid, ChannelPrivate):
                return False
    except Exception as e:
        logger.warning(f"Send document {document} to {cid} error: {e}", exec_info=True)

    return result


def send_message(client: Client, cid: int, text: str, mid: int = None,
                 markup: InlineKeyboardMarkup = None) -> Optional[Union[bool, Message]]:
    # Send a message to a chat
    result = None
    try:
        if not text.strip():
            return None

        flood_wait = True
        while flood_wait:
            flood_wait = False
            try:
                result = client.send_message(
                    chat_id=cid,
                    text=text,
                    parse_mode="html",
                    disable_web_page_preview=True,
                    reply_to_message_id=mid,
                    reply_markup=markup
                )
            except FloodWait as e:
                flood_wait = True
                wait_flood(e)
            except (PeerIdInvalid, ChannelInvalid, ChannelPrivate):
                return False
    except Exception as e:
        logger.warning(f"Send message to {cid} error: {e}", exc_info=True)

    return result


def send_report_message(secs: int, client: Client, cid: int, text: str, mid: int = None,
                        markup: InlineKeyboardMarkup = None) -> Optional[Message]:
    # Send a message that will be auto deleted to a chat
    result = None
    try:
        if not text.strip():
            return None

        flood_wait = True
        while flood_wait:
            flood_wait = False
            try:
                result = client.send_message(
                    chat_id=cid,
                    text=text,
                    parse_mode="html",
                    disable_web_page_preview=True,
                    reply_to_message_id=mid,
                    reply_markup=markup
                )
            except FloodWait as e:
                flood_wait = True
                wait_flood(e)

        if not result:
            return None

        mid = result.message_id
        mids = [mid]
        delay(secs, delete_messages, [client, cid, mids])
    except Exception as e:
        logger.warning(f"Send report message to {cid} error: {e}", exc_info=True)

    return result
