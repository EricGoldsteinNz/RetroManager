
def convertToHumanReadableFilesize(filesize : int) -> str:
    humanReadableFileSize = "ERROR"
    if filesize is null:
        humanReadableFileSize = ""
    elif filesize > 1024*1024: #More than 1 Megabyte
        humanReadableFileSize = f"{round(filesize/(1024*1024),2)} MB"
    elif filesize > 1024: #More than 1 Kilobyte
        humanReadableFileSize = f"{round(filesize/1024,2)} KB"
    else: #Less than 1 Kilobyte
        humanReadableFileSize = f"{filesize} Bytes"

