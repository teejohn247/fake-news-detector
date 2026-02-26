import re

class HeuristicDetector:
    """
    Rule-based fake news detection.
    Each 'yes' (good sign) adds points. High score = likely REAL. Low score = likely FAKE.
    Criteria: Too many CAPS? Emotional words? Trusted source? Factual statement?
    """
    # User-friendly criterion labels for display
    CRITERION_LABELS = {
        'excessive_caps': 'Too many CAPITAL LETTERS?',
        'emotional_words': 'Emotional words (SHOCKING!!!)?',
        'trusted_source': 'Mentions trusted source (BBC, Reuters)?',
        'factual_pattern': 'Simple factual statement?',
        'excessive_punctuation': 'Excessive punctuation (!!!???)?',
    }

    def __init__(self):
        """Initialize rule-based detector with trusted sources"""
        self.trusted_sources = [
            'bbc.com', 'reuters.com', 'apnews.com', 'nytimes.com',
            'theguardian.com', 'washingtonpost.com', 'cnn.com',
            'npr.org', 'politifact.com', 'snopes.com', 'factcheck.org',
            'bbc', 'reuters', 'associated press', 'ap news'
        ]
        self.sensational_emotional_words = [
            'shocking', 'unbelievable', 'amazing', 'incredible', 'outrageous',
            'scandal', 'bombshell', 'explosive', 'stunning', 'breaking',
            'urgent', 'alert', 'danger', 'exposed', 'revealed',
            'hate', 'furious', 'terrified', 'horrified', 'disgusted',
            'ecstatic', 'devastated', 'outraged', 'warning'
        ]
        print("✓ Heuristic detector initialized")

    def check_excessive_caps(self, text):
        """Too many CAPITAL LETTERS? Yes = penalize"""
        if len(text) == 0:
            return 0
        caps_ratio = sum(1 for c in text if c.isupper()) / len(text)
        if caps_ratio > 0.25:
            return -2
        elif caps_ratio > 0.15:
            return -1
        return 0

    def check_emotional_words(self, text):
        """Emotional words like SHOCKING!!!? Yes = penalize. Uses whole-word matching."""
        text_lower = text.lower()
        count = 0
        for w in self.sensational_emotional_words:
            if re.search(r'\b' + re.escape(w) + r'\b', text_lower):
                count += 1
        if count >= 4:
            return -3
        elif count >= 2:
            return -2
        elif count >= 1:
            return -1
        return 0

    def check_trusted_source(self, text, source_url=None):
        """Trusted source (BBC, Reuters)? Yes = add points. Can check text or provided source_url."""
        text_lower = (text or '').lower()
        count = sum(1 for s in self.trusted_sources if s in text_lower)
        if source_url:
            url_lower = source_url.lower()
            url_count = sum(1 for s in self.trusted_sources if s in url_lower)
            count = max(count, url_count)
        if count >= 2:
            return 2
        elif count >= 1:
            return 1
        return 0

    def check_factual_pattern(self, text):
        """
        Simple factual statement? (e.g. "Nigeria is an African country")
        Short, neutral, declarative = add points. Avoids false positives on facts.
        """
        text_clean = text.strip()
        if len(text_clean) < 15:
            return 0
        text_lower = text_clean.lower()
        # Factual patterns: "X is a/an Y", "X is the", "X are"
        factual_patterns = [
            r'\bis\s+(?:a|an|the)\s+',  # "is a", "is an", "is the"
            r'\bare\s+(?:a|an|the)\s+',
            r'\b(?:located|situated)\s+in\b',
            r'\b(?:country|continent|capital|city)\b',
            r'\b(?:percent|%\s*of)\b',
        ]
        has_factual = any(re.search(p, text_lower) for p in factual_patterns)
        # No sensational words, no excessive punctuation
        has_bad = any(w in text_lower for w in self.sensational_emotional_words[:15])
        has_excessive = '!!!' in text or '???' in text or text.count('!') > 2
        if has_factual and not has_bad and not has_excessive:
            # Short factual statement (like "Nigeria is an African country")
            words = len(text_clean.split())
            if words <= 15:
                return 2
            elif words <= 50:
                return 1
        return 0

    def check_excessive_punctuation(self, text):
        """Excessive punctuation (!!!???)? Yes = penalize"""
        score = 0
        if '!!!' in text or '???' in text:
            score -= 2
        elif text.count('!') > 3 or text.count('?') > 3:
            score -= 1
        return score

    def predict(self, text, source_url=None):
        """
        Predict if news is REAL or FAKE.
        High score = likely real. Low score = likely fake.
        source_url: optional URL where article was found (e.g. theguardian.com/...) for trusted source check
        """
        try:
            details = {
                'excessive_caps': self.check_excessive_caps(text),
                'emotional_words': self.check_emotional_words(text),
                'trusted_source': self.check_trusted_source(text, source_url),
                'factual_pattern': self.check_factual_pattern(text),
                'excessive_punctuation': self.check_excessive_punctuation(text),
            }
            score = sum(details.values())

            if score >= 0:
                label = 'REAL'
                confidence = min(0.5 + (score * 0.12), 0.95)
            else:
                label = 'FAKE'
                confidence = min(0.5 + (abs(score) * 0.1), 0.95)

            return {
                'label': label,
                'confidence': round(confidence, 4),
                'score': score,
                'details': details,
                'details_labels': self.CRITERION_LABELS,
                'method': 'Heuristic Rules'
            }
        except Exception as e:
            print(f"Error in heuristic prediction: {e}")
            return {
                'label': 'ERROR',
                'confidence': 0.0,
                'score': 0,
                'details': {},
                'details_labels': {},
                'error': str(e)
            }
