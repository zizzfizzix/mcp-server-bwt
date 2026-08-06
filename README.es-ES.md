

# mcp-server-bwt

> Servidor MCP para Bing Webmaster Tools

Este servidor MCP ([Model Context Protocol](https://modelcontextprotocol.io/introduction)) actúa como un puente entre [asistentes de IA compatibles](https://modelcontextprotocol.io/clients) como Claude o Cursor y la API de Bing Webmaster Tools. Expone toda la funcionalidad de Bing Webmaster Tools disponible a través de [`bing-webmaster-tools`](https://github.com/merj/bing-webmaster-tools) como herramientas MCP que pueden ser utilizadas por asistentes de IA para interactuar con tu cuenta de Bing Webmaster Tools.

## Ejemplo de uso con Claude

Una vez configurado, puedes usar el servidor MCP con Claude para interactuar con tu cuenta de Bing Webmaster Tools. A continuación, se muestran algunos ejemplos de preguntas:

- "Enumera todos mis sitios verificados en Bing Webmaster Tools"
- "Envía mi página principal para indexación"
- "Obtén estadísticas de tráfico para mi sitio web"
- "Revisa si hay problemas de rastreo en mi sitio"
- "Obtén estadísticas de palabras clave para 'mi producto'"

Claude utilizará las herramientas MCP adecuadas para cumplir con tus solicitudes.

## Requisitos

- [Python](https://www.python.org) >= 3.13
- [Nodejs](https://nodejs.org)
- [Clave de API de Bing Webmaster Tools](https://learn.microsoft.com/en-us/bingwebmaster/getting-access#using-api-key)

## Instalación

### Usando uvx (recomendado)

Al utilizar [`uvx`](https://docs.astral.sh/uv/guides/tools/) no se requiere una instalación específica. Lo usaremos para ejecutar directamente *mcp_server_bwt* desde la aplicación cliente.

#### Añadir a Claude Desktop con uvx

[En tu configuración de Claude](https://modelcontextprotocol.io/quickstart/user#2-add-the-filesystem-mcp-server) especifica:

```json
"mcpServers": {
  "mcp_server_bwt": {
    "command": "uvx",
    "args": [
      "--from",
      "git+https://github.com/zizzfizzix/mcp-server-bwt",
      "mcp_server_bwt"
    ]
  }
}
```

#### Añadir a Zed con uvx

En tu settings.json de Zed, añade:

```json
"context_servers": [
  "bwtServer": {
    "command": "uvx",
    "args": [
      "--from",
      "git+https://github.com/zizzfizzix/mcp-server-bwt",
      "mcp_server_bwt"
    ]
  }
]
```

### Usando make

Alternativamente, puedes instalar `mcp_server_bwt` utilizando make:

```bash
make install
```

#### Añadir a Claude Desktop con make

[En tu configuración de Claude](https://modelcontextprotocol.io/quickstart/user#2-add-the-filesystem-mcp-server) especifica:

```json
"mcpServers": {
  "bwtServer": {
    "command": "/PATH/TO/mcp-server-bwt/.venv/bin/python",
    "args": ["/PATH/TO/mcp-server-bwt/mcp_server_bwt/main.py"],
    "env": {
      "BING_WEBMASTER_API_KEY": "YOUR_API_KEY_HERE"
    }
  }
}
```

#### Añadir a Zed con make

En tu settings.json de Zed, añade:

```json
"context_servers": {
  "bwtServer": {
    "command": "/PATH/TO/mcp-server-bwt/.venv/bin/python",
    "args": ["/PATH/TO/mcp-server-bwt/mcp_server_bwt/main.py"],
    "env": {
      "BING_WEBMASTER_API_KEY": "YOUR_API_KEY_HERE"
    }
  }
}
```

## Herramientas disponibles

El servidor proporciona la siguiente funcionalidad de la API de Bing Webmaster Tools (más información en la [documentación de la API](https://learn.microsoft.com/en-us/dotnet/api/microsoft.bing.webmaster.api.interfaces?view=bing-webmaster-dotnet)):

### Gestión de sitios

- `get_sites`: Enumera todos los sitios verificados en tu cuenta de Bing Webmaster Tools
- `add_site`: Añade un nuevo sitio a tu cuenta
- `verify_site`: Verifica la propiedad de un sitio
- `remove_site`: Elimina un sitio de tu cuenta
- `get_site_roles`: Obtiene los roles para un sitio específico
- `add_site_roles`: Añade roles a un sitio
- `remove_site_role`: Elimina un rol de un sitio
- `get_site_moves`: Obtiene información sobre cambios de dirección de sitios
- `submit_site_move`: Envía una solicitud de cambio de dirección de sitio

### Envío de URL

- `submit_url`: Envía una única URL para indexación
- `submit_url_batch`: Envía múltiples URLs para indexación en un lote
- `submit_content`: Envía contenido para indexación
- `submit_feed`: Envía un feed para indexación
- `get_feeds`: Obtiene todos los feeds enviados
- `get_feed_details`: Obtiene detalles sobre un feed específico
- `remove_feed`: Elimina un feed de tu cuenta
- `get_url_submission_quota`: Comprueba tu cuota de envío de URL
- `get_content_submission_quota`: Comprueba tu cuota de envío de contenido
- `fetch_url`: Obtiene una URL para indexación
- `get_fetched_urls`: Obtiene todas las URLs obtenidas
- `get_fetched_url_details`: Obtiene detalles sobre una URL obtenida específica

### Análisis de tráfico

- `get_query_stats`: Obtiene estadísticas para consultas de búsqueda
- `get_query_traffic_stats`: Obtiene estadísticas de tráfico para consultas de búsqueda
- `get_query_page_stats`: Obtiene estadísticas de páginas para consultas de búsqueda
- `get_query_page_detail_stats`: Obtiene estadísticas detalladas de páginas para consultas de búsqueda
- `get_page_stats`: Obtiene estadísticas para páginas
- `get_page_query_stats`: Obtiene estadísticas de consultas para páginas
- `get_rank_and_traffic_stats`: Obtiene estadísticas de clasificación y tráfico

### Rastreo

- `get_crawl_stats`: Obtiene estadísticas de rastreo
- `get_crawl_settings`: Obtiene la configuración de rastreo
- `save_crawl_settings`: Guarda la configuración de rastreo
- `get_crawl_issues`: Obtiene problemas de rastreo

### Análisis de palabras clave

- `get_keyword`: Obtiene información sobre una palabra clave
- `get_keyword_stats`: Obtiene estadísticas para una palabra clave
- `get_related_keywords`: Obtiene palabras clave relacionadas

### Análisis de enlaces

- `get_link_counts`: Obtiene recuentos de enlaces
- `get_url_links`: Obtiene enlaces para una URL
- `get_deep_link`: Obtiene información sobre enlaces profundos
- `get_deep_link_blocks`: Obtiene bloqueos de enlaces profundos
- `add_deep_link_block`: Añade un bloqueo de enlace profundo
- `remove_deep_link_block`: Elimina un bloqueo de enlace profundo
- `update_deep_link`: Actualiza un enlace profundo
- `get_deep_link_algo_urls`: Obtiene URLs para el algoritmo de enlaces profundos
- `get_connected_pages`: Obtiene páginas conectadas
- `add_connected_page`: Añade una página conectada

### Gestión de contenido

- `get_url_info`: Obtiene información sobre una URL
- `get_url_traffic_info`: Obtiene información de tráfico para una URL
- `get_children_url_info`: Obtiene información sobre URLs secundarias
- `get_children_url_traffic_info`: Obtiene información de tráfico para URLs secundarias

### Bloqueo de contenido

- `get_blocked_urls`: Obtiene URLs bloqueadas
- `add_blocked_url`: Añade una URL a la lista de bloqueados
- `remove_blocked_url`: Elimina una URL de la lista de bloqueados
- `get_active_page_preview_blocks`: Obtiene bloqueos activos de vista previa de páginas
- `add_page_preview_block`: Añade un bloqueo de vista previa de página
- `remove_page_preview_block`: Elimina un bloqueo de vista previa de página

### Configuración regional

- `get_country_region_settings`: Obtiene la configuración de país/región
- `add_country_region_settings`: Añade la configuración de país/región
- `remove_country_region_settings`: Elimina la configuración de país/región

### Gestión de URL

- `get_query_parameters`: Obtiene parámetros de consulta
- `add_query_parameter`: Añade un parámetro de consulta
- `remove_query_parameter`: Elimina un parámetro de consulta
- `enable_disable_query_parameter`: Habilita o deshabilita un parámetro de consulta

## Desarrollo

Para ejecutar todas las pruebas:

```bash
make test
```

Para compilar la aplicación:

```bash
make build
```

Para realizar un análisis de código (linting) del proyecto:

```bash
make lint
```

Para formatear el proyecto:

```bash
make format
```

### Variables de entorno

Se requieren las siguientes variables de entorno:

- `BING_WEBMASTER_API_KEY`: Tu clave de API de Bing Webmaster Tools

### Inicio del servidor

Para iniciar el servidor MCP:

```bash
make start
```

### Inspector de MCP

Puedes usar el inspector de MCP para probar el servidor:

```bash
make mcp_inspector
```

### Creación a partir de una plantilla

Este servidor MCP fue creado a partir de una plantilla cookiecutter. Para crear uno similar, ejecuta:

```bash
uvx cookiecutter gh:zizzfizzix/python-base-mcp-server
```

## Licencia

mcp-server-bwt está licenciado bajo la Licencia MIT. Esto significa que tienes libertad para usar, modificar y distribuir el software, sujeto a los términos y condiciones de la Licencia MIT. Para más detalles, consulta el archivo LICENSE en el repositorio del proyecto.
