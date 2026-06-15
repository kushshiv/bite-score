CATEGORY_COVER_IMAGES: dict[str, str] = {
    "indian": "https://images.unsplash.com/photo-1585937421612-70a008296f36?w=800&h=500&fit=crop",
    "italian": "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?w=800&h=500&fit=crop",
    "street-food": "https://images.unsplash.com/photo-1567620905732-2d1ec7ab7440?w=800&h=500&fit=crop",
    "healthy": "https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=800&h=500&fit=crop",
    "cafe": "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=800&h=500&fit=crop",
    "bakery": "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=800&h=500&fit=crop",
    "asian-fusion": "https://images.unsplash.com/photo-1569718211065-1ea9108a2bda?w=800&h=500&fit=crop",
    "mexican": "https://images.unsplash.com/photo-1565299585323-38d6b0865b47?w=800&h=500&fit=crop",
    "mediterranean": "https://images.unsplash.com/photo-1540189549336-e6e99c3679fe?w=800&h=500&fit=crop",
    "fast-casual": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=800&h=500&fit=crop",
}

DEFAULT_COVER_IMAGE = "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?w=800&h=500&fit=crop"


def cover_for_category(slug: str | None) -> str:
    if slug and slug in CATEGORY_COVER_IMAGES:
        return CATEGORY_COVER_IMAGES[slug]
    return DEFAULT_COVER_IMAGE
