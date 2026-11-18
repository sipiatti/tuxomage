#!/usr/bin/python3
"""Launcher installed as /usr/bin/tuxomage by the Debian package."""
import sys

sys.path.insert(0, "/usr/share/tuxomage")

from tuxomage.app import main  # noqa: E402

sys.exit(main())
