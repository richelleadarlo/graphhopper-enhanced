from graphhopper_enhanced import format_duration, format_distance


def test_format_duration():
    assert format_duration(0) == "00:00:00"
    assert format_duration(1000) == "00:00:01"
    assert format_duration(61000) == "00:01:01"
    assert format_duration(3661000) == "01:01:01"


def test_format_distance_km():
    assert format_distance(1000, "km") == "1.00 km"
    assert format_distance(5500, "km") == "5.50 km"


def test_format_distance_miles():
    # 1 km = ~0.6211 miles, so 1000 m = ~0.62 miles
    out = format_distance(1000, "miles")
    assert out.endswith("miles")
    assert float(out.split()[0]) > 0.5
    assert float(out.split()[0]) < 1.0
