import nextsong
from nextsong.config import get as get_config
import warnings
from pathlib import Path


class Playlist:
    class PlaylistState:
        def __init__(self, iterator):
            self.__iterator = iterator

        def __next__(self):
            return next(self.__iterator)

    def __init__(
        self,
        *children,
        shuffle=None,
        portion=None,
        count=None,
        recent_portion=None,
        weight=None,
        loop=None,
    ):

        for child in children:
            if isinstance(child, Playlist):
                if child.__options["loop"]:
                    raise ValueError(
                        "loop=True is only allowed for the top-level Playlist"
                    )
            elif isinstance(child, str):
                pass
            else:
                raise ValueError(f"child {repr(child)} of unknown type")

        self.__children = children

        if loop:
            if weight is not None:
                raise ValueError("weight requires loop=False")
            if shuffle:
                if count is not None:
                    raise ValueError("count requires loop=False or shuffle=False")
                if portion is not None:
                    raise ValueError("portion requires loop=False or shuffle=False")
            else:
                if recent_portion is not None:
                    raise ValueError("recent_portion requires shuffle=True")
        else:
            if recent_portion is not None:
                if shuffle:
                    raise ValueError("recent_portion requires loop=True")
                else:
                    raise ValueError(
                        "recent_portion requires loop=True and shuffle=True"
                    )

        self.__options = {
            "shuffle": shuffle,
            "portion": portion,
            "count": count,
            "recent_portion": recent_portion,
            "weight": weight,
            "loop": loop,
        }

    def __create_sequence(self):
        processed_children = []
        for child in self.__children:
            if isinstance(child, Playlist):
                processed_children.append(child.__create_sequence())
            if isinstance(child, str):
                root = Path(get_config("media_root"))
                resolved_path = (root / child).resolve()
                if resolved_path.exists():
                    paths = [resolved_path]
                else:
                    paths = sorted(p.resolve() for p in root.glob(child))
                    paths = [p for p in paths if p.exists()]
                    if not paths:
                        warnings.warn(
                            f'file "{resolved_path}" not found and has no matches as a glob pattern'
                        )

                if get_config("media_exts"):
                    supported_paths = []
                    for path in paths:
                        if path.suffix.lower().lstrip(".") in get_config("media_exts"):
                            supported_paths.append(path)
                        else:
                            warnings.warn(
                                f'file "{path}" has unsupported extension and will be skipped'
                            )
                else:
                    supported_paths = paths

                processed_children.extend(str(p) for p in supported_paths)

        if self.__options["loop"]:
            if self.__options["shuffle"]:
                return nextsong.sequence.ShuffledLoopingSequence(
                    *processed_children, recent_portion=self.__options["recent_portion"]
                )
            else:
                return nextsong.sequence.OrderedLoopingSequence(
                    *processed_children,
                    portion=self.__options["portion"],
                    count=self.__options["count"],
                )
        else:
            return nextsong.sequence.FiniteSequence(
                *processed_children,
                weight=self.__options["weight"],
                portion=self.__options["portion"],
                count=self.__options["count"],
                shuffle=self.__options["shuffle"],
            )

    def __iter__(self):
        return self.PlaylistState(iter(self.__create_sequence()))

    def save_xml(self, filepath=None):
        from lxml import etree

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
                    if val == True:
                        attributes[key] = "true"
                        continue
                    if val == False:
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
            elem = etree.Element("playlist", **to_attributes(node.__options))
            for child in node.__children:
                subelem = to_elem(child)
                elem.append(subelem)
            return elem

        elem = to_elem(self)
        root.append(elem)

        tree = etree.ElementTree(root)
        tree.write(filepath, pretty_print=True)

    @staticmethod
    def load_xml(filepath=None):
        from lxml import etree

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
            elif elem.tag.lower() == "playlist":
                children = [to_node(x) for x in elem]
                children = [x for x in children if x is not None]
                options = to_options(elem.attrib)
                return Playlist(*children, **options)
            else:
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
