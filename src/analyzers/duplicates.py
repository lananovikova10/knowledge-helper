"""Duplicate detection analyzer for finding similar/duplicate articles"""

from __future__ import annotations
from typing import List, Tuple, Optional, Callable, TYPE_CHECKING
from datetime import datetime
from dataclasses import dataclass
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import os

from ..api.client import YouTrackClient
from ..models.article import Article

try:
    from rapidfuzz import fuzz
    RAPIDFUZZ_AVAILABLE = True
except ImportError:
    RAPIDFUZZ_AVAILABLE = False
    print("Warning: rapidfuzz not installed. Fuzzy matching will be limited.")

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    print("Warning: scikit-learn not installed. Content similarity will be limited.")


def _compare_article_chunk(
    article1: Article,
    other_articles: List[Article],
    words1: set,
    other_word_sets: List[set],
    title_weight: float,
    content_weight: float
) -> List[DuplicatePair]:
    """
    Compare one article against a chunk of other articles (for parallel processing)

    This function must be at module level for ProcessPoolExecutor to pickle it.

    Args:
        article1: Article to compare
        other_articles: List of articles to compare against
        words1: Pre-computed word set for article1's title
        other_word_sets: Pre-computed word sets for other articles' titles
        title_weight: Weight for title similarity
        content_weight: Weight for content similarity

    Returns:
        List of DuplicatePair objects found
    """
    pairs = []

    for idx, article2 in enumerate(other_articles):
        words2 = other_word_sets[idx]

        # Quick filter: if titles share less than 30% words, skip
        overlap = len(words1 & words2)
        min_words = min(len(words1), len(words2))

        if min_words > 0 and overlap / min_words < 0.3:
            continue

        # Calculate title similarity
        title_sim = _calculate_title_similarity_static(article1.summary, article2.summary)

        if title_sim < 0.4:
            continue

        # Calculate content similarity
        content_sim = _calculate_content_similarity_static(article1.summary, article2.summary)

        # Calculate overall confidence
        confidence = title_weight * title_sim + content_weight * content_sim

        if confidence >= 0.3:
            reasons = []
            if title_sim > 0.9:
                reasons.append("Very similar titles")
            elif title_sim > 0.7:
                reasons.append("Similar titles")

            if content_sim > 0.8:
                reasons.append("Very similar content")
            elif content_sim > 0.5:
                reasons.append("Similar content")

            pair = DuplicatePair(
                article1=article1,
                article2=article2,
                confidence_score=confidence,
                title_similarity=title_sim,
                content_similarity=content_sim,
                reasons=reasons if reasons else ["Low similarity"]
            )
            pairs.append(pair)

    return pairs


def _calculate_title_similarity_static(title1: str, title2: str) -> float:
    """Static version of title similarity for parallel processing"""
    title1 = title1.lower().strip()
    title2 = title2.lower().strip()

    if title1 == title2:
        return 1.0

    if RAPIDFUZZ_AVAILABLE:
        similarity = fuzz.token_sort_ratio(title1, title2) / 100.0
        return similarity
    else:
        # Fallback: word overlap
        words1 = set(title1.split())
        words2 = set(title2.split())
        if words1 and words2:
            overlap = len(words1 & words2) / max(len(words1), len(words2))
            return overlap
        return 0.0


def _calculate_content_similarity_static(text1: str, text2: str) -> float:
    """Static version of content similarity for parallel processing"""
    if not SKLEARN_AVAILABLE:
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        if words1 and words2:
            overlap = len(words1 & words2) / max(len(words1), len(words2))
            return overlap
        return 0.0

    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.metrics.pairwise import cosine_similarity

        texts = [text1, text2]
        vectorizer = TfidfVectorizer(lowercase=True, stop_words='english', ngram_range=(1, 2))
        tfidf_matrix = vectorizer.fit_transform(texts)
        similarity_matrix = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
        return float(similarity_matrix[0][0])
    except Exception:
        return 0.0


@dataclass
class DuplicatePair:
    """Represents a potential duplicate article pair"""

    article1: Article
    article2: Article
    confidence_score: float  # 0.0 to 1.0
    title_similarity: float
    content_similarity: float
    reasons: List[str]  # List of reasons why these might be duplicates

    def __str__(self):
        return (f"Duplicate Pair (confidence: {self.confidence_score:.2%})\n"
                f"  Article 1: {self.article1.id} - {self.article1.summary}\n"
                f"  Article 2: {self.article2.id} - {self.article2.summary}\n"
                f"  Reasons: {', '.join(self.reasons)}")


@dataclass
class DuplicateReport:
    """Report of duplicate detection analysis"""

    project_id: str
    total_articles: int
    duplicate_pairs: List[DuplicatePair]
    confidence_threshold: float
    generated_at: datetime

    @property
    def duplicate_count(self) -> int:
        """Number of duplicate pairs found"""
        return len(self.duplicate_pairs)

    @property
    def articles_with_duplicates(self) -> int:
        """Number of unique articles that have duplicates"""
        unique_articles = set()
        for pair in self.duplicate_pairs:
            unique_articles.add(pair.article1.id)
            unique_articles.add(pair.article2.id)
        return len(unique_articles)

    def get_sorted_pairs(self, sort_by: str = 'confidence') -> List[DuplicatePair]:
        """
        Get duplicate pairs sorted by specified field

        Args:
            sort_by: Field to sort by ('confidence', 'title', 'content')

        Returns:
            Sorted list of duplicate pairs
        """
        if sort_by == 'title':
            return sorted(self.duplicate_pairs, key=lambda p: p.title_similarity, reverse=True)
        elif sort_by == 'content':
            return sorted(self.duplicate_pairs, key=lambda p: p.content_similarity, reverse=True)
        else:  # confidence or default
            return sorted(self.duplicate_pairs, key=lambda p: p.confidence_score, reverse=True)

    def __str__(self):
        """Human-readable string representation"""
        return (f"Duplicate Detection Report for {self.project_id}\n"
                f"Total articles: {self.total_articles}\n"
                f"Duplicate pairs: {self.duplicate_count}\n"
                f"Articles with duplicates: {self.articles_with_duplicates}\n"
                f"Confidence threshold: {self.confidence_threshold:.0%}")


class DuplicateDetector:
    """Analyzer for detecting duplicate or similar articles"""

    def __init__(
        self,
        client: YouTrackClient,
        confidence_threshold: float = 0.75,
        title_weight: float = 0.4,
        content_weight: float = 0.6
    ):
        """
        Initialize duplicate detector

        Args:
            client: YouTrack API client
            confidence_threshold: Minimum confidence score to report as duplicate (0.0-1.0)
            title_weight: Weight given to title similarity in overall score
            content_weight: Weight given to content similarity in overall score
        """
        self.client = client
        self.confidence_threshold = confidence_threshold
        self.title_weight = title_weight
        self.content_weight = content_weight

        if not RAPIDFUZZ_AVAILABLE:
            print("⚠️  rapidfuzz not available. Install with: pip install rapidfuzz")

        if not SKLEARN_AVAILABLE:
            print("⚠️  scikit-learn not available. Install with: pip install scikit-learn")

    def analyze(self, project_id: str, batch_size: int = 100) -> DuplicateReport:
        """
        Analyze articles in a project to find duplicates

        Args:
            project_id: YouTrack project ID
            batch_size: Number of articles to fetch per API request

        Returns:
            DuplicateReport containing analysis results
        """
        # Fetch all articles from the project
        print(f"Fetching articles from project '{project_id}'...")
        raw_articles = self.client.get_all_articles(project_id, batch_size=batch_size)

        # Convert to Article objects
        articles = [
            Article.from_api_response(data, project_id=project_id)
            for data in raw_articles
        ]

        print(f"Found {len(articles)} articles. Analyzing for duplicates...")

        # Find duplicate pairs
        duplicate_pairs = self._find_duplicates(articles)

        # Filter by confidence threshold
        duplicate_pairs = [
            pair for pair in duplicate_pairs
            if pair.confidence_score >= self.confidence_threshold
        ]

        # Create report
        report = DuplicateReport(
            project_id=project_id,
            total_articles=len(articles),
            duplicate_pairs=duplicate_pairs,
            confidence_threshold=self.confidence_threshold,
            generated_at=datetime.now()
        )

        return report

    def _find_duplicates(self, articles: List[Article]) -> List[DuplicatePair]:
        """
        Find all duplicate pairs in a list of articles with parallel processing

        Args:
            articles: List of articles to compare

        Returns:
            List of DuplicatePair objects
        """
        duplicate_pairs = []
        n = len(articles)

        print(f"Comparing {n} articles ({n * (n - 1) // 2} pairs)...")

        # For small datasets, use sequential processing
        if n < 50:
            return self._find_duplicates_sequential(articles)

        # For larger datasets, use parallel processing
        return self._find_duplicates_parallel(articles)

    def _find_duplicates_sequential(self, articles: List[Article]) -> List[DuplicatePair]:
        """Sequential duplicate detection with early filtering"""
        duplicate_pairs = []

        # Pre-compute title word sets for fast filtering
        title_word_sets = []
        for article in articles:
            words = set(article.summary.lower().split())
            title_word_sets.append(words)

        # Compare each article with every other article
        for i in range(len(articles)):
            for j in range(i + 1, len(articles)):
                article1 = articles[i]
                article2 = articles[j]

                # Quick filter: if titles share less than 30% words, skip
                words1 = title_word_sets[i]
                words2 = title_word_sets[j]
                overlap = len(words1 & words2)
                min_words = min(len(words1), len(words2))

                if min_words > 0 and overlap / min_words < 0.3:
                    continue  # Skip this pair, too different

                # Calculate similarity scores
                title_sim = self._calculate_title_similarity(article1, article2)

                # Early exit if title similarity is too low
                if title_sim < 0.4:
                    continue

                content_sim = self._calculate_content_similarity(article1, article2)

                # Calculate overall confidence score
                confidence = (
                    self.title_weight * title_sim +
                    self.content_weight * content_sim
                )

                # Determine reasons for similarity
                reasons = []
                if title_sim > 0.9:
                    reasons.append("Very similar titles")
                elif title_sim > 0.7:
                    reasons.append("Similar titles")

                if content_sim > 0.8:
                    reasons.append("Very similar content")
                elif content_sim > 0.5:
                    reasons.append("Similar content")

                # Only create pair if there's some similarity
                if confidence >= 0.3:  # Lower threshold for collecting pairs
                    pair = DuplicatePair(
                        article1=article1,
                        article2=article2,
                        confidence_score=confidence,
                        title_similarity=title_sim,
                        content_similarity=content_sim,
                        reasons=reasons if reasons else ["Low similarity"]
                    )
                    duplicate_pairs.append(pair)

        return duplicate_pairs

    def _find_duplicates_parallel(self, articles: List[Article]) -> List[DuplicatePair]:
        """Parallel duplicate detection using threading (safer for web contexts)"""
        duplicate_pairs = []
        n = len(articles)

        # Pre-compute title word sets
        title_word_sets = []
        for article in articles:
            words = set(article.summary.lower().split())
            title_word_sets.append(words)

        # Create batches of articles to process
        batch_size = max(10, n // 10)  # Process in ~10 batches
        batches = []

        for i in range(0, n, batch_size):
            batch_end = min(i + batch_size, n)
            batches.append((i, batch_end))

        print(f"Processing {len(batches)} batches with threading...")

        # Use thread pool (better for I/O and web contexts)
        max_workers = min(4, len(batches))

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit batch processing tasks
            futures = []
            for batch_start, batch_end in batches:
                future = executor.submit(
                    self._process_article_batch,
                    articles,
                    title_word_sets,
                    batch_start,
                    batch_end
                )
                futures.append(future)

            # Collect results as they complete
            completed = 0
            for future in as_completed(futures):
                try:
                    pairs = future.result()
                    duplicate_pairs.extend(pairs)
                    completed += 1
                    print(f"Completed batch {completed}/{len(batches)}")
                except Exception as e:
                    print(f"Error in batch processing: {e}")

        return duplicate_pairs

    def _process_article_batch(
        self,
        articles: List[Article],
        title_word_sets: List[set],
        batch_start: int,
        batch_end: int
    ) -> List[DuplicatePair]:
        """Process a batch of articles for duplicate detection"""
        pairs = []
        n = len(articles)

        for i in range(batch_start, batch_end):
            article1 = articles[i]
            words1 = title_word_sets[i]

            for j in range(i + 1, n):
                article2 = articles[j]
                words2 = title_word_sets[j]

                # Quick filter
                overlap = len(words1 & words2)
                min_words = min(len(words1), len(words2))

                if min_words > 0 and overlap / min_words < 0.3:
                    continue

                # Calculate similarities
                title_sim = self._calculate_title_similarity(article1, article2)

                if title_sim < 0.4:
                    continue

                content_sim = self._calculate_content_similarity(article1, article2)

                # Calculate confidence
                confidence = (
                    self.title_weight * title_sim +
                    self.content_weight * content_sim
                )

                if confidence >= 0.3:
                    reasons = []
                    if title_sim > 0.9:
                        reasons.append("Very similar titles")
                    elif title_sim > 0.7:
                        reasons.append("Similar titles")

                    if content_sim > 0.8:
                        reasons.append("Very similar content")
                    elif content_sim > 0.5:
                        reasons.append("Similar content")

                    pair = DuplicatePair(
                        article1=article1,
                        article2=article2,
                        confidence_score=confidence,
                        title_similarity=title_sim,
                        content_similarity=content_sim,
                        reasons=reasons if reasons else ["Low similarity"]
                    )
                    pairs.append(pair)

        return pairs

    def _calculate_title_similarity(self, article1: Article, article2: Article) -> float:
        """
        Calculate similarity between two article titles

        Args:
            article1: First article
            article2: Second article

        Returns:
            Similarity score (0.0 to 1.0)
        """
        title1 = article1.summary.lower().strip()
        title2 = article2.summary.lower().strip()

        # Exact match
        if title1 == title2:
            return 1.0

        # Fuzzy matching with rapidfuzz if available
        if RAPIDFUZZ_AVAILABLE:
            # Token sort ratio is good for titles with word reordering
            similarity = fuzz.token_sort_ratio(title1, title2) / 100.0
            return similarity
        else:
            # Fallback: simple substring matching
            if title1 in title2 or title2 in title1:
                return 0.8

            # Word overlap
            words1 = set(title1.split())
            words2 = set(title2.split())
            if words1 and words2:
                overlap = len(words1 & words2) / max(len(words1), len(words2))
                return overlap

            return 0.0

    def _calculate_content_similarity(self, article1: Article, article2: Article) -> float:
        """
        Calculate similarity between article content using TF-IDF and cosine similarity

        Args:
            article1: First article
            article2: Second article

        Returns:
            Similarity score (0.0 to 1.0)
        """
        # For now, we'll use title as a proxy for content since we may not have full text
        # In a full implementation, we'd fetch the article content

        if not SKLEARN_AVAILABLE:
            # Fallback to simple word overlap
            words1 = set(article1.summary.lower().split())
            words2 = set(article2.summary.lower().split())
            if words1 and words2:
                overlap = len(words1 & words2) / max(len(words1), len(words2))
                return overlap
            return 0.0

        try:
            # Use TF-IDF vectorizer for content similarity
            texts = [article1.summary, article2.summary]

            # Create TF-IDF vectors
            vectorizer = TfidfVectorizer(
                lowercase=True,
                stop_words='english',
                ngram_range=(1, 2)  # Use unigrams and bigrams
            )

            tfidf_matrix = vectorizer.fit_transform(texts)

            # Calculate cosine similarity
            similarity_matrix = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])

            return float(similarity_matrix[0][0])

        except Exception as e:
            print(f"Warning: Content similarity calculation failed: {e}")
            return 0.0

    def group_duplicates(self, report: DuplicateReport) -> dict[str, List[Article]]:
        """
        Group articles that are duplicates of each other

        Args:
            report: Duplicate detection report

        Returns:
            Dictionary mapping group ID to list of duplicate articles
        """
        # Build adjacency list of duplicates
        adjacency = defaultdict(set)

        for pair in report.duplicate_pairs:
            adjacency[pair.article1.id].add(pair.article2.id)
            adjacency[pair.article2.id].add(pair.article1.id)

        # Find connected components (groups of duplicates)
        visited = set()
        groups = {}
        group_id = 0

        def dfs(article_id, group):
            if article_id in visited:
                return
            visited.add(article_id)
            group.append(article_id)
            for neighbor in adjacency[article_id]:
                dfs(neighbor, group)

        for article_id in adjacency.keys():
            if article_id not in visited:
                group = []
                dfs(article_id, group)
                if len(group) > 1:
                    groups[f"group_{group_id}"] = group
                    group_id += 1

        return groups
