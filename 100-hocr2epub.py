#!/usr/bin/env python3

import glob
import os
import re
import shutil
import subprocess
import sys
import zipfile
import shlex
from datetime import datetime
from pathlib import Path

from _shared import (
    load_config,
    get_page_num,
)


src = Path("090-ocr")

# write EPUB file
# dst = Path(Path(__file__).stem + ".epub")

# write unpacked EPUB files to workdir
dst = Path(".")


config = load_config()


if dst != Path(".") and dst.exists():
    print(f"error: output exists: {dst}")
    sys.exit(1)


# downscale to 300 dpi
# 600 dpi -> 300 dpi: 90 MB -> 60 MB
scale = 300 / config.scan_resolution


hocr_to_epub_fxl = "hocr-to-epub-fxl"

# TODO dont commit
if 1:
    hocr_to_epub_fxl = "/home/user/src/archive-hocr-tools/bin/hocr-to-epub-fxl"

args = [
    hocr_to_epub_fxl,
    "--output", str(dst),
]

if dst == Path("."):
    args.append("--output-unpacked")


def git_modified():
    return subprocess.check_output(
        ["git", "show", "-s", "--format=%cI", "HEAD"],
        text=True,
    ).strip()


def stat_modified(path):
    ts = Path(path).stat().st_mtime
    dt = datetime.fromtimestamp(ts).astimezone()
    return dt.isoformat(timespec="seconds")


doc_modified = max(
    git_modified(),
    stat_modified(src),
)


args += [
    "--scale", str(scale),
    "--image-format", "avif",
    "--text-format", "html",
    # TODO? move these config items to 000-config.py
    "--doc-modified", doc_modified,
    "--doc-title", "Versteh Mich Bitte",
    "--doc-subtitle", "Charakter- und Temperament-Typen",
    # "--doc-subject", "",
    "--doc-date", "1990-07-01",
    "--doc-edition", "1", # TODO
    "--doc-extent", "276 pages", # NOTE actually 280 pages
    "--color-image-pages", "281,282",
    "--doc-author", "David Keirsey",
    "--doc-author", "Marilyn Bates",
    # "--doc-introducer", "",
    # "--doc-contributor", "",
    # "--doc-translator", "",
    "--doc-publisher", "Prometheus Books",
    "--doc-language", "de", # german
    # "--doc-language", "en", # english
    "--doc-isbn", "9780960695447",
    "--doc-cover-image", "0663-level/281.tiff",
    "--canonical-url-base", "https://milahu.github.io/david-keirsey-versteh-mich-bitte-1990/",
    "--doc-description", """
Finden Sie Ihren Stil

Beginnen Sie mit dem Ausfüllen des Fragebogens auf Seite 6.
Verschaffen Sie sich dann ein eigenes Bild (S. 221-273).
Vielleicht werden Sie auch Spaß daran haben,
mit Ihrer Frau, den Kindern oder Freunden über Ihre Unterschiede sprechen.

Die Autoren sind Ausbilder von Therapeuten und Diagnostikern für Verhaltensstörungen
an der California State University (Fullerton Campus).
Unzufrieden mit der Maturitätstheorie eines Freud, Maslow, Erickson, Sheehey, Levinson und anderer,
bestehen sie darauf, daß nicht jeder die gleichen Wachstumsphasen zur Reife durchläuft.
"Man kann eine oder zwei Identitätskrisen haben —
aber ich will keine, habe keine und kann keine haben.
Der Grund hierfür ist nicht, daß ich in meiner Entwicklung zurückgeblieben
oder in einem unreifen Stadium, einer Übergangsphase
oder einer bestimmten Zeit meines Lebens stehengeblieben bin.
Für mich ticken die Uhren anders."

Professor Keirsey ist seit langen Jahren klinischer Psychologe
und gehört der Schule der Gestaltpsychologie an.
Nachdem er 10 Jahre lang Hunderte von Problemen
in Zusammenhang mit Erziehung, Elternschaft, Ehe und Unternehmensführung behandelt hat,
fordert Dr. Keirsey jetzt den Leser zur "Abkehr vom Pygmalion-Projekt" auf,
jenem nie endenden, vergeblichen Versuch,
den Anderen in eine getreue Kopie des eigenen Ichs umzuformen.
"Es ist ganz richtig," meint er, "einen völlig gegensätzlichen Partner zu heiraten
und Kinder zu zeugen, die aus ganz anderem Holz geschnitzt sind:
dagegen ist es keinesfalls richtig,
Ehe und Elternschaft als Freibrief aufzufassen,
der es gestattet, den Ehepartner und die Kinder nach dem Muster des eigenen Ichs zu modellieren.
Legen Sie Ihren Meissel hin! Lassen Sie es gut sein: Freuen Sie sich darüber!"
""",
]


print(">", shlex.join(args + sys.argv[1:]) + f" {src}/*.hocr")


hocr_files = list(src.glob("*.hocr"))

hocr_files.sort()

subprocess.run(
    args + sys.argv[1:] + hocr_files,
    check=True,
)


if dst == Path("."):
    print("done ./index.xhtml")
    sys.exit(0)


print(f"done {dst}")


# extract the EPUB content files

# rm -rf $dst.unzip
unzip_dir = Path(str(dst) + ".unzip")
shutil.rmtree(unzip_dir, ignore_errors=True)
unzip_dir.mkdir()


# unzip -q ../$dst
with zipfile.ZipFile(dst) as z:
    z.extractall(unzip_dir)


print(f"done {unzip_dir}/index.html")
