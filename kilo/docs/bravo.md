# Stage 1: Scraping JSON Data from Web Server and Writing to Storage

To specify this stage, I need to know:

## 1.1. Web Server Details:

### Define QueryLimits
    
    @dataclass
    class QueryLimits:
        total_items: int
        max_queries_per_page: int
        full_pages: int = field(init=False)
        full_page_queries: int = field(init=False)
        last_page_queries: int = field(init=False)
        
        def __post_init__(self) -> None:
            if self.total_items > 0 and self.max_queries_per_page > 0:
                self.full_pages: int = self.total_items // self.max_queries_per_page
                self.full_page_queries: int = self.max_queries_per_page
                self.last_page_queries: int = self.total_items % self.max_queries_per_page
            else:
                self.full_pages = self.full_page_queries = self.last_page_queries = 0
        
        def offset(self, page: int) -> int:
            return page * self.full_page_queries
            
    def build_query_limits(url: str) -> QueryLimits:
        response = webclient.get(url)
        error_message = response.get("errorMessage", None)
        total_items = response.get("total", 0)
        max_queries_per_page = response.get("maxLimitPermitido", 0)
        return QueryLimits(total_items, max_queries_per_page)


### 1.1.1. Target URL(s):
What is the specific URL(s) or endpoint(s) on the web server you need to scrape data from?
The system will scrape data from different URLs and endpoints on differents web server.
    
#### Precios Claros

##### Endpoints

home: str: "https://d3e6htiiul5ek9.cloudfront.net/dev/"

endpoint build_url(url: str, offset: int, queries: int) -> str: f"{url:s}?offset={offset:d}&limit={queries:d}"

endpoint points_of_sale() -> str: f"{home:s}sucursales"

endpoint points_of_sale_first_query() -> str: f"{points_of_sale():s}?limit=0"

endpoint points_of_sale_next_query_url(
    offset: int, 
    queries: int
) -> str: build_url(points_of_sale, offset, queries)

endpoint articles_per_point_of_sale(
    point_of_sale: str
) -> str: home + "productos?id_sucursal=" + point_of_sale
    
endpoint articles_first_query_url(
    articles_per_point_of_sale_url: str
) -> str: articles_per_point_of_sale_url + "&limit=0"
    
endpoint articles_next_query_url(
    articles_per_point_of_sale_url: str, 
    offset: int, 
    queries: int
    ) -> str: build_url(articles_per_point_of_sale, offset, queries)

##### Authentication method
None

##### Expected Data Volume
High

##### JSON Data Structure

In the former version of this software, the json data structure is described below. 
However, we want to change some field names and eliminate some fields.

point_of_sale(json_from_webserver: dict[str, str]) -> dict[str, str]:
{   "identifier": json_from_webserver["id"],
    "provincia": (json_from_webserver["provincia"]).lower(),
    "localidad": (json_from_webserver["localidad"]).lower(),
    "direccion": (json_from_webserver["direccion"]).lower(),
    "bandera": (json_from_webserver["banderaDescripcion"]).lower(),
    "comercio": (json_from_webserver["comercioRazonSocial"]).lower(),
    "sucursal": (json_from_webserver["sucursalNombre"]).lower(),
}

point_of_sale example
{    "identifier": "11-2-1075", 
     "provincia": "ar-a", 
     "localidad": "barrio casta\u00ef\u00bf\u00bdares", 
     "direccion": "avenida fuerza aerea esq. aguas blancas 0", 
     "bandera": "changomas", 
     "comercio": "wal mart argentina s.r.l.", 
     "sucursal": "salta fuerza a\u00e9rea"
}

articles_per_point_of_sale(json_from_webserver: dict[str, str]) -> dict[str, str]:
{   "identifier": json_from_webserver["id"],
    "marca": (json_from_webserver["marca"]).lower(),
    "nombre": (json_from_webserver["nombre"]).lower(),
    "presentacion": (json_from_webserver["presentacion"]).lower(),
    "precio": json_from_webserver["precio"],
    "precio_min": json_from_webserver["precioMin"],
    "precio_max": json_from_webserver["precioMax"],
    "point_of_sale": json_from_webserver["point_of_sale"],
}

articles_per_point_of_sale example
{"identifier": "7791130002431", 
 "marca": "finish", 
 "nombre": "abrillantador para lavavajilla finish 400 ml", 
 "presentacion": "400.0 ml", 
 "precio": 12150.0, 
 "precio_min": 12150.0, 
 "precio_max": 12150.0, 
 "point_of_sale": "2-1-021"
}

##### Data Fields of Interest
    * **1.2.2. Data Fields of Interest:**  Which specific fields from the JSON data are you interested in extracting and storing? Not all fields might be relevant for your pipeline.

    1. We want the point_of_sale with the same content as described above. However, we want to translate the names of the fields to english. 
        point_of_sale(json_from_webserver: dict[str, str]) -> dict[str, str]:
        {   "key": json_from_webserver["id"],
            "state": (json_from_webserver["provincia"]).lower(),
            "city": (json_from_webserver["localidad"]).lower(),
            "address": (json_from_webserver["direccion"]).lower(),
            "flag": (json_from_webserver["banderaDescripcion"]).lower(),
            "company": (json_from_webserver["comercioRazonSocial"]).lower(),
            "branch": (json_from_webserver["sucursalNombre"]).lower(),
        }
 
    2. We want articles_per_point_of_sale with the following fields
        articles_per_point_of_sale(json_from_webserver: dict[str, str]) -> dict[str, str]:
        {   "identifier": json_from_webserver["id"],
            "brand": (json_from_webserver["marca"]).lower(),
            "name": (json_from_webserver["nombre"]).lower(),
            "package": (json_from_webserver["presentacion"]).lower(),
            "price": str(int(float(json_from_webserver["precio"])*100)),
            "point_of_sale_key": json_from_webserver["point_of_sale"],
        }
        
##### Data Consistency and Quality
    * **1.2.3. Data Consistency and Quality:** Are there any known inconsistencies in the data? Are there null values, unexpected data types, or variations in the JSON structure across different responses?
    
#### Carrefour    
    
    
    
* **1.3. Storage Details:**
    * **1.3.1. Storage Type:** Where will you store the scraped JSON data? (e.g., cloud storage like AWS S3, Azure Blob Storage, Google Cloud Storage, a file system, a NoSQL database, etc.)
    * **1.3.2. Storage Location/Path:**  Specific path or bucket/container within the chosen storage type where the JSON files will be written.
    * **1.3.3. File Naming Convention:** How will you name the JSON files you store? (e.g., based on timestamp, source, etc.)
    * **1.3.4. Data Retention Policy (for raw JSON):** How long do you need to retain the raw scraped JSON data in storage?
    * **1.3.5. Access Control for Storage:** Who/what processes need to access the stored JSON data, and what level of access (read, write)?
