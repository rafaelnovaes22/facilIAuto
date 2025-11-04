"""
Validation script for HTML Parser and Extractors.

This script validates the HTML parser implementation without using pytest.
"""

import sys
from pathlib import Path

# Add scraper to path
sys.path.insert(0, str(Path(__file__).parent))

from scraper.html_parser import HTMLParser
from scraper.extractors import FieldExtractor


def test_html_parser():
    """Test HTMLParser functionality"""
    print("Testing HTMLParser...")
    
    parser = HTMLParser(selector_config_path="config/selectors.yaml")
    
    # Test initialization
    assert parser.selectors is not None
    print("  ✓ Initialization successful")
    
    # Test parse valid HTML
    html = "<html><body><h1>Test</h1></body></html>"
    soup = parser.parse(html)
    assert soup is not None
    assert soup.find('h1').text == 'Test'
    print("  ✓ Parse valid HTML")
    
    # Test parse empty HTML
    try:
        parser.parse("")
        assert False, "Should raise ValueError"
    except ValueError:
        print("  ✓ Parse empty HTML raises error")
    
    # Test extract field with selector
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
    print("  ✓ Extract field with selector")
    
    # Test extract field fallback
    html = """
    <html>
        <body>
            <h1>Toyota Corolla 2022</h1>
        </body>
    </html>
    """
    soup = parser.parse(html)
    result = parser.extract_field(soup, 'nome')
    assert result == "Toyota Corolla 2022"
    print("  ✓ Extract field with fallback")
    
    # Test extract field not found
    html = "<html><body><p>Test</p></body></html>"
    soup = parser.parse(html)
    result = parser.extract_field(soup, 'nome')
    assert result is None
    print("  ✓ Extract field not found returns None")
    
    # Test extract images
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
    print("  ✓ Extract multiple images")
    
    # Test extract vehicle links
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
    print("  ✓ Extract vehicle links")
    
    # Test extract vehicle links deduplication
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
    print("  ✓ Extract vehicle links with deduplication")
    
    # Test extract next page URL
    html = """
    <html>
        <body>
            <a class="next-page" href="/page/2">Next</a>
        </body>
    </html>
    """
    url = parser.extract_next_page_url(html, "http://example.com")
    assert url == "http://example.com/page/2"
    print("  ✓ Extract next page URL")
    
    # Test extract next page not found
    html = "<html><body><p>Last page</p></body></html>"
    url = parser.extract_next_page_url(html, "http://example.com")
    assert url is None
    print("  ✓ Extract next page not found returns None")
    
    # Test extract vehicle complete
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
    print("  ✓ Extract complete vehicle data")
    
    # Test selector stats tracking
    stats = parser.get_selector_stats()
    assert isinstance(stats, dict)
    print("  ✓ Selector stats tracking")
    
    print("✅ HTMLParser tests passed\n")


def test_field_extractor():
    """Test FieldExtractor functionality"""
    print("Testing FieldExtractor...")
    
    extractor = FieldExtractor(selector_config_path="config/selectors.yaml")
    
    # Test initialization
    assert extractor.config is not None
    print("  ✓ Initialization successful")
    
    # Test extract price Brazilian format
    assert extractor.extract_price("R$ 95.990,00") == 95990.0
    assert extractor.extract_price("R$ 125.000,00") == 125000.0
    assert extractor.extract_price("Preço: R$ 89.900") == 89900.0
    print("  ✓ Extract price Brazilian format")
    
    # Test extract price simple format
    assert extractor.extract_price("95990") == 95990.0
    assert extractor.extract_price("125000") == 125000.0
    print("  ✓ Extract price simple format")
    
    # Test extract price invalid
    assert extractor.extract_price("") is None
    assert extractor.extract_price("abc") is None
    assert extractor.extract_price("R$ 5.000") is None  # Too low
    assert extractor.extract_price("R$ 600.000") is None  # Too high
    print("  ✓ Extract price invalid returns None")
    
    # Test extract km various formats
    assert extractor.extract_km("50.000 km") == 50000
    assert extractor.extract_km("50000") == 50000
    assert extractor.extract_km("KM: 45.000") == 45000
    assert extractor.extract_km("45.000 quilômetros") == 45000
    print("  ✓ Extract km various formats")
    
    # Test extract km invalid
    assert extractor.extract_km("") is None
    assert extractor.extract_km("abc") is None
    assert extractor.extract_km("600.000 km") is None  # Too high
    print("  ✓ Extract km invalid returns None")
    
    # Test extract year single
    assert extractor.extract_year("2022") == 2022
    assert extractor.extract_year("Ano: 2023") == 2023
    print("  ✓ Extract year single format")
    
    # Test extract year double format
    assert extractor.extract_year("2022/2023") == 2023  # Model year
    assert extractor.extract_year("2021/2022") == 2022
    print("  ✓ Extract year double format")
    
    # Test extract year invalid
    assert extractor.extract_year("") is None
    assert extractor.extract_year("abc") is None
    assert extractor.extract_year("2009") is None  # Too old
    assert extractor.extract_year("2027") is None  # Too new
    print("  ✓ Extract year invalid returns None")
    
    # Test extract doors
    assert extractor.extract_doors("4 portas") == 4
    assert extractor.extract_doors("Portas: 2") == 2
    assert extractor.extract_doors("5") == 5
    print("  ✓ Extract doors")
    
    # Test extract doors invalid
    assert extractor.extract_doors("") is None
    assert extractor.extract_doors("abc") is None
    assert extractor.extract_doors("10 portas") is None  # Out of range
    print("  ✓ Extract doors invalid returns None")
    
    # Test normalize cambio
    assert extractor.normalize_cambio("manual") == "Manual"
    assert extractor.normalize_cambio("Automático") == "Automático"
    assert extractor.normalize_cambio("automático cvt") == "Automático CVT"
    assert extractor.normalize_cambio("CVT") == "Automático CVT"
    assert extractor.normalize_cambio("automatizada") == "Automatizada"
    assert extractor.normalize_cambio("AMT") == "Automatizada"
    print("  ✓ Normalize cambio")
    
    # Test normalize cambio invalid
    assert extractor.normalize_cambio("") is None
    assert extractor.normalize_cambio("unknown") is None
    print("  ✓ Normalize cambio invalid returns None")
    
    # Test normalize combustivel
    assert extractor.normalize_combustivel("flex") == "Flex"
    assert extractor.normalize_combustivel("Flexível") == "Flex"
    assert extractor.normalize_combustivel("gasolina") == "Gasolina"
    assert extractor.normalize_combustivel("diesel") == "Diesel"
    assert extractor.normalize_combustivel("elétrico") == "Elétrico"
    assert extractor.normalize_combustivel("híbrido") == "Híbrido"
    print("  ✓ Normalize combustivel")
    
    # Test normalize combustivel invalid
    assert extractor.normalize_combustivel("") is None
    assert extractor.normalize_combustivel("unknown") is None
    print("  ✓ Normalize combustivel invalid returns None")
    
    # Test normalize categoria
    assert extractor.normalize_categoria("hatch") == "Hatch"
    assert extractor.normalize_categoria("Hatchback") == "Hatch"
    assert extractor.normalize_categoria("sedan") == "Sedan"
    assert extractor.normalize_categoria("Sedã") == "Sedan"
    assert extractor.normalize_categoria("SUV") == "SUV"
    assert extractor.normalize_categoria("pickup") == "Pickup"
    assert extractor.normalize_categoria("Picape") == "Pickup"
    assert extractor.normalize_categoria("van") == "Van"
    print("  ✓ Normalize categoria")
    
    # Test normalize categoria invalid
    assert extractor.normalize_categoria("") is None
    assert extractor.normalize_categoria("unknown") is None
    print("  ✓ Normalize categoria invalid returns None")
    
    # Test validate images
    urls = [
        "http://example.com/img1.jpg",
        "https://example.com/img2.png",
        "invalid-url",
        "",
        "http://example.com/img1.jpg",  # Duplicate
    ]
    valid = extractor.validate_images(urls)
    assert len(valid) == 2  # Only 2 unique valid URLs
    assert "http://example.com/img1.jpg" in valid
    assert "https://example.com/img2.png" in valid
    print("  ✓ Validate images")
    
    # Test validate images empty
    assert extractor.validate_images([]) == []
    assert extractor.validate_images(None) == []
    print("  ✓ Validate images empty returns empty list")
    
    # Test extract and normalize complete
    raw_data = {
        'nome': 'Toyota Corolla GLi',
        'preco': 'R$ 95.990,00',
        'ano': '2022/2023',
        'quilometragem': '45.000 km',
        'cambio': 'automático cvt',
        'combustivel': 'flex',
        'categoria': 'sedan',
        'portas': '4 portas',
        'imagens': ['http://example.com/img1.jpg', 'http://example.com/img2.jpg'],
        'url_original': 'http://example.com/car/1'
    }
    normalized = extractor.extract_and_normalize(raw_data)
    assert normalized['nome'] == 'Toyota Corolla GLi'
    assert normalized['preco'] == 95990.0
    assert normalized['ano'] == 2023
    assert normalized['quilometragem'] == 45000
    assert normalized['cambio'] == 'Automático CVT'
    assert normalized['combustivel'] == 'Flex'
    assert normalized['categoria'] == 'Sedan'
    assert normalized['portas'] == 4
    assert len(normalized['imagens']) == 2
    assert normalized['url_original'] == 'http://example.com/car/1'
    print("  ✓ Extract and normalize complete data")
    
    # Test extract and normalize partial
    raw_data = {
        'nome': 'Toyota Corolla',
        'preco': 'R$ 95.990,00',
        'ano': '2022',
    }
    normalized = extractor.extract_and_normalize(raw_data)
    assert 'nome' in normalized
    assert 'preco' in normalized
    assert 'ano' in normalized
    assert 'quilometragem' not in normalized
    assert 'cambio' not in normalized
    print("  ✓ Extract and normalize partial data")
    
    print("✅ FieldExtractor tests passed\n")


def main():
    """Run all validation tests"""
    print("=" * 60)
    print("HTML Parser and Extractors Validation")
    print("=" * 60 + "\n")
    
    try:
        test_html_parser()
        test_field_extractor()
        
        print("=" * 60)
        print("✅ ALL TESTS PASSED")
        print("=" * 60)
        return 0
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
