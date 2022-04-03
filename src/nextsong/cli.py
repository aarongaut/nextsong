def nextsong():
    import argparse
    from nextsong.config import get as get_cfg
    import nextsong

    parser = argparse.ArgumentParser(prog="nextsong")
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s {nextsong.__version__}",
    )
    parser.add_argument(
        "-m",
        "--media-root",
        help="root directory for media files [%(default)s]",
        default=get_cfg("media_root"),
    )
    parser.add_argument(
        "-e",
        "--media-ext",
        action="append",
        help="permit file extension, repeatable [%(default)s]",
        default=get_cfg("media_exts"),
    )
    parser.add_argument(
        "-p",
        "--playlist",
        help="xml playlist filepath [%(default)s]",
        default=get_cfg("playlist_path"),
    )
    parser.add_argument(
        "-s",
        "--state",
        help="playlist state filepath [%(default)s]",
        default=get_cfg("state_path"),
    )
    parser.add_argument(
        "-n",
        "--new-state",
        action="store_true",
        help="start playlist over, ignoring existing state file [%(default)s]",
        default=get_cfg("new_state"),
    )
    args = parser.parse_args()

    import pickle
    from pathlib import Path

    with nextsong.config.Config(
        media_root=args.media_root,
        media_exts=args.media_ext or None,
        playlist_path=args.playlist,
        state_path=args.state,
        new_state=args.new_state,
    ):
        state = None
        if not get_cfg("new_state"):
            try:
                with open(get_cfg("state_path"), "rb") as f:
                    state = pickle.load(f)
            except FileNotFoundError:
                pass
        if state is None:
            playlist = nextsong.playlist.Playlist.load_xml()
            state = iter(playlist)

        try:
            media = next(state)
        except StopIteration:
            media = None
        with open(get_cfg("state_path"), "wb") as f:
            pickle.dump(state, f)

        if media is None:
            print()
        else:
            print(media)
