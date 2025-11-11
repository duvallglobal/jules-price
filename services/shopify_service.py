import os
import shopify

def push_to_shopify(listing):
    """
    Pushes a listing to Shopify using the Shopify API.
    """
    try:
        shop_url = os.getenv("SHOPIFY_SHOP_URL")
        api_version = os.getenv("SHOPIFY_API_VERSION")
        access_token = os.getenv("SHOPIFY_ACCESS_TOKEN")

        session = shopify.Session(shop_url, api_version, access_token)
        shopify.ShopifyResource.activate_session(session)

        new_product = shopify.Product()
        new_product.title = listing.title
        new_product.body_html = listing.description
        new_product.tags = [tag.name for tag in listing.tags]

        # Add product specifics as metafields if needed, or as variants
        new_product.variants = [
            {
                "price": listing.price,
                "sku": listing.sku,
                "weight": listing.item_weight,
                "weight_unit": "lb"
            }
        ]

        # Add images
        images = []
        for photo in listing.photos:
            with open(photo.original_url, "rb") as f:
                image_data = f.read()
            images.append({"attachment": image_data})
        new_product.images = images

        new_product.save()

        if new_product.errors:
            return {'status': 'error', 'message': new_product.errors.full_messages()}
        else:
            return {'status': 'success', 'shopify_id': new_product.id}

    except Exception as e:
        print(f"Error pushing to Shopify: {e}")
        return {'status': 'error', 'message': str(e)}
