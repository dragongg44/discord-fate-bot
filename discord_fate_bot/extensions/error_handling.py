import logging
import textwrap

from discord.ext.commands import Cog, CommandInvokeError, UserInputError

from ..emojis import random_error_emoji
from ..scenes import AspectIdError, NoCurrentSceneError
from ..util import ValidationError

logger = logging.getLogger(__name__)

def setup(bot):
    bot.add_cog(ErrorHandlingCog())


class ErrorHandlingCog(Cog):
    @Cog.listener()
    async def on_command_error(self, ctx, error):
        # Commands wrap their exceptions with this one.
        if isinstance(error, CommandInvokeError):
            error = error.__cause__

        if isinstance(error, UserInputError):
            message = (
                f"Sorry, I didn't understand:\n\n" \
                f"{quote(ctx.message)}\n\n" \
                f"{punctuate(error)}"
            )
            await send_error_message(ctx, message, help_separator=' ')
        elif isinstance(error, AspectIdError):
            message = (
                f"Sorry, there's no aspect in the current scene with id " \
                f"{error.aspect_id}."
            )
            await send_error_message(ctx, message)
        elif isinstance(error, NoCurrentSceneError):
            message = (
                f"Sorry, there's no current scene in this channel. You can " \
                f"start a new scene using **!scene new**."
            )
            await send_error_message(ctx, message)
        elif isinstance(error, ValidationError):
            message = f"{error}:\n\n"
            message += '\n'.join(
                f'    •  {complaint}'
                for complaint in error.complaints
            )
            await send_error_message(ctx, message)
        else:
            message = f"Sorry, something unexpected went wrong."
            await send_error_message(ctx, message)
            raise error

async def send_error_message(ctx, message, *, help_separator='\n\n'):
    """Send an error message with our standard boilerplate."""
    emoji = random_error_emoji()
    help_command = '!help ' + format_command_for_help(ctx.command)
    final_message = (
        f"{emoji}  {ctx.author.mention} {message}{help_separator}" \
        f"Try **{help_command}** for more information. "\
        f"(Feel free to DM {ctx.me.mention}.)"
    )
    await ctx.send(content=final_message)

def format_command_for_help(command):
    result = ''
    if command.parent:
        result += format_command_for_help(command.parent) + ' '
    result += command.name
    return result

def quote(message):
    content = message.content
    return textwrap.indent(content, '> ', lambda line: True)

def punctuate(text):
    text = str(text)
    if text[-1] in '!?.':
        return text
    return f"{text}."

