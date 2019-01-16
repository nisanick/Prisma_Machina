
import re


class TextChecker:

    @staticmethod
    def replace_emotes(text: str, bot) -> str:
        emote_string = ":[A-z0-9]+:"
        return_text = text
        expression = re.compile(emote_string)
        result = expression.findall(text)

        for word in set(result):
            emote_name = word[1:-1]
            emote = word
            for emoji in bot.emojis:
                if emoji.name.lower() == emote_name.lower():
                    emote = emoji
                    break
            return_text = return_text.replace(word, "<:{}:{}>".format(emote.name, emote.id))

        return return_text
