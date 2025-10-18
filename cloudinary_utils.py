"""
Cloudinary utility functions for file uploads
Handles video, image, and document uploads to Cloudinary
"""
import os
import cloudinary
import cloudinary.uploader
import cloudinary.api
from werkzeug.utils import secure_filename
from flask import current_app


def init_cloudinary():
    """Initialize Cloudinary with credentials from config"""
    if current_app.config.get('USE_CLOUDINARY'):
        cloudinary.config(
            cloud_name=current_app.config['CLOUDINARY_CLOUD_NAME'],
            api_key=current_app.config['CLOUDINARY_API_KEY'],
            api_secret=current_app.config['CLOUDINARY_API_SECRET'],
            secure=True
        )
        return True
    return False


def upload_video(file, course_id=None, lesson_id=None):
    """
    Upload video to Cloudinary with optimizations

    Args:
        file: FileStorage object from Flask request
        course_id: Optional course ID for folder organization
        lesson_id: Optional lesson ID for naming

    Returns:
        dict: Upload result with url, secure_url, public_id, etc.
    """
    if not current_app.config.get('USE_CLOUDINARY'):
        return None

    try:
        # Create folder path
        folder = f"shikkhadwar/courses/{course_id}/videos" if course_id else "shikkhadwar/videos"

        # Generate unique filename
        filename = secure_filename(file.filename)
        base_name = os.path.splitext(filename)[0]
        if lesson_id:
            public_id = f"{folder}/lesson_{lesson_id}_{base_name}"
        else:
            public_id = f"{folder}/{base_name}"

        # Upload with video optimizations
        result = cloudinary.uploader.upload(
            file,
            resource_type="video",
            public_id=public_id,
            overwrite=True,
            folder=folder,
            # Video optimizations
            quality="auto:good",  # Automatic quality optimization
            fetch_format="auto",  # Best format based on browser
            # Transformations for efficient streaming
            eager=[
                {"streaming_profile": "hd", "format": "m3u8"},  # HLS streaming
                {"width": 1280, "height": 720, "crop": "limit", "quality": "auto"}  # HD preview
            ],
            eager_async=True,  # Process transformations in background
            # Metadata
            context=f"course_id={course_id}|lesson_id={lesson_id}" if course_id else None,
            tags=["course_video", f"course_{course_id}"] if course_id else ["video"]
        )

        return result
    except Exception as e:
        print(f"Cloudinary video upload error: {e}")
        return None


def upload_image(file, folder="images", public_id=None):
    """
    Upload image to Cloudinary with optimizations

    Args:
        file: FileStorage object from Flask request
        folder: Folder path in Cloudinary
        public_id: Optional custom public_id

    Returns:
        dict: Upload result with url, secure_url, public_id, etc.
    """
    if not current_app.config.get('USE_CLOUDINARY'):
        return None

    try:
        folder_path = f"shikkhadwar/{folder}"

        # Generate public_id if not provided
        if not public_id:
            filename = secure_filename(file.filename)
            base_name = os.path.splitext(filename)[0]
            public_id = f"{folder_path}/{base_name}"
        else:
            public_id = f"{folder_path}/{public_id}"

        # Upload with image optimizations
        result = cloudinary.uploader.upload(
            file,
            resource_type="image",
            public_id=public_id,
            overwrite=True,
            # Image optimizations
            quality="auto:good",
            fetch_format="auto",  # WebP for modern browsers, fallback for others
            # Generate responsive versions
            eager=[
                {"width": 300, "height": 300, "crop": "fill", "quality": "auto"},  # Thumbnail
                {"width": 800, "crop": "limit", "quality": "auto"},  # Medium
                {"width": 1200, "crop": "limit", "quality": "auto"}  # Large
            ],
            eager_async=True,
            tags=["image", folder]
        )

        return result
    except Exception as e:
        print(f"Cloudinary image upload error: {e}")
        return None


def upload_document(file, course_id=None, resource_type="raw"):
    """
    Upload document/resource to Cloudinary

    Args:
        file: FileStorage object from Flask request
        course_id: Optional course ID for folder organization
        resource_type: Type of resource (default: "raw" for PDFs, docs, etc.)

    Returns:
        dict: Upload result with url, secure_url, public_id, etc.
    """
    if not current_app.config.get('USE_CLOUDINARY'):
        return None

    try:
        # Create folder path
        folder = f"shikkhadwar/courses/{course_id}/resources" if course_id else "shikkhadwar/resources"

        # Generate unique filename
        filename = secure_filename(file.filename)
        base_name = os.path.splitext(filename)[0]
        public_id = f"{folder}/{base_name}"

        # Upload document
        result = cloudinary.uploader.upload(
            file,
            resource_type=resource_type,
            public_id=public_id,
            overwrite=True,
            # Metadata
            context=f"course_id={course_id}" if course_id else None,
            tags=["resource", f"course_{course_id}"] if course_id else ["resource"]
        )

        return result
    except Exception as e:
        print(f"Cloudinary document upload error: {e}")
        return None


def delete_file(public_id, resource_type="image"):
    """
    Delete file from Cloudinary

    Args:
        public_id: The public_id of the file to delete
        resource_type: Type of resource (image, video, raw)

    Returns:
        dict: Deletion result
    """
    if not current_app.config.get('USE_CLOUDINARY'):
        return None

    try:
        result = cloudinary.uploader.destroy(public_id, resource_type=resource_type)
        return result
    except Exception as e:
        print(f"Cloudinary delete error: {e}")
        return None


def get_video_url(public_id, transformations=None):
    """
    Get optimized video URL with optional transformations

    Args:
        public_id: The public_id of the video
        transformations: Optional dict of transformations

    Returns:
        str: Cloudinary video URL
    """
    if not current_app.config.get('USE_CLOUDINARY'):
        return None

    try:
        if transformations:
            return cloudinary.CloudinaryVideo(public_id).build_url(**transformations)
        else:
            # Default: HD quality, auto format
            return cloudinary.CloudinaryVideo(public_id).build_url(
                quality="auto:good",
                fetch_format="auto"
            )
    except Exception as e:
        print(f"Cloudinary video URL error: {e}")
        return None


def get_image_url(public_id, transformations=None):
    """
    Get optimized image URL with optional transformations

    Args:
        public_id: The public_id of the image
        transformations: Optional dict of transformations

    Returns:
        str: Cloudinary image URL
    """
    if not current_app.config.get('USE_CLOUDINARY'):
        return None

    try:
        if transformations:
            return cloudinary.CloudinaryImage(public_id).build_url(**transformations)
        else:
            # Default: auto quality and format
            return cloudinary.CloudinaryImage(public_id).build_url(
                quality="auto:good",
                fetch_format="auto"
            )
    except Exception as e:
        print(f"Cloudinary image URL error: {e}")
        return None


def is_cloudinary_url(url):
    """Check if a URL is from Cloudinary"""
    if not url:
        return False
    return 'cloudinary.com' in url or 'res.cloudinary.com' in url
