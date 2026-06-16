from app.services.business_query import business_to_list_item, businesses_in_area
from app.services.covers import cover_for_category


def test_business_to_list_item_includes_cover_and_scores(
    db_session, sample_business, sample_review
):
    item = business_to_list_item(db_session, sample_business)
    assert item.slug == "test-kitchen"
    assert item.review_count == 1
    assert item.overall_percent > 0
    assert item.cover_image_url is None


def test_business_to_list_item_with_cover_image(db_session, sample_business):
    sample_business.cover_image_url = cover_for_category("indian")
    db_session.commit()
    db_session.refresh(sample_business)

    item = business_to_list_item(db_session, sample_business)
    assert item.cover_image_url == cover_for_category("indian")


def test_businesses_in_area_filters_by_radius(db_session, geo_businesses):
    items = businesses_in_area(
        db_session,
        city="Berlin",
        near_lat=52.52,
        near_lng=13.405,
        radius_km=5,
    )
    slugs = {item.slug for item in items}
    assert slugs == {"near-kitchen", "mid-kitchen"}
    assert all(item.distance_km is not None for item in items)


def test_businesses_in_area_without_geo_returns_all_in_city(db_session, geo_businesses):
    items = businesses_in_area(db_session, city="Berlin")
    assert len(items) == 3
    assert all(item.distance_km is None for item in items)


def test_businesses_in_area_excludes_missing_coordinates(db_session, geo_businesses):
    from app.models.business import Business
    from app.models.category import Category
    from app.models.enums import BusinessType
    from app.models.location import Location

    category = Category(name="No Geo", slug="no-geo")
    db_session.add(category)
    db_session.flush()
    business = Business(
        name="No Coords",
        slug="no-coords",
        category_id=category.id,
        business_type=BusinessType.RESTAURANT,
    )
    db_session.add(business)
    db_session.flush()
    db_session.add(
        Location(
            business_id=business.id,
            address="Unknown",
            city="Berlin",
            country="Germany",
        )
    )
    db_session.commit()

    items = businesses_in_area(
        db_session,
        city="Berlin",
        near_lat=52.52,
        near_lng=13.405,
    )
    assert len(items) == 3
    assert all(item.slug != "no-coords" for item in items)
