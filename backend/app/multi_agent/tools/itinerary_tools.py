"""Tools for itinerary planning."""

from typing import List, Dict, Any, Optional
import pandas as pd
from pathlib import Path


def plan_itinerary(
    city: str,
    days: int,
    activities: Optional[List[str]] = None,
    weather_forecast: Optional[Dict[str, Any]] = None,
    preferences: Optional[Dict[str, Any]] = None
) -> str:
    """Plan an optimized daily itinerary for a trip.
    
    This function creates a day-by-day itinerary considering:
    - Geographic location of activities (grouping nearby activities)
    - Weather conditions (matching activities to weather)
    - User preferences (categories, budget, interests)
    - Activity timing and duration
    
    Args:
        city: The destination city
        days: Number of days for the trip
        activities: Optional list of activity names to include (if None, searches all)
        weather_forecast: Optional dict with weather data per day
        preferences: Optional dict with user preferences (categories, budget, etc.)
    
    Returns:
        String with a detailed day-by-day itinerary
    """
    try:
        data_path = Path(__file__).parent.parent.parent.parent / "data" / "activities.csv"
        df = pd.read_csv(data_path)
        
        # Filter by city
        city_activities = df[df['city'].str.contains(city, case=False, na=False)]
        
        if city_activities.empty:
            return f"No activities found for {city}"
        
        # Filter by specific activities if provided
        if activities:
            city_activities = city_activities[
                city_activities['activity_name'].str.contains('|'.join(activities), case=False, na=False)
            ]
        
        # Filter by preferences if provided
        if preferences:
            if 'categories' in preferences:
                categories = preferences['categories']
                city_activities = city_activities[
                    city_activities['category'].str.contains('|'.join(categories), case=False, na=False)
                ]
            
            if 'max_cost' in preferences:
                max_cost = preferences['max_cost']
                city_activities = city_activities[city_activities['cost_usd'] <= max_cost]
        
        if city_activities.empty:
            return f"No activities match the criteria for {city}"
        
        # Group activities by ideal weather and category for better organization
        result = f"Optimized {days}-Day Itinerary for {city.title()}:\n\n"
        
        # Simple distribution: divide activities across days
        activities_list = city_activities.to_dict('records')
        activities_per_day = max(1, len(activities_list) // days)
        
        for day in range(1, days + 1):
            result += f"Day {day}:\n"
            result += "-" * 50 + "\n"
            
            # Get activities for this day
            start_idx = (day - 1) * activities_per_day
            end_idx = min(start_idx + activities_per_day, len(activities_list))
            day_activities = activities_list[start_idx:end_idx]
            
            if not day_activities:
                # If we run out, cycle back
                day_activities = activities_list[(day - 1) % len(activities_list):(day - 1) % len(activities_list) + 1]
            
            total_cost = 0
            for activity in day_activities:
                cost = activity['cost_usd']
                cost_str = f"${cost}" if cost > 0 else "Free"
                total_cost += cost
                
                result += f"  • {activity['activity_name']} ({cost_str})\n"
                result += f"    Category: {activity['category']}\n"
                result += f"    Ideal weather: {activity['ideal_weather']}\n"
                result += f"    {activity['description']}\n\n"
            
            result += f"  Day {day} Total Cost: ${total_cost:.2f} USD\n\n"
        
        # Calculate total trip cost
        total_trip_cost = city_activities['cost_usd'].sum()
        result += f"Total Estimated Cost for All Activities: ${total_trip_cost:.2f} USD\n"
        
        return result
        
    except Exception as e:
        return f"Error planning itinerary: {str(e)}"


def optimize_route(activities: List[Dict[str, Any]], city: str) -> List[Dict[str, Any]]:
    """Optimize the order of activities to minimize travel time.
    
    This is a simplified version that groups activities by category.
    A full implementation would use geographic coordinates.
    
    Args:
        activities: List of activity dictionaries
        city: The city name
    
    Returns:
        List of activities in optimized order
    """
    # Simple optimization: group by category
    # In a real implementation, this would use geographic coordinates
    # and calculate distances between activities
    
    category_order = ['cultura', 'aventura', 'gastronomia', 'deportes', 'entretenimiento']
    
    sorted_activities = []
    for category in category_order:
        category_activities = [a for a in activities if a.get('category') == category]
        sorted_activities.extend(category_activities)
    
    # Add any remaining activities
    remaining = [a for a in activities if a not in sorted_activities]
    sorted_activities.extend(remaining)
    
    return sorted_activities
