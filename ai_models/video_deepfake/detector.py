import cv2
import numpy as np
from typing import Dict, List, Any
import asyncio
from collections import deque


class VideoDeepfakeDetector:
    """AI-powered video deepfake detection system."""
    
    def __init__(self):
        self.frame_sample_rate = 30  # Analyze every 30th frame
        self.max_frames = 100  # Maximum frames to analyze
    
    async def detect(self, file_path: str) -> Dict[str, Any]:
        """Detect deepfake in video file."""
        
        # Open video
        cap = cv2.VideoCapture(file_path)
        
        if not cap.isOpened():
            return {
                'error': 'Could not open video file',
                'risk_score': 0.0,
                'is_manipulated': False
            }
        
        # Get video properties
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        duration = frame_count / fps if fps > 0 else 0
        
        # Extract frames for analysis
        frames = []
        frame_indices = []
        
        for i in range(0, min(frame_count, self.max_frames * self.frame_sample_rate), self.frame_sample_rate):
            cap.set(cv2.CAP_PROP_POS_FRAMES, i)
            ret, frame = cap.read()
            if ret:
                frames.append(frame)
                frame_indices.append(i)
        
        cap.release()
        
        if not frames:
            return {
                'error': 'Could not extract frames from video',
                'risk_score': 0.0,
                'is_manipulated': False
            }
        
        # Perform various checks
        checks = {
            'temporal_consistency': self._analyze_temporal_consistency(frames),
            'blink_detection': self._detect_blinks(frames),
            'lip_sync': self._analyze_lip_sync(frames),
            'face_consistency': self._analyze_face_consistency(frames),
            'compression_artifacts': self._analyze_compression_artifacts(frames),
            'lighting_consistency': self._analyze_lighting_consistency(frames),
            'motion_analysis': self._analyze_motion(frames)
        }
        
        # Calculate overall risk score
        risk_score = self._calculate_risk_score(checks)
        
        return {
            'video_info': {
                'fps': fps,
                'frame_count': frame_count,
                'duration': duration,
                'frames_analyzed': len(frames)
            },
            'checks': checks,
            'risk_score': risk_score,
            'is_manipulated': risk_score > 0.5
        }
    
    def _analyze_temporal_consistency(self, frames: List[np.ndarray]) -> Dict[str, Any]:
        """Analyze temporal consistency across frames."""
        issues = []
        risk_score = 0.0
        
        if len(frames) < 2:
            return {'issues': ['Insufficient frames for analysis'], 'risk_score': 0.0}
        
        # Calculate frame differences
        frame_diffs = []
        for i in range(len(frames) - 1):
            diff = cv2.absdiff(frames[i], frames[i + 1])
            diff_score = np.mean(diff)
            frame_diffs.append(diff_score)
        
        # Check for sudden jumps (possible frame splicing)
        diff_mean = np.mean(frame_diffs)
        diff_std = np.std(frame_diffs)
        
        for i, diff in enumerate(frame_diffs):
            if diff > diff_mean + 3 * diff_std:
                issues.append(f"Sudden frame jump detected at frame {i}")
                risk_score += 0.2
        
        # Check for unnatural consistency (possible loop)
        if diff_std < 5:
            issues.append("Unusually consistent frame differences")
            risk_score += 0.15
        
        return {
            'mean_frame_diff': diff_mean,
            'frame_diff_std': diff_std,
            'issues': issues,
            'risk_score': min(risk_score, 1.0)
        }
    
    def _detect_blinks(self, frames: List[np.ndarray]) -> Dict[str, Any]:
        """Detect eye blinking patterns."""
        issues = []
        risk_score = 0.0
        
        try:
            # Load face and eye cascades
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            eye_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_eye.xml')
            
            blink_count = 0
            total_faces = 0
            
            for frame in frames:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, 1.1, 4)
                
                for (x, y, w, h) in faces:
                    total_faces += 1
                    face_region = gray[y:y+h, x:x+w]
                    eyes = eye_cascade.detectMultiScale(face_region, 1.1, 4)
                    
                    # Simple blink detection based on eye aspect ratio
                    if len(eyes) >= 2:
                        for (ex, ey, ew, eh) in eyes:
                            aspect_ratio = ew / eh if eh > 0 else 0
                            if aspect_ratio < 2:  # Eyes closed
                                blink_count += 1
                                break
            
            # Calculate blink rate
            if total_faces > 0:
                blink_rate = blink_count / total_faces
                
                # Normal blink rate is around 15-20 blinks per minute
                # For our sampled frames, we expect some blinks
                if blink_rate < 0.05:
                    issues.append(f"Unusually low blink rate: {blink_rate:.3f}")
                    risk_score += 0.3
                elif blink_rate > 0.5:
                    issues.append(f"Unusually high blink rate: {blink_rate:.3f}")
                    risk_score += 0.2
        except Exception as e:
            issues.append(f"Blink detection failed: {str(e)}")
        
        return {
            'blink_count': blink_count if 'blink_count' in locals() else 0,
            'total_faces': total_faces if 'total_faces' in locals() else 0,
            'issues': issues,
            'risk_score': min(risk_score, 1.0)
        }
    
    def _analyze_lip_sync(self, frames: List[np.ndarray]) -> Dict[str, Any]:
        """Analyze lip synchronization (simplified)."""
        issues = []
        risk_score = 0.0
        
        # This is a simplified analysis - real lip sync requires audio
        # We analyze mouth region consistency
        try:
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            
            mouth_regions = []
            for frame in frames:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, 1.1, 4)
                
                for (x, y, w, h) in faces:
                    # Mouth region (lower half of face)
                    mouth_y = y + int(h * 0.6)
                    mouth_h = int(h * 0.3)
                    mouth_region = gray[mouth_y:mouth_y+mouth_h, x:x+w]
                    
                    if mouth_region.size > 0:
                        mouth_regions.append(np.mean(mouth_region))
            
            if len(mouth_regions) > 1:
                mouth_variance = np.var(mouth_regions)
                
                # Check for unnatural mouth movement
                if mouth_variance < 100:
                    issues.append("Unusually consistent mouth region (possible static face)")
                    risk_score += 0.25
                elif mouth_variance > 5000:
                    issues.append("Excessive mouth region variation")
                    risk_score += 0.2
        except Exception as e:
            issues.append(f"Lip sync analysis failed: {str(e)}")
        
        return {
            'mouth_variance': mouth_variance if 'mouth_variance' in locals() else 0,
            'issues': issues,
            'risk_score': min(risk_score, 1.0)
        }
    
    def _analyze_face_consistency(self, frames: List[np.ndarray]) -> Dict[str, Any]:
        """Analyze face consistency across frames."""
        issues = []
        risk_score = 0.0
        
        try:
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            
            face_sizes = []
            face_positions = []
            
            for frame in frames:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, 1.1, 4)
                
                for (x, y, w, h) in faces:
                    face_sizes.append(w * h)
                    face_positions.append((x, y))
            
            if len(face_sizes) > 1:
                # Check for size consistency
                size_std = np.std(face_sizes)
                size_mean = np.mean(face_sizes)
                
                if size_std > size_mean * 0.3:
                    issues.append("Inconsistent face sizes across frames")
                    risk_score += 0.2
                
                # Check for position consistency
                if len(face_positions) > 1:
                    x_positions = [pos[0] for pos in face_positions]
                    y_positions = [pos[1] for pos in face_positions]
                    
                    x_std = np.std(x_positions)
                    y_std = np.std(y_positions)
                    
                    if x_std > 100 or y_std > 100:
                        issues.append("Excessive face movement detected")
                        risk_score += 0.15
        except Exception as e:
            issues.append(f"Face consistency analysis failed: {str(e)}")
        
        return {
            'face_count': len(face_sizes),
            'issues': issues,
            'risk_score': min(risk_score, 1.0)
        }
    
    def _analyze_compression_artifacts(self, frames: List[np.ndarray]) -> Dict[str, Any]:
        """Analyze compression artifacts."""
        issues = []
        risk_score = 0.0
        
        # Check for block artifacts (common in compressed videos)
        artifact_scores = []
        
        for frame in frames:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            h, w = gray.shape
            
            # Check for 8x8 block boundaries
            block_diffs = []
            for i in range(0, h-8, 8):
                for j in range(0, w-8, 8):
                    block1 = gray[i:i+8, j:j+8]
                    block2 = gray[i:i+8, j+8:j+16] if j+16 < w else block1
                    if block1.shape == block2.shape:
                        diff = np.mean(np.abs(block1.astype(float) - block2.astype(float)))
                        block_diffs.append(diff)
            
            if block_diffs:
                artifact_scores.append(np.std(block_diffs))
        
        if artifact_scores:
            mean_artifacts = np.mean(artifact_scores)
            
            # Low artifact variance might indicate recompression (possible manipulation)
            if mean_artifacts < 5:
                issues.append("Unusual compression pattern detected")
                risk_score += 0.2
        
        return {
            'mean_artifact_score': np.mean(artifact_scores) if artifact_scores else 0,
            'issues': issues,
            'risk_score': min(risk_score, 1.0)
        }
    
    def _analyze_lighting_consistency(self, frames: List[np.ndarray]) -> Dict[str, Any]:
        """Analyze lighting consistency across frames."""
        issues = []
        risk_score = 0.0
        
        brightness_values = []
        for frame in frames:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            brightness = np.mean(gray)
            brightness_values.append(brightness)
        
        if len(brightness_values) > 1:
            brightness_std = np.std(brightness_values)
            brightness_mean = np.mean(brightness_values)
            
            # Check for sudden brightness changes
            for i in range(len(brightness_values) - 1):
                change = abs(brightness_values[i] - brightness_values[i + 1])
                if change > brightness_mean * 0.3:
                    issues.append(f"Sudden brightness change at frame {i}")
                    risk_score += 0.15
            
            # Check for unnatural consistency
            if brightness_std < 2:
                issues.append("Unusually consistent lighting")
                risk_score += 0.1
        
        return {
            'brightness_mean': np.mean(brightness_values),
            'brightness_std': brightness_std,
            'issues': issues,
            'risk_score': min(risk_score, 1.0)
        }
    
    def _analyze_motion(self, frames: List[np.ndarray]) -> Dict[str, Any]:
        """Analyze motion patterns."""
        issues = []
        risk_score = 0.0
        
        if len(frames) < 2:
            return {'issues': ['Insufficient frames'], 'risk_score': 0.0}
        
        # Calculate optical flow (simplified)
        motion_scores = []
        
        for i in range(len(frames) - 1):
            gray1 = cv2.cvtColor(frames[i], cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(frames[i + 1], cv2.COLOR_BGR2GRAY)
            
            # Calculate frame difference as motion proxy
            diff = cv2.absdiff(gray1, gray2)
            motion_score = np.mean(diff)
            motion_scores.append(motion_score)
        
        if motion_scores:
            motion_mean = np.mean(motion_scores)
            motion_std = np.std(motion_scores)
            
            # Check for unnatural motion patterns
            if motion_std > motion_mean * 2:
                issues.append("Inconsistent motion patterns")
                risk_score += 0.2
            
            # Check for static video (possible image sequence)
            if motion_mean < 5:
                issues.append("Very low motion detected")
                risk_score += 0.15
        
        return {
            'mean_motion': np.mean(motion_scores),
            'motion_std': np.std(motion_scores),
            'issues': issues,
            'risk_score': min(risk_score, 1.0)
        }
    
    def _calculate_risk_score(self, checks: Dict[str, Any]) -> float:
        """Calculate overall deepfake risk score."""
        weighted_scores = {
            'temporal_consistency': 0.25,
            'blink_detection': 0.2,
            'lip_sync': 0.15,
            'face_consistency': 0.2,
            'compression_artifacts': 0.1,
            'lighting_consistency': 0.05,
            'motion_analysis': 0.05
        }
        
        total_score = 0.0
        for check_name, weight in weighted_scores.items():
            if check_name in checks:
                total_score += checks[check_name]['risk_score'] * weight
        
        return min(total_score, 1.0)
