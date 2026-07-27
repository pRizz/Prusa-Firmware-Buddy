#include <errno.h>
#include <ff.h>
#include <buddy/ffconf.h>
#include <limits.h>
#include <string.h>
#include <sys/iosupport.h>
#include <sys/stat.h>
#include <sys/syslimits.h>

#include <buddy/filesystem.h>

#define FAT_MAX_FILES 268435437
#define IS_EMPTY(s)   (!s || !s[0])

#define FF_YEAR         0b1111111000000000
#define FF_MONTH        0b0000000111100000
#define FF_DAY          0b0000000000011111
#define FF_YEAR_OFFSET  9
#define FF_MONTH_OFFSET 5
#define FF_DAY_OFFSET   0

#define FF_HOUR          0b1111100000000000
#define FF_MINUTE        0b0000011111100000
#define FF_SECOND        0b0000000000011111
#define FF_HOUR_OFFSET   11
#define FF_MINUTE_OFFSET 5
#define FF_SECOND_OFFSET 0

#define FF_VALUE(value, type) ((value & type) >> type##_OFFSET)

namespace fatfs {

int get_errno(FRESULT result);
int stat_r(struct _reent *r, const char *path, struct stat *st);
int chmod_r(struct _reent *r, const char *path, mode_t mode);
int device_index();

time_t get_posix_time(DWORD fdate, DWORD ftime) {
    struct tm tm;
    memset(&tm, 0, sizeof(struct tm));

    tm.tm_year = FF_VALUE(fdate, FF_YEAR) + 80; // FAT year origin from 1980, tm_year origin from 1900
    tm.tm_mon = FF_VALUE(fdate, FF_MONTH) - 1; // FAT count months from 1, tm from 0 :-O
    tm.tm_mday = FF_VALUE(fdate, FF_DAY);
    tm.tm_hour = FF_VALUE(ftime, FF_HOUR);
    tm.tm_min = FF_VALUE(ftime, FF_MINUTE);
    tm.tm_sec = FF_VALUE(ftime, FF_SECOND);

    return mktime(&tm);
}

int chdir_r(struct _reent *r, const char *path) {
    if (IS_EMPTY(path)) {
        r->_errno = EINVAL;
        return -1;
    }

    path = process_path(path, "usb");

    const FRESULT result = f_chdir(path);
    r->_errno = get_errno(result);

    return result == FR_OK ? 0 : -1;
}

int link_r(struct _reent *r, __attribute__((unused)) const char *existing, __attribute__((unused)) const char *new_link) {
    // Links are not supported on FAT.
    r->_errno = ENOTSUP;
    return -1;
}

int unlink_r(struct _reent *r, const char *path) {
    if (IS_EMPTY(path)) {
        r->_errno = EINVAL;
        return -1;
    }

    path = process_path(path, "usb");

    const FRESULT result = f_unlink(path);
    r->_errno = get_errno(result);

    return result == FR_OK ? 0 : -1;
}

int rename_r(struct _reent *r, const char *old_name, const char *new_name) {
    if (IS_EMPTY(old_name) || IS_EMPTY(new_name)) {
        r->_errno = EINVAL;
        return -1;
    }

    old_name = process_path(old_name, "usb");
    new_name = process_path(new_name, "usb");

    const FRESULT result = f_rename(old_name, new_name);
    r->_errno = get_errno(result);

    return result == FR_OK ? 0 : -1;
}

int mkdir_r(struct _reent *r, const char *path, int mode) {
    if (IS_EMPTY(path)) {
        r->_errno = EINVAL;
        return -1;
    }

    path = process_path(path, "usb");

    const FRESULT result = f_mkdir(path);
    const int result_errno = get_errno(result);
    r->_errno = result_errno;

    if (result != FR_OK) {
        return -1;
    }

    if (!(mode & IS_IWALL)) {
        // Write not enabled, make new dir readonly.
        chmod_r(r, path, 0);
    }

    // Preserve mkdir's errno even when optional chmod support is unavailable.
    r->_errno = result_errno;
    return 0;
}

DIR_ITER *diropen_r(struct _reent *r, DIR_ITER *dir_state, const char *path) {
    if (IS_EMPTY(path)) {
        r->_errno = EINVAL;
        return nullptr;
    }

    path = process_path(path, "usb");

    const FRESULT result = f_opendir(static_cast<DIR *>(dir_state->dirStruct), path);
    r->_errno = get_errno(result);

    return result == FR_OK ? dir_state : nullptr;
}

int dirreset_r(struct _reent *r, DIR_ITER *dir_state) {
    const FRESULT result = f_rewinddir(static_cast<DIR *>(dir_state->dirStruct));
    r->_errno = get_errno(result);

    return result == FR_OK ? 0 : -1;
}

int dirnext_r(struct _reent *r, DIR_ITER *dir_state, char *filename, struct stat *file_stat) {
    if (filename == nullptr || file_stat == nullptr) {
        r->_errno = EINVAL;
        return -1;
    }

    FILINFO file_info;
    FRESULT result;
    do {
        result = f_readdir(static_cast<DIR *>(dir_state->dirStruct), &file_info);
        r->_errno = get_errno(result);

        if (result != FR_OK) {
            return -1;
        }
        if (file_info.fname[0] == 0) {
            break;
        }
    } while (file_info.fattrib & (AM_SYS | AM_HID));

    if (!file_info.fname[0]) {
        r->_errno = ENOENT;
        return -1;
    }

    if (file_info.altname[0] != 0) {
        strlcpy(filename, file_info.altname, NAME_MAX);
        const uint8_t len = strnlen(filename, NAME_MAX);
        // filename is NAME_MAX bytes, so the short and long names fit.
        strlcpy(filename + len + 1, file_info.fname, NAME_MAX - len - 1);
    } else {
        strlcpy(filename, file_info.fname, NAME_MAX);
        const uint8_t len = strnlen(filename, NAME_MAX);
        filename[len + 1] = 0;
    }

    file_stat->st_mode = file_info.fattrib & AM_DIR ? S_IFDIR : S_IFREG;
    file_stat->st_mtime = get_posix_time(file_info.fdate, file_info.ftime);

    return 0;
}

int dirclose_r(struct _reent *r, DIR_ITER *dir_state) {
    const FRESULT result = f_closedir(static_cast<DIR *>(dir_state->dirStruct));
    r->_errno = get_errno(result);

    return 0;
}

int statvfs_r(struct _reent *r, const char *path, struct statvfs *buf) {
    if (IS_EMPTY(path)) {
        r->_errno = EINVAL;
        return -1;
    }

    path = process_path(path, "usb");

    FATFS *filesystem;
    DWORD free_clusters;
    const FRESULT result = f_getfree(path, &free_clusters, &filesystem);
    if (result != FR_OK) {
        r->_errno = get_errno(result);
        return -1;
    }

    memset(buf, 0, sizeof(struct statvfs));

    buf->f_frsize = filesystem->csize;
#if FF_MAX_SS != FF_MIN_SS
    buf->f_bsize = filesystem->ssize;
#else
    buf->f_bsize = FF_MAX_SS;
#endif
    buf->f_bfree = free_clusters;
    buf->f_bavail = buf->f_bfree;
    buf->f_files = 0; // TODO: Count all inodes
    buf->f_ffree = FAT_MAX_FILES - buf->f_files;
    buf->f_favail = buf->f_ffree;
    buf->f_fsid = (device_index() & 0xFFFF) | (static_cast<uint32_t>(filesystem->pdrv) << 16);
    buf->f_flag = ST_NOSUID;
#ifdef _USE_LFN
    buf->f_namemax = _MAX_LFN;
#else
    buf->f_namemax = 12;
#endif

    return 0;
}

int rmdir_r(struct _reent *r, const char *path) {
    return unlink_r(r, path);
}

int lstat_r(struct _reent *r, const char *file, struct stat *st) {
    // FAT doesn't support links, so lstat is identical to stat.
    return stat_r(r, file, st);
}

} // namespace fatfs
