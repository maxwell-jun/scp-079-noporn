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

from pyrogram import Client

from .. import glovar
from .etc import thread
from .channel import share_bad_user, share_data
from .file import save
from .telegram import delete_messages, kick_chat_member

# Enable logging
logger = logging.getLogger(__name__)


def add_bad_user(client: Client, uid: int) -> bool:
    try:
        glovar.bad_ids["users"].add(uid)
        save("bad_ids")
        share_bad_user(client, uid)
        return True
    except Exception as e:
        logger.warning(f"Add bad user error: {e}", exc_info=True)

    return False


def ban_user(client: Client, gid: int, uid: int) -> bool:
    try:
        thread(kick_chat_member, (client, gid, uid))
        return True
    except Exception as e:
        logger.warning(f"Ban user error: {e}", exc_info=True)

    return False


def delete_message(client: Client, gid: int, mid: int) -> bool:
    try:
        mids = [mid]
        thread(delete_messages, (client, gid, mids))
        return True
    except Exception as e:
        logger.warning(f"Delete message error: {e}", exc_info=True)

    return False


def update_score(client: Client, uid: int) -> bool:
    try:
        nsfw_count = len(glovar.user_ids[uid]["nsfw"])
        nsfw_score = nsfw_count * 0.6
        warn_score = glovar.user_ids[uid]["score"]["warn"]
        glovar.user_ids[uid]["score"]["total"] = nsfw_score + warn_score
        save("user_ids")
        share_data(
            client=client,
            sender="NOPORN",
            receivers=["NOSPAM"],
            action="update",
            action_type="score",
            data={
                "id": uid,
                "score": nsfw_score
            }
        )
        return True
    except Exception as e:
        logger.warning(f"Update score error: {e}", exc_info=True)

    return False
