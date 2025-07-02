# EFA XML-API Documentation

**Author**: Ivan Bernardi, Dataquality  
**Location**: Bolzano, 2019

## Introduction

The EFA XML-API allows access to various public transport functions via HTTP requests in XML or JSON format.

## Available Requests

### 1. StopFinder-Request
- **Purpose**: Suggests stops based on a name input
- **URL**: `http://efa.sta.bz.it/apb/XML_STOPFINDER_REQUEST`
- **Parameters**:
  - `odvSugMacro=1`
  - `name_sf=bolzano stazione`
  - Optional: `quality`

### 2. Trip-Request
- **Purpose**: Queries a connection from origin to destination
- **URL**: `http://efa.sta.bz.it/apb/XML_TRIP_REQUEST2`
- **Parameters**:
  - `name_origin`
  - `type_origin`
  - `name_destination`
  - `type_destination`
  - `odvMacro=true`
  - `calcNumberOfTrips=1`
  - Optional: `excludedMeans`, `itdTripDateTimeDepArr=dep|arr`

### 3. DM-Request (Departure Monitor)
- **Purpose**: Departure monitor for one or more stops
- **URL**: `http://efa.sta.bz.it/apb/XML_DM_REQUEST`
- **Parameters**:
  - `language=de`
  - `type_dm=stop`
  - `name_dm`
  - `mode=direct`
  - `limit=100`

### 4. Coord-Request
- **Purpose**: Determines points within a radius of coordinates
- **URL**: `http://efa.sta.bz.it/apb/XSLT_COORD_REQUEST`
- **Parameters**:
  - `coord=<lon>:<lat>:WGS84[DD.DDDDD]`
  - `radius_1`
  - `type_1=BUS_POINT`
  - `inclFilter=1`
  - `outputFormat=json`

### 5. Addinfo-Request
- **Purpose**: Lists additional information about lines and stops
- **URL**: `http://efa.sta.bz.it/apb/XML_ADDINFO_REQUEST`


## General Parameters

- **language**: `de` | `it` | `en` | `ld1` | `ld2`
- **locationServerActive=1**: Activates the location server
- **odvMacro=true`
- **odvSugMacro=true`
- **coordOutputFormat**:
  - `APBV`
  - `PROJ[+init=epsg:<Code>]`
  - `WGS84[DD.DDDDD]`
  - `STRING`

- **outputFormat**: `XML` (default) | `JSON`

- **Date and Time Parameters**:
  - `itdDateDay`, `itdDateMonth`, `itdDateYear`, `itdDateYearMonth`, `itdDateDayMonthYear`
  - `itdTime`, `itdTimeHour`, `itdTimeMinute`


## Sample Data Structures

### Stop (from StopFinder-Request)
```json
{
  "name": "Bolzano, Stazione di Bolzano",
  "stateless": "66000468",
  "anyType": "stop",
  "quality": "985",
  "coords": "680974.00000,348072.00000"
}
```

### Trip (from Trip-Request)
```json
{
  "trip": {
    "distance": "0",
    "duration": "00:20",
    "interchange": "0",
    "legs": [],
    "itdFare": {}
  }
}
```

### Leg (example for a train segment)
```json
{
  "mode": {
    "name": "R 10937 Treno regionale",
    "number": "10937",
    "type": "6",
    "destination": "Rovereto, Stazione di Rovereto"
  },
  "diva": {
    "line": "04100",
    "operator": "Trenitalia"
  }
}
```

## Reference Documents

- **Official Documentation**:  
  https://data.civis.bz.it/dataset/575f7455-6447-4626-a474-0f93ff03067b/resource/c4e66cdf-7749-40ad-bcfd-179f18743d84/download/dokumentationxmlschnittstelleapbv32014-08-28.pdf

- **Similar APIs**:  
  - Linz: http://data.linz.gv.at/katalog/linz_ag/linz_ag_linien/fahrplan/LINZ_LINIEN_Schnittstelle_EFA_V1.pdf  
  - London: http://content.tfl.gov.uk/journey-planner-api-documentation.pdf
