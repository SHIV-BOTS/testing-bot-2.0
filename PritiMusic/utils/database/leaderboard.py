from PritiMusic.core.mongo import mongodb as db

clone_lb = db.clone_leaderboard

async def update_leaderboard(bot_id: int, bot_username: str):
    """Har baar gaana play hone par clone bot ka counter badhayega."""
    await clone_lb.update_one(
        {"bot_id": bot_id},
        {"$inc": {"plays": 1}, "$set": {"bot_username": bot_username}},
        upsert=True
    )

async def get_leaderboard():
    """Top clone bots ko fetch karega."""
    return await clone_lb.find().sort("plays", -1).limit(10).to_list(length=10)

async def reset_leaderboard():
    """Monthly leaderboard clear karne ke liye."""
    await clone_lb.drop()
