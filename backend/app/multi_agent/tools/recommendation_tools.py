"""Tools for personalized recommendations."""

from typing import List, Dict, Any, Optional
import pandas as pd
from pathlib import Path


def get_recommendations(
    city: str,
    preferences: Optional[Dict[str, Any]] = None,
    budget: Optional[float] = None,
    days: Optional[int] = None
) -> str:
    """Get personalized activity and flight recommendations.
    
    This function analyzes user preferences and provides ranked recommendations
    for activities and flights based on:
    - User preferences (categories, interests)
    - Budget constraints
    - Time available
    - Popularity and value
    
    Args:
        city: The destination city
        preferences: Optional dict with user preferences:
            - categories: List of preferred categories
            - interests: List of interests
            - must_see: List of must-see activities
        budget: Optional total budget in USD
        days: Optional number of days available
    
    Returns:
        String with personalized recommendations and rankings
    """
    try:
        data_path = Path(__file__).parent.parent.parent.parent / "data" / "activities.csv"
        df = pd.read_csv(data_path)
        
        # Filter by city
        city_activities = df[df['city'].str.contains(city, case=False, na=False)]
        
        if city_activities.empty:
            return f"No activities found for {city}"
        
        result = f"Personalized Recommendations for {city.title()}:\n\n"
        
        # Apply preference filters
        if preferences:
            if 'categories' in preferences and preferences['categories']:
                categories = preferences['categories']
                city_activities = city_activities[
                    city_activities['category'].str.contains('|'.join(categories), case=False, na=False)
                ]
        
        # Budget-based recommendations
        if budget:
            # Calculate cost per activity
            city_activities = city_activities.copy()
            city_activities['value_score'] = city_activities.apply(
                lambda x: 1.0 / max(x['cost_usd'], 1) if x['cost_usd'] > 0 else 2.0,
                axis=1
            )
            
            # Sort by value (free activities first, then by inverse cost)
            city_activities = city_activities.sort_values(
                by=['value_score', 'cost_usd'],
                ascending=[False, True]
            )
            
            # Filter to fit budget
            cumulative_cost = city_activities['cost_usd'].cumsum()
            city_activities = city_activities[cumulative_cost <= budget]
            
            result += f"Budget-Conscious Recommendations (within ${budget} USD):\n"
        else:
            result += "Top Recommendations:\n"
        
        # Rank activities
        # Priority: free activities, then by category match, then by cost
        city_activities = city_activities.sort_values(
            by=['cost_usd', 'category'],
            ascending=[True, True]
        )
        
        # Show top recommendations
        top_n = min(10, len(city_activities))
        top_activities = city_activities.head(top_n)
        
        result += "\n" + "=" * 60 + "\n"
        result += "Ranked Activity Recommendations:\n"
        result += "=" * 60 + "\n\n"
        
        for idx, (_, activity) in enumerate(top_activities.iterrows(), 1):
            cost = activity['cost_usd']
            cost_str = f"${cost}" if cost > 0 else "Free"
            
            result += f"{idx}. {activity['activity_name']}\n"
            result += f"   Cost: {cost_str} | Category: {activity['category']}\n"
            result += f"   {activity['description']}\n"
            
            # Add value indicator
            if cost == 0:
                result += "   ⭐ Great Value: Free activity\n"
            elif cost < 20:
                result += "   ⭐ Good Value: Affordable option\n"
            
            result += "\n"
        
        # Calculate total cost of recommendations
        total_cost = top_activities['cost_usd'].sum()
        result += f"\nTotal Cost of Top Recommendations: ${total_cost:.2f} USD\n"
        
        if budget and total_cost > budget:
            result += f"⚠️  Note: Total exceeds budget by ${total_cost - budget:.2f} USD\n"
        
        return result
        
    except Exception as e:
        return f"Error getting recommendations: {str(e)}"


def optimize_budget(
    total_budget: float,
    flight_cost: float,
    days: int,
    city: str
) -> str:
    """Optimize budget distribution across flight, activities, and other expenses.
    
    Args:
        total_budget: Total available budget in USD
        flight_cost: Cost of flights in USD
        days: Number of days for the trip
        city: Destination city
    
    Returns:
        String with optimized budget breakdown and recommendations
    """
    try:
        # Calculate remaining budget after flights
        remaining_budget = total_budget - flight_cost
        
        if remaining_budget < 0:
            return f"Error: Flight cost (${flight_cost:.2f}) exceeds total budget (${total_budget:.2f})"
        
        # Budget allocation strategy:
        # - 40% for activities
        # - 30% for food/dining
        # - 20% for accommodation (estimated)
        # - 10% for miscellaneous
        
        activity_budget = remaining_budget * 0.4
        food_budget = remaining_budget * 0.3
        accommodation_budget = remaining_budget * 0.2
        misc_budget = remaining_budget * 0.1
        
        # Per day breakdown
        activity_per_day = activity_budget / days if days > 0 else 0
        food_per_day = food_budget / days if days > 0 else 0
        
        result = f"Optimized Budget Breakdown for {city.title()} ({days} days):\n\n"
        result += "=" * 60 + "\n"
        result += f"Total Budget: ${total_budget:.2f} USD\n"
        result += f"Flight Cost: ${flight_cost:.2f} USD\n"
        result += f"Remaining Budget: ${remaining_budget:.2f} USD\n\n"
        
        result += "Recommended Allocation:\n"
        result += "-" * 60 + "\n"
        result += f"Activities: ${activity_budget:.2f} (${activity_per_day:.2f} per day)\n"
        result += f"Food & Dining: ${food_budget:.2f} (${food_per_day:.2f} per day)\n"
        result += f"Accommodation: ${accommodation_budget:.2f}\n"
        result += f"Miscellaneous: ${misc_budget:.2f}\n\n"
        
        # Get activity recommendations within budget
        data_path = Path(__file__).parent.parent.parent.parent / "data" / "activities.csv"
        df = pd.read_csv(data_path)
        city_activities = df[df['city'].str.contains(city, case=False, na=False)]
        
        if not city_activities.empty:
            affordable_activities = city_activities[city_activities['cost_usd'] <= activity_per_day]
            result += f"\nActivities within daily budget (${activity_per_day:.2f}):\n"
            
            if not affordable_activities.empty:
                for _, activity in affordable_activities.head(5).iterrows():
                    cost_str = f"${activity['cost_usd']}" if activity['cost_usd'] > 0 else "Free"
                    result += f"  • {activity['activity_name']}: {cost_str}\n"
            else:
                result += "  (Consider free activities or adjust budget)\n"
        
        return result
        
    except Exception as e:
        return f"Error optimizing budget: {str(e)}"
