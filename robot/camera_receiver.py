class CameraStreamSettings:
    some_available_window_sizes = [ (640,480), (320,240), (256,144), (480,270), (640,360) ] # not necessairly comprehensive
    available_formats = [ "YUV420", "RGB565", "RGB32", "Z16 (GS)" ]
    def __init__(self, *, width, height, format):
        assert format in self.available_formats, f"in CameraStreamSettings(format=thing) thing needs to be one of {self.available_formats}"
        self.width = int(width)
        self.height = int(height)
        if format == "YUV420":
            self.bytes_per_pixel = 12/8
            self.enum_number = 0
        elif format == "RGB565":
            self.bytes_per_pixel = 2
            self.enum_number = 1
        elif format == "RGB32":
            self.bytes_per_pixel = 4
            self.enum_number = 2
        elif format == "Z16 (GS)":
            self.bytes_per_pixel = 2
            self.enum_number = 3
        
        self.bytes_per_frame = int(width*height*self.bytes_per_pixel)


def frame_generator(*, path_to_capturer_mmap_executable, camera_stream_settings, file_path_of_camera="/dev/video0",):
    """
        Example:
            import numpy
            camera_stream_settings = CameraStreamSettings(
                height=270,
                width=480,
                format="RGB565" # "YUV420", "RGB565", "RGB32", or "Z16 (GS)" <- last one is used for depth cameras
            )
            for frame_as_bytes in frame_generator(
                path_to_capturer_mmap_executable="./capturer_mmap"
                file_path_of_camera="/dev/video0",
                camera_stream_settings=camera_stream_settings,
            ):
                uint8_array = numpy.frombuffer(frame_as_bytes, dtype=numpy.uint8)
                frame = uint8_array.reshape((camera_stream_settings.width, camera_stream_settings.height, -1))
    """
    import subprocess
    import os
    if not os.path.isfile(file_path_of_camera):
        raise Exception(f'''Are you sure the camera is plugged in? {repr(file_path_of_camera)} isn't a file''')
    
    args = [
        path_to_capturer_mmap_executable,
        "-D", file_path_of_camera,
        "--pixel-format", f"{camera_stream_settings.enum_number}",
        "-w", f"{camera_stream_settings.width}*{camera_stream_settings.height}",
    ]
    process = subprocess.Popen(args, bufsize=-1, stdout=subprocess.PIPE)
    def inner_generator():
        if process.returncode != None:
            raise Exception(f'''Camera stream stopped with exit code of: {process.returncode}''')
        yield process.stdout.read(camera_stream_settings.bytes_per_frame)
    
    generator = inner_generator()
    generator.kill = lambda *args, **kwargs: process.kill(*args, **kwargs)
    return generator


import numpy
# use the following command to find your camera's settings: v4l2-ctl -d /dev/video0 --list-formats-ext
camera_stream_settings = CameraStreamSettings(
    height=270,
    width=480,
    format="RGB565" # "YUV420", "RGB565", "RGB32", or "Z16 (GS)" <- last one is used for depth cameras
)
for frame_as_bytes in frame_generator(
    path_to_capturer_mmap_executable="./capturer_mmap",
    file_path_of_camera="/dev/video0",
    camera_stream_settings=camera_stream_settings,
):
    uint8_array = numpy.frombuffer(frame_as_bytes, dtype=numpy.uint8)
    frame = uint8_array.reshape((camera_stream_settings.width, camera_stream_settings.height, -1))
    
