from . import DirectMessageLogger
from . import ExceptionHandler
from . import RoleDivider
from . import Statistics


def setup(bot):
    """ Called when this extension is loaded. """
    bot.add_cog(DirectMessageLogger(bot))
    bot.add_cog(ExceptionHandler(bot))
    bot.add_cog(RoleDivider(bot))
    bot.add_cog(Statistics(bot))
