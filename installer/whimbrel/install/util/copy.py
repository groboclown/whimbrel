
import os
import shutil
from zipfile import ZipFile, ZIP_DEFLATED


def discover_files(src_dir, archive_path, file_found_callback):
    """
    Finds all the files in the source directory, and how they map
    into the archive path (a relative directory).

    :param src_dir:
    :param archive_path:
    :param file_found_callback: takes the arguments

        (source_path=source full path, dest_path=destination file name, filename=file name,
        name=name without extension, ext=extension)

        and returns True if the file should be ignored, or
        False if it should be included.  This is only for discovered
        files, not directories.
    :return: nothing
    """
    copy_dirs = [[src_dir, archive_path]]
    while len(copy_dirs) > 0:
        next_src_dir, next_archive_path = copy_dirs.pop()
        for name in os.listdir(next_src_dir):
            name_split = os.path.extsep(name)
            src_filename = os.path.join(next_src_dir, name)
            dest_filename = os.path.join(next_archive_path, name)
            if os.path.isdir(src_filename):
                copy_dirs.append([src_filename, dest_filename])
            else:
                file_found_callback(
                        source_path=src_filename,
                        dest_path=dest_filename,
                        filename=name,
                        name=name_split[0],
                        ext=name_split[1])


def file_copy_and_zip(src_filename, archive_file_path, dest_basedir, zip_file):
    assert isinstance(src_filename, str)
    assert isinstance(zip_file, ZipFile)

    out_file = os.path.join(dest_basedir, archive_file_path)
    if not os.path.isdir(os.path.dirname(out_file)):
        os.makedirs(os.path.dirname(out_file))

    zip_file.write(src_filename, arcname=archive_file_path)
    shutil.copyfile(src_filename, out_file)


def zip_dir(zip_filename, src_dir, make_dir_root=False):
    def add_to_zip(zf, path, zippath):
        assert isinstance(zf, ZipFile)
        if os.path.isfile(path):
            zf.write(path, zippath, ZIP_DEFLATED)
        elif os.path.isdir(path):
            for nm in os.listdir(path):
                add_to_zip(zf, os.path.join(path, nm), os.path.join(zippath, nm))
        # else: ignore

    with ZipFile(zip_filename, 'w') as zf:
        if make_dir_root or not os.path.isdir(src_dir):
            add_to_zip(zf, src_dir, os.path.basename(src_dir))
        else:
            for nm in os.listdir(src_dir):
                add_to_zip(zf, os.path.join(src_dir, nm), nm)


def data_copy_and_zip(src_data, archive_file_path,  dest_basedir, zip_file):
    assert isinstance(zip_file, ZipFile)

    out_file = os.path.join(dest_basedir, archive_file_path)
    if not os.path.isdir(os.path.dirname(out_file)):
        os.makedirs(os.path.dirname(out_file))

    zip_file.writestr(archive_file_path, src_data)
    with open(out_file, "wb") as f:
        if isinstance(src_data, str):
            src_data = src_data.encode("utf-8")
        f.write(src_data)


def replace_tokens(token_dict, src):
    assert isinstance(token_dict, dict)
    assert isinstance(src, str)

    with open(src, 'r') as f:
        ret = f.read()
        for k, v in token_dict.items():
            ret = ret.replace('@{0}@'.format(k), v)
        return ret
