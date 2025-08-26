"""
Enhanced Backend Optimization Module for DU Admission Analyzer
Implements caching, pagination, compression, and performance improvements
"""

from fastapi import FastAPI, Query, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.gzip import GZipMiddleware
import pandas as pd
import json
import hashlib
import time
from functools import lru_cache
from typing import Dict, List, Optional, Any
import asyncio
from concurrent.futures import ThreadPoolExecutor
import logging

logger = logging.getLogger(__name__)

class DataCache:
    """Simple in-memory cache for frequently accessed data"""
    
    def __init__(self, max_size: int = 100, ttl: int = 3600):
        self.cache = {}
        self.timestamps = {}
        self.max_size = max_size
        self.ttl = ttl  # Time to live in seconds
    
    def _is_expired(self, key: str) -> bool:
        if key not in self.timestamps:
            return True
        return time.time() - self.timestamps[key] > self.ttl
    
    def get(self, key: str) -> Optional[Any]:
        if key in self.cache and not self._is_expired(key):
            return self.cache[key]
        elif key in self.cache:
            # Clean up expired entry
            del self.cache[key]
            del self.timestamps[key]
        return None
    
    def set(self, key: str, value: Any) -> None:
        # Clean up if cache is full
        if len(self.cache) >= self.max_size:
            # Remove oldest entry
            oldest_key = min(self.timestamps.keys(), key=lambda k: self.timestamps[k])
            del self.cache[oldest_key]
            del self.timestamps[oldest_key]
        
        self.cache[key] = value
        self.timestamps[key] = time.time()
    
    def clear(self) -> None:
        self.cache.clear()
        self.timestamps.clear()

# Global cache instances
data_cache = DataCache(max_size=50, ttl=1800)  # 30 minutes TTL
analytics_cache = DataCache(max_size=20, ttl=3600)  # 1 hour TTL

class OptimizedBackendService:
    """Service class for optimized backend operations"""
    
    def __init__(self):
        self.executor = ThreadPoolExecutor(max_workers=4)
    
    @staticmethod
    def generate_cache_key(*args) -> str:
        """Generate cache key from arguments"""
        key_string = "_".join(str(arg) for arg in args)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    async def get_paginated_data(
        self, 
        data: pd.DataFrame, 
        page: int = 1, 
        page_size: int = 100,
        filters: Optional[Dict] = None,
        search: Optional[str] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "asc"
    ) -> Dict[str, Any]:
        """Get paginated and filtered data with caching"""
        
        # Generate cache key
        cache_key = self.generate_cache_key(
            "paginated_data", page, page_size, 
            json.dumps(filters or {}, sort_keys=True),
            search or "", sort_by or "", sort_order,
            len(data)  # Include data length to invalidate on data change
        )
        
        # Check cache first
        cached_result = data_cache.get(cache_key)
        if cached_result:
            logger.info(f"Cache hit for paginated data: {cache_key[:8]}")
            return cached_result
        
        # Process data in thread pool
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            self.executor, 
            self._process_paginated_data,
            data, page, page_size, filters, search, sort_by, sort_order
        )
        
        # Cache the result
        data_cache.set(cache_key, result)
        logger.info(f"Cached paginated data: {cache_key[:8]}")
        
        return result
    
    def _process_paginated_data(
        self, 
        data: pd.DataFrame, 
        page: int, 
        page_size: int,
        filters: Optional[Dict],
        search: Optional[str],
        sort_by: Optional[str],
        sort_order: str
    ) -> Dict[str, Any]:
        """Process paginated data synchronously"""
        
        filtered_data = data.copy()
        
        # Apply search filter
        if search:
            search_mask = (
                filtered_data['NAME OF THE COLLEGE'].str.contains(search, case=False, na=False) |
                filtered_data['NAME OF THE PROGRAM'].str.contains(search, case=False, na=False)
            )
            filtered_data = filtered_data[search_mask]
        
        # Apply column filters
        if filters:
            for column, value in filters.items():
                if column in filtered_data.columns and value:
                    if column in ['NAME OF THE COLLEGE', 'NAME OF THE PROGRAM']:
                        # Text filter
                        filtered_data = filtered_data[
                            filtered_data[column].str.contains(value, case=False, na=False)
                        ]
                    else:
                        # Exact match filter
                        filtered_data = filtered_data[filtered_data[column] == value]
        
        # Apply sorting
        if sort_by and sort_by in filtered_data.columns:
            ascending = sort_order.lower() == "asc"
            filtered_data = filtered_data.sort_values(by=sort_by, ascending=ascending)
        
        # Calculate pagination
        total_records = len(filtered_data)
        total_pages = (total_records + page_size - 1) // page_size
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        
        # Get page data
        page_data = filtered_data.iloc[start_idx:end_idx]
        
        return {
            "data": page_data.to_dict('records'),
            "pagination": {
                "current_page": page,
                "page_size": page_size,
                "total_records": total_records,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_previous": page > 1
            },
            "filters_applied": filters or {},
            "search_applied": search or "",
            "sort_applied": {
                "column": sort_by,
                "order": sort_order
            }
        }
    
    async def get_optimized_analytics(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Get analytics with caching and optimization"""
        
        # Generate cache key based on data characteristics
        data_hash = hashlib.md5(str(data.shape).encode()).hexdigest()
        cache_key = f"analytics_{data_hash}"
        
        # Check cache
        cached_analytics = analytics_cache.get(cache_key)
        if cached_analytics:
            logger.info(f"Cache hit for analytics: {cache_key[:8]}")
            return cached_analytics
        
        # Generate analytics in thread pool
        loop = asyncio.get_event_loop()
        analytics = await loop.run_in_executor(
            self.executor,
            self._compute_analytics,
            data
        )
        
        # Cache the result
        analytics_cache.set(cache_key, analytics)
        logger.info(f"Cached analytics: {cache_key[:8]}")
        
        return analytics
    
    def _compute_analytics(self, data: pd.DataFrame) -> Dict[str, Any]:
        """Compute analytics synchronously"""
        
        try:
            # Basic statistics
            total_records = len(data)
            total_colleges = data['NAME OF THE COLLEGE'].nunique()
            total_programs = data['NAME OF THE PROGRAM'].nunique()
            
            # Category-wise totals
            numeric_columns = ['UR', 'OBC', 'SC', 'ST', 'EWS', 'SIKH', 'PwBD']
            category_totals = {}
            for col in numeric_columns:
                if col in data.columns:
                    category_totals[col] = int(data[col].sum())
            
            total_seats = sum(category_totals.values())
            
            # Top colleges by seats
            college_stats = data.groupby('NAME OF THE COLLEGE')[numeric_columns].sum()
            college_stats['Total_Seats'] = college_stats.sum(axis=1)
            top_colleges = college_stats.nlargest(10, 'Total_Seats')
            
            # Top programs by seats
            program_stats = data.groupby('NAME OF THE PROGRAM')[numeric_columns].sum()
            program_stats['Total_Seats'] = program_stats.sum(axis=1)
            top_programs = program_stats.nlargest(10, 'Total_Seats')
            
            # Efficiency metrics
            efficiency_metrics = {
                "data_completeness": (data.notna().sum().sum() / (len(data) * len(data.columns))) * 100,
                "college_coverage": total_colleges,
                "program_coverage": total_programs,
                "average_seats_per_college": total_seats / total_colleges if total_colleges > 0 else 0,
                "average_seats_per_program": total_seats / total_programs if total_programs > 0 else 0
            }
            
            return {
                "overview": {
                    "total_records": total_records,
                    "total_colleges": total_colleges,
                    "total_programs": total_programs,
                    "total_seats": total_seats
                },
                "category_totals": category_totals,
                "top_colleges": top_colleges.head(10).to_dict('index'),
                "top_programs": top_programs.head(10).to_dict('index'),
                "efficiency_metrics": efficiency_metrics,
                "timestamp": time.time()
            }
            
        except Exception as e:
            logger.error(f"Error computing analytics: {str(e)}")
            return {"error": str(e)}
    
    async def get_college_programs(self, data: pd.DataFrame, college_name: str) -> Dict[str, Any]:
        """Get programs for a specific college with caching"""
        
        cache_key = self.generate_cache_key("college_programs", college_name, len(data))
        cached_result = data_cache.get(cache_key)
        if cached_result:
            return cached_result
        
        try:
            college_data = data[data['NAME OF THE COLLEGE'] == college_name]
            
            if college_data.empty:
                result = {"error": f"College '{college_name}' not found"}
            else:
                numeric_columns = ['UR', 'OBC', 'SC', 'ST', 'EWS', 'SIKH', 'PwBD']
                programs = []
                
                for _, row in college_data.iterrows():
                    program_info = {
                        "program_name": row['NAME OF THE PROGRAM'],
                        "seats": {col: int(row[col]) for col in numeric_columns if col in row},
                        "total_seats": sum(int(row[col]) for col in numeric_columns if col in row)
                    }
                    programs.append(program_info)
                
                total_college_seats = sum(p["total_seats"] for p in programs)
                
                result = {
                    "college_name": college_name,
                    "total_programs": len(programs),
                    "total_seats": total_college_seats,
                    "programs": programs
                }
            
            data_cache.set(cache_key, result)
            return result
            
        except Exception as e:
            return {"error": str(e)}
    
    @staticmethod
    def compress_response(data: Dict[str, Any]) -> Dict[str, Any]:
        """Compress large responses by summarizing data"""
        
        if "data" in data and isinstance(data["data"], list):
            # If response is too large, provide summary instead
            if len(str(data)) > 1000000:  # 1MB threshold
                original_count = len(data["data"])
                # Keep only first 100 records for large datasets
                data["data"] = data["data"][:100]
                data["compressed"] = True
                data["original_count"] = original_count
                data["message"] = f"Response compressed. Showing first 100 of {original_count} records."
        
        return data

# Global service instance
backend_service = OptimizedBackendService()

def setup_optimized_routes(app: FastAPI):
    """Setup optimized API routes"""
    
    # Add compression middleware
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    @app.get("/api/v2/data")
    async def get_optimized_data(
        request: Request,
        page: int = Query(1, ge=1, description="Page number"),
        page_size: int = Query(100, ge=1, le=1000, description="Records per page"),
        college: Optional[str] = Query(None, description="Filter by college name"),
        program: Optional[str] = Query(None, description="Filter by program name"),
        category: Optional[str] = Query(None, description="Filter by category"),
        search: Optional[str] = Query(None, description="Search in college/program names"),
        sort_by: Optional[str] = Query(None, description="Sort by column"),
        sort_order: str = Query("asc", regex="^(asc|desc)$", description="Sort order")
    ):
        """Optimized paginated data endpoint with caching"""
        
        try:
            # Get data from the service (this would be injected in real implementation)
            # For now, we'll simulate getting it from the global analytics service
            from src.analytics import get_current_clean_data
            data = get_current_clean_data()
            
            if data is None or data.empty:
                raise HTTPException(status_code=404, detail="No data available")
            
            # Prepare filters
            filters = {}
            if college:
                filters['NAME OF THE COLLEGE'] = college
            if program:
                filters['NAME OF THE PROGRAM'] = program
            if category:
                filters[category] = 1  # Assuming category filter means has seats in that category
            
            # Get paginated data
            result = await backend_service.get_paginated_data(
                data=data,
                page=page,
                page_size=page_size,
                filters=filters,
                search=search,
                sort_by=sort_by,
                sort_order=sort_order
            )
            
            # Compress if needed
            result = backend_service.compress_response(result)
            
            return JSONResponse(content=result)
            
        except Exception as e:
            logger.error(f"Error in optimized data endpoint: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/v2/analytics")
    async def get_optimized_analytics():
        """Optimized analytics endpoint with caching"""
        
        try:
            from src.analytics import get_current_clean_data
            data = get_current_clean_data()
            
            if data is None or data.empty:
                raise HTTPException(status_code=404, detail="No data available")
            
            analytics = await backend_service.get_optimized_analytics(data)
            
            return JSONResponse(content=analytics)
            
        except Exception as e:
            logger.error(f"Error in optimized analytics endpoint: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/v2/colleges/{college_name}/programs")
    async def get_college_programs(college_name: str):
        """Get programs for a specific college"""
        
        try:
            from src.analytics import get_current_clean_data
            data = get_current_clean_data()
            
            if data is None or data.empty:
                raise HTTPException(status_code=404, detail="No data available")
            
            result = await backend_service.get_college_programs(data, college_name)
            
            if "error" in result:
                raise HTTPException(status_code=404, detail=result["error"])
            
            return JSONResponse(content=result)
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error in college programs endpoint: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.get("/api/v2/stats")
    async def get_performance_stats():
        """Get backend performance statistics"""
        
        try:
            stats = {
                "cache_stats": {
                    "data_cache_size": len(data_cache.cache),
                    "analytics_cache_size": len(analytics_cache.cache),
                    "data_cache_hits": getattr(data_cache, 'hits', 0),
                    "analytics_cache_hits": getattr(analytics_cache, 'hits', 0)
                },
                "system_stats": {
                    "active_threads": backend_service.executor._threads,
                    "timestamp": time.time()
                }
            }
            
            return JSONResponse(content=stats)
            
        except Exception as e:
            logger.error(f"Error in stats endpoint: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @app.post("/api/v2/cache/clear")
    async def clear_cache():
        """Clear all caches"""
        
        try:
            data_cache.clear()
            analytics_cache.clear()
            
            return JSONResponse(content={
                "message": "All caches cleared successfully",
                "timestamp": time.time()
            })
            
        except Exception as e:
            logger.error(f"Error clearing cache: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

# Function to add helper for analytics service
def add_current_data_helper():
    """Add helper function to analytics module"""
    
    analytics_helper = '''
# Add this to src/analytics.py

_current_clean_data = None

def set_current_clean_data(data: pd.DataFrame):
    """Set the current clean data for caching"""
    global _current_clean_data
    _current_clean_data = data

def get_current_clean_data() -> pd.DataFrame:
    """Get the current clean data"""
    global _current_clean_data
    return _current_clean_data
    '''
    
    return analytics_helper
