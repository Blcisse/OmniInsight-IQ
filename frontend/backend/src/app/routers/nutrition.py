from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_db


router = APIRouter(prefix="/api/nutrition-intelligence", tags=["nutrition-intelligence"])


class NutritionInsight(BaseModel):
    """AI-driven nutrition insights for Thryvion Health."""
    id: str
    title: str
    description: str
    category: str  # "macros", "vitamins", "minerals", "hydration", "timing"
    priority: str  # "high", "medium", "low"
    impact_score: float  # 0-100
    confidence: float  # 0-1
    created_at: str
    data_points: Optional[dict] = None


class NutritionProduct(BaseModel):
    """Food product with nutritional analysis."""
    id: str
    name: str
    category: str
    calories: float
    protein: float  # grams
    carbs: float  # grams
    fat: float  # grams
    fiber: float  # grams
    sugar: float  # grams
    sodium: float  # mg
    health_score: float  # 0-100
    serving_size: str
    allergens: List[str]
    benefits: List[str]


class NutritionTrend(BaseModel):
    """Nutrition trends and patterns."""
    id: str
    trend_name: str
    category: str
    direction: str  # "rising", "stable", "declining"
    percentage_change: float
    period: str  # "7d", "30d", "90d"
    description: str
    related_products: List[str]


def get_mock_nutrition_insights() -> List[NutritionInsight]:
    """Generate mock nutrition insights for Thryvion Health."""
    now = datetime.now().isoformat()
    
    return [
        NutritionInsight(
            id="ins_001",
            title="Increase Omega-3 Fatty Acids",
            description="Your diet is low in EPA and DHA omega-3s. These essential fatty acids support heart health, brain function, and reduce inflammation.",
            category="macros",
            priority="high",
            impact_score=88.0,
            confidence=0.92,
            created_at=now,
            data_points={"current": 0.5, "target": 2.0, "unit": "g/day"}
        ),
        NutritionInsight(
            id="ins_002",
            title="Optimize Vitamin D Intake",
            description="Your Vitamin D levels appear suboptimal. Consider increasing sun exposure or supplementation for immune and bone health.",
            category="vitamins",
            priority="high",
            impact_score=90.0,
            confidence=0.88,
            created_at=now,
            data_points={"current": 35, "target": 50, "unit": "ng/mL"}
        ),
        NutritionInsight(
            id="ins_003",
            title="Balance Macronutrient Ratios",
            description="Your protein intake is excellent, but carbohydrate timing could be optimized around workouts for better performance.",
            category="macros",
            priority="medium",
            impact_score=75.0,
            confidence=0.85,
            created_at=now,
            data_points={"protein": 95, "carbs": 220, "fat": 65, "unit": "g/day"}
        ),
        NutritionInsight(
            id="ins_004",
            title="Increase Magnesium Rich Foods",
            description="Magnesium supports muscle recovery, sleep quality, and stress management. Your intake appears low.",
            category="minerals",
            priority="medium",
            impact_score=78.0,
            confidence=0.80,
            created_at=now,
            data_points={"current": 280, "target": 400, "unit": "mg/day"}
        ),
        NutritionInsight(
            id="ins_005",
            title="Hydration Timing Strategy",
            description="Hydration is adequate but timing can be optimized. Front-load water intake in the morning for better metabolism.",
            category="hydration",
            priority="low",
            impact_score=65.0,
            confidence=0.75,
            created_at=now,
            data_points={"current": 2.5, "target": 3.0, "unit": "L/day"}
        ),
    ]


def get_mock_nutrition_products() -> List[NutritionProduct]:
    """Generate mock nutrition product data."""
    return [
        NutritionProduct(
            id="prod_001",
            name="Wild-Caught Salmon",
            category="Protein",
            calories=206,
            protein=22.1,
            carbs=0,
            fat=12.4,
            fiber=0,
            sugar=0,
            sodium=59,
            health_score=95.0,
            serving_size="100g",
            allergens=["fish"],
            benefits=["High in Omega-3", "Excellent protein source", "Vitamin D rich"]
        ),
        NutritionProduct(
            id="prod_002",
            name="Organic Spinach",
            category="Vegetables",
            calories=23,
            protein=2.9,
            carbs=3.6,
            fat=0.4,
            fiber=2.2,
            sugar=0.4,
            sodium=79,
            health_score=98.0,
            serving_size="100g",
            allergens=[],
            benefits=["Iron rich", "High in vitamins", "Antioxidants"]
        ),
        NutritionProduct(
            id="prod_003",
            name="Greek Yogurt (Plain)",
            category="Dairy",
            calories=97,
            protein=10.0,
            carbs=3.6,
            fat=5.0,
            fiber=0,
            sugar=3.2,
            sodium=36,
            health_score=88.0,
            serving_size="100g",
            allergens=["dairy"],
            benefits=["Probiotic", "High protein", "Calcium source"]
        ),
        NutritionProduct(
            id="prod_004",
            name="Quinoa",
            category="Grains",
            calories=120,
            protein=4.4,
            carbs=21.3,
            fat=1.9,
            fiber=2.8,
            sugar=0.9,
            sodium=7,
            health_score=92.0,
            serving_size="100g (cooked)",
            allergens=[],
            benefits=["Complete protein", "Gluten-free", "High fiber"]
        ),
        NutritionProduct(
            id="prod_005",
            name="Almonds",
            category="Nuts",
            calories=579,
            protein=21.2,
            carbs=21.6,
            fat=49.9,
            fiber=12.5,
            sugar=4.4,
            sodium=1,
            health_score=90.0,
            serving_size="100g",
            allergens=["tree nuts"],
            benefits=["Vitamin E", "Healthy fats", "Magnesium rich"]
        ),
        NutritionProduct(
            id="prod_006",
            name="Blueberries",
            category="Fruits",
            calories=57,
            protein=0.7,
            carbs=14.5,
            fat=0.3,
            fiber=2.4,
            sugar=10.0,
            sodium=1,
            health_score=94.0,
            serving_size="100g",
            allergens=[],
            benefits=["Antioxidants", "Brain health", "Low glycemic"]
        ),
    ]


def get_mock_nutrition_trends() -> List[NutritionTrend]:
    """Generate mock nutrition trends."""
    return [
        NutritionTrend(
            id="trend_001",
            trend_name="Plant-Based Protein Adoption",
            category="Protein",
            direction="rising",
            percentage_change=15.3,
            period="30d",
            description="Increased interest in plant-based protein sources like legumes, quinoa, and pea protein.",
            related_products=["Quinoa", "Lentils", "Chickpeas"]
        ),
        NutritionTrend(
            id="trend_002",
            trend_name="Omega-3 Supplementation",
            category="Supplements",
            direction="rising",
            percentage_change=22.1,
            period="30d",
            description="Growing awareness of omega-3 benefits leading to increased fish oil and algae supplement usage.",
            related_products=["Wild-Caught Salmon", "Sardines", "Algae Oil"]
        ),
        NutritionTrend(
            id="trend_003",
            trend_name="Low-Sugar Alternatives",
            category="Sweeteners",
            direction="rising",
            percentage_change=18.7,
            period="30d",
            description="Shift away from refined sugar toward natural sweeteners and sugar alternatives.",
            related_products=["Stevia", "Monk Fruit", "Allulose"]
        ),
        NutritionTrend(
            id="trend_004",
            trend_name="Fermented Foods Interest",
            category="Gut Health",
            direction="rising",
            percentage_change=25.4,
            period="30d",
            description="Increased consumption of probiotic-rich fermented foods for gut health.",
            related_products=["Greek Yogurt", "Kimchi", "Sauerkraut", "Kombucha"]
        ),
        NutritionTrend(
            id="trend_005",
            trend_name="Intermittent Fasting",
            category="Eating Patterns",
            direction="stable",
            percentage_change=2.1,
            period="30d",
            description="Sustained interest in time-restricted eating and intermittent fasting protocols.",
            related_products=[]
        ),
    ]


async def get_db_optional():
    """Optional database dependency that returns None if DB not configured."""
    try:
        async for session in get_db():
            yield session
    except RuntimeError:
        yield None


@router.get("/insights", response_model=List[NutritionInsight])
async def get_nutrition_insights(
    category: Optional[str] = None,
    priority: Optional[str] = None,
    min_impact: Optional[float] = None,
    db: AsyncSession = Depends(get_db_optional),
) -> List[NutritionInsight]:
    """
    Get AI-driven nutrition insights for Thryvion Health.
    
    Falls back to mock data when database is not configured.
    """
    # For now, return mock data (database not configured)
    # TODO: Implement database queries when DB is set up
    insights = get_mock_nutrition_insights()
    
    # Apply filters if provided
    if category:
        insights = [i for i in insights if i.category == category]
    if priority:
        insights = [i for i in insights if i.priority == priority]
    if min_impact is not None:
        insights = [i for i in insights if i.impact_score >= min_impact]
    
    return insights


@router.get("/products", response_model=List[NutritionProduct])
async def get_nutrition_products(
    category: Optional[str] = None,
    min_health_score: Optional[float] = None,
    limit: int = 20,
    db: AsyncSession = Depends(get_db_optional),
) -> List[NutritionProduct]:
    """
    Get nutrition product database with health scores.
    
    Falls back to mock data when database is not configured.
    """
    # For now, return mock data (database not configured)
    # TODO: Implement database queries when ready
    products = get_mock_nutrition_products()
    
    # Apply filters if provided
    if category:
        products = [p for p in products if p.category == category]
    if min_health_score is not None:
        products = [p for p in products if p.health_score >= min_health_score]
    
    # Apply limit
    products = products[:limit]
    
    return products


@router.get("/products/{product_id}", response_model=NutritionProduct)
async def get_nutrition_product(
    product_id: str,
    db: AsyncSession = Depends(get_db_optional),
) -> NutritionProduct:
    """Get detailed information for a specific nutrition product."""
    products = get_mock_nutrition_products()
    
    for product in products:
        if product.id == product_id:
            return product
    
    # Return first product if not found (for demo)
    return products[0] if products else None


@router.get("/trends", response_model=List[NutritionTrend])
async def get_nutrition_trends(
    category: Optional[str] = None,
    direction: Optional[str] = None,
    period: str = "30d",
    db: AsyncSession = Depends(get_db_optional),
) -> List[NutritionTrend]:
    """
    Get nutrition trends and patterns.
    
    Falls back to mock data when database is not configured.
    """
    # For now, return mock data (database not configured)
    # TODO: Implement database queries and trend analysis when ready
    trends = get_mock_nutrition_trends()
    
    # Apply filters if provided
    if category:
        trends = [t for t in trends if t.category == category]
    if direction:
        trends = [t for t in trends if t.direction == direction]
    
    return trends
