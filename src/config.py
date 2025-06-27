"""Configuration management for the project."""

import os

# OpenAI API key should be set via environment variable
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Base URLs for the EFA APIs
STOPFINDER_URL = "https://efa.sta.bz.it/apb/XML_STOPFINDER_REQUEST"
TRIP_REQUEST_URL = "https://efa.sta.bz.it/apb/XML_TRIP_REQUEST2"

# Default model for OpenAI
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
