from explore_solution.explore_visitor import generate_search_points


def test_generate_search_points_has_dense_arena_coverage():
    points = generate_search_points()

    assert len(points) >= 24
    assert len(set(points)) == len(points)
    assert max(x for x, _ in points) > 4.0
    assert min(x for x, _ in points) >= 0.5
    assert max(y for _, y in points) <= 2.5
    assert min(y for _, y in points) >= -2.5
    assert all(abs(y) <= 2.5 for _, y in points)
    assert all(0.5 <= x <= 5.5 for x, _ in points)
