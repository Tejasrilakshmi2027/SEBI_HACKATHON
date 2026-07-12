import numpy as np
import librosa
import librosa.display
from typing import Dict, List, Any
import asyncio


class AudioAnalyzer:
    """AI-powered audio analysis for voice cloning detection."""
    
    def __init__(self):
        self.sample_rate = 22050
        self.hop_length = 512
    
    async def analyze(self, file_path: str) -> Dict[str, Any]:
        """Analyze audio for synthetic voice detection."""
        
        try:
            # Load audio
            y, sr = librosa.load(file_path, sr=self.sample_rate)
            
            # Perform various checks
            checks = {
                'spectral_analysis': self._analyze_spectrum(y, sr),
                'pitch_analysis': self._analyze_pitch(y, sr),
                'noise_analysis': self._analyze_noise(y),
                'rhythm_analysis': self._analyze_rhythm(y, sr),
                'timbre_analysis': self._analyze_timbre(y, sr),
                'silence_analysis': self._analyze_silence(y),
                'quality_analysis': self._analyze_quality(y)
            }
            
            # Calculate overall risk score
            risk_score = self._calculate_risk_score(checks)
            
            return {
                'audio_info': {
                    'duration': len(y) / sr,
                    'sample_rate': sr,
                    'samples': len(y)
                },
                'checks': checks,
                'risk_score': risk_score,
                'is_synthetic': risk_score > 0.5
            }
        except Exception as e:
            return {
                'error': f'Audio analysis failed: {str(e)}',
                'risk_score': 0.0,
                'is_synthetic': False
            }
    
    def _analyze_spectrum(self, y: np.ndarray, sr: int) -> Dict[str, Any]:
        """Analyze spectral characteristics."""
        issues = []
        risk_score = 0.0
        
        # Compute spectrogram
        D = librosa.amplitude_to_db(np.abs(librosa.stft(y)), ref=np.max)
        
        # Analyze spectral flatness (measure of tone-like vs noise-like)
        spectral_flatness = librosa.feature.spectral_flatness(y=y)
        mean_flatness = np.mean(spectral_flatness)
        
        # Synthetic voices often have unusual spectral flatness
        if mean_flatness < 0.1:
            issues.append(f"Unusually low spectral flatness: {mean_flatness:.3f}")
            risk_score += 0.2
        elif mean_flatness > 0.5:
            issues.append(f"Unusually high spectral flatness: {mean_flatness:.3f}")
            risk_score += 0.15
        
        # Analyze spectral centroid
        spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
        centroid_std = np.std(spectral_centroid)
        
        if centroid_std < 500:
            issues.append("Unusually consistent spectral centroid")
            risk_score += 0.15
        
        return {
            'mean_flatness': mean_flatness,
            'centroid_std': centroid_std,
            'issues': issues,
            'risk_score': min(risk_score, 1.0)
        }
    
    def _analyze_pitch(self, y: np.ndarray, sr: int) -> Dict[str, Any]:
        """Analyze pitch characteristics."""
        issues = []
        risk_score = 0.0
        
        # Extract pitch using librosa
        pitches, magnitudes = librosa.piptrack(y=y, sr=sr)
        
        # Get dominant pitch for each frame
        pitch_values = []
        for t in range(pitches.shape[1]):
            index = magnitudes[:, t].argmax()
            pitch = pitches[index, t]
            if pitch > 0:
                pitch_values.append(pitch)
        
        if len(pitch_values) > 0:
            pitch_mean = np.mean(pitch_values)
            pitch_std = np.std(pitch_values)
            
            # Synthetic voices often have unnatural pitch consistency
            if pitch_std < 10:
                issues.append(f"Unusually consistent pitch (std: {pitch_std:.2f})")
                risk_score += 0.25
            
            # Check for pitch range
            pitch_range = np.max(pitch_values) - np.min(pitch_values)
            if pitch_range < 50:
                issues.append(f"Very narrow pitch range: {pitch_range:.2f} Hz")
                risk_score += 0.2
        else:
            issues.append("Could not detect pitch")
            risk_score += 0.1
        
        return {
            'pitch_mean': np.mean(pitch_values) if pitch_values else 0,
            'pitch_std': np.std(pitch_values) if pitch_values else 0,
            'pitch_range': np.max(pitch_values) - np.min(pitch_values) if pitch_values else 0,
            'issues': issues,
            'risk_score': min(risk_score, 1.0)
        }
    
    def _analyze_noise(self, y: np.ndarray) -> Dict[str, Any]:
        """Analyze noise characteristics."""
        issues = []
        risk_score = 0.0
        
        # Calculate signal-to-noise ratio
        signal_power = np.mean(y ** 2)
        
        # Estimate noise from silent portions
        silence_threshold = 0.01
        silent_frames = np.abs(y) < silence_threshold
        noise_power = np.mean(y[silent_frames] ** 2) if np.any(silent_frames) else 0
        
        if noise_power > 0:
            snr = 10 * np.log10(signal_power / noise_power)
            
            if snr < 10:
                issues.append(f"Low signal-to-noise ratio: {snr:.2f} dB")
                risk_score += 0.15
            elif snr > 50:
                issues.append(f"Suspiciously high signal-to-noise ratio: {snr:.2f} dB")
                risk_score += 0.2
        
        # Analyze noise floor consistency
        noise_segments = []
        for i in range(0, len(y), 2048):
            segment = y[i:i+2048]
            if len(segment) == 2048:
                noise_segments.append(np.std(segment))
        
        if noise_segments:
            noise_std = np.std(noise_segments)
            if noise_std < 0.01:
                issues.append("Unusually consistent noise floor")
                risk_score += 0.15
        
        return {
            'snr': snr if 'snr' in locals() else 0,
            'noise_std': noise_std if noise_segments else 0,
            'issues': issues,
            'risk_score': min(risk_score, 1.0)
        }
    
    def _analyze_rhythm(self, y: np.ndarray, sr: int) -> Dict[str, Any]:
        """Analyze rhythmic patterns."""
        issues = []
        risk_score = 0.0
        
        # Extract tempo
        tempo, beat_frames = librosa.beat.beat_track(y=y, sr=sr)
        
        # Analyze beat consistency
        if len(beat_frames) > 1:
            beat_intervals = np.diff(beat_frames)
            beat_std = np.std(beat_intervals)
            
            # Synthetic speech might have unnatural rhythm
            if beat_std < 5:
                issues.append("Unusually consistent rhythm")
                risk_score += 0.15
        
        # Analyze onset strength
        onset_envelope = librosa.onset.onset_strength(y=y, sr=sr)
        onset_std = np.std(onset_envelope)
        
        if onset_std < 0.1:
            issues.append("Unusually consistent onset strength")
            risk_score += 0.1
        
        return {
            'tempo': tempo,
            'beat_std': beat_std if 'beat_std' in locals() else 0,
            'onset_std': onset_std,
            'issues': issues,
            'risk_score': min(risk_score, 1.0)
        }
    
    def _analyze_timbre(self, y: np.ndarray, sr: int) -> Dict[str, Any]:
        """Analyze timbre characteristics."""
        issues = []
        risk_score = 0.0
        
        # Extract MFCCs (Mel-frequency cepstral coefficients)
        mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        
        # Analyze MFCC consistency
        mfcc_std = np.std(mfccs, axis=1)
        mean_mfcc_std = np.mean(mfcc_std)
        
        if mean_mfcc_std < 5:
            issues.append("Unusually consistent timbre characteristics")
            risk_score += 0.2
        
        # Analyze MFCC delta (change over time)
        mfcc_delta = librosa.feature.delta(mfccs)
        delta_mean = np.mean(np.abs(mfcc_delta))
        
        if delta_mean < 0.5:
            issues.append("Unusually slow timbre changes")
            risk_score += 0.15
        
        return {
            'mean_mfcc_std': mean_mfcc_std,
            'delta_mean': delta_mean,
            'issues': issues,
            'risk_score': min(risk_score, 1.0)
        }
    
    def _analyze_silence(self, y: np.ndarray) -> Dict[str, Any]:
        """Analyze silence patterns."""
        issues = []
        risk_score = 0.0
        
        # Detect silent portions
        silence_threshold = 0.01
        is_silent = np.abs(y) < silence_threshold
        
        # Count silence segments
        silence_segments = []
        in_silence = False
        silence_start = 0
        
        for i, silent in enumerate(is_silent):
            if silent and not in_silence:
                silence_start = i
                in_silence = True
            elif not silent and in_silence:
                silence_segments.append(i - silence_start)
                in_silence = False
        
        if in_silence:
            silence_segments.append(len(y) - silence_start)
        
        # Analyze silence patterns
        if len(silence_segments) > 0:
            mean_silence = np.mean(silence_segments)
            silence_std = np.std(silence_segments)
            
            # Synthetic audio might have unnatural silence patterns
            if silence_std < 100:
                issues.append("Unusually consistent silence duration")
                risk_score += 0.15
            
            # Check for total silence ratio
            total_silence = sum(silence_segments)
            silence_ratio = total_silence / len(y)
            
            if silence_ratio < 0.05:
                issues.append("Very low silence ratio (possible continuous generation)")
                risk_score += 0.1
        
        return {
            'silence_count': len(silence_segments),
            'mean_silence': np.mean(silence_segments) if silence_segments else 0,
            'silence_ratio': total_silence / len(y) if 'total_silence' in locals() else 0,
            'issues': issues,
            'risk_score': min(risk_score, 1.0)
        }
    
    def _analyze_quality(self, y: np.ndarray) -> Dict[str, Any]:
        """Analyze overall audio quality."""
        issues = []
        risk_score = 0.0
        
        # Check for clipping
        max_amplitude = np.max(np.abs(y))
        if max_amplitude > 0.99:
            issues.append("Audio clipping detected")
            risk_score += 0.1
        
        # Check for DC offset
        dc_offset = np.mean(y)
        if abs(dc_offset) > 0.1:
            issues.append(f"DC offset detected: {dc_offset:.3f}")
            risk_score += 0.1
        
        # Check for zero crossings
        zero_crossings = librosa.feature.zero_crossing_rate(y)
        mean_zcr = np.mean(zero_crossings)
        
        if mean_zcr < 0.05:
            issues.append("Unusually low zero-crossing rate")
            risk_score += 0.1
        elif mean_zcr > 0.5:
            issues.append("Unusually high zero-crossing rate")
            risk_score += 0.1
        
        return {
            'max_amplitude': max_amplitude,
            'dc_offset': dc_offset,
            'mean_zcr': mean_zcr,
            'issues': issues,
            'risk_score': min(risk_score, 1.0)
        }
    
    def _calculate_risk_score(self, checks: Dict[str, Any]) -> float:
        """Calculate overall synthetic voice risk score."""
        weighted_scores = {
            'spectral_analysis': 0.2,
            'pitch_analysis': 0.25,
            'noise_analysis': 0.15,
            'rhythm_analysis': 0.15,
            'timbre_analysis': 0.15,
            'silence_analysis': 0.05,
            'quality_analysis': 0.05
        }
        
        total_score = 0.0
        for check_name, weight in weighted_scores.items():
            if check_name in checks:
                total_score += checks[check_name]['risk_score'] * weight
        
        return min(total_score, 1.0)
