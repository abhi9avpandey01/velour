# Wardrobe Module Documentation

## Overview

The Wardrobe module is the core business entity of Velour. It allows users to manage their physical clothing items digitally. The architecture is designed to support future AI metadata enrichment (such as automatic category detection or color extraction) without requiring changes to the existing schema or API layer.

## Architecture

This module follows the project's Clean Architecture standards:

- **API Layer**: `app/api/v1/wardrobe.py` exposes RESTful endpoints. All endpoints require an authenticated user.
- **Service Layer**: `app/services/wardrobe_service.py` houses the business logic. Every method requires a `user_id` to guarantee tenant isolation.
- **Repository Layer**: `app/repositories/wardrobe_repository.py` handles database queries, advanced filtering, and pagination.
- **Data Models**: `app/models/wardrobe.py` and `app/models/enums.py` map exactly to the Postgres schema.

## Enums

To enforce data integrity, the system utilizes strict Postgres ENUM types:
- `Category` (e.g., Tops, Bottoms)
- `Season` (e.g., Summer, Winter)
- `Occasion` (e.g., Casual, Formal)
- `Pattern` (e.g., Solid, Striped)

## Search & Filtering

The `WardrobeRepository.list_by_user` method supports:
- **Exact matching**: For enums and booleans (`category`, `season`, `favorite`, `archived`)
- **Fuzzy matching (ilike)**: For `color`, `brand`
- **Global Search**: The `search` parameter performs an `ilike` query across `name`, `notes`, and `brand` simultaneously using SQLAlchemy's `or_` operator.
- **Sorting**: Configurable via `sort_by` and `sort_desc`.
- **Pagination**: Zero-indexed `skip` and `limit`.

## Future AI Integration

When AI classification is implemented, it should hook into the `WardrobeItemUpdate` schema or run asynchronously in a Celery background worker, updating the metadata (`category`, `color`, `pattern`) of the created `WardrobeItem` using the `WardrobeService.update_item()` method.
