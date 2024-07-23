from pyrogram import Client, filters
from pyrogram.types import ChatPermissions
from datetime import datetime, timedelta
import asyncio

API_TOKEN = "YOUR_API_TOKEN"
app = Client("task_promote_bot", bot_token=API_TOKEN)

# Dictionary to store promotion details
promotion_details = {}

@app.on_message(filters.group & ~filters.service)
async def count_messages(client, message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    current_date = datetime.now().date()

    if chat_id in promotion_details:
        if user_id in promotion_details[chat_id]:
            promo_data = promotion_details[chat_id][user_id]
            if promo_data["promotion_date"] == current_date:
                promo_data["message_count"] += 1

@app.on_message(filters.command("taskpromote", prefixes="/") & filters.group)
async def promote_user(client, message):
    if message.from_user.status not in ["administrator", "creator"]:
        await message.reply("You need to be an admin to use this command.")
        return
    
    if len(message.command) != 2 or not message.command[1].isdigit():
        await message.reply("Usage: /taskpromote <number_of_messages>")
        return
    
    target_user = message.reply_to_message.from_user
    if not target_user:
        await message.reply("You need to reply to the user's message whom you want to promote.")
        return

    chat_id = message.chat.id
    user_id = target_user.id
    required_message_count = int(message.command[1])
    current_date = datetime.now().date()

    promotion_details.setdefault(chat_id, {})[user_id] = {
        "required_message_count": required_message_count,
        "message_count": 0,
        "promotion_date": current_date,
        "promoted": True
    }

    await client.promote_chat_member(
        chat_id, user_id,
        can_manage_chat=True,
        can_change_info=True,
        can_delete_messages=True,
        can_invite_users=True,
        can_restrict_members=True,
        can_pin_messages=True,
        can_promote_members=True,
        can_manage_video_chats=True
    )

    await message.reply(f"{target_user.mention} has been promoted. They must send {required_message_count} messages today to stay promoted.")

    # Schedule demotion after 24 hours
    await asyncio.sleep(24 * 60 * 60)

    if promotion_details[chat_id][user_id]["message_count"] < required_message_count:
        await client.restrict_chat_member(chat_id, user_id, permissions=ChatPermissions())
        await message.reply(f"{target_user.mention} has been demoted for not meeting the message requirement.")
        promotion_details[chat_id][user_id]["promoted"] = False
    else:
        await message.reply(f"{target_user.mention} has met the message requirement and remains promoted.")

app.run()
