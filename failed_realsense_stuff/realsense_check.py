import pyrealsense2 as rs

stream_width = 848
stream_height = 480
stream_framerate = 60

pipeline = rs.pipeline()                                                               # declares and initializes the pipeline variable
# if config.realsense_settings:
# device = find_device_that_supports_advanced_mode() # pipeline.get_active_profile().get_device()
# rs.rs400_advanced_mode(device).load_json(json.dumps(config.realsense_settings))
conf = rs.config()
conf.enable_stream(rs.stream.depth, stream_width, stream_height, rs.format.z16, stream_framerate)  # this starts the depth stream and sets the size and format
conf.enable_stream(rs.stream.color, stream_width, stream_height, rs.format.bgr8, stream_framerate) # this starts the color stream and set the size and format
conf.enable_stream(rs.stream.accel)
conf.enable_stream(rs.stream.gyro)
cfg = pipeline.start(conf)
profile = cfg.get_stream(rs.stream.depth)
intr = profile.as_video_stream_profile().get_intrinsics()

frame = runtime.realsense.frame = pipeline.wait_for_frames()
runtime.realsense.acceleration = frame[2].as_motion_frame().get_motion_data()
runtime.realsense.gyro         = frame[3].as_motion_frame().get_motion_data()
yield frame_number, array(frame.get_color_frame().get_data()), array(frame.get_depth_frame().get_data())