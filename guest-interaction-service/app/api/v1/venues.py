"""
API endpoints for venue discovery and recommendations.
"""
from fastapi import APIRouter, Query
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

router = APIRouter(prefix="/api/venues", tags=["venues"])


# Pydantic models for venues
class Address(BaseModel):
    street: str
    city: str
    state: str
    zipCode: str
    country: str
    coordinates: Optional[dict] = None

class ContactInfo(BaseModel):
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None

class Venue(BaseModel):
    id: str
    name: str
    type: str  # 'hotel' | 'restaurant' | 'cafe' | 'retail'
    description: str
    address: Address
    contact: ContactInfo
    images: List[str] = []
    rating: float
    reviewCount: int = 0
    priceRange: str = "$$"  # '$' | '$$' | '$$$' | '$$$$'
    amenities: List[str] = []
    openingHours: Optional[dict] = None
    isAvailable: bool = True
    businessId: str
    createdAt: str
    updatedAt: str


class Recommendation(BaseModel):
    id: str
    venueId: str
    venue: Venue
    reason: str
    confidence: float
    category: str


# Mock data (в реальном приложении это будет из базы данных)
# Using Unsplash images for better visualization
MOCK_VENUES = [
    # Hotels
    Venue(
        id="1",
        name="Grand Hotel",
        type="hotel",
        description="Luxury hotel in the city center with stunning views and world-class amenities",
        address=Address(
            street="123 Main St",
            city="New York",
            state="NY",
            zipCode="10001",
            country="USA"
        ),
        contact=ContactInfo(
            phone="+1-212-555-0100",
            email="info@grandhotel.com",
            website="https://grandhotel.com"
        ),
        images=[
            "https://images.unsplash.com/photo-1566073771259-6a8506099945?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=600&q=80",
            "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=600&q=80",
            "https://images.unsplash.com/photo-1611892440504-42a792e24d32?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=600&q=80"
        ],
        rating=4.5,
        reviewCount=234,
        priceRange="$$$$",
        amenities=["WiFi", "Pool", "Spa", "Gym", "Room Service", "Concierge"],
        businessId="biz-1",
        createdAt=datetime.now().isoformat(),
        updatedAt=datetime.now().isoformat()
    ),
    Venue(
        id="4",
        name="Beach Resort",
        type="hotel",
        description="Seaside luxury resort with private beach access and tropical paradise atmosphere",
        address=Address(
            street="101 Ocean Drive",
            city="Miami",
            state="FL",
            zipCode="33139",
            country="USA"
        ),
        contact=ContactInfo(
            phone="+1-305-555-0400",
            email="info@beachresort.com",
            website="https://beachresort.com"
        ),
        images=[
            "https://images.unsplash.com/photo-1520250497591-112f2f6a7b96?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=600&q=80",
            "https://images.unsplash.com/photo-1571896349842-33c89424de2d?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=600&q=80",
            "https://images.unsplash.com/photo-1559827260-dc66d52bef19?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=600&q=80"
        ],
        rating=4.7,
        reviewCount=312,
        priceRange="$$$$",
        amenities=["Beach Access", "Pool", "Spa", "Restaurant", "Bar", "Water Sports"],
        businessId="biz-4",
        createdAt=datetime.now().isoformat(),
        updatedAt=datetime.now().isoformat()
    ),
    Venue(
        id="7",
        name="Mountain View Lodge",
        type="hotel",
        description="Cozy mountain retreat with breathtaking views and rustic charm",
        address=Address(
            street="500 Mountain Road",
            city="Aspen",
            state="CO",
            zipCode="81611",
            country="USA"
        ),
        contact=ContactInfo(
            phone="+1-970-555-0700",
            email="info@mountainviewlodge.com",
            website="https://mountainviewlodge.com"
        ),
        images=[
            "https://images.unsplash.com/photo-1551882547-ec40ba82c093?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=600&q=80",
            "https://images.unsplash.com/photo-1571896349842-33c89424de2d?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=600&q=80",
            "https://images.unsplash.com/photo-1564501049412-61c2a3083791?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=600&q=80"
        ],
        rating=4.6,
        reviewCount=198,
        priceRange="$$$",
        amenities=["Fireplace", "Ski Access", "Hot Tub", "Restaurant", "WiFi"],
        businessId="biz-7",
        createdAt=datetime.now().isoformat(),
        updatedAt=datetime.now().isoformat()
    ),
    # Restaurants
    Venue(
        id="2",
        name="Bella Restaurant",
        type="restaurant",
        description="Authentic Italian fine dining with traditional recipes and elegant atmosphere",
        address=Address(
            street="456 Oak Ave",
            city="New York",
            state="NY",
            zipCode="10002",
            country="USA"
        ),
        contact=ContactInfo(
            phone="+1-212-555-0200",
            email="reservations@bellarestaurant.com",
            website="https://bellarestaurant.com"
        ),
        images=[
            "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=600&q=80",
            "https://images.unsplash.com/photo-1555396273-367ea4eb3db5?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=600&q=80",
            "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=600&q=80"
        ],
        rating=4.8,
        reviewCount=189,
        priceRange="$$$",
        amenities=["Outdoor Seating", "Parking", "WiFi", "Wine Selection", "Reservations"],
        businessId="biz-2",
        createdAt=datetime.now().isoformat(),
        updatedAt=datetime.now().isoformat()
    ),
    Venue(
        id="5",
        name="Sushi Master",
        type="restaurant",
        description="Authentic Japanese cuisine with master chefs and fresh ingredients daily",
        address=Address(
            street="202 Cherry Blvd",
            city="Los Angeles",
            state="CA",
            zipCode="90012",
            country="USA"
        ),
        contact=ContactInfo(
            phone="+1-213-555-0500",
            email="reservations@sushimaster.com",
            website="https://sushimaster.com"
        ),
        images=[
            "https://images.unsplash.com/photo-1579584425555-c3ce17fd4351?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=600&q=80",
            "https://images.unsplash.com/photo-1579952363873-27f3bade9f55?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=600&q=80",
            "https://images.unsplash.com/photo-1579584425555-c3ce17fd4351?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=600&q=80"
        ],
        rating=4.9,
        reviewCount=278,
        priceRange="$$$$",
        amenities=["Parking", "Reservations", "Private Dining", "Sake Bar"],
        businessId="biz-5",
        createdAt=datetime.now().isoformat(),
        updatedAt=datetime.now().isoformat()
    ),
    Venue(
        id="8",
        name="Steakhouse Prime",
        type="restaurant",
        description="Premium steakhouse with dry-aged beef and extensive wine collection",
        address=Address(
            street="789 Broadway",
            city="Chicago",
            state="IL",
            zipCode="60611",
            country="USA"
        ),
        contact=ContactInfo(
            phone="+1-312-555-0800",
            email="reservations@steakhouseprime.com",
            website="https://steakhouseprime.com"
        ),
        images=[
            "https://images.unsplash.com/photo-1546833999-b9f581a1996d?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=600&q=80",
            "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=600&q=80",
            "https://images.unsplash.com/photo-1555396273-367ea4eb3db5?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=600&q=80"
        ],
        rating=4.7,
        reviewCount=245,
        priceRange="$$$$",
        amenities=["Private Dining", "Wine Cellar", "Valet Parking", "Reservations"],
        businessId="biz-8",
        createdAt=datetime.now().isoformat(),
        updatedAt=datetime.now().isoformat()
    ),
    Venue(
        id="9",
        name="Taco Fiesta",
        type="restaurant",
        description="Vibrant Mexican restaurant with authentic street food and margaritas",
        address=Address(
            street="321 Sunset Blvd",
            city="Los Angeles",
            state="CA",
            zipCode="90028",
            country="USA"
        ),
        contact=ContactInfo(
            phone="+1-323-555-0900",
            email="hello@tacofiesta.com",
            website="https://tacofiesta.com"
        ),
        images=[
            "https://images.unsplash.com/photo-1565299585323-38174c0a5e0e?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=600&q=80",
            "https://images.unsplash.com/photo-1571997478779-1ac61a27d0d0?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=600&q=80",
            "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=600&q=80"
        ],
        rating=4.4,
        reviewCount=167,
        priceRange="$$",
        amenities=["Outdoor Seating", "Bar", "Live Music", "Takeout"],
        businessId="biz-9",
        createdAt=datetime.now().isoformat(),
        updatedAt=datetime.now().isoformat()
    ),
    # Cafes
    Venue(
        id="3",
        name="Coffee Corner",
        type="cafe",
        description="Cozy coffee shop with artisanal roasts and homemade pastries",
        address=Address(
            street="789 Pine Rd",
            city="New York",
            state="NY",
            zipCode="10003",
            country="USA"
        ),
        contact=ContactInfo(
            phone="+1-212-555-0300",
            email="hello@coffeecorner.com"
        ),
        images=[
            "https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=600&q=80",
            "https://images.unsplash.com/photo-1447933601403-0c6688de566e?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=600&q=80",
            "https://images.unsplash.com/photo-1511920170033-f8396924c348?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=600&q=80"
        ],
        rating=4.3,
        reviewCount=156,
        priceRange="$",
        amenities=["WiFi", "Outdoor Seating", "Pastries", "Vegan Options"],
        businessId="biz-3",
        createdAt=datetime.now().isoformat(),
        updatedAt=datetime.now().isoformat()
    ),
    Venue(
        id="6",
        name="Artisan Bakery",
        type="cafe",
        description="Fresh baked goods daily with European-style breads and pastries",
        address=Address(
            street="303 Flour Street",
            city="San Francisco",
            state="CA",
            zipCode="94102",
            country="USA"
        ),
        contact=ContactInfo(
            phone="+1-415-555-0600",
            email="hello@artisanbakery.com"
        ),
        images=[
            "https://images.unsplash.com/photo-1509440159596-0249088772ff?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=600&q=80",
            "https://images.unsplash.com/photo-1555507036-ab1f4038808a?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=600&q=80",
            "https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=600&q=80"
        ],
        rating=4.6,
        reviewCount=142,
        priceRange="$$",
        amenities=["WiFi", "Takeout", "Outdoor Seating", "Gluten-Free Options"],
        businessId="biz-6",
        createdAt=datetime.now().isoformat(),
        updatedAt=datetime.now().isoformat()
    ),
    Venue(
        id="10",
        name="Tea Garden",
        type="cafe",
        description="Peaceful tea house with over 50 varieties of premium teas and light snacks",
        address=Address(
            street="555 Zen Way",
            city="Portland",
            state="OR",
            zipCode="97201",
            country="USA"
        ),
        contact=ContactInfo(
            phone="+1-503-555-1000",
            email="info@teagarden.com",
            website="https://teagarden.com"
        ),
        images=[
            "https://images.unsplash.com/photo-1559056199-641a0ac8b55e?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=600&q=80",
            "https://images.unsplash.com/photo-1544787219-7f47ccb76574?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=600&q=80",
            "https://images.unsplash.com/photo-1559056199-641a0ac8b55e?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=600&q=80"
        ],
        rating=4.5,
        reviewCount=98,
        priceRange="$$",
        amenities=["WiFi", "Quiet Space", "Tea Ceremony", "Vegan Options"],
        businessId="biz-10",
        createdAt=datetime.now().isoformat(),
        updatedAt=datetime.now().isoformat()
    ),
    # Retail
    Venue(
        id="11",
        name="Fashion Boutique",
        type="retail",
        description="Trendy fashion boutique with designer clothing and accessories",
        address=Address(
            street="888 Fashion Ave",
            city="New York",
            state="NY",
            zipCode="10019",
            country="USA"
        ),
        contact=ContactInfo(
            phone="+1-212-555-1100",
            email="info@fashionboutique.com",
            website="https://fashionboutique.com"
        ),
        images=[
            "https://images.unsplash.com/photo-1441986300917-64674bd600d8?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=600&q=80",
            "https://images.unsplash.com/photo-1445205170230-053b83016050?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=600&q=80",
            "https://images.unsplash.com/photo-1556912172-45b7abe8b7e1?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=600&q=80"
        ],
        rating=4.4,
        reviewCount=123,
        priceRange="$$$",
        amenities=["Personal Styling", "Alterations", "Gift Wrapping", "Loyalty Program"],
        businessId="biz-11",
        createdAt=datetime.now().isoformat(),
        updatedAt=datetime.now().isoformat()
    ),
    Venue(
        id="12",
        name="Tech Store Pro",
        type="retail",
        description="Latest electronics and gadgets with expert tech support",
        address=Address(
            street="777 Tech Plaza",
            city="Seattle",
            state="WA",
            zipCode="98101",
            country="USA"
        ),
        contact=ContactInfo(
            phone="+1-206-555-1200",
            email="info@techstorepro.com",
            website="https://techstorepro.com"
        ),
        images=[
            "https://images.unsplash.com/photo-1498049794561-7780e7231661?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=600&q=80",
            "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=600&q=80",
            "https://images.unsplash.com/photo-1523275335684-37898b6baf30?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=600&q=80"
        ],
        rating=4.6,
        reviewCount=289,
        priceRange="$$$",
        amenities=["Tech Support", "Installation", "Warranty", "Trade-In Program"],
        businessId="biz-12",
        createdAt=datetime.now().isoformat(),
        updatedAt=datetime.now().isoformat()
    ),
    # More Hotels
    Venue(
        id="13",
        name="City Center Plaza",
        type="hotel",
        description="Modern business hotel in the heart of downtown with conference facilities",
        address=Address(
            street="200 Business Blvd",
            city="Chicago",
            state="IL",
            zipCode="60601",
            country="USA"
        ),
        contact=ContactInfo(
            phone="+1-312-555-1300",
            email="info@citycenterplaza.com",
            website="https://citycenterplaza.com"
        ),
        images=[
            "https://images.unsplash.com/photo-1564501049412-61c2a3083791?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=600&q=80",
            "https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=600&q=80",
            "https://images.unsplash.com/photo-1611892440504-42a792e24d32?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=600&q=80"
        ],
        rating=4.4,
        reviewCount=187,
        priceRange="$$$",
        amenities=["Business Center", "Conference Rooms", "WiFi", "Gym", "Restaurant"],
        businessId="biz-13",
        createdAt=datetime.now().isoformat(),
        updatedAt=datetime.now().isoformat()
    ),
    Venue(
        id="14",
        name="Garden Inn",
        type="hotel",
        description="Charming boutique hotel with beautiful gardens and peaceful atmosphere",
        address=Address(
            street="150 Garden Lane",
            city="Portland",
            state="OR",
            zipCode="97201",
            country="USA"
        ),
        contact=ContactInfo(
            phone="+1-503-555-1400",
            email="info@gardeninn.com",
            website="https://gardeninn.com"
        ),
        images=[
            "https://images.unsplash.com/photo-1551882547-ec40ba82c093?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=600&q=80",
            "https://images.unsplash.com/photo-1566073771259-6a8506099945?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=600&q=80",
            "https://images.unsplash.com/photo-1611892440504-42a792e24d32?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=600&q=80"
        ],
        rating=4.5,
        reviewCount=156,
        priceRange="$$",
        amenities=["Garden", "Breakfast", "WiFi", "Parking", "Pet Friendly"],
        businessId="biz-14",
        createdAt=datetime.now().isoformat(),
        updatedAt=datetime.now().isoformat()
    ),
    # More Restaurants
    Venue(
        id="15",
        name="Pizza Palace",
        type="restaurant",
        description="Authentic New York style pizza with fresh ingredients and family recipes",
        address=Address(
            street="555 Pizza Street",
            city="New York",
            state="NY",
            zipCode="10004",
            country="USA"
        ),
        contact=ContactInfo(
            phone="+1-212-555-1500",
            email="orders@pizzapalace.com",
            website="https://pizzapalace.com"
        ),
        images=[
            "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=600&q=80",
            "https://images.unsplash.com/photo-1571997478779-1ac61a27d0d0?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=600&q=80",
            "https://images.unsplash.com/photo-1565299585323-38174c0a5e0e?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=600&q=80"
        ],
        rating=4.6,
        reviewCount=312,
        priceRange="$$",
        amenities=["Delivery", "Takeout", "Outdoor Seating", "Family Friendly"],
        businessId="biz-15",
        createdAt=datetime.now().isoformat(),
        updatedAt=datetime.now().isoformat()
    ),
    Venue(
        id="16",
        name="BBQ Smokehouse",
        type="restaurant",
        description="Texas-style barbecue with slow-smoked meats and homemade sides",
        address=Address(
            street="789 Smoke Road",
            city="Austin",
            state="TX",
            zipCode="78701",
            country="USA"
        ),
        contact=ContactInfo(
            phone="+1-512-555-1600",
            email="info@bbqsmokehouse.com",
            website="https://bbqsmokehouse.com"
        ),
        images=[
            "https://images.unsplash.com/photo-1546833999-b9f581a1996d?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=600&q=80",
            "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=600&q=80",
            "https://images.unsplash.com/photo-1555396273-367ea4eb3db5?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=600&q=80"
        ],
        rating=4.8,
        reviewCount=423,
        priceRange="$$$",
        amenities=["Outdoor Seating", "Live Music", "Catering", "Takeout"],
        businessId="biz-16",
        createdAt=datetime.now().isoformat(),
        updatedAt=datetime.now().isoformat()
    ),
    Venue(
        id="17",
        name="Vegan Delight",
        type="restaurant",
        description="Plant-based cuisine with creative dishes and sustainable practices",
        address=Address(
            street="321 Green Street",
            city="Los Angeles",
            state="CA",
            zipCode="90015",
            country="USA"
        ),
        contact=ContactInfo(
            phone="+1-213-555-1700",
            email="hello@vegandelight.com",
            website="https://vegandelight.com"
        ),
        images=[
            "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=600&q=80",
            "https://images.unsplash.com/photo-1555396273-367ea4eb3db5?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=600&q=80",
            "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=600&q=80"
        ],
        rating=4.7,
        reviewCount=234,
        priceRange="$$",
        amenities=["Vegan", "Gluten-Free Options", "Outdoor Seating", "WiFi"],
        businessId="biz-17",
        createdAt=datetime.now().isoformat(),
        updatedAt=datetime.now().isoformat()
    ),
    Venue(
        id="18",
        name="Seafood Harbor",
        type="restaurant",
        description="Fresh seafood restaurant with daily catches and ocean views",
        address=Address(
            street="888 Harbor Way",
            city="Boston",
            state="MA",
            zipCode="02101",
            country="USA"
        ),
        contact=ContactInfo(
            phone="+1-617-555-1800",
            email="reservations@seafoodharbor.com",
            website="https://seafoodharbor.com"
        ),
        images=[
            "https://images.unsplash.com/photo-1579584425555-c3ce17fd4351?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=600&q=80",
            "https://images.unsplash.com/photo-1579952363873-27f3bade9f55?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=600&q=80",
            "https://images.unsplash.com/photo-1414235077428-338989a2e8c0?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=600&q=80"
        ],
        rating=4.6,
        reviewCount=298,
        priceRange="$$$",
        amenities=["Ocean View", "Reservations", "Parking", "Wine Selection"],
        businessId="biz-18",
        createdAt=datetime.now().isoformat(),
        updatedAt=datetime.now().isoformat()
    ),
    # More Cafes
    Venue(
        id="19",
        name="Espresso Bar",
        type="cafe",
        description="Specialty coffee shop with expert baristas and artisanal roasts",
        address=Address(
            street="444 Coffee Ave",
            city="Seattle",
            state="WA",
            zipCode="98101",
            country="USA"
        ),
        contact=ContactInfo(
            phone="+1-206-555-1900",
            email="hello@espressobar.com"
        ),
        images=[
            "https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=600&q=80",
            "https://images.unsplash.com/photo-1447933601403-0c6688de566e?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=600&q=80",
            "https://images.unsplash.com/photo-1511920170033-f8396924c348?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=600&q=80"
        ],
        rating=4.7,
        reviewCount=201,
        priceRange="$$",
        amenities=["WiFi", "Laptop Friendly", "Pastries", "Loyalty Program"],
        businessId="biz-19",
        createdAt=datetime.now().isoformat(),
        updatedAt=datetime.now().isoformat()
    ),
    Venue(
        id="20",
        name="Smoothie Bowl",
        type="cafe",
        description="Healthy smoothie bowls and fresh juices with organic ingredients",
        address=Address(
            street="222 Health Street",
            city="San Diego",
            state="CA",
            zipCode="92101",
            country="USA"
        ),
        contact=ContactInfo(
            phone="+1-619-555-2000",
            email="hello@smoothiebowl.com"
        ),
        images=[
            "https://images.unsplash.com/photo-1509440159596-0249088772ff?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=600&q=80",
            "https://images.unsplash.com/photo-1555507036-ab1f4038808a?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=600&q=80",
            "https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=600&q=80"
        ],
        rating=4.5,
        reviewCount=178,
        priceRange="$$",
        amenities=["Vegan Options", "Gluten-Free", "Outdoor Seating", "WiFi"],
        businessId="biz-20",
        createdAt=datetime.now().isoformat(),
        updatedAt=datetime.now().isoformat()
    ),
    # More Retail
    Venue(
        id="21",
        name="Book Nook",
        type="retail",
        description="Independent bookstore with cozy reading nooks and author events",
        address=Address(
            street="111 Library Lane",
            city="Portland",
            state="OR",
            zipCode="97201",
            country="USA"
        ),
        contact=ContactInfo(
            phone="+1-503-555-2100",
            email="info@booknook.com",
            website="https://booknook.com"
        ),
        images=[
            "https://images.unsplash.com/photo-1481627834876-b7833e8f5570?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=600&q=80",
            "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=600&q=80",
            "https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=600&q=80"
        ],
        rating=4.6,
        reviewCount=145,
        priceRange="$$",
        amenities=["Reading Space", "Events", "Coffee", "Gift Cards"],
        businessId="biz-21",
        createdAt=datetime.now().isoformat(),
        updatedAt=datetime.now().isoformat()
    ),
    Venue(
        id="22",
        name="Sports Gear Pro",
        type="retail",
        description="Complete sports equipment store with expert fitting and advice",
        address=Address(
            street="999 Athletic Blvd",
            city="Denver",
            state="CO",
            zipCode="80201",
            country="USA"
        ),
        contact=ContactInfo(
            phone="+1-303-555-2200",
            email="info@sportsgearpro.com",
            website="https://sportsgearpro.com"
        ),
        images=[
            "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=600&q=80",
            "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=600&q=80",
            "https://images.unsplash.com/photo-1523275335684-37898b6baf30?ixlib=rb-4.0.3&auto=format&fit=crop&w=800&h=600&q=80"
        ],
        rating=4.5,
        reviewCount=267,
        priceRange="$$$",
        amenities=["Expert Fitting", "Equipment Rental", "Repair Service", "Loyalty Program"],
        businessId="biz-22",
        createdAt=datetime.now().isoformat(),
        updatedAt=datetime.now().isoformat()
    ),
]


@router.get("/recommendations")
async def get_recommendations() -> dict:
    """Get personalized venue recommendations."""
    recommendations = [
        Recommendation(
            id=f"rec-{venue.id}",
            venueId=venue.id,
            venue=venue,
            reason="Based on your preferences" if i == 0 else "Popular in your area",
            confidence=0.85 + (i * 0.05),
            category="personalized"
        )
        for i, venue in enumerate(MOCK_VENUES[:3])
    ]
    # Ensure proper serialization with mode='python' to get native Python types
    return {
        "data": [rec.model_dump(mode='python') for rec in recommendations],
        "message": "Recommendations retrieved successfully"
    }


@router.get("/trending")
async def get_trending(limit: int = Query(6, ge=1, le=50)) -> dict:
    """Get trending venues."""
    trending = MOCK_VENUES[:limit] if limit <= len(MOCK_VENUES) else MOCK_VENUES
    # Ensure proper serialization with mode='python' to get native Python types
    return {
        "data": [venue.model_dump(mode='python') for venue in trending],
        "message": "Trending venues retrieved successfully"
    }


@router.get("/{venue_id}")
async def get_venue(venue_id: str) -> dict:
    """Get venue by ID."""
    venue = next((v for v in MOCK_VENUES if v.id == venue_id), None)
    if not venue:
        return {"error": "Venue not found", "data": None}
    # Ensure proper serialization with mode='python' to get native Python types
    return {
        "data": venue.model_dump(mode='python'),
        "message": "Venue retrieved successfully"
    }


