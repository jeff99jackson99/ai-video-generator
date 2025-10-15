"""Tests for service modules."""

import pytest
from pathlib import Path
from src.services.script_enhancer import ScriptEnhancer
from src.services.caption_generator import CaptionGenerator


def test_script_enhancer_basic():
    """Test basic script enhancement without API keys."""
    enhancer = ScriptEnhancer()
    script = "This is a test video about artificial intelligence."
    
    # Test basic enhancement (no API keys)
    result = enhancer._basic_enhancement(script)
    
    assert "enhanced_script" in result
    assert "scenes" in result
    assert "keywords" in result
    assert len(result["scenes"]) > 0


def test_script_enhancer_keywords():
    """Test keyword extraction."""
    enhancer = ScriptEnhancer()
    text = "Artificial intelligence and machine learning are transforming technology."
    
    keywords = enhancer.extract_keywords(text)
    
    assert isinstance(keywords, list)
    assert len(keywords) > 0


def test_caption_generator_srt_time():
    """Test SRT time formatting."""
    generator = CaptionGenerator()
    
    time_str = generator._format_srt_time(65.5)
    assert time_str == "00:01:05,500"
    
    time_str = generator._format_srt_time(3661.123)
    assert time_str == "01:01:01,123"


def test_caption_generator_style_config():
    """Test caption style configurations."""
    generator = CaptionGenerator()
    
    modern_style = generator.get_caption_style_config("modern")
    assert modern_style["fontsize"] == 70
    assert modern_style["color"] == "white"
    
    classic_style = generator.get_caption_style_config("classic")
    assert classic_style["color"] == "yellow"


@pytest.mark.asyncio
async def test_caption_from_script():
    """Test caption generation from script."""
    generator = CaptionGenerator()
    
    script = "Hello world. This is a test."
    scenes = [
        {"text": "Hello world.", "audio_start": 0, "audio_end": 2},
        {"text": "This is a test.", "audio_start": 2, "audio_end": 4}
    ]
    
    captions = await generator.generate_captions_from_script(script, scenes, 4.0)
    
    assert len(captions) > 0
    assert captions[0]["start_time"] >= 0
    assert "text" in captions[0]

