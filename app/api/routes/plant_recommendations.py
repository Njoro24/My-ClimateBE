from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio
from datetime import datetime
import json

router = APIRouter()

# Pydantic models for plant recommendations
class PlantRecommendationRequest(BaseModel):
    location: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class PlantRequirements(BaseModel):
    rainfall: str
    temperature: str
    soilPH: str
    soilType: Optional[str] = None

class PlantRecommendation(BaseModel):
    id: int
    name: str
    scientificName: str
    localName: str
    successRate: int
    plantingTime: str
    harvestTime: str
    benefits: List[str]
    requirements: PlantRequirements
    image: str
    aiInsights: str
    category: str
    difficulty: str

class ClimateData(BaseModel):
    temperature: float
    humidity: float
    rainfall: float
    season: str
    soilType: str
    elevation: Optional[float] = None

class PlantRecommendationResponse(BaseModel):
    location: str
    climateData: ClimateData
    recommendations: List[PlantRecommendation]
    timestamp: datetime

# Mock data for Kenyan indigenous plants
KENYAN_PLANTS_DATABASE = [
    {
        "id": 1,
        "name": "Maize (Mahindi)",
        "scientificName": "Zea mays",
        "localName": "Mahindi",
        "successRate": 85,
        "plantingTime": "March - May",
        "harvestTime": "July - September",
        "benefits": [
            "High nutritional value",
            "Drought resistant varieties available",
            "Good market demand",
            "Can be intercropped with beans"
        ],
        "requirements": {
            "rainfall": "500-800mm",
            "temperature": "20-30°C",
            "soilPH": "6.0-7.5",
            "soilType": "Well-drained loamy soil"
        },
        "image": "https://images.unsplash.com/photo-1574323347407-f5e1ad6d020b?w=300&h=200&fit=crop&q=80",
        "aiInsights": "Based on current climate patterns, maize shows excellent adaptation potential in your region. Consider drought-resistant varieties for better yields.",
        "category": "Cereal",
        "difficulty": "Easy"
    },
    {
        "id": 2,
        "name": "Sorghum (Mtama)",
        "scientificName": "Sorghum bicolor",
        "localName": "Mtama",
        "successRate": 92,
        "plantingTime": "March - April",
        "harvestTime": "August - September",
        "benefits": [
            "Extremely drought tolerant",
            "Rich in antioxidants",
            "Gluten-free grain",
            "Traditional Kenyan crop"
        ],
        "requirements": {
            "rainfall": "300-600mm",
            "temperature": "25-35°C",
            "soilPH": "6.0-8.5",
            "soilType": "Sandy loam to clay loam"
        },
        "image": "https://images.unsplash.com/photo-1544197150-b99a580bb7a8?w=300&h=200&fit=crop&q=80",
        "aiInsights": "Highly recommended for climate resilience. Sorghum thrives in semi-arid conditions and requires minimal water.",
        "category": "Cereal",
        "difficulty": "Easy"
    },
    {
        "id": 3,
        "name": "Sweet Potato (Viazi vitamu)",
        "scientificName": "Ipomoea batatas",
        "localName": "Viazi vitamu",
        "successRate": 88,
        "plantingTime": "February - April",
        "harvestTime": "June - August",
        "benefits": [
            "High vitamin A content",
            "Improves soil structure",
            "Multiple harvests possible",
            "Nutritious leaves edible"
        ],
        "requirements": {
            "rainfall": "400-700mm",
            "temperature": "18-25°C",
            "soilPH": "5.5-7.0",
            "soilType": "Well-drained sandy loam"
        },
        "image": "https://images.unsplash.com/photo-1553062407-98eeb64c6a62?w=300&h=200&fit=crop&q=80",
        "aiInsights": "Perfect for food security. Orange varieties provide essential nutrients for children and improve soil health.",
        "category": "Root Vegetable",
        "difficulty": "Easy"
    },
    {
        "id": 4,
        "name": "Cassava (Muhogo)",
        "scientificName": "Manihot esculenta",
        "localName": "Muhogo",
        "successRate": 90,
        "plantingTime": "March - May",
        "harvestTime": "12-18 months",
        "benefits": [
            "Drought and pest resistant",
            "Long storage life",
            "High carbohydrate content",
            "Grows in poor soils"
        ],
        "requirements": {
            "rainfall": "500-1000mm",
            "temperature": "20-30°C",
            "soilPH": "5.5-7.0",
            "soilType": "Well-drained sandy soil"
        },
        "image": "https://images.unsplash.com/photo-1518843875459-f738682238a6?w=300&h=200&fit=crop&q=80",
        "aiInsights": "Excellent choice for food security. Cassava can survive harsh conditions and provides reliable yields even in poor soils.",
        "category": "Root Vegetable",
        "difficulty": "Easy"
    },
    {
        "id": 5,
        "name": "Finger Millet (Wimbi)",
        "scientificName": "Eleusine coracana",
        "localName": "Wimbi",
        "successRate": 87,
        "plantingTime": "March - April",
        "harvestTime": "August - September",
        "benefits": [
            "High calcium content",
            "Drought tolerant",
            "Long storage life",
            "Traditional superfood"
        ],
        "requirements": {
            "rainfall": "400-750mm",
            "temperature": "20-27°C",
            "soilPH": "5.0-8.2",
            "soilType": "Well-drained loamy soil"
        },
        "image": "https://images.unsplash.com/photo-1595854341625-f33ee10dbf94?w=300&h=200&fit=crop&q=80",
        "aiInsights": "Ideal for nutritional security. Finger millet is highly nutritious and well-adapted to marginal lands.",
        "category": "Cereal",
        "difficulty": "Medium"
    },
    {
        "id": 6,
        "name": "African Nightshade (Managu)",
        "scientificName": "Solanum nigrum",
        "localName": "Managu",
        "successRate": 95,
        "plantingTime": "Year-round",
        "harvestTime": "6-8 weeks",
        "benefits": [
            "Rich in iron and vitamins",
            "Fast growing",
            "Medicinal properties",
            "Traditional leafy vegetable"
        ],
        "requirements": {
            "rainfall": "300-800mm",
            "temperature": "15-25°C",
            "soilPH": "6.0-7.5",
            "soilType": "Fertile, well-drained soil"
        },
        "image": "https://images.unsplash.com/photo-1530587191325-3db32d826c18?w=300&h=200&fit=crop&q=80",
        "aiInsights": "Perfect for kitchen gardens. Managu is highly nutritious and can be grown year-round with minimal care.",
        "category": "Leafy Vegetable",
        "difficulty": "Easy"
    },
    {
        "id": 7,
        "name": "Cowpeas (Kunde)",
        "scientificName": "Vigna unguiculata",
        "localName": "Kunde",
        "successRate": 89,
        "plantingTime": "March - May",
        "harvestTime": "June - August",
        "benefits": [
            "High protein content",
            "Nitrogen fixation",
            "Drought tolerant",
            "Both leaves and pods edible"
        ],
        "requirements": {
            "rainfall": "400-700mm",
            "temperature": "20-30°C",
            "soilPH": "6.0-7.5",
            "soilType": "Sandy loam to clay loam"
        },
        "image": "https://images.unsplash.com/photo-1592419044706-39796d40f98c?w=300&h=200&fit=crop&q=80",
        "aiInsights": "Excellent for soil improvement. Cowpeas fix nitrogen naturally and provide both protein-rich grains and nutritious leaves.",
        "category": "Legume",
        "difficulty": "Easy"
    }
]

async def get_climate_data(location: str) -> ClimateData:
    """
    Get real climate data for Kenyan locations based on meteorological data.
    Uses actual average climate conditions for different regions.
    """
    location_lower = location.lower()
    
    # Real climate data for major Kenyan cities/regions
    if "nairobi" in location_lower:
        return ClimateData(
            temperature=19.3,  # Average annual temperature
            humidity=67,
            rainfall=869,      # Annual rainfall in mm
            season="wet" if datetime.now().month in [3,4,5,10,11,12] else "dry",
            soilType="clay loam",
            elevation=1795
        )
    elif "mombasa" in location_lower or "coast" in location_lower:
        return ClimateData(
            temperature=26.8,
            humidity=78,
            rainfall=1024,
            season="wet" if datetime.now().month in [4,5,10,11,12] else "dry",
            soilType="sandy loam",
            elevation=17
        )
    elif "kisumu" in location_lower or "nyanza" in location_lower:
        return ClimateData(
            temperature=23.5,
            humidity=72,
            rainfall=1200,
            season="wet" if datetime.now().month in [3,4,5,9,10,11] else "dry",
            soilType="clay",
            elevation=1131
        )
    elif "nakuru" in location_lower or "rift valley" in location_lower:
        return ClimateData(
            temperature=17.8,
            humidity=63,
            rainfall=965,
            season="wet" if datetime.now().month in [3,4,5,10,11] else "dry",
            soilType="volcanic",
            elevation=1850
        )
    elif "eldoret" in location_lower or "uasin gishu" in location_lower:
        return ClimateData(
            temperature=16.2,
            humidity=65,
            rainfall=1200,
            season="wet" if datetime.now().month in [4,5,6,7,8] else "dry",
            soilType="clay loam",
            elevation=2120
        )
    elif "meru" in location_lower or "eastern" in location_lower:
        return ClimateData(
            temperature=20.1,
            humidity=68,
            rainfall=1350,
            season="wet" if datetime.now().month in [3,4,5,10,11,12] else "dry",
            soilType="volcanic loam",
            elevation=1554
        )
    elif "garissa" in location_lower or "north eastern" in location_lower:
        return ClimateData(
            temperature=29.2,
            humidity=45,
            rainfall=279,      # Arid region
            season="wet" if datetime.now().month in [4,5,10,11] else "dry",
            soilType="sandy",
            elevation=147
        )
    elif "turkana" in location_lower or "lodwar" in location_lower:
        return ClimateData(
            temperature=30.8,
            humidity=42,
            rainfall=187,      # Very arid
            season="wet" if datetime.now().month in [4,5] else "dry",
            soilType="sandy loam",
            elevation=506
        )
    elif "kitale" in location_lower or "trans nzoia" in location_lower:
        return ClimateData(
            temperature=18.9,
            humidity=69,
            rainfall=1270,
            season="wet" if datetime.now().month in [4,5,6,7,8] else "dry",
            soilType="clay loam",
            elevation=1875
        )
    elif "machakos" in location_lower or "eastern" in location_lower:
        return ClimateData(
            temperature=21.4,
            humidity=61,
            rainfall=715,
            season="wet" if datetime.now().month in [3,4,5,10,11] else "dry",
            soilType="sandy clay loam",
            elevation=1372
        )
    else:
        # Default for central Kenya highlands
        return ClimateData(
            temperature=20.5,
            humidity=65,
            rainfall=950,
            season="wet" if datetime.now().month in [3,4,5,10,11] else "dry",
            soilType="clay loam",
            elevation=1500
        )

def calculate_plant_suitability(plant: dict, climate: ClimateData) -> int:
    """
    Calculate how suitable a plant is for the given climate conditions.
    Returns a score from 0-100.
    """
    score = plant["successRate"]  # Base success rate
    
    # Adjust based on temperature
    temp_range = plant["requirements"]["temperature"]
    if "20-30" in temp_range and 20 <= climate.temperature <= 30:
        score += 5
    elif "15-25" in temp_range and 15 <= climate.temperature <= 25:
        score += 5
    elif "25-35" in temp_range and 25 <= climate.temperature <= 35:
        score += 5
    
    # Adjust based on rainfall
    rainfall_req = plant["requirements"]["rainfall"]
    if "300-600" in rainfall_req and 300 <= climate.rainfall <= 600:
        score += 5
    elif "400-700" in rainfall_req and 400 <= climate.rainfall <= 700:
        score += 5
    elif "500-800" in rainfall_req and 500 <= climate.rainfall <= 800:
        score += 5
    elif "500-1000" in rainfall_req and 500 <= climate.rainfall <= 1000:
        score += 5
    
    # Cap at 100
    return min(score, 100)

def generate_ai_insights(plant: dict, climate: ClimateData, suitability_score: int) -> str:
    """
    Generate AI insights based on plant characteristics and climate data.
    """
    base_insight = plant["aiInsights"]
    
    if suitability_score >= 90:
        return f"{base_insight} Current conditions are optimal for this crop."
    elif suitability_score >= 80:
        return f"{base_insight} Good growing conditions expected."
    elif suitability_score >= 70:
        return f"{base_insight} Consider supplemental irrigation during dry periods."
    else:
        return f"{base_insight} May require additional care due to current climate conditions."

@router.post("/recommendations", response_model=PlantRecommendationResponse)
async def get_plant_recommendations(request: PlantRecommendationRequest):
    """
    Get AI-powered plant recommendations based on location and climate data.
    """
    try:
        # Get climate data for the location
        climate_data = await get_climate_data(request.location)
        
        # Calculate suitability scores for all plants
        suitable_plants = []
        for plant_data in KENYAN_PLANTS_DATABASE:
            suitability_score = calculate_plant_suitability(plant_data, climate_data)
            
            # Update AI insights based on current conditions
            enhanced_insights = generate_ai_insights(plant_data, climate_data, suitability_score)
            
            # Create plant recommendation with updated success rate
            plant_rec = PlantRecommendation(
                id=plant_data["id"],
                name=plant_data["name"],
                scientificName=plant_data["scientificName"],
                localName=plant_data["localName"],
                successRate=suitability_score,
                plantingTime=plant_data["plantingTime"],
                harvestTime=plant_data["harvestTime"],
                benefits=plant_data["benefits"],
                requirements=PlantRequirements(**plant_data["requirements"]),
                image=plant_data["image"],
                aiInsights=enhanced_insights,
                category=plant_data["category"],
                difficulty=plant_data["difficulty"]
            )
            suitable_plants.append(plant_rec)
        
        # Sort by suitability score (success rate) in descending order
        suitable_plants.sort(key=lambda x: x.successRate, reverse=True)
        
        # Return top 6 recommendations
        top_recommendations = suitable_plants[:6]
        
        return PlantRecommendationResponse(
            location=request.location,
            climateData=climate_data,
            recommendations=top_recommendations,
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating plant recommendations: {str(e)}")

@router.get("/plants", response_model=List[PlantRecommendation])
async def get_all_plants():
    """
    Get all available plants in the database.
    """
    try:
        plants = []
        for plant_data in KENYAN_PLANTS_DATABASE:
            plant = PlantRecommendation(
                id=plant_data["id"],
                name=plant_data["name"],
                scientificName=plant_data["scientificName"],
                localName=plant_data["localName"],
                successRate=plant_data["successRate"],
                plantingTime=plant_data["plantingTime"],
                harvestTime=plant_data["harvestTime"],
                benefits=plant_data["benefits"],
                requirements=PlantRequirements(**plant_data["requirements"]),
                image=plant_data["image"],
                aiInsights=plant_data["aiInsights"],
                category=plant_data["category"],
                difficulty=plant_data["difficulty"]
            )
            plants.append(plant)
        
        return plants
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching plants: {str(e)}")

@router.get("/plants/{plant_id}", response_model=PlantRecommendation)
async def get_plant_by_id(plant_id: int):
    """
    Get detailed information about a specific plant.
    """
    try:
        plant_data = next((p for p in KENYAN_PLANTS_DATABASE if p["id"] == plant_id), None)
        
        if not plant_data:
            raise HTTPException(status_code=404, detail="Plant not found")
        
        plant = PlantRecommendation(
            id=plant_data["id"],
            name=plant_data["name"],
            scientificName=plant_data["scientificName"],
            localName=plant_data["localName"],
            successRate=plant_data["successRate"],
            plantingTime=plant_data["plantingTime"],
            harvestTime=plant_data["harvestTime"],
            benefits=plant_data["benefits"],
            requirements=PlantRequirements(**plant_data["requirements"]),
            image=plant_data["image"],
            aiInsights=plant_data["aiInsights"],
            category=plant_data["category"],
            difficulty=plant_data["difficulty"]
        )
        
        return plant
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching plant: {str(e)}")

@router.get("/categories")
async def get_plant_categories():
    """
    Get all available plant categories.
    """
    try:
        categories = list(set(plant["category"] for plant in KENYAN_PLANTS_DATABASE))
        return {"categories": categories}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching categories: {str(e)}")

@router.get("/health")
async def plant_recommendations_health():
    """
    Health check for plant recommendations service.
    """
    return {
        "status": "healthy",
        "service": "plant_recommendations",
        "timestamp": datetime.utcnow(),
        "total_plants": len(KENYAN_PLANTS_DATABASE)
    }