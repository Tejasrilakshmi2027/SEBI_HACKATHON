import cv2
import numpy as np
from PIL import Image, ImageChops, ImageFilter
import io
from typing import Dict, List, Any
import aiofiles
from datetime import datetime
import exifread


class ImageDeepfakeDetector:
    """AI-powered image deepfake detection system."""
    
    def __init__(self):
        # Known manipulation indicators
        self.manipulation_indicators = {
            'inconsistent_blur': 0.3,
            'edge_artifacts': 0.25,
            'noise_inconsistency': 0.2,
            'color_inconsistency': 0.15,
            'metadata_anomalies': 0.1
        }
    
    async def detect(self, file_path: str) -> Dict[str, Any]:
        """Detect deepfake/manipulation in image."""
        
        # Read image
        with open(file_path, 'rb') as f:
            image_bytes = f.read()
        
        img = Image.open(io.BytesIO(image_bytes))
        img_array = np.array(img)
        
        # Perform various checks
        checks = {
            'metadata_analysis': self._analyze_metadata(file_path),
            'blur_analysis': self._analyze_blur(img_array),
            'edge_analysis': self._analyze_edges(img_array),
            'noise_analysis': self._analyze_noise(img_array),
            'color_analysis': self._analyze_colors(img_array),
            'face_analysis': await self._analyze_faces(img_array),
            'compression_analysis': self._analyze_compression(img),
            'ela_analysis': self._perform_ela(img)
        }
        
        # Calculate overall risk score
        risk_score = self._calculate_risk_score(checks)
        
        return {
            'image_info': {
                'format': img.format,
                'size': img.size,
                'mode': img.mode
            },
            'checks': checks,
            'risk_score': risk_score,
            'is_manipulated': risk_score > 0.5
        }
    
    def _analyze_metadata(self, file_path: str) -> Dict[str, Any]:
        """Analyze image metadata."""
        issues = []
        risk_score = 0.0
        
        try:
            with open(file_path, 'rb') as f:
                tags = exifread.process_file(f)
            
            # Check for missing EXIF data
            if not tags:
                issues.append("No EXIF metadata found")
                risk_score += 0.3
            else:
                # Check for software editing indicators
                software = str(tags.get('Software', ''))
                if software and any(editor in software.lower() for editor in ['photoshop', 'gimp', 'editor']):
                    issues.append(f"Image editing software detected: {software}")
                    risk_score += 0.4
                
                # Check for inconsistent dates
                date_taken = str(tags.get('DateTimeOriginal', ''))
                date_modified = str(tags.get('DateTime', ''))
                if date_taken and date_modified and date_taken != date_modified:
                    issues.append("Inconsistent date metadata")
                    risk_score += 0.2
                
                # Check for camera model
                camera_model = str(tags.get('Model', ''))
                if not camera_model:
                    issues.append("No camera model information")
                    risk_score += 0.1
        except Exception as e:
            issues.append(f"Metadata analysis failed: {str(e)}")
            risk_score += 0.1
        
        return {
            'issues': issues,
            'risk_score': min(risk_score, 1.0)
        }
    
    def _analyze_blur(self, img_array: np.ndarray) -> Dict[str, Any]:
        """Analyze blur consistency across image."""
        issues = []
        risk_score = 0.0
        
        # Convert to grayscale if needed
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array
        
        # Calculate Laplacian variance (blur detection)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        
        # Check for inconsistent blur (divide image into regions)
        h, w = gray.shape
        regions = [
            gray[0:h//2, 0:w//2],
            gray[0:h//2, w//2:w],
            gray[h//2:h, 0:w//2],
            gray[h//2:h, w//2:w]
        ]
        
        variances = [cv2.Laplacian(region, cv2.CV_64F).var() for region in regions]
        variance_std = np.std(variances)
        
        if variance_std > 50:
            issues.append(f"Inconsistent blur across regions (std: {variance_std:.2f})")
            risk_score += 0.3
        
        if laplacian_var < 10:
            issues.append(f"Image appears overly blurred (variance: {laplacian_var:.2f})")
            risk_score += 0.2
        
        return {
            'laplacian_variance': laplacian_var,
            'region_variance_std': variance_std,
            'issues': issues,
            'risk_score': min(risk_score, 1.0)
        }
    
    def _analyze_edges(self, img_array: np.ndarray) -> Dict[str, Any]:
        """Analyze edge artifacts."""
        issues = []
        risk_score = 0.0
        
        # Convert to grayscale
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array
        
        # Apply Canny edge detection
        edges = cv2.Canny(gray, 100, 200)
        
        # Count edge pixels
        edge_count = np.sum(edges > 0)
        total_pixels = edges.shape[0] * edges.shape[1]
        edge_ratio = edge_count / total_pixels
        
        # Check for unusual edge density
        if edge_ratio > 0.3:
            issues.append(f"Unusually high edge density: {edge_ratio:.3f}")
            risk_score += 0.2
        elif edge_ratio < 0.01:
            issues.append(f"Unusually low edge density: {edge_ratio:.3f}")
            risk_score += 0.2
        
        # Check for sharp edge transitions (possible splicing)
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        gradient_magnitude = np.sqrt(sobelx**2 + sobely**2)
        
        high_gradient_count = np.sum(gradient_magnitude > 200)
        if high_gradient_count > total_pixels * 0.05:
            issues.append("Excessive sharp edge transitions detected")
            risk_score += 0.25
        
        return {
            'edge_ratio': edge_ratio,
            'high_gradient_count': high_gradient_count,
            'issues': issues,
            'risk_score': min(risk_score, 1.0)
        }
    
    def _analyze_noise(self, img_array: np.ndarray) -> Dict[str, Any]:
        """Analyze noise consistency."""
        issues = []
        risk_score = 0.0
        
        # Convert to grayscale
        if len(img_array.shape) == 3:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        else:
            gray = img_array
        
        # Calculate noise using standard deviation
        noise_level = np.std(gray)
        
        # Check noise in different regions
        h, w = gray.shape
        regions = [
            gray[0:h//2, 0:w//2],
            gray[0:h//2, w//2:w],
            gray[h//2:h, 0:w//2],
            gray[h//2:h, w//2:w]
        ]
        
        noise_levels = [np.std(region) for region in regions]
        noise_std = np.std(noise_levels)
        
        if noise_std > 10:
            issues.append(f"Inconsistent noise across regions (std: {noise_std:.2f})")
            risk_score += 0.3
        
        if noise_level < 5:
            issues.append(f"Unusually low noise level: {noise_level:.2f}")
            risk_score += 0.2
        
        return {
            'overall_noise': noise_level,
            'noise_consistency_std': noise_std,
            'issues': issues,
            'risk_score': min(risk_score, 1.0)
        }
    
    def _analyze_colors(self, img_array: np.ndarray) -> Dict[str, Any]:
        """Analyze color consistency."""
        issues = []
        risk_score = 0.0
        
        if len(img_array.shape) != 3:
            return {'issues': ['Not a color image'], 'risk_score': 0.0}
        
        # Calculate color histograms
        hist_r = cv2.calcHist([img_array], [0], None, [256], [0, 256])
        hist_g = cv2.calcHist([img_array], [1], None, [256], [0, 256])
        hist_b = cv2.calcHist([img_array], [2], None, [256], [0, 256])
        
        # Check for color channel inconsistencies
        mean_r = np.mean(hist_r)
        mean_g = np.mean(hist_g)
        mean_b = np.mean(hist_b)
        
        color_std = np.std([mean_r, mean_g, mean_b])
        
        if color_std > 50:
            issues.append(f"Inconsistent color channels (std: {color_std:.2f})")
            risk_score += 0.2
        
        # Check for unusual saturation
        hsv = cv2.cvtColor(img_array, cv2.COLOR_RGB2HSV)
        saturation = hsv[:, :, 1]
        mean_saturation = np.mean(saturation)
        
        if mean_saturation > 200:
            issues.append("Unusually high saturation")
            risk_score += 0.15
        
        return {
            'color_std': color_std,
            'mean_saturation': mean_saturation,
            'issues': issues,
            'risk_score': min(risk_score, 1.0)
        }
    
    async def _analyze_faces(self, img_array: np.ndarray) -> Dict[str, Any]:
        """Analyze faces for manipulation."""
        issues = []
        risk_score = 0.0
        
        try:
            # Load face cascade
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            
            # Convert to grayscale
            if len(img_array.shape) == 3:
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = img_array
            
            # Detect faces
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)
            
            if len(faces) == 0:
                issues.append("No faces detected")
            else:
                # Check for multiple faces with different sizes (possible face swap)
                face_sizes = [w * h for (x, y, w, h) in faces]
                if len(face_sizes) > 1:
                    size_std = np.std(face_sizes)
                    if size_std > np.mean(face_sizes) * 0.5:
                        issues.append("Inconsistent face sizes detected")
                        risk_score += 0.2
                
                # Analyze each face region
                for (x, y, w, h) in faces:
                    face_region = gray[y:y+h, x:x+w]
                    
                    # Check for blur inconsistency in face
                    face_laplacian = cv2.Laplacian(face_region, cv2.CV_64F).var()
                    if face_laplacian < 20:
                        issues.append("Face region appears unusually blurred")
                        risk_score += 0.15
        except Exception as e:
            issues.append(f"Face analysis failed: {str(e)}")
        
        return {
            'face_count': len(faces) if 'faces' in locals() else 0,
            'issues': issues,
            'risk_score': min(risk_score, 1.0)
        }
    
    def _analyze_compression(self, img: Image.Image) -> Dict[str, Any]:
        """Analyze compression artifacts."""
        issues = []
        risk_score = 0.0
        
        # Check for JPEG compression artifacts
        if img.format == 'JPEG':
            # JPEG images typically have compression artifacts
            # Check for block artifacts
            img_array = np.array(img)
            if len(img_array.shape) == 3:
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = img_array
            
            # Check for 8x8 block artifacts (JPEG compression)
            h, w = gray.shape
            block_diffs = []
            
            for i in range(0, h-8, 8):
                for j in range(0, w-8, 8):
                    block1 = gray[i:i+8, j:j+8]
                    block2 = gray[i+8:i+16, j:j+8] if i+16 < h else block1
                    if block1.shape == block2.shape:
                        diff = np.mean(np.abs(block1.astype(float) - block2.astype(float)))
                        block_diffs.append(diff)
            
            if block_diffs:
                block_std = np.std(block_diffs)
                if block_std < 5:
                    issues.append("Unusual compression pattern detected")
                    risk_score += 0.2
        
        return {
            'format': img.format,
            'issues': issues,
            'risk_score': min(risk_score, 1.0)
        }
    
    def _perform_ela(self, img: Image.Image) -> Dict[str, Any]:
        """Perform Error Level Analysis."""
        issues = []
        risk_score = 0.0
        
        try:
            # Save image at known quality
            temp_buffer = io.BytesIO()
            img.save(temp_buffer, format='JPEG', quality=95)
            temp_buffer.seek(0)
            
            # Reload
            resaved = Image.open(temp_buffer)
            
            # Calculate difference
            if img.mode != resaved.mode:
                img = img.convert(resaved.mode)
            
            ela_img = ImageChops.difference(img, resaved)
            
            # Scale for visibility
            extrema = ela_img.getextrema()
            max_diff = max([ex[1] for ex in extrema])
            if max_diff == 0:
                max_diff = 1
            
            scale = 255.0 / max_diff
            ela_img = ImageChops.multiply(ela_img, scale)
            
            # Analyze ELA result
            ela_array = np.array(ela_img)
            ela_mean = np.mean(ela_array)
            ela_std = np.std(ela_array)
            
            # High ELA values indicate potential manipulation
            if ela_mean > 30:
                issues.append(f"High ELA values detected (mean: {ela_mean:.2f})")
                risk_score += 0.3
            
            if ela_std > 40:
                issues.append(f"Inconsistent ELA values (std: {ela_std:.2f})")
                risk_score += 0.25
        except Exception as e:
            issues.append(f"ELA analysis failed: {str(e)}")
        
        return {
            'ela_mean': ela_mean if 'ela_mean' in locals() else 0,
            'ela_std': ela_std if 'ela_std' in locals() else 0,
            'issues': issues,
            'risk_score': min(risk_score, 1.0)
        }
    
    def _calculate_risk_score(self, checks: Dict[str, Any]) -> float:
        """Calculate overall deepfake risk score."""
        weighted_scores = {
            'metadata_analysis': 0.15,
            'blur_analysis': 0.15,
            'edge_analysis': 0.15,
            'noise_analysis': 0.15,
            'color_analysis': 0.1,
            'face_analysis': 0.2,
            'compression_analysis': 0.05,
            'ela_analysis': 0.05
        }
        
        total_score = 0.0
        for check_name, weight in weighted_scores.items():
            if check_name in checks:
                total_score += checks[check_name]['risk_score'] * weight
        
        return min(total_score, 1.0)
