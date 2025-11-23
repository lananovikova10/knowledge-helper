"""YouTrack API client for fetching article data"""

import requests
from typing import List, Dict, Any, Optional
from datetime import datetime


class YouTrackAPIError(Exception):
    """Custom exception for YouTrack API errors"""
    pass


class YouTrackClient:
    """Client for interacting with YouTrack API (documented and undocumented endpoints)"""

    def __init__(self, base_url: str, token: str):
        """
        Initialize YouTrack API client

        Args:
            base_url: Base URL of YouTrack instance. Can be:
                - Standalone/InCloud: https://youtrack.example.com
                - Cloud (default): https://example.youtrack.cloud
                - Cloud (MyJetBrains): https://example.myjetbrains.com/youtrack
            token: API authentication token
        """
        self.base_url = self._normalize_base_url(base_url)
        self.token = token
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        })

    def _normalize_base_url(self, base_url: str) -> str:
        """
        Normalize the base URL to ensure it ends with /api

        Args:
            base_url: Raw base URL from configuration

        Returns:
            Normalized URL ending with /api
        """
        url = base_url.rstrip('/')

        # If URL already ends with /api, return as is
        if url.endswith('/api'):
            return url

        # Otherwise append /api
        return f"{url}/api"

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[Any, Any]:
        """
        Make HTTP request to YouTrack API

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint path
            **kwargs: Additional arguments for requests

        Returns:
            JSON response data

        Raises:
            YouTrackAPIError: If request fails
        """
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            raise YouTrackAPIError(f"HTTP {e.response.status_code}: {e.response.text}")
        except requests.exceptions.RequestException as e:
            raise YouTrackAPIError(f"Request failed: {str(e)}")
        except ValueError as e:
            raise YouTrackAPIError(f"Invalid JSON response: {str(e)}")

    def get_articles(self, project_id: str, top: int = 100, skip: int = 0) -> List[Dict[str, Any]]:
        """
        Get articles from a KB project using undocumented API

        This endpoint provides article metadata including view counts and creation dates.

        Args:
            project_id: YouTrack project ID
            top: Maximum number of articles to fetch (pagination)
            skip: Number of articles to skip (pagination)

        Returns:
            List of article dictionaries with fields: id, created, summary, viewCounters
        """
        # Using the undocumented API endpoint with view counters
        fields = "id,created,summary,updated,viewCounters(views(created))"
        endpoint = f"/admin/projects/{project_id}/articles"
        params = {
            "$top": top,
            "$skip": skip,
            "fields": fields
        }

        try:
            response = self._make_request("GET", endpoint, params=params)
            return response if isinstance(response, list) else []
        except YouTrackAPIError as e:
            print(f"Warning: Failed to fetch articles: {e}")
            return []

    def get_all_articles(self, project_id: str, batch_size: int = 100) -> List[Dict[str, Any]]:
        """
        Fetch all articles from a KB project using pagination

        Args:
            project_id: YouTrack project ID
            batch_size: Number of articles to fetch per request

        Returns:
            List of all articles in the project
        """
        all_articles = []
        skip = 0

        while True:
            batch = self.get_articles(project_id, top=batch_size, skip=skip)
            if not batch:
                break

            all_articles.extend(batch)
            skip += batch_size

            # If we got fewer articles than batch_size, we've reached the end
            if len(batch) < batch_size:
                break

        return all_articles

    def get_article_by_id(self, project_id: str, article_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific article

        Args:
            project_id: YouTrack project ID
            article_id: Article ID

        Returns:
            Article details or None if not found
        """
        fields = "id,created,updated,summary,content,viewCounters(views(created))"
        endpoint = f"/admin/projects/{project_id}/articles/{article_id}"
        params = {"fields": fields}

        try:
            return self._make_request("GET", endpoint, params=params)
        except YouTrackAPIError:
            return None

    def get_project_info(self, project_id: str) -> Optional[Dict[str, Any]]:
        """
        Get information about a KB project

        Args:
            project_id: YouTrack project ID

        Returns:
            Project information or None if not found
        """
        endpoint = f"/admin/projects/{project_id}"
        params = {"fields": "id,name,shortName"}

        try:
            return self._make_request("GET", endpoint, params=params)
        except YouTrackAPIError:
            return None

    def test_connection(self) -> bool:
        """
        Test if the API connection and authentication are working

        Returns:
            True if connection is successful, False otherwise
        """
        try:
            # Try to fetch projects as a connection test
            # This is a simple endpoint that should work with any valid token
            endpoint = "/admin/projects"
            params = {"fields": "id", "$top": 1}
            self._make_request("GET", endpoint, params=params)
            return True
        except YouTrackAPIError:
            return False
