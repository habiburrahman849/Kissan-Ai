# Kissan AI - Product Overview

## Purpose
Kissan AI is a dual-brain agricultural assistant designed for Pakistani farmers. It combines a persistent memory system with RAG (Retrieval-Augmented Generation) to deliver personalized, context-aware farming advice in Urdu and English.

## Value Proposition
- Remembers individual farmer profiles, crop cycles, and past interactions
- Provides localized agricultural guidance grounded in Pakistan-specific data (crop calendars, census data, land utilization stats)
- Integrates real-time weather data to give actionable, timely advice
- Works as a website-first experience with a clean multi-page frontend

## Key Features

### Conversational AI
- Chat interface powered by Qwen LLM (qwen-plus via Alibaba DashScope)
- Mock Urdu response mode when API credentials are not configured
- Memory-augmented responses using Mem0 cloud memory search/save

### Farmer Memory System
- Per-farmer persistent memory stored in SQLite
- Crop cycle tracking: start date, harvest date, crop type
- Document upload registry for future RAG indexing
- Memory extraction from conversations (crop mentions, dates, locations)

### RAG Knowledge Base
- Pakistan agricultural PDFs: crop calendars, area/production stats, fertilizer data, water availability, census reports
- Vector index for semantic document retrieval
- Seed retriever (swappable with LangChain + Qdrant/Chroma in production)

### Weather Integration
- OpenWeatherMap-backed weather page
- Contextual weather data injected into farming advice

### Multi-Page Frontend
- `index.html` - Landing/home page
- `chat.html` - Main AI chat interface
- `weather.html` - Weather dashboard
- `profile.html` - Farmer profile management
- `settings.html` - App settings
- `login.html` - Authentication
- `help.html` - Help/documentation

## Target Users
- Pakistani farmers seeking crop guidance
- Agricultural extension workers
- Agri-tech developers building on top of the platform

## Use Cases
- "When should I plant wheat in Punjab?" → RAG + crop calendar lookup
- "What's the weather like today?" → OpenWeatherMap integration
- "Remember I planted cotton last month" → Memory extraction + storage
- Personalized advice based on farmer's historical crop data
