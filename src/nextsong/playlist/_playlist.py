"""Implementation of playlist subpackage"""

__all__ = ["Playlist"]

from pathlib import Path
import pickle
import warnings

from lxml import etree

import nextsong.sequence as seq
from nextsong.config import get as get_config


class Playlist:
    """A class used to describe and iterate over a media playlist

    This is the nextsong library's primary class. The general workflow
    is to create a Playlist instance then iterate over it using the
    builtin iter and next functions. A Playlist may also be saved and
    loaded from an XML file using the save_xml method and load_xml
    static method.
    """

    class PlaylistState:
        def __init__(self, iterator):
            self.__iterator = iterator

        def __next__(self):
            return next(self.__iterator)

        def save(self, filepath=None):
            if filepath is None:
                filepath = get_config("state_path")
            with open(filepath, "wb") as file:
                return pickle.dump(self, file)

    def __init__(
        self,
        *children,
        shuffle=None,
        loop=None,
        portion=None,
        count=None,
        recent_portion=None,
        weight=None,
    ):
        """Create a new Playlist instance

        Positional arguments are items in the playlist. Each item should
        be either another Playlist instance or a string. A string should
        be an absolute path or a path relative to the globally
        configured 'media_root'. A string may also be a glob pattern. If
        the literal file cannot be found, it will be expanded to a list
        of files under the pathlib glob expansion rules.

        Keyword arguments
        -----------------
        shuffle:
            If True, the Playlist will iterate through its children in a
            random order.
        loop:
            If True, the Playlist will loop forever through its
            children. Only the top-level Playlist can have loop=True.
        portion:
            A number or pair of numbers between 0 and 1. Specifies the
            portion of items in the playlist to be used in a pass of the
            Playlist. For example a portion of 0.2 means only 20% of
            items in the Playlist will be used. If a pair of numbers is
            given, a uniformly random value between the pair of numbers
            will be used. This argument is mutually exclusive with
            count.
        count:
            An integer or pair of integers. Specifies the number of
            items in the playlist to be used in a pass of the Playlist.
            For example a count of 2 means only 2 of items in the
            Playlist will be used. If a pair of numbers is given, a
            uniformly random value between the pair of numbers
            (inclusive) will be used. This argument is mutually
            exclusive with portion.
        recent_portion:
            A number between 0 and 1. This argument can only be used if
            shuffle and loop are both True. By default, a shuffled
            looping Playlist doesn't select items truly independently.
            Items that were recently selected are marked as recent, and
            only non-recent items are candidates for selection. This
            argument specifies the maximum portion of the Playlist that
            can be recent. For example, if recent_portion is 0.2 and the
            Playlist has 10 items, the two most recently selected items
            will not be randomly selected.
        weight:
            A non-negative number indicating the relative likelyhood of
            this Playlist being chosen over its siblings during a random
            sampling. A Playlist with a weight of zero is disabled and
            will never be selected.
        """

        self.__validate_children(children)
        self.__children = children

        options = {
            "shuffle": shuffle,
            "portion": portion,
            "count": count,
            "recent_portion": recent_portion,
            "weight": weight,
            "loop": loop,
        }
        self.__validate_options(options)
        self.__options = options

    @staticmethod
    def __validate_children(children):
        for child in children:
            if isinstance(child, Playlist):
                if child.options["loop"]:
                    raise ValueError(
                        "loop=True is only allowed for the top-level Playlist"
                    )
            elif isinstance(child, str):
                pass
            else:
                raise ValueError(f"child {repr(child)} of unknown type")

    @staticmethod
    def __validate_options(options):
        if options["loop"]:
            if options["weight"] is not None:
                raise ValueError("weight requires loop=False")
            if options["shuffle"]:
                if options["count"] is not None:
                    raise ValueError("count requires loop=False or shuffle=False")
                if options["portion"] is not None:
                    raise ValueError("portion requires loop=False or shuffle=False")
            else:
                if options["recent_portion"] is not None:
                    raise ValueError("recent_portion requires shuffle=True")
        else:
            if options["recent_portion"] is not None:
                if options["shuffle"]:
                    raise ValueError("recent_portion requires loop=True")
                raise ValueError("recent_portion requires loop=True and shuffle=True")

    @property
    def children(self):
        return list(self.__children)

    @property
    def options(self):
        return dict(self.__options)

    @staticmethod
    def __resolve_path(path):
        root = Path(get_config("media_root"))
        resolved_path = (root / path).resolve()
        if resolved_path.exists():
            resolved_paths = [resolved_path]
        else:
            resolved_paths = sorted(p.resolve() for p in root.glob(path))
            resolved_paths = [p for p in resolved_paths if p.exists()]
            if not resolved_paths:
                warnings.warn(
                    f'file "{resolved_path}" not found and has no matches as a glob pattern'
                )

        if get_config("media_exts"):
            supported_paths = []
            for resolved_path in resolved_paths:
                if resolved_path.suffix.lower().lstrip(".") in get_config("media_exts"):
                    supported_paths.append(resolved_path)
                else:
                    warnings.warn(
                        f'file "{resolved_path}" has unsupported extension and will be skipped'
                    )
        else:
            supported_paths = resolved_paths
        return supported_paths

    def create_sequence(self):
        processed_children = []
        for child in self.children:
            if isinstance(child, Playlist):
                processed_children.append(child.create_sequence())
            if isinstance(child, str):
                processed_children.extend(self.__resolve_path(child))

        if self.options["loop"]:
            if self.options["shuffle"]:
                return seq.ShuffledLoopingSequence(
                    *processed_children, recent_portion=self.options["recent_portion"]
                )
            return seq.OrderedLoopingSequence(
                *processed_children,
                portion=self.options["portion"],
                count=self.options["count"],
            )

        return seq.FiniteSequence(
            *processed_children,
            weight=self.options["weight"],
            portion=self.options["portion"],
            count=self.options["count"],
            shuffle=self.options["shuffle"],
        )

    def __iter__(self):
        return self.PlaylistState(iter(self.create_sequence()))

    def save_xml(self, filepath=None):
        if filepath is None:
            filepath = get_config("playlist_path")

        root = etree.Element("nextsong")

        meta = etree.Element("meta")
        root.append(meta)

        def to_attributes(options):
            attributes = {}
            for key, val in options.items():
                if val is None:
                    continue
                if isinstance(val, bool):
                    if val is True:
                        attributes[key] = "true"
                        continue
                    if val is False:
                        attributes[key] = "false"
                        continue
                if isinstance(val, (int, float)):
                    attributes[key] = str(val)
                    continue
                if isinstance(val, (tuple, list)):
                    attributes[key] = " ".join(str(x) for x in val)
                    continue
                warnings.warn(f'could not serialize option "{key}" with value "{val}"')
            return attributes

        def to_elem(node):
            if isinstance(node, str):
                elem = etree.Element("path")
                elem.text = node
                return elem
            if isinstance(node, Playlist):
                elem = etree.Element("playlist", **to_attributes(node.options))
                for child in node.children:
                    subelem = to_elem(child)
                    elem.append(subelem)
                return elem
            raise ValueError(f"Unexpected Playlist item: {node}")

        elem = to_elem(self)
        root.append(elem)

        tree = etree.ElementTree(root)
        tree.write(filepath, pretty_print=True)

    @staticmethod
    def load_xml(filepath=None):
        if filepath is None:
            filepath = get_config("playlist_path")

        def to_options(attributes):
            options = {}
            for key, val in attributes.items():
                if val == "true":
                    options[key] = True
                    continue
                if val == "false":
                    options[key] = False
                    continue
                tokens = val.split(" ")
                parsed_tokens = []
                for token in tokens:
                    parse_type = float if "." in token else int
                    try:
                        parsed_tokens.append(parse_type(token))
                    except ValueError:
                        warnings.warn(
                            f'could not deserialize attribute "{key}" with value "{val}"'
                        )
                        continue
                if len(parsed_tokens) == 1:
                    options[key] = parsed_tokens[0]
                else:
                    options[key] = parsed_tokens
            return options

        def to_node(elem):
            if elem.tag.lower() == "path":
                return elem.text
            if elem.tag.lower() == "playlist":
                children = [to_node(x) for x in elem]
                children = [x for x in children if x is not None]
                options = to_options(elem.attrib)
                return Playlist(*children, **options)
            warnings.warn(f'unexpected tag "{elem.tag}"')
            return None

        tree = etree.parse(filepath)
        root = tree.getroot()
        if root.tag.lower() == "playlist":
            elem = root
        else:
            subelems = [x for x in root if x.tag.lower() == "playlist"]
            if len(subelems) != 1:
                raise ValueError("could not find element with playlist tag")
            elem = subelems[0]

        return to_node(elem)

    @staticmethod
    def load_state(filepath=None, *, handle_not_found=True):
        if filepath is None:
            filepath = get_config("state_path")
        try:
            with open(filepath, "rb") as file:
                return pickle.load(file)
        except FileNotFoundError:
            if handle_not_found:
                return None
            raise