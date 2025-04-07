from typing import Any, Dict, List
import httpx


class WeatherRepository:
    def __init__(self, user_agent: str):
        self.user_agent = user_agent

    async def send_request(self, url: str) -> Any | None:
        """Make a request to the NWS API with proper error handling."""
        headers = {"User-Agent": self.user_agent, "Accept": "application/geo+json"}
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url, headers=headers, timeout=30.0)
                response.raise_for_status()
                return response.json()
            except Exception:
                return None


class WeatherService:
    def __init__(self, api_base: str, repository: WeatherRepository):
        self.nws_api_base = api_base
        self.repository = repository

    async def get_alerts(self, state: str) -> List[str]:
        url = f"{self.nws_api_base}/alerts/active/area/{state}"
        data = await self.repository.send_request(url)

        if not data or "features" not in data:
            return ["Unable to fetch alerts or no alerts found."]

        if not data["features"]:
            return ["No active alerts for this state."]

        return [self.format_alert(feature) for feature in data["features"]]

    async def get_forecast(self, latitude: float, longitude: float) -> List[str]:
        # First get the forecast grid endpoint
        points_url = f"{self.nws_api_base}/points/{latitude},{longitude}"
        points_data = await self.send_request(points_url)

        if not points_data:
            return ["Unable to fetch forecast data for this location."]

        # Get the forecast URL from the points response
        forecast_url = points_data["properties"]["forecast"]
        forecast_data = await self.send_request(forecast_url)

        if not forecast_data:
            return ["Unable to fetch detailed forecast."]

        # Format the periods into a readable forecast
        periods = forecast_data["properties"]["periods"]
        forecasts = []
        for period in periods[:5]:  # Only show next 5 periods
            forecast = f"""
    {period['name']}:
    Temperature: {period['temperature']}°{period['temperatureUnit']}
    Wind: {period['windSpeed']} {period['windDirection']}
    Forecast: {period['detailedForecast']}
    """
            forecasts.append(forecast)
        return forecasts

    def format_alert(self, feature: Dict[str, Any]) -> str:
        """Format an alert feature into a readable string."""
        props = feature["properties"]
        return f"""
    Event: {props.get('event', 'Unknown')}
    Area: {props.get('areaDesc', 'Unknown')}
    Severity: {props.get('severity', 'Unknown')}
    Description: {props.get('description', 'No description available')}
    Instructions: {props.get('instruction', 'No specific instructions provided')}
    """
