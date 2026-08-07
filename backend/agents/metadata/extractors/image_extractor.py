# -*- coding: utf-8 -*-
"""Image metadata extractor."""

from datetime import datetime, timezone
import struct
from typing import Any, Dict, Optional, Tuple
from PIL import Image
import piexif
from backend.agents.metadata.exceptions import ParserFailureError
from backend.agents.metadata.schema import (
    ImageMetadata,
    GPSMetadata,
    CameraMetadata,
    ExtractionConfidence,
)

class ImageExtractor:
    """Extracts width, height, color space, and detailed EXIF structures from images."""
    
    @staticmethod
    def _parse_rational(val: Any) -> float:
        """Helper to parse EXIF rational values (num, den)."""
        if isinstance(val, (tuple, list)) and len(val) == 2:
            num, den = val
            return float(num) / float(den) if den != 0 else 0.0
        try:
            return float(val)
        except (ValueError, TypeError):
            return 0.0

    @classmethod
    def _convert_gps(cls, ref: str, raw_coords: Any) -> Optional[float]:
        """Converts raw GPS coordinates (D, M, S rationals) to decimal degrees."""
        if not raw_coords or not isinstance(raw_coords, (tuple, list)) or len(raw_coords) < 3:
            return None
            
        try:
            d = cls._parse_rational(raw_coords[0])
            m = cls._parse_rational(raw_coords[1])
            s = cls._parse_rational(raw_coords[2])
            
            decimal = d + (m / 60.0) + (s / 3600.0)
            
            # Negate for South / West directions
            if ref in ("S", "W"):
                decimal = -decimal
                
            # Verify boundary bounds
            if ref in ("N", "S") and not (-90.0 <= decimal <= 90.0):
                return None
            if ref in ("E", "W") and not (-180.0 <= decimal <= 180.0):
                return None
                
            return decimal
        except Exception:
            return None

    @classmethod
    def _parse_gps_datetime(cls, gps_date: bytes, gps_time: Any) -> Optional[datetime]:
        """Assembles a UTC datetime object from GPS Date/Time EXIF tags."""
        try:
            date_str = gps_date.decode("utf-8").strip() if isinstance(gps_date, bytes) else str(gps_date).strip()
            # date_str is usually "YYYY:MM:DD"
            parts = [int(p) for p in date_str.replace("-", ":").split(":")]
            if len(parts) != 3:
                return None
                
            year, month, day = parts
            
            # Parse time rationals
            h = int(cls._parse_rational(gps_time[0]))
            m = int(cls._parse_rational(gps_time[1]))
            s = int(cls._parse_rational(gps_time[2]))
            
            return datetime(year, month, day, h, m, s, tzinfo=timezone.utc)
        except Exception:
            return None

    @classmethod
    def _parse_exif_datetime(cls, date_bytes: Any) -> Optional[datetime]:
        """Parses standard EXIF datetime string 'YYYY:MM:DD HH:MM:SS'."""
        if not date_bytes:
            return None
        try:
            date_str = date_bytes.decode("utf-8").strip() if isinstance(date_bytes, bytes) else str(date_bytes).strip()
            # Standard separator is colon
            dt = datetime.strptime(date_str, "%Y:%m:%d %H:%M:%S")
            return dt.replace(tzinfo=timezone.utc)
        except Exception:
            return None

    @classmethod
    def extract(cls, file_path: str) -> ImageMetadata:
        """Parses image binary headers using PIL and piexif.
        
        Args:
            file_path: Absolute string path to the file.
            
        Returns:
            ImageMetadata schema.
            
        Raises:
            ParserFailureError: If unable to read/parse image structure.
        """
        try:
            with Image.open(file_path) as img:
                width, height = img.size
                color_space = img.info.get("icc_profile")
                color_space_name = "ICC Profile Present" if color_space else img.mode
                
            orientation = None
            gps_meta = None
            camera_meta = None
            
            try:
                # Load exif via piexif
                exif_dict = piexif.load(file_path)
                
                # 1. Orientation
                if exif_dict.get("0th") and piexif.ImageIFD.Orientation in exif_dict["0th"]:
                    orientation = exif_dict["0th"][piexif.ImageIFD.Orientation]
                    
                # 2. Camera attributes
                if exif_dict.get("0th"):
                    make_b = exif_dict["0th"].get(piexif.ImageIFD.Make)
                    model_b = exif_dict["0th"].get(piexif.ImageIFD.Model)
                    soft_b = exif_dict["0th"].get(piexif.ImageIFD.Software)
                    
                    make = make_b.decode("utf-8").strip() if make_b else None
                    model = model_b.decode("utf-8").strip() if model_b else None
                    software = soft_b.decode("utf-8").strip() if soft_b else None
                    
                    lens = None
                    if exif_dict.get("Exif"):
                        lens_b = exif_dict["Exif"].get(piexif.ExifIFD.LensModel)
                        if lens_b:
                            lens = lens_b.decode("utf-8").strip()
                            
                    if make or model or lens or software:
                        camera_meta = CameraMetadata(
                            make=make,
                            model=model,
                            lens=lens,
                            software=software,
                            confidence=ExtractionConfidence.VERIFIED
                        )
                        
                # 3. GPS Coordinates
                if exif_dict.get("GPS"):
                    gps = exif_dict["GPS"]
                    lat_ref_b = gps.get(piexif.GPSIFD.GPSLatitudeRef)
                    lat_raw = gps.get(piexif.GPSIFD.GPSLatitude)
                    long_ref_b = gps.get(piexif.GPSIFD.GPSLongitudeRef)
                    long_raw = gps.get(piexif.GPSIFD.GPSLongitude)
                    
                    lat_ref = lat_ref_b.decode("utf-8") if lat_ref_b else None
                    long_ref = long_ref_b.decode("utf-8") if long_ref_b else None
                    
                    lat = cls._convert_gps(lat_ref, lat_raw) if lat_ref and lat_raw else None
                    lon = cls._convert_gps(long_ref, long_raw) if long_ref and long_raw else None
                    
                    alt_ref = gps.get(piexif.GPSIFD.GPSAltitudeRef)
                    alt_raw = gps.get(piexif.GPSIFD.GPSAltitude)
                    alt = cls._parse_rational(alt_raw) if alt_raw else None
                    if alt is not None and alt_ref == 1:
                        alt = -alt
                        
                    gps_date = gps.get(piexif.GPSIFD.GPSDateStamp)
                    gps_time = gps.get(piexif.GPSIFD.GPSTimeStamp)
                    gps_dt = cls._parse_gps_datetime(gps_date, gps_time) if gps_date and gps_time else None
                    
                    # If GPS timestamp is missing, try fallback to standard EXIF DateTime tag
                    if not gps_dt and exif_dict.get("0th"):
                        dt_b = exif_dict["0th"].get(piexif.ImageIFD.DateTime)
                        gps_dt = cls._parse_exif_datetime(dt_b)
                        
                    if lat is not None or lon is not None:
                        gps_meta = GPSMetadata(
                            latitude=lat,
                            longitude=lon,
                            altitude=alt,
                            timestamp=gps_dt,
                            confidence=ExtractionConfidence.VERIFIED
                        )
                        
            except Exception:
                # EXIF is missing or corrupt - load basic bounds only
                pass
                
            return ImageMetadata(
                width=width,
                height=height,
                orientation=orientation,
                color_space=color_space_name,
                gps=gps_meta,
                camera=camera_meta
            )
            
        except Exception as e:
            raise ParserFailureError(f"Failed parsing image file: {e}")
