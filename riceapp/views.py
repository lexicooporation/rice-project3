from django.shortcuts import render, redirect, get_object_or_404
from django.core.files.storage import FileSystemStorage
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Avg
import tensorflow as tf
import numpy as np
from PIL import Image
import os
import json
import cv2 
from .models import ClassificationResult
from .forms import CustomUserCreationForm, CustomAuthenticationForm, ImageUploadForm
from django.conf import settings




# Load trained model with fallback for production
try:
    # Try absolute path first (for local development)
    model = tf.keras.models.load_model(r'C:\Users\HP\Documents\clinton\rice_project\models\2')
    print("Model loaded from absolute path")
except Exception as e:
    try:
        # Try relative path for production
        model_path = os.path.join(settings.BASE_DIR, 'models', '2')
        model = tf.keras.models.load_model(model_path)
        print("Model loaded from relative path")
    except Exception as e2:
        # Create a dummy model for initial deployment
        print(f"Model loading failed: {e2}")
        # You'll need to upload your model files to GitHub
        model = None

# UPDATE CLASS NAMES TO MATCH NEW MODEL
class_names = ['Bacterial Leaf Blight', 'Brown Spot', 'Healthy Rice Leaf', 'Leaf Blast', 'Sheath Blight']

# Load disease information from JSON
def load_disease_info():
    try:
        with open('rice_disease_info.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        # Fallback data if JSON file is not found - UPDATED FOR NEW CLASSES
        return {
            'Bacterial Leaf Blight': {
                'disease_name': 'Bacterial Leaf Blight',
                'scientific_name': 'Xanthomonas oryzae pv. oryzae',
                'symptoms': [
                    'Water-soaked lesions on leaf edges',
                    'Yellowish-white stripes along veins',
                    'Lesions with wavy margins',
                    'Milky dew droplets in morning'
                ],
                'causes': [
                    'Bacterial infection through wounds',
                    'Contaminated seeds or plant debris',
                    'High humidity and temperature',
                    'Poor field sanitation'
                ],
                'prevention_methods': [
                    'Use certified disease-free seeds',
                    'Avoid overhead irrigation',
                    'Practice field sanitation',
                    'Plant resistant varieties'
                ],
                'organic_cures': [
                    {
                        'name': 'Copper-based Sprays',
                        'type': 'Bactericide',
                        'examples': ['Copper hydroxide', 'Copper oxychloride'],
                        'application': 'Spray every 7-10 days',
                        'cost': 'Low to Medium'
                    },
                    {
                        'name': 'Bio-control Agents',
                        'type': 'Biological',
                        'examples': ['Pseudomonas fluorescens', 'Bacillus subtilis'],
                        'application': 'Seed treatment and foliar spray',
                        'cost': 'Medium'
                    }
                ],
                'chemical_pesticides': [
                    {
                        'name': 'Streptomycin',
                        'dosage': '500-1000 ppm',
                        'application': 'Spray at first symptom appearance',
                        'safety_period': '14 days',
                        'cost': 'Medium'
                    },
                    {
                        'name': 'Copper Compounds',
                        'dosage': 'As per manufacturer',
                        'application': 'Preventive spray during humid conditions',
                        'safety_period': '7 days',
                        'cost': 'Low'
                    }
                ],
                'cultural_controls': [
                    'Avoid nitrogen over-fertilization',
                    'Ensure proper drainage',
                    'Remove infected plants',
                    'Practice crop rotation'
                ]
            },
            'Brown Spot': {
                'disease_name': 'Brown Spot',
                'scientific_name': 'Cochliobolus miyabeanus',
                'symptoms': [
                    'Circular brown spots on leaves',
                    'Spots with yellow halos',
                    'Lesions may coalesce',
                    'Reduced grain quality'
                ],
                'causes': [
                    'Fungal infection',
                    'Nutrient deficiency (especially silicon)',
                    'High humidity',
                    'Poor soil conditions'
                ],
                'prevention_methods': [
                    'Balanced fertilization',
                    'Silicon application',
                    'Proper field drainage',
                    'Use resistant varieties'
                ],
                'organic_cures': [
                    {
                        'name': 'Neem-based Products',
                        'type': 'Antifungal',
                        'examples': ['Neem oil', 'Neem cake'],
                        'application': 'Spray every 10-15 days',
                        'cost': 'Low'
                    },
                    {
                        'name': 'Garlic and Chili Extract',
                        'type': 'Natural fungicide',
                        'examples': ['Homemade extract'],
                        'application': 'Weekly spray',
                        'cost': 'Very Low'
                    }
                ],
                'chemical_pesticides': [
                    {
                        'name': 'Carbendazim',
                        'dosage': '1g per liter of water',
                        'application': 'Spray at disease onset',
                        'safety_period': '21 days',
                        'cost': 'Low'
                    },
                    {
                        'name': 'Mancozeb',
                        'dosage': '2g per liter of water',
                        'application': 'Preventive spray',
                        'safety_period': '15 days',
                        'cost': 'Low'
                    }
                ],
                'cultural_controls': [
                    'Improve soil fertility',
                    'Avoid water stress',
                    'Remove infected debris',
                    'Practice proper spacing'
                ]
            },
            'Healthy Rice Leaf': {
                'disease_name': 'Healthy Rice Leaf',
                'characteristics': [
                    'Vibrant green color',
                    'Uniform leaf surface',
                    'No spots or discoloration',
                    'Proper leaf orientation'
                ],
                'maintenance_practices': [
                    'Regular monitoring for early detection',
                    'Balanced nutrient management',
                    'Proper water management',
                    'Weed control'
                ],
                'monitoring_recommendations': [
                    'Check leaves weekly for any changes',
                    'Monitor weather conditions',
                    'Watch for pest activity',
                    'Maintain field records'
                ]
            },
            'Leaf Blast': {
                'disease_name': 'Leaf Blast',
                'scientific_name': 'Pyricularia oryzae',
                'symptoms': [
                    'Diamond-shaped lesions with gray centers',
                    'Brown or reddish borders',
                    'Lesions may coalesce',
                    'Complete leaf drying in severe cases'
                ],
                'causes': [
                    'Fungal pathogen',
                    'High humidity and cool temperatures',
                    'Excessive nitrogen fertilization',
                    'Poor air circulation'
                ],
                'prevention_methods': [
                    'Use blast-resistant varieties',
                    'Avoid excessive nitrogen',
                    'Proper planting time',
                    'Field sanitation'
                ],
                'organic_cures': [
                    {
                        'name': 'Trichoderma-based Products',
                        'type': 'Bio-fungicide',
                        'examples': ['Trichoderma harzianum', 'Trichoderma viride'],
                        'application': 'Seed treatment and soil application',
                        'cost': 'Medium'
                    },
                    {
                        'name': 'Plant Extracts',
                        'type': 'Natural antifungal',
                        'examples': ['Tulsi extract', 'Eucalyptus oil'],
                        'application': 'Foliar spray every 10 days',
                        'cost': 'Low'
                    }
                ],
                'chemical_pesticides': [
                    {
                        'name': 'Tricyclazole',
                        'dosage': '0.5-1.0 g per liter',
                        'application': 'Spray at disease appearance',
                        'safety_period': '30 days',
                        'cost': 'Medium'
                    },
                    {
                        'name': 'Isoprothiolane',
                        'dosage': 'As per manufacturer',
                        'application': 'Preventive and curative',
                        'safety_period': '21 days',
                        'cost': 'Medium'
                    }
                ],
                'cultural_controls': [
                    'Avoid dense planting',
                    'Ensure proper drainage',
                    'Remove infected plants',
                    'Time planting to avoid blast-favorable conditions'
                ]
            },
            'Sheath Blight': {
                'disease_name': 'Sheath Blight',
                'scientific_name': 'Rhizoctonia solani',
                'symptoms': [
                    'Oval or elliptical greenish-gray lesions',
                    'Lesions on leaf sheaths',
                    'White fungal growth',
                    'Plant lodging in severe cases'
                ],
                'causes': [
                    'Soil-borne fungus',
                    'High plant density',
                    'High humidity',
                    'Excessive nitrogen'
                ],
                'prevention_methods': [
                    'Proper plant spacing',
                    'Balanced fertilization',
                    'Water management',
                    'Use tolerant varieties'
                ],
                'organic_cures': [
                    {
                        'name': 'Bio-fungicides',
                        'type': 'Biological control',
                        'examples': ['Pseudomonas spp.', 'Trichoderma spp.'],
                        'application': 'Soil and foliar application',
                        'cost': 'Medium'
                    },
                    {
                        'name': 'Botanical Extracts',
                        'type': 'Natural fungicide',
                        'examples': ['Neem oil', 'Garlic extract'],
                        'application': 'Regular spray',
                        'cost': 'Low'
                    }
                ],
                'chemical_pesticides': [
                    {
                        'name': 'Validamycin',
                        'dosage': '2-3 ml per liter',
                        'application': 'Spray at disease onset',
                        'safety_period': '14 days',
                        'cost': 'Medium'
                    },
                    {
                        'name': 'Hexaconazole',
                        'dosage': '1-2 ml per liter',
                        'application': 'Curative spray',
                        'safety_period': '21 days',
                        'cost': 'Medium'
                    }
                ],
                'cultural_controls': [
                    'Avoid water stagnation',
                    'Practice crop rotation',
                    'Remove infected debris',
                    'Maintain proper plant population'
                ]
            }
        }

disease_info = load_disease_info()

# ADD THIS NEW FUNCTION FOR LEAF DETECTION
def is_leaf_like(image):
    """Basic checks for leaf-like characteristics"""
    try:
        # Convert PIL Image to numpy array
        img_array = np.array(image)
        
        # Convert RGB to BGR for OpenCV (if image is RGB)
        if len(img_array.shape) == 3 and img_array.shape[2] == 3:
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        
        # Convert to HSV color space
        hsv = cv2.cvtColor(img_array, cv2.COLOR_BGR2HSV)
        
        # Define green color range in HSV
        lower_green = np.array([35, 40, 40])
        upper_green = np.array([85, 255, 255])
        
        # Create mask for green pixels
        green_mask = cv2.inRange(hsv, lower_green, upper_green)

        # Calculate percentage of green pixels
        green_ratio = np.sum(green_mask > 0) / (image.size[0] * image.size[1])
        
        # Consider it leaf-like if at least 15% is green
        return green_ratio > 0.15
        
    except Exception as e:
        # If any error occurs in leaf detection, proceed with classification
        print(f"Leaf detection error: {e}")
        return True

def home(request):
    return render(request, 'index.html')

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! Welcome to Rice Disease Detector.')
            return redirect('home')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Welcome back, {username}!')
                next_url = request.GET.get('next', 'home')
                return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('home')

@login_required
def classification_history(request):
    classifications = ClassificationResult.objects.filter(user=request.user)
    
    # Calculate stats for the template
    total_count = classifications.count()
    healthy_count = classifications.filter(predicted_class='Healthy Rice Leaf').count()
    disease_count = total_count - healthy_count
    avg_confidence = classifications.aggregate(avg_conf=Avg('confidence'))['avg_conf'] or 0
    
    context = {
        'classifications': classifications,
        'total_count': total_count,
        'healthy_count': healthy_count,
        'disease_count': disease_count,
        'avg_confidence': round(avg_confidence, 1)
    }
    
    return render(request, 'classification_history.html', context)

@login_required
def classification_result_detail(request, result_id):
    """View individual classification result details"""
    result = get_object_or_404(ClassificationResult, id=result_id, user=request.user)
    
    context = {
        'result': result,
        'predicted_class': result.predicted_class,
        'confidence': result.confidence,
        'class_probabilities': result.class_probabilities,
        'disease_info': result.disease_info or {},
        'uploaded_file_url': result.image.url,
        'user_authenticated': True,
    }
    
    return render(request, 'classification_result.html', context)

def classify_rice_disease(request):
    if request.method == 'POST' and request.FILES.get('image'):
        # Save uploaded file
        uploaded_file = request.FILES['image']
        fs = FileSystemStorage()
        filename = fs.save(uploaded_file.name, uploaded_file)
        uploaded_file_url = fs.url(filename)
        
        # Preprocess image
        image_path = fs.path(filename)
        image = Image.open(image_path)
        
        # Convert to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')
            
        # CHECK IF IMAGE IS LEAF-LIKE BEFORE CLASSIFICATION
        if not is_leaf_like(image):
            context = {
                'uploaded_file_url': uploaded_file_url,
                'error': 'The uploaded image does not appear to be a rice leaf. Please upload a clear image of a rice leaf for accurate disease detection.',
            }
            # Render the upload page again with error message
            return render(request, 'upload_image.html', context)
            
        # Resize to match model input
        image = image.resize((256, 256))
        img_array = tf.keras.preprocessing.image.img_to_array(image)
        img_array = tf.expand_dims(img_array, 0)  # Add batch dimension
        
        # Make prediction
        predictions = model.predict(img_array)
        
        # Debug info
        print(f"Raw predictions: {predictions}")
        
        predicted_class = class_names[np.argmax(predictions[0])]
        confidence = round(100 * np.max(predictions[0]), 2)
        
        class_probabilities = {
            class_names[i]: round(float(predictions[0][i]) * 100, 2) 
            for i in range(len(class_names))
        }
        
        # Get disease information
        current_disease_info = disease_info.get(predicted_class, {})
        
        # Save classification result to database only if user is logged in
        if request.user.is_authenticated:
            classification_result = ClassificationResult.objects.create(
                user=request.user,
                image=uploaded_file,
                predicted_class=predicted_class,
                confidence=confidence,
                class_probabilities=class_probabilities,
                disease_info=current_disease_info
            )
            result_id = classification_result.id
        else:
            result_id = None
        
        context = {
            'uploaded_file_url': uploaded_file_url,
            'predicted_class': predicted_class,
            'confidence': confidence,
            'class_probabilities': class_probabilities,
            'disease_info': current_disease_info,
            'result_id': result_id,
            'user_authenticated': request.user.is_authenticated,
        }
        
        return render(request, 'classification_result.html', context)
    
    return render(request, 'upload_image.html')