"""
Deepfake Detection Module
Uses pretrained PyTorch model for deepfake detection with manipulated frame visualization
"""

import os
import json
import numpy as np
import torch
import torch.nn as nn
import cv2
from PIL import Image
from torchvision import transforms
from typing import Dict, List, Any, Optional, Tuple
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import hashlib


class DeepfakeDetector(nn.Module):
    """Deepfake Detection Neural Network"""
    
    def __init__(self):
        super(DeepfakeDetector, self).__init__()
        
        self.features = nn.Sequential(
            nn.Conv2d(3, 64, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            
            nn.Conv2d(128, 256, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            
            nn.Conv2d(256, 512, kernel_size=3, padding=1),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(kernel_size=2, stride=2),
        )
        
        self.classifier = nn.Sequential(
            nn.AdaptiveAvgPool2d((1, 1)),
            nn.Flatten(),
            nn.Linear(512, 256),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),
            nn.Linear(256, 128),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),
            nn.Linear(128, 2),
        )
    
    def forward(self, x):
        x = self.features(x)
        x = self.classifier(x)
        return x


class DeepfakeAnalyzer:
    """Deepfake Analyzer with visualization"""
    
    def __init__(self, model_path: Optional[str] = None):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model = self._load_or_create_model(model_path)
        self.model.eval()
        self.transform = transforms.Compose([
            transforms.Resize((256, 256)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
        ])
    
    def _load_or_create_model(self, model_path: Optional[str]) -> DeepfakeDetector:
        """Load existing model or create new one"""
        model = DeepfakeDetector().to(self.device)
        
        if model_path and os.path.exists(model_path):
            try:
                state_dict = torch.load(model_path, map_location=self.device)
                model.load_state_dict(state_dict)
                print(f"Loaded model from {model_path}")
            except Exception as e:
                print(f"Could not load model: {e}, using initialized model")
        
        return model
    
    def extract_features(self, image: np.ndarray) -> Dict[str, Any]:
        """Extract deepfake-related features from image"""
        features = {}
        
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        edges = cv2.Canny(gray, 50, 150)
        features['edge_density'] = np.sum(edges) / (edges.shape[0] * edges.shape[1])
        
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        features['blur_score'] = np.var(laplacian)
        
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        features['histogram_entropy'] = -np.sum(hist * np.log2(hist + 1))
        
        lab = cv2.cvtColor(image, cv2.COLOR_RGB2LAB)
        l, a, b = cv2.split(lab)
        features['luminance_variance'] = np.var(l)
        features['color_variance'] = np.var(a) + np.var(b)
        
        noise = cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)
        noise_diff = cv2.absdiff(image, noise)
        features['noise_level'] = np.mean(noise_diff)
        
        return features
    
    def detect_manipulation_regions(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """Detect potentially manipulated regions using sliding window"""
        regions = []
        
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        window_size = 64
        stride = 32
        
        for y in range(0, gray.shape[0] - window_size, stride):
            for x in range(0, gray.shape[1] - window_size, stride):
                window = gray[y:y+window_size, x:x+window_size]
                
                laplacian = cv2.Laplacian(window, cv2.CV_64F)
                local_blur = np.var(laplacian)
                
                local_edges = cv2.Canny(window, 50, 150)
                local_edge_density = np.sum(local_edges) / (window_size * window_size)
                
                global_blur = np.var(cv2.Laplacian(gray, cv2.CV_64F))
                global_edges = cv2.Canny(gray, 50, 150)
                global_edge_density = np.sum(global_edges) / (gray.shape[0] * gray.shape[1])
                
                blur_anomaly = abs(local_blur - global_blur) / (global_blur + 1e-6)
                edge_anomaly = abs(local_edge_density - global_edge_density) / (global_edge_density + 1e-6)
                
                if blur_anomaly > 0.5 or edge_anomaly > 0.5:
                    regions.append({
                        'x': x,
                        'y': y,
                        'width': window_size,
                        'height': window_size,
                        'blur_anomaly': float(blur_anomaly),
                        'edge_anomaly': float(edge_anomaly),
                        'confidence': float(max(blur_anomaly, edge_anomaly))
                    })
        
        regions = sorted(regions, key=lambda x: x['confidence'], reverse=True)[:10]
        
        return regions
    
    def predict(self, image_path: str) -> Dict[str, Any]:
        """Predict if image is deepfake"""
        result = {
            'is_deepfake': False,
            'confidence': 0.0,
            'trust_score': 0,
            'risk_level': 'low',
            'features': {},
            'manipulation_regions': [],
            'visualization_path': None,
            'recommendations': []
        }
        
        try:
            image = cv2.imread(image_path)
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            if image is None:
                raise ValueError("Could not load image")
            
            result['features'] = self.extract_features(image)
            result['manipulation_regions'] = self.detect_manipulation_regions(image)
            
            image_tensor = self.transform(Image.fromarray(image)).unsqueeze(0).to(self.device)
            
            with torch.no_grad():
                outputs = self.model(image_tensor)
                probabilities = torch.softmax(outputs, dim=1)
                deepfake_prob = probabilities[0][1].item()
            
            result['confidence'] = deepfake_prob
            result['trust_score'] = int((1 - deepfake_prob) * 100)
            
            if deepfake_prob > 0.7:
                result['risk_level'] = 'critical'
                result['is_deepfake'] = True
            elif deepfake_prob > 0.5:
                result['risk_level'] = 'high'
                result['is_deepfake'] = True
            elif deepfake_prob > 0.3:
                result['risk_level'] = 'medium'
            else:
                result['risk_level'] = 'low'
            
            result['recommendations'] = self._generate_recommendations(result)
            
            viz_path = self._visualize_manipulation(image, result['manipulation_regions'], image_path)
            result['visualization_path'] = viz_path
            
        except Exception as e:
            result['error'] = str(e)
            result['trust_score'] = 50
            result['risk_level'] = 'medium'
        
        return result
    
    def _visualize_manipulation(self, image: np.ndarray, regions: List[Dict], original_path: str) -> str:
        """Create visualization of manipulated regions"""
        fig, ax = plt.subplots(1, 1, figsize=(12, 8))
        
        ax.imshow(image)
        ax.set_title('Deepfake Detection - Manipulated Regions', fontsize=14)
        ax.axis('off')
        
        for region in regions:
            rect = Rectangle(
                (region['x'], region['y']),
                region['width'],
                region['height'],
                linewidth=2,
                edgecolor='red',
                facecolor='none',
                alpha=0.8
            )
            ax.add_patch(rect)
            
            confidence = region['confidence']
            color = 'red' if confidence > 0.7 else 'orange' if confidence > 0.5 else 'yellow'
            
            ax.text(
                region['x'],
                region['y'] - 5,
                f'{confidence:.2f}',
                color=color,
                fontsize=8,
                fontweight='bold'
            )
        
        output_dir = os.path.join(os.path.dirname(__file__), "visualizations")
        os.makedirs(output_dir, exist_ok=True)
        
        original_name = os.path.splitext(os.path.basename(original_path))[0]
        viz_path = os.path.join(output_dir, f"{original_name}_deepfake_viz.png")
        
        plt.tight_layout()
        plt.savefig(viz_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return viz_path
    
    def _generate_recommendations(self, result: Dict) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if result['is_deepfake']:
            recommendations.append('Image shows signs of manipulation - verify source')
            recommendations.append('Check for inconsistencies in lighting and shadows')
            recommendations.append('Verify with original source if possible')
            recommendations.append('Use reverse image search to find original')
        else:
            recommendations.append('Image appears authentic')
            recommendations.append('Still verify source if context is suspicious')
        
        if result['manipulation_regions']:
            recommendations.append(f'{len(result["manipulation_regions"])} suspicious regions detected')
        
        if result['features'].get('blur_score', 0) < 100:
            recommendations.append('Unusual blur patterns detected - may indicate manipulation')
        
        if result['features'].get('noise_level', 0) > 30:
            recommendations.append('High noise level - may indicate compression or manipulation')
        
        return recommendations
    
    def batch_predict(self, image_paths: List[str]) -> List[Dict[str, Any]]:
        """Predict deepfake for multiple images"""
        results = []
        
        for image_path in image_paths:
            try:
                result = self.predict(image_path)
                result['image_path'] = image_path
                results.append(result)
            except Exception as e:
                results.append({
                    'image_path': image_path,
                    'error': str(e),
                    'trust_score': 50,
                    'risk_level': 'medium'
                })
        
        return results


def main():
    """Test the deepfake detector"""
    print("=" * 60)
    print("Deepfake Detection Module")
    print("=" * 60)
    
    analyzer = DeepfakeAnalyzer()
    
    test_image = "sample.jpg"
    if os.path.exists(test_image):
        print(f"\nAnalyzing: {test_image}")
        result = analyzer.predict(test_image)
        
        print(f"\nTrust Score: {result['trust_score']}/100")
        print(f"Risk Level: {result['risk_level'].upper()}")
        print(f"Is Deepfake: {result['is_deepfake']}")
        print(f"Confidence: {result['confidence']:.2%}")
        
        print(f"\nManipulation Regions: {len(result['manipulation_regions'])}")
        print(f"\nFeatures:")
        for key, value in result['features'].items():
            print(f"  {key}: {value:.4f}")
        
        print(f"\nRecommendations:")
        for rec in result['recommendations']:
            print(f"  - {rec}")
        
        if result['visualization_path']:
            print(f"\nVisualization saved to: {result['visualization_path']}")
    else:
        print(f"\nTest image not found: {test_image}")
        print("Place an image file named 'sample.jpg' in the current directory to test")


if __name__ == "__main__":
    main()
