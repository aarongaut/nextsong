def nextsong():
    import argparse
    from nextsong.config import get as get_cfg

    parser = argparse.ArgumentParser(prog="nextsong")
    parser.add_argument(
        "-m",
        "--media-root",
        help="The root directory for media files [%(default)s]",
        default=get_cfg("media_root"),
    )
    parser.add_argument(
        "-e",
        "--media-ext",
        action="append",
        help="Permitted extension for media files (can be repeated for multiple extensions) [%(default)s]",
        default=get_cfg("media_exts"),
    )
    parser.add_argument(
        "-p",
        "--playlist",
        help="Path to the playlist xml file [%(default)s]",
        default=get_cfg("playlist_path"),
    )
    parser.add_argument(
        "-s",
        "--state",
        help="Path to the playlist state file [%(default)s]",
        default=get_cfg("state_path"),
    )
    parser.add_argument(
        "-n",
        "--new-state",
        help="Start the playlist over, ignoring an existing state file [%(default)s]",
        default=get_cfg("new_state"),
    )
    args = parser.parse_args()

    import nextsong
    import pickle
    from pathlib import Path

    with nextsong.config.Config(
        media_root=args.media_root,
        media_exts=args.media_ext or None,
        playlist_path=args.playlist,
        state_path=args.state,
        new_state=args.new_state,
    ):
        if not get_cfg("new_state") and Path(get_cfg("state_path")).exists():
            with open(get_cfg("state_path"), "rb") as f:
                state = pickle.load(f)
        else:
            playlist = nextsong.playlist.Playlist.load_xml(get_cfg("playlist_path"))
            state = iter(playlist)
        media = next(state)
        with open(get_cfg("state_path"), "wb") as f:
            pickle.dump(state, f)
        print(media, end="")
