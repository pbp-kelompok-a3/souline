def serialize_review(review):
    return {
        'username': review.reviewer.username if review.reviewer else 'Anonymous',
        'location': review.location if hasattr(review, 'location') else 'Unknown',
        'review_text': review.review_text,
        'rating_value': float(review.rating_value),
    }

def serialize_timeline_post_as_review(post):
    location = "Unknown"
    try:
        if hasattr(post.author, 'userprofile') and post.author.userprofile.location:
            location = post.author.userprofile.location
    except:
        pass

    return {
        'username': post.author.username,
        'location': location,
        'review_text': post.text,
        'rating_value': 5.0, 
    }

def serialize_brand_detail(brand, user=None):
    internal_reviews = [serialize_review(r) for r in brand.reviews.all()]

    timeline_posts = brand.posts.all().select_related('author')
    timeline_reviews = [serialize_timeline_post_as_review(p) for p in timeline_posts]

    all_reviews = internal_reviews + timeline_reviews

    data = {
        'id': brand.pk,
        'name': brand.brand_name,
        'description': brand.description,
        'tag': brand.category_tag,
        'thumbnail': brand.thumbnail_url,
        'rating': float(brand.average_rating),
        'link': brand.link,
        'reviews': all_reviews, 
    }
    
    return data

def serialize_brand_list(brands, user=None):
    return [serialize_brand_detail(brand, user) for brand in brands]