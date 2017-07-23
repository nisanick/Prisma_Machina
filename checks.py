import config

async def can_manage_bot(ctx):
    if ctx.message.author.id in config.ADMIN_USERS:
        return True
    for role in ctx.message.author.roles:
        if role.name in config.ADMIN_ROLES:
            return True
    return False

async def in_admin_channel(ctx):
    return ctx.channel.id == int(config.ADMINISTRATION_CHANNEL)
