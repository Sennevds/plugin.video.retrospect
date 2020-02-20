# SPDX-License-Identifier: CC-BY-NC-SA-4.0

from resources.lib.logger import Logger
from resources.lib.paramparsers.action import Action
from resources.lib.paramparsers.parameter import Parameter
from resources.lib.paramparsers.paramparser import ParamParser

from resources.lib.channelinfo import ChannelInfo
from resources.lib.chn_class import Channel
from resources.lib.mediaitem import MediaItem

# The main URL mapping if parameters.
URL_MAP = {
    Action.LIST_FOLDER: {
        Parameter.CHANNEL: 0,
        Parameter.CHANNEL_CODE: 1,
        Parameter.PICKLE: -2,
    },
    Action.LIST_CATEGORY: {
        Parameter.CATEGORY: 0,
    }
}


class UriParser(ParamParser):
    def __init__(self, add_on_id, add_on_path, query):
        """ Creates a base UriParser object.

        :param str add_on_id:    The id of the add-on
        :param str query:        The url to parse
        :param str add_on_path:  The add-on plugin-uri (the plugin://....) part

        """

        super(UriParser, self).__init__(add_on_id, add_on_path, query)

    def parse_url(self):
        """ Extracts the actual parameters as a dictionary from the passed in querystring.

        :return: dict() of keywords and values.
        :rtype: dict[str,str|None|MediaItem]

        """

        self._params = dict()

        url_parts = self._addon_path.split("/")[3:]
        if not url_parts[0]:
            return self._params

        action = url_parts.pop(0)
        self._params[Parameter.ACTION] = action

        parameters = URL_MAP.get(action)
        if not parameters:
            raise NotImplementedError("Action '{}' is not implemented".format(action))

        for parameter, idx in parameters.items():
            # Check of optional parameters
            if idx < 0:
                idx = -idx
                if len(url_parts) <= idx:
                    continue
            try:
                self._params[parameter] = url_parts[idx] or None
            except IndexError as ex:
                raise ValueError("Missing parameter: {}".format(parameter), ex)

        pickle = self._params.get(Parameter.PICKLE)
        if pickle:
            Logger.debug("Found Pickle: %s", pickle)
            self._params[Parameter.ITEM] = self._pickler.de_pickle_media_item(pickle)

        return self._params

        # This does not work yet.
        # params = self._addon_path.split("/")
        # params_count = len(params)
        # for param, param_idx in URL_MAP.items():
        #     # if the index is higher than the parameter count, stop
        #     if param_idx >= params_count:
        #         continue
        #
        #     self._params[param] = params[param_idx] or None
        #
        # # If there was an item, de-pickle it
        # pickle = self._params.get(Parameter.PICKLE)
        # if pickle:
        #     self._params[Parameter.ITEM] = self._pickler.de_pickle_media_item(pickle)
        #
        # return self._params

    def _create_url(self, channel, action, item=None, category=None):
        """ Creates an URL that includes an action.

        :param ChannelInfo|Channel|None channel:    The channel object to use for the URL.
        :param str action:                          Action to create an url for
        :param MediaItem item:                      The media item to add
        :param str category:                        The category to use.

        :return: a complete action url with all keywords and values
        :rtype: str|unicode

        """

        if not action:
            raise ValueError("Cannot create URL without 'action'")

        if action == Action.ALL_FAVOURITES:
            return "plugin://{}/{}".format(self._addon_id, action)

        if action == Action.LIST_FOLDER:
            pickle = None
            if item:
                pickle = self._pickler.pickle_media_item(item)
            return "plugin://{}/{}/{}/{}/{}".format(
                self._addon_id, action,
                channel.moduleName, channel.channelCode or "", pickle or "")

        raise NotImplementedError("Action '{}' is not implemented".format(action))

    def __str__(self):
        return "Uri-{}".format(super(UriParser, self).__str__())