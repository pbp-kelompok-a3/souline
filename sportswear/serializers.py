def serialize_review(review):
    return {
        'username': review.reviewer.username if review.reviewer else 'Anonymous',
        'location': review.location,
        'review_text': review.review_text,
        'rating_value': float(review.rating_value),
    }

def serialize_brand_detail(brand, user=None):
    data = {
        'id': brand.pk,
        'name': brand.brand_name,
        'description': brand.description,
        'tag': brand.category_tag,
        'thumbnail': brand.thumbnail_url,
        'rating': float(brand.average_rating),
        'link': brand.link,
        'reviews': [serialize_review(r) for r in brand.reviews.all()],
    }

    if user and user.is_authenticated and user.is_staff:
        data['admin_notes'] = brand.admin_notes
    
    return data

def serialize_brand_list(brands, user=None):
    return [serialize_brand_detail(brand, user) for brand in brands]