"""
Tests for HTML Parser module.

Requirements: 9.1, 9.2, 9.3, 6.3
"""

import pytest
from pathlib import Path
from scraper.html_parser import HTMLParser


class TestHTMLParser:
    """Test HTMLParser class"""
    
    @pytest.fixture
    def parser(self):
        """Create parser instance"""
        return HTMLParser(selector_config_path="config/selectors.yaml")
    
    def test_parse_valid_html(self, parser):
        """Test parsing valid HTML"""
        html = "<html><body><h1>Test</h1></body></html>"
        soup = parser.parse(html)
        
        assert soup is not None
        assert soup.find('h1').text == 'Test'
    
    def test_parse_empty_html(self, parser):
        """Test parsing empty HTML raises error"""
        with pytest.raises(ValueError, match="HTML content is empty"):
            parser.parse("")
    
    def test_parse_invalid_html(self, parser):
        """Test parsing invalid HTML raises error"""
        with pytest.raises(ValueError):
            parser.parse("   ")
    
    def test_extract_field_with_selector(self, parser):
        """Test extracting field with CSS selector"""
        html = """
        <html>
            <body>
                <h1 class="vehicle-title">Toyota Corolla 2022</h1>
            </body>
        </html>
        """
        soup = parser.parse(html)
        result = parser.extract_field(soup, 'nome')
        
        assert result == "Toyota Corolla 2022"
    
    def test_extract_field_fallback(self, parser):
        """Test selector fallback mechanism"""
        html = """
        <html>
            <body>
                <h1>Toyota Corolla 2022</h1>
            </body>
        </html>
        """
        soup = parser.parse(html)
        # Should fallback to 'h1' selector
        result = parser.extract_field(soup, 'nome')
        
        assert result == "Toyota Corolla 2022"
    
    def test_extract_field_not_found(self, parser):
        """Test extracting non-existent field"""
        html = "<html><body><p>Test</p></body></html>"
        soup = parser.parse(html)
        result = parser.extract_field(soup, 'nome')
        
        assert result is None
    
    def test_extract_images(self, parser):
        """Test extracting multiple images"""
        html = """
        <html>
            <body>
                <div class="vehicle-gallery">
                    <img src="http://example.com/img1.jpg" />
                    <img src="http://example.com/img2.jpg" />
                </div>
            </body>
        </html>
        """
        soup = parser.parse(html)
        result = parser.extract_field(soup, 'imagens', base_url="http://example.com")
        
        assert result is not None
        urls = result.split(',')
        assert len(urls) == 2
        assert "img1.jpg" in urls[0]
        assert "img2.jpg" in urls[1]
    
    def test_extract_vehicle_links(self, parser):
        """Test extracting vehicle links from listing"""
        html = """
        <html>
            <body>
                <a class="vehicle-card" href="/veiculo/1">Car 1</a>
                <a class="vehicle-card" href="/veiculo/2">Car 2</a>
            </body>
        </html>
        """
        urls = parser.extract_vehicle_links(html, "http://example.com")
        
        assert len(urls) == 2
        assert "http://example.com/veiculo/1" in urls
        assert "http://example.com/veiculo/2" in urls
    
    def test_extract_vehicle_links_deduplication(self, parser):
        """Test that duplicate links are removed"""
        html = """
        <html>
            <body>
                <a class="vehicle-card" href="/veiculo/1">Car 1</a>
                <a class="vehicle-card" href="/veiculo/1">Car 1 Again</a>
            </body>
        </html>
        """
        urls = parser.extract_vehicle_links(html, "http://example.com")
        
        assert len(urls) == 1
    
    def test_extract_next_page_url(self, parser):
        """Test extracting next page URL"""
        html = """
        <html>
            <body>
                <a class="next-page" href="/page/2">Next</a>
            </body>
        </html>
        """
        url = parser.extract_next_page_url(html, "http://example.com")
        
        assert url == "http://example.com/page/2"
    
    def test_extract_next_page_not_found(self, parser):
        """Test when no next page exists"""
        html = "<html><body><p>Last page</p></body></html>"
        url = parser.extract_next_page_url(html, "http://example.com")
        
        assert url is None
    
    def test_extract_vehicle_complete(self, parser):
        """Test extracting complete vehicle data"""
        html = """
        <html>
            <body>
                <h1 class="vehicle-title">Toyota Corolla GLi</h1>
                <span class="vehicle-price">R$ 95.990,00</span>
                <span class="vehicle-year">2022</span>
                <span class="vehicle-km">45.000 km</span>
                <span class="vehicle-fuel">Flex</span>
                <span class="vehicle-transmission">Automático CVT</span>
                <span class="vehicle-category">Sedan</span>
            </body>
        </html>
        """
        data = parser.extract_vehicle(html, "http://example.com/car/1")
        
        assert 'nome' in data
        assert 'preco' in data
        assert 'ano' in data
        assert 'url_original' in data
        assert data['url_original'] == "http://example.com/car/1"
    
    def test_selector_stats_tracking(self, parser):
        """Test that selector usage is tracked"""
        html = "<h1>Test</h1>"
        soup = parser.parse(html)
        
        # Extract field multiple times
        parser.extract_field(soup, 'nome')
        parser.extract_field(soup, 'nome')
        
        stats = parser.get_selector_stats()
        assert 'nome' in stats
        assert any('h1' in key for key in stats['nome'].keys())
