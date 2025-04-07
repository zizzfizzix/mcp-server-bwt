from mcp.server.fastmcp import FastMCP
from mcp-server-bwt.services.weather import WeatherRepository, WeatherService
from mcp-server-bwt.tools.weather import add_weather_tools

mcp = FastMCP("mcp-server-bwt")

weather_repository = WeatherRepository("weather-app/1.0")
weather_service = WeatherService("https://api.weather.gov", weather_repository)
add_weather_tools(mcp, weather_service)

if __name__ == "__main__":
    mcp.run(transport="stdio")
