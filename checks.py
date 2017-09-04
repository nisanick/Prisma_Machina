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


def react_check(self, reaction, user):
    if user is None or user.id != self.author.id:
        return False

    if reaction.message.id != self.message.id:
        return False

    for emoji, process in [('❌', False), ('✅', True)]:
        if reaction.emoji == emoji:
            self.process_transaction = process
            return True
    return False
