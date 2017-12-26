import cv2

from duckietown_segmaps.draw_map_on_images import plot_map
from duckietown_segmaps.maps import FRAME_AXLE
from duckietown_segmaps.transformations import TransformationsInfo
import duckietown_utils as dtu
from ground_projection.ground_projection_geometry import GroundProjectionGeometry

import numpy as np
from duckietown_utils.jpg import write_bgr_to_file_as_jpg

__all__ = [
    'simulate_image',
]

@dtu.contract(gpg=GroundProjectionGeometry, pose='SE2')
def simulate_image(sm_orig, pose, gpg, blur_sigma):
    camera_info = gpg.get_camera_info() 
    blank = generate_blank(camera_info)
    tinfo = TransformationsInfo()

    frames = list(set(_.id_frame for _ in sm_orig.points.values()))    
    id_frame = frames[0]
    dtu.logger.debug('frames: %s choose %s' % (frames, id_frame))

    tinfo.add_transformation(frame1=id_frame, frame2=FRAME_AXLE, g=pose) 
        
    sm_axle = tinfo.transform_map_to_frame(sm_orig, FRAME_AXLE)
    
    rectified_synthetic = plot_map(blank, sm_axle, gpg, do_segments=False)
    
    dtu.write_bgr_to_file_as_jpg(rectified_synthetic, 'rectified_synthetic.jpg')
    
    distorted_synthetic = gpg.distort(rectified_synthetic)
    
    distorted_synthetic = add_noise(distorted_synthetic)
#     distorted_synthetic = cv2.medianBlur(distorted_synthetic, 3)
    distorted_synthetic = cv2.GaussianBlur(distorted_synthetic, (0,0), blur_sigma)
    return distorted_synthetic
    
def add_noise(image, intensity = 20, noise_blur = 1):
    noise = np.random.randn(image.shape[0], image.shape[1], 3) * intensity
    noise = cv2.GaussianBlur(noise, (0,0), noise_blur)
    image = image*1.0 + noise
    image = image.clip(0, 255).astype('uint8')
    return image


def generate_blank(camera_info):
    H = camera_info.height
    W = camera_info.width
    bgr = np.zeros(dtype='uint8', shape=(H, W, 3))
    bgr.fill(128)
    return bgr
    