from ctypes import windll, create_unicode_buffer
from json import dumps
import os
import string
import tempfile
import zipfile

from bottle import get, request, response, run


PREPARED_ZIPS = {}


def get_drives():
    drives = []
    bitmask = windll.kernel32.GetLogicalDrives()
    for letter in map(lambda l: "{}:".format(l), string.ascii_uppercase):
        if bitmask & 1:
            drives.append({"name": letter, "type": "disk"})
        bitmask >>= 1

    return drives


def walk_dir(dir_path):
    return [os.path.join(dp, f) for dp, _, fn in os.walk(dir_path) for f in fn]


@get("/")
def root():
    response.status = 200
    response.headers["Content-Type"] = "application/json"
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return dumps(get_drives())


@get("/<drive:re:[A-Z]:>")
def nav_drive(drive):
    full_path = os.path.join(drive, os.sep)

    if not os.access(full_path, os.R_OK):
        response.status = 500
        response.headers["Content-Type"] = "application/json"
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        yield dumps({"status": "inaccessible"})

    elif getattr(request.query, "zip", "false") == "true":
        response.status = 200
        response.headers["Content-Type"] = "application/json"
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"

        if full_path in PREPARED_ZIPS:
            yield dumps({"location": PREPARED_ZIPS[full_path]})

        else:
            zip_fd, short_zip_abspath = tempfile.mkstemp(".zip")
            os.close(zip_fd)

            buffer = create_unicode_buffer(
                windll.kernel32.GetLongPathNameW(short_zip_abspath, 0, 0))
            windll.kernel32.GetLongPathNameW(
                short_zip_abspath, buffer, len(buffer))
            zip_abspath = buffer.value

            PREPARED_ZIPS[full_path] = zip_abspath
            yield dumps({"location": zip_abspath})

            with zipfile.ZipFile(zip_abspath, "w", zipfile.ZIP_DEFLATED) as zip:
                for file in walk_dir(full_path):
                    zip.write(file)

    else:
        dir_list = []
        file_list = []

        for entry in sorted(os.listdir(full_path)):
            try:
                stat_info = os.stat(os.path.join(full_path, entry))

            except OSError:
                continue

            obj = {
                "name": entry,
                "modified": stat_info.st_mtime * 1000
            }

            if os.path.isfile(os.path.join(full_path, entry)):
                obj["type"] = "file"
                obj["size"] = stat_info.st_size
                file_list.append(obj)

            else:
                obj["type"] = "directory"
                dir_list.append(obj)

        response.status = 200
        response.headers["Content-Type"] = "application/json"
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        yield dumps(dir_list + file_list)


@get("/<drive:re:[A-Z]:>/<path:path>")
def nav_path(drive, path):
    full_path = os.path.join(drive, os.sep, path.replace("/", os.sep))

    if not os.path.exists(full_path):
        response.status = 404
        response.headers["Content-Type"] = "application/json"
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        yield dumps({"status": "not_exists"})

    elif os.path.isfile(full_path):
        response.status = 200
        response.headers["Content-Type"] = "binary/octet-stream"
        response.headers["Content-Disposition"] = "attachment; filename={}".format(
            os.path.basename(full_path))
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"

        with open(full_path, "rb") as fd:
            while True:
                chunk = fd.read(1024)
                if not chunk:
                    break

                yield chunk

        for archived_path, zip_path in list(PREPARED_ZIPS.items()):
            if zip_path == full_path:
                os.unlink(zip_path)
                del PREPARED_ZIPS[archived_path]

    else:
        if getattr(request.query, "zip", "false") == "true":
            response.status = 200
            response.headers["Content-Type"] = "application/json"
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"

            if full_path in PREPARED_ZIPS:
                yield dumps({"location": PREPARED_ZIPS[full_path]})

            else:
                zip_fd, short_zip_abspath = tempfile.mkstemp(".zip")
                os.close(zip_fd)

                buffer = create_unicode_buffer(
                    windll.kernel32.GetLongPathNameW(short_zip_abspath, 0, 0))
                windll.kernel32.GetLongPathNameW(
                    short_zip_abspath, buffer, len(buffer))
                zip_abspath = buffer.value

                PREPARED_ZIPS[full_path] = zip_abspath
                yield dumps({"location": zip_abspath})

                with zipfile.ZipFile(zip_abspath, "w", zipfile.ZIP_DEFLATED) as zip:
                    for file in walk_dir(full_path):
                        zip.write(file)

        else:
            dir_list = []
            file_list = []

            for entry in sorted(os.listdir(full_path)):
                try:
                    stat_info = os.stat(os.path.join(full_path, entry))

                except OSError:
                    continue

                obj = {
                    "name": entry,
                    "modified": stat_info.st_mtime * 1000
                }

                if os.path.isfile(os.path.join(full_path, entry)):
                    obj["type"] = "file"
                    obj["size"] = stat_info.st_size
                    file_list.append(obj)

                else:
                    obj["type"] = "directory"
                    dir_list.append(obj)

            response.status = 200
            response.headers["Content-Type"] = "application/json"
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
            yield dumps(dir_list + file_list)


run(host="0.0.0.0", port=38080, quiet=True, debug=False)
