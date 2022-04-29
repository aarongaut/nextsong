"""Implementation of playlist subpackage"""

__all__ = ["Playlist", "ensure_state"]

from pathlib import Path
import pickle
import warnings
import time
import os

from lxml import etree  # type:ignore

import nextsong.sequence as seq
from nextsong.config import Config, get as get_cfg
from nextsong.datatypes import OnChange


class Playlist:
    """A class used to describe and iterate over a media playlist

    This is the nextsong library's primary class. The general workflow
    is to create a Playlist instance then iterate over it using the
    builtin iter and next functions. A Playlist may also be saved and
    loaded from an XML file using the save_xml method and load_xml
    static method.
    """

    class PlaylistState:
        """Represents the state of iteration through a Playlist

        This class is an iterator on a Playlist and can be pickled
        to a file.

        A PlaylistState can be used as the subject of a 'with'
        statement to ensure the pickle file is written at the end of
        the 'with' block. If the state was originally loaded from a
        file, the same file will be written to. Otherwise, the
        "state_path" config value will be used.
        """

        def __init__(self, iterator, from_path=None):
            """Internal constructor for PlaylistState

            Users should instead call Playlist.__iter__ or
            Playlist.load_state to create a PlaylistState.
            """
            self.__iterator = seq.WithPeek(iterator)
            self.__from_path = from_path
            self.creation_time = time.time()

        def __next__(self):
            return next(self.__iterator)

        def save(self, filepath=None):
            """Pickles a PlaylistState instance to a file

            Arguments
            ---------
            filepath: str or None
                The desired path to pickle to. If None, uses the value
                of the "state_path" config.
            """
            with Config(state_path=filepath) as cfg:
                with open(cfg.state_path, "wb") as file:
                    return pickle.dump(self, file)

        def peek(self):
            """Peek at the next track without consuming it"""
            return self.__iterator.peek()

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc_value, traceback):
            self.save(self.__from_path)

        @staticmethod
        def load(filepath=None, *, handle_not_found=False):
            """Loads a pickled PlaylistState instance from a file

            Arguments
            ---------
            filepath: str or None
                The path to the pickle file. If None, uses the value of
                the "state_path" config.
            handle_not_found: bool
                Determines what should happen if the given filepath
                doesn't exist. If True, a value of None is returned.
                If False, the FileNotFoundError is allowed to
                propagate.
            """
            try:
                with Config(state_path=filepath) as cfg:
                    with open(cfg.state_path, "rb") as file:
                        return pickle.load(file)
            except FileNotFoundError:
                if handle_not_found:
                    return None
                raise

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
            children.
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
                pass
            elif isinstance(child, str):
                pass
            else:
                raise ValueError(f"child {repr(child)} of unknown type")

    @staticmethod
    def __validate_options(options):
        if options["loop"]:
            if options["shuffle"]:
                if options["count"] is not None:
                    raise ValueError(
                        "count requires loop=False or shuffle=False"
                    )
                if options["portion"] is not None:
                    raise ValueError(
                        "portion requires loop=False or shuffle=False"
                    )
            else:
                if options["recent_portion"] is not None:
                    raise ValueError("recent_portion requires shuffle=True")
        else:
            if options["recent_portion"] is not None:
                if options["shuffle"]:
                    raise ValueError("recent_portion requires loop=True")
                raise ValueError(
                    "recent_portion requires loop=True and shuffle=True"
                )

    @property
    def children(self):
        """The items iterated over by the Playlist

        Returns a list of items this Playlist iterates over, including
        sub-Playlists and paths to media files.
        """
        return list(self.__children)

    @property
    def options(self):
        """Values that modify the Playlist's iteration rules

        Returns a dictioinary of the options in use by the Playlist.
        """
        return dict(self.__options)

    @staticmethod
    def __resolve_path(path):
        root = Path(get_cfg("media_root"))
        resolved_path = (root / path).resolve()
        if resolved_path.exists():
            resolved_paths = [resolved_path]
        else:
            resolved_paths = sorted(p for p in root.glob(path))
            resolved_paths = [p for p in resolved_paths if p.is_file()]
            if not resolved_paths:
                warnings.warn(
                    f'file "{resolved_path}" not found and has no matches as '
                    "a glob pattern"
                )

        if get_cfg("media_exts"):
            supported_paths = []
            for resolved_path in resolved_paths:
                if resolved_path.suffix.lower().lstrip(".") in get_cfg(
                    "media_exts"
                ):
                    supported_paths.append(resolved_path)
                else:
                    warnings.warn(
                        f'file "{resolved_path}" has unsupported extension '
                        "and will be skipped"
                    )
        else:
            supported_paths = resolved_paths
        return [str(p) for p in supported_paths]

    def __create_sequence(self):
        processed_children = []
        for child in self.children:
            if isinstance(child, Playlist):
                # pylint: disable=protected-access
                # Reason: accessing a protected member of another
                # instance of the same class
                processed_children.append(child.__create_sequence())
            if isinstance(child, str):
                processed_children.extend(self.__resolve_path(child))

        if self.options["loop"]:
            if self.options["shuffle"]:
                return seq.ShuffledLoopingSequence(
                    *processed_children,
                    weight=self.options["weight"],
                    recent_portion=self.options["recent_portion"],
                )
            return seq.OrderedLoopingSequence(
                *processed_children,
                weight=self.options["weight"],
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
        return self.PlaylistState(iter(self.__create_sequence()))

    def paths(self):
        """List all filepaths that appear in the Playlist

        This flattens the Playlist and any descendant Playlists and
        resolves any glob patterns to get a flat list of all files
        referenced by the Playlist. There are no guarantees about the
        order or uniqueness of the listed values.
        """
        tracks = []
        for child in self.children:
            if isinstance(child, Playlist):
                tracks.extend(child.paths())
            elif isinstance(child, str):
                tracks.extend(self.__resolve_path(child))
        return tracks

    def save_xml(self, filepath=None):
        """Save the Playlist to an xml file

        The Playlist can later be recreated using Playlist.load_xml

        Arguments
        ---------
        filepath: str or None
            The desired path of the xml file. If None, uses the value of
            the "playlist_path" config.
        """
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
                warnings.warn(
                    f'could not serialize option "{key}" with value "{val}"'
                )
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
        with Config(playlist_path=filepath) as cfg:
            with open(cfg.playlist_path, "wb") as file:
                tree.write(file, pretty_print=True)

    @staticmethod
    def load_xml(filepath=None):
        """Create a Playlist instance loaded from an xml file

        The xml file should follow the format of one created by
        Playlist.save_xml.

        Arguments
        ---------
        filepath: str or None
            The path to the xml file. If None, uses the value of the
            "playlist_path" config.
        """

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
                            f'could not deserialize attribute "{key}" with '
                            f'value "{val}"'
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

        with Config(playlist_path=filepath) as cfg:
            try:
                tree = etree.parse(cfg.playlist_path)
            except OSError:
                # lxml.etree only raises a basic OSError. Try opening
                # ourselves to trigger a more detailed error.
                with open(cfg.playlist_path, "r"):
                    pass
                raise
        root = tree.getroot()
        if root.tag.lower() == "playlist":
            elem = root
        else:
            subelems = [x for x in root if x.tag.lower() == "playlist"]
            if len(subelems) != 1:
                raise ValueError("could not find element with playlist tag")
            elem = subelems[0]

        return to_node(elem)

    load_state = PlaylistState.load


def _handle_playlist_change(state):
    with Config() as cfg:
        if cfg.on_change == OnChange.IGNORE:
            state.creation_time = time.time()
        elif cfg.on_change == OnChange.RESTART:
            playlist = Playlist.load_xml()
            state = iter(playlist)
            state.save()
        elif cfg.on_change == OnChange.SEEK:
            playlist = Playlist.load_xml()
            try:
                next_track = next(state)
            except StopIteration:
                next_track = None
            state = iter(playlist)
            if next_track in playlist.paths():
                # We've confirmed the next track should appear in the
                # new playlist, but it's possible the track is very
                # unlikely or even impossible to actually be reached,
                # so there is a cap on the number of skips to avoid
                # an infinite loop.
                for _ in range(cfg.max_seek_skips):
                    if state.peek() == next_track:
                        break
                    try:
                        next(state)
                    except StopIteration:
                        state = iter(playlist)
                        break
                else:
                    warnings.warn(
                        "Gave up seeking to next track in new "
                        f"playlist after {cfg.max_seek_skips} attempts"
                    )
                    state = iter(playlist)
            else:
                warnings.warn("Next track not in new playlist. Starting over.")
        else:
            raise NotImplementedError
    return state


def ensure_state(
    *, state_path=None, playlist_path=None, new_state=None, on_change=None
):
    """Loads a Playlist.PlaylistState or creates a new one

    This function will either load an existing PlaylistState from the
    filesystem, or if it doesn't exist, load a Playlist from the
    filesystem and use it to create a new PlaylistState.

    Keyword arguments may be set to override config values of the same
    name. See the nextsong.config docs for more information.
    """
    with Config(
        state_path=state_path,
        playlist_path=playlist_path,
        new_state=new_state,
        on_change=on_change,
    ) as cfg:
        state = None

        if not cfg.new_state:
            try:
                state = Playlist.load_state()
            except FileNotFoundError:
                pass

        if state:
            playlist_mtime = -1
            try:
                playlist_mtime = os.path.getmtime(cfg.playlist_path)
            except OSError as err:
                lines = [
                    "Failed to fetch playlist modified time with error:",
                    f"\t{err}",
                    "Change detection will be skipped",
                ]
                warnings.warn("\n".join(lines))
            if state.creation_time < playlist_mtime:
                state = _handle_playlist_change(state)
                state.save()
        else:
            playlist = Playlist.load_xml()
            state = iter(playlist)
            state.save()

        return state
