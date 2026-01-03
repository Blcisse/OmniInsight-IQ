from datetime import datetime, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_db


router = APIRouter(prefix="/api/optimization", tags=["optimization"])


class OptimizationMetric(BaseModel):
    """Health optimization metrics for nutrition and wellness tracking."""
    id: str
    metric_name: str
    current_value: float
    target_value: float
    unit: str
    category: str  # e.g., "nutrition", "wellness", "performance"
    status: str  # "optimal", "needs_improvement", "critical"
    last_updated: str
    trend: str  # "improving", "stable", "declining"


class OptimizationRecommendation(BaseModel):
    """AI-driven recommendations for health optimization."""
    id: str
    title: str
    description: str
    priority: str  # "high", "medium", "low"
    category: str
    impact_score: float  # 0-100
    effort_level: str  # "easy", "moderate", "challenging"
    estimated_improvement: str
    action_items: List[str]
    created_at: str


def get_mock_optimization_metrics() -> List[OptimizationMetric]:
    """Generate mock optimization metrics for demo purposes."""
    now = datetime.now().isoformat()
    
    return [
        OptimizationMetric(
            id="opt_001",
            metric_name="Daily Caloric Balance",
            current_value=2150.0,
            target_value=2000.0,
            unit="kcal",
            category="nutrition",
            status="needs_improvement",
            last_updated=now,
            trend="stable"
        ),
        OptimizationMetric(
            id="opt_002",
            metric_name="Protein Intake",
            current_value=85.0,
            target_value=100.0,
            unit="g",
            category="nutrition",
            status="needs_improvement",
            last_updated=now,
            trend="improving"
        ),
        OptimizationMetric(
            id="opt_003",
            metric_name="Hydration Level",
            current_value=2.5,
            target_value=3.0,
            unit="L",
            category="wellness",
            status="needs_improvement",
            last_updated=now,
            trend="stable"
        ),
        OptimizationMetric(
            id="opt_004",
            metric_name="Nutrient Diversity Score",
            current_value=78.0,
            target_value=85.0,
            unit="score",
            category="nutrition",
            status="optimal",
            last_updated=now,
            trend="improving"
        ),
        OptimizationMetric(
            id="opt_005",
            metric_name="Fiber Intake",
            current_value=28.0,
            target_value=30.0,
            unit="g",
            category="nutrition",
            status="optimal",
            last_updated=now,
            trend="improving"
        ),
        OptimizationMetric(
            id="opt_006",
            metric_name="Vitamin D Levels",
            current_value=35.0,
            target_value=50.0,
            unit="ng/mL",
            category="wellness",
            status="needs_improvement",
            last_updated=now,
            trend="declining"
        ),
        OptimizationMetric(
            id="opt_007",
            metric_name="Omega-3 Index",
            current_value=6.5,
            target_value=8.0,
            unit="%",
            category="nutrition",
            status="needs_improvement",
            last_updated=now,
            trend="stable"
        ),
        OptimizationMetric(
            id="opt_008",
            metric_name="Sleep Quality Score",
            current_value=72.0,
            target_value=85.0,
            unit="score",
            category="wellness",
            status="needs_improvement",
            last_updated=now,
            trend="improving"
        ),
    ]


def get_mock_optimization_recommendations() -> List[OptimizationRecommendation]:
    """Generate mock optimization recommendations for demo purposes."""
    now = datetime.now().isoformat()
    
    return [
        OptimizationRecommendation(
            id="rec_001",
            title="Increase Lean Protein Intake",
            description="Your protein intake is 15g below target. Increasing lean protein can help with muscle recovery and satiety.",
            priority="high",
            category="nutrition",
            impact_score=85.0,
            effort_level="easy",
            estimated_improvement="+15g protein/day",
            action_items=[
                "Add Greek yogurt to breakfast (15g protein)",
                "Include chicken breast or fish at lunch",
                "Consider a protein shake post-workout"
            ],
            created_at=now
        ),
        OptimizationRecommendation(
            id="rec_002",
            title="Optimize Vitamin D Levels",
            description="Your Vitamin D levels are below optimal range. This can affect immunity and bone health.",
            priority="high",
            category="wellness",
            impact_score=90.0,
            effort_level="easy",
            estimated_improvement="+15 ng/mL in 8 weeks",
            action_items=[
                "Take 2000 IU Vitamin D3 supplement daily",
                "Get 15-20 minutes of sunlight exposure",
                "Include fatty fish (salmon, mackerel) 2-3x/week"
            ],
            created_at=now
        ),
        OptimizationRecommendation(
            id="rec_003",
            title="Increase Daily Hydration",
            description="You're 500ml below your hydration target. Proper hydration supports metabolism and cognitive function.",
            priority="medium",
            category="wellness",
            impact_score=70.0,
            effort_level="easy",
            estimated_improvement="+0.5L water/day",
            action_items=[
                "Drink 1 glass of water upon waking",
                "Keep a water bottle at your desk",
                "Set hourly hydration reminders"
            ],
            created_at=now
        ),
        OptimizationRecommendation(
            id="rec_004",
            title="Boost Omega-3 Fatty Acids",
            description="Your Omega-3 index is below optimal. Omega-3s support heart and brain health.",
            priority="medium",
            category="nutrition",
            impact_score=78.0,
            effort_level="moderate",
            estimated_improvement="+1.5% index in 12 weeks",
            action_items=[
                "Eat fatty fish 3x per week (salmon, sardines, mackerel)",
                "Consider 1000mg EPA/DHA supplement",
                "Add chia seeds or flaxseeds to meals"
            ],
            created_at=now
        ),
        OptimizationRecommendation(
            id="rec_005",
            title="Reduce Caloric Intake by 150 kcal",
            description="You're slightly above your target caloric intake. Small adjustments can improve body composition.",
            priority="medium",
            category="nutrition",
            impact_score=65.0,
            effort_level="easy",
            estimated_improvement="-150 kcal/day",
            action_items=[
                "Reduce portion sizes by 10%",
                "Replace sugary drinks with water or tea",
                "Choose lower-calorie snack options"
            ],
            created_at=now
        ),
        OptimizationRecommendation(
            id="rec_006",
            title="Improve Sleep Quality",
            description="Your sleep quality score indicates room for improvement. Better sleep enhances recovery and cognitive performance.",
            priority="high",
            category="wellness",
            impact_score=88.0,
            effort_level="moderate",
            estimated_improvement="+13 points sleep score",
            action_items=[
                "Establish consistent sleep/wake times",
                "Reduce screen time 1 hour before bed",
                "Create a cool, dark sleep environment",
                "Avoid caffeine after 2 PM"
            ],
            created_at=now
        ),
    ]


@router.get("/metrics", response_model=List[OptimizationMetric])
async def get_optimization_metrics(
    category: Optional[str] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
) -> List[OptimizationMetric]:
    """
    Get health optimization metrics.
    
    Falls back to mock data when database is not configured.
    """
    # For now, return mock data (database not configured)
    # TODO: Implement database queries when DB is set up
    metrics = get_mock_optimization_metrics()
    
    # Apply filters if provided
    if category:
        metrics = [m for m in metrics if m.category == category]
    if status:
        metrics = [m for m in metrics if m.status == status]
    
    return metrics


@router.get("/recommendations", response_model=List[OptimizationRecommendation])
async def get_optimization_recommendations(
    priority: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
) -> List[OptimizationRecommendation]:
    """
    Get AI-driven optimization recommendations.
    
    Falls back to mock data when database is not configured.
    """
    # For now, return mock data (database not configured)
    # TODO: Implement database queries and AI recommendations when ready
    recommendations = get_mock_optimization_recommendations()
    
    # Apply filters if provided
    if priority:
        recommendations = [r for r in recommendations if r.priority == priority]
    if category:
        recommendations = [r for r in recommendations if r.category == category]
    
    # Apply limit
    recommendations = recommendations[:limit]
    
    return recommendations
