from mcp.server.fastmcp import FastMCP
from mcp-server-bwt.services.weather import WeatherService


def add_weather_tools(mcp: FastMCP, weather_service: WeatherService) -> None:
    @mcp.tool()
    async def get_alerts(state: str) -> str:
        """Get weather alerts for a US state.

        Args:
            state: Two-letter US state code (e.g. CA, NY)
        """
        alerts = await weather_service.get_alerts(state)
        return "\n---\n".join(alerts)

    @mcp.tool()
    async def get_forecast(latitude: float, longitude: float) -> str:
        """Get weather forecast for a location.

        Args:
            latitude: Latitude of the location
            longitude: Longitude of the location
        """
        forecasts = await weather_service.get_forecast(latitude, longitude)
        return "\n---\n".join(forecasts)
