from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from pathlib import Path
import json
import os

app = FastAPI(title="Ticket Booking App")

# Add middleware to prevent caching during development
class NoCacheMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        if request.url.path.startswith("/static") or request.url.path == "/":
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        return response

app.add_middleware(NoCacheMiddleware)

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Data models
class BookingRequest(BaseModel):
    name: str
    email: str
    date: str
    time: Optional[str] = None
    quantity: int
    additional_info: Optional[dict] = None

class BookingResponse(BaseModel):
    booking_id: str
    status: str
    message: str

# In-memory storage (in production, use a database)
bookings = {
    "movies": [],
    "trains": [],
    "flights": []
}

@app.get("/", response_class=HTMLResponse)
async def read_root():
    """Serve the main HTML page"""
    html_path = Path("templates/index.html")
    if not html_path.exists():
        raise HTTPException(status_code=500, detail="index.html not found")
    
    response = FileResponse(str(html_path))
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@app.get("/movies", response_class=HTMLResponse)
async def movies_page():
    """Serve the movies booking page"""
    return FileResponse("templates/movies.html")

@app.get("/trains", response_class=HTMLResponse)
async def trains_page():
    """Serve the trains booking page"""
    return FileResponse("templates/trains.html")

@app.get("/flights", response_class=HTMLResponse)
async def flights_page():
    """Serve the flights booking page"""
    return FileResponse("templates/flights.html")

@app.get("/profile", response_class=HTMLResponse)
async def profile_page():
    """Serve the profile/bookings page"""
    return FileResponse("templates/profile.html")

@app.post("/api/book/movie", response_model=BookingResponse)
async def book_movie(booking: BookingRequest):
    """Book a movie ticket"""
    booking_id = f"MOV{datetime.now().strftime('%Y%m%d%H%M%S')}"
    booking_data = {
        "booking_id": booking_id,
        "type": "movie",
        **booking.dict()
    }
    bookings["movies"].append(booking_data)
    return BookingResponse(
        booking_id=booking_id,
        status="success",
        message=f"Movie ticket booked successfully! Booking ID: {booking_id}"
    )

@app.post("/api/book/train", response_model=BookingResponse)
async def book_train(booking: BookingRequest):
    """Book a train ticket"""
    booking_id = f"TRN{datetime.now().strftime('%Y%m%d%H%M%S')}"
    booking_data = {
        "booking_id": booking_id,
        "type": "train",
        **booking.dict()
    }
    bookings["trains"].append(booking_data)
    return BookingResponse(
        booking_id=booking_id,
        status="success",
        message=f"Train ticket booked successfully! Booking ID: {booking_id}"
    )

@app.post("/api/book/flight", response_model=BookingResponse)
async def book_flight(booking: BookingRequest):
    """Book a flight ticket"""
    booking_id = f"FLT{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # Check if it's a round trip
    is_round_trip = booking.additional_info and booking.additional_info.get('trip_type') == 'round-trip'
    
    booking_data = {
        "booking_id": booking_id,
        "type": "flight",
        **booking.dict()
    }
    bookings["flights"].append(booking_data)
    
    # Create appropriate success message
    if is_round_trip:
        return_date = booking.additional_info.get('return_date', 'N/A')
        message = f"Round trip flight booked successfully! Booking ID: {booking_id}\nDeparture: {booking.date}, Return: {return_date}"
    else:
        message = f"One-way flight booked successfully! Booking ID: {booking_id}"
    
    return BookingResponse(
        booking_id=booking_id,
        status="success",
        message=message
    )

@app.get("/api/bookings/{booking_type}")
async def get_bookings(booking_type: str):
    """Get all bookings for a specific type"""
    if booking_type not in bookings:
        raise HTTPException(status_code=404, detail="Invalid booking type")
    return {"bookings": bookings[booking_type]}

@app.get("/api/bookings")
async def get_all_bookings():
    """Get all bookings for all types"""
    return {
        "movies": bookings["movies"],
        "trains": bookings["trains"],
        "flights": bookings["flights"]
    }

@app.delete("/api/cancel/{booking_type}/{booking_id}")
async def cancel_booking(booking_type: str, booking_id: str):
    """Cancel a booking by ID"""
    if booking_type not in bookings:
        raise HTTPException(status_code=404, detail="Invalid booking type")
    
    # Find and remove the booking
    booking_list = bookings[booking_type]
    for i, booking in enumerate(booking_list):
        if booking.get("booking_id") == booking_id:
            removed_booking = booking_list.pop(i)
            return {
                "status": "success",
                "message": f"Booking {booking_id} has been cancelled successfully",
                "booking_id": booking_id
            }
    
    raise HTTPException(status_code=404, detail="Booking not found")

# Common airports data
AIRPORTS = [
    # USA Airports
    {"code": "JFK", "name": "John F. Kennedy International Airport", "city": "New York", "country": "United States"},
    {"code": "LAX", "name": "Los Angeles International Airport", "city": "Los Angeles", "country": "United States"},
    {"code": "ORD", "name": "O'Hare International Airport", "city": "Chicago", "country": "United States"},
    {"code": "DFW", "name": "Dallas/Fort Worth International Airport", "city": "Dallas", "country": "United States"},
    {"code": "DEN", "name": "Denver International Airport", "city": "Denver", "country": "United States"},
    {"code": "SFO", "name": "San Francisco International Airport", "city": "San Francisco", "country": "United States"},
    {"code": "SEA", "name": "Seattle-Tacoma International Airport", "city": "Seattle", "country": "United States"},
    {"code": "LAS", "name": "McCarran International Airport", "city": "Las Vegas", "country": "United States"},
    {"code": "MIA", "name": "Miami International Airport", "city": "Miami", "country": "United States"},
    {"code": "ATL", "name": "Hartsfield-Jackson Atlanta International Airport", "city": "Atlanta", "country": "United States"},
    {"code": "BOS", "name": "Logan International Airport", "city": "Boston", "country": "United States"},
    {"code": "PHX", "name": "Phoenix Sky Harbor International Airport", "city": "Phoenix", "country": "United States"},
    {"code": "IAH", "name": "George Bush Intercontinental Airport", "city": "Houston", "country": "United States"},
    {"code": "MSP", "name": "Minneapolis-Saint Paul International Airport", "city": "Minneapolis", "country": "United States"},
    {"code": "DTW", "name": "Detroit Metropolitan Airport", "city": "Detroit", "country": "United States"},
    {"code": "PHL", "name": "Philadelphia International Airport", "city": "Philadelphia", "country": "United States"},
    {"code": "LGA", "name": "LaGuardia Airport", "city": "New York", "country": "United States"},
    {"code": "BWI", "name": "Baltimore-Washington International Airport", "city": "Baltimore", "country": "United States"},
    {"code": "SLC", "name": "Salt Lake City International Airport", "city": "Salt Lake City", "country": "United States"},
    {"code": "DCA", "name": "Ronald Reagan Washington National Airport", "city": "Washington", "country": "United States"},
    
    # Indian Airports
    {"code": "DEL", "name": "Indira Gandhi International Airport", "city": "New Delhi", "country": "India"},
    {"code": "BOM", "name": "Chhatrapati Shivaji Maharaj International Airport", "city": "Mumbai", "country": "India"},
    {"code": "BLR", "name": "Kempegowda International Airport", "city": "Bangalore", "country": "India"},
    {"code": "CCU", "name": "Netaji Subhas Chandra Bose International Airport", "city": "Kolkata", "country": "India"},
    {"code": "MAA", "name": "Chennai International Airport", "city": "Chennai", "country": "India"},
    {"code": "HYD", "name": "Rajiv Gandhi International Airport", "city": "Hyderabad", "country": "India"},
    {"code": "PNQ", "name": "Pune Airport", "city": "Pune", "country": "India"},
    {"code": "COK", "name": "Cochin International Airport", "city": "Kochi", "country": "India"},
    {"code": "GOI", "name": "Dabolim Airport", "city": "Goa", "country": "India"},
    {"code": "AMD", "name": "Sardar Vallabhbhai Patel International Airport", "city": "Ahmedabad", "country": "India"},
    {"code": "JAI", "name": "Jaipur International Airport", "city": "Jaipur", "country": "India"},
    {"code": "LKO", "name": "Chaudhary Charan Singh International Airport", "city": "Lucknow", "country": "India"},
    {"code": "IXC", "name": "Chandigarh Airport", "city": "Chandigarh", "country": "India"},
    {"code": "VNS", "name": "Lal Bahadur Shastri Airport", "city": "Varanasi", "country": "India"},
    {"code": "PAT", "name": "Jay Prakash Narayan Airport", "city": "Patna", "country": "India"},
    
    # European Airports
    {"code": "LHR", "name": "Heathrow Airport", "city": "London", "country": "United Kingdom"},
    {"code": "LGW", "name": "Gatwick Airport", "city": "London", "country": "United Kingdom"},
    {"code": "CDG", "name": "Charles de Gaulle Airport", "city": "Paris", "country": "France"},
    {"code": "ORY", "name": "Orly Airport", "city": "Paris", "country": "France"},
    {"code": "FRA", "name": "Frankfurt Airport", "city": "Frankfurt", "country": "Germany"},
    {"code": "MUC", "name": "Munich Airport", "city": "Munich", "country": "Germany"},
    {"code": "AMS", "name": "Amsterdam Airport Schiphol", "city": "Amsterdam", "country": "Netherlands"},
    {"code": "FCO", "name": "Leonardo da Vinci-Fiumicino Airport", "city": "Rome", "country": "Italy"},
    {"code": "MXP", "name": "Milan Malpensa Airport", "city": "Milan", "country": "Italy"},
    {"code": "MAD", "name": "Adolfo Suárez Madrid-Barajas Airport", "city": "Madrid", "country": "Spain"},
    {"code": "BCN", "name": "Barcelona-El Prat Airport", "city": "Barcelona", "country": "Spain"},
    {"code": "ZUR", "name": "Zurich Airport", "city": "Zurich", "country": "Switzerland"},
    {"code": "VIE", "name": "Vienna International Airport", "city": "Vienna", "country": "Austria"},
    {"code": "BRU", "name": "Brussels Airport", "city": "Brussels", "country": "Belgium"},
    {"code": "CPH", "name": "Copenhagen Airport", "city": "Copenhagen", "country": "Denmark"},
    {"code": "ARN", "name": "Stockholm Arlanda Airport", "city": "Stockholm", "country": "Sweden"},
    {"code": "OSL", "name": "Oslo Gardermoen Airport", "city": "Oslo", "country": "Norway"},
    {"code": "HEL", "name": "Helsinki Airport", "city": "Helsinki", "country": "Finland"},
    {"code": "DUB", "name": "Dublin Airport", "city": "Dublin", "country": "Ireland"},
    {"code": "LIS", "name": "Lisbon Airport", "city": "Lisbon", "country": "Portugal"},
    {"code": "ATH", "name": "Athens International Airport", "city": "Athens", "country": "Greece"},
    {"code": "PRG", "name": "Václav Havel Airport Prague", "city": "Prague", "country": "Czech Republic"},
    {"code": "WAW", "name": "Warsaw Chopin Airport", "city": "Warsaw", "country": "Poland"},
    {"code": "IST", "name": "Istanbul Airport", "city": "Istanbul", "country": "Turkey"},
    
    # Japanese Airports
    {"code": "NRT", "name": "Narita International Airport", "city": "Tokyo", "country": "Japan"},
    {"code": "HND", "name": "Haneda Airport", "city": "Tokyo", "country": "Japan"},
    {"code": "KIX", "name": "Kansai International Airport", "city": "Osaka", "country": "Japan"},
    {"code": "ITM", "name": "Osaka International Airport", "city": "Osaka", "country": "Japan"},
    {"code": "NGO", "name": "Chubu Centrair International Airport", "city": "Nagoya", "country": "Japan"},
    {"code": "FUK", "name": "Fukuoka Airport", "city": "Fukuoka", "country": "Japan"},
    {"code": "CTS", "name": "New Chitose Airport", "city": "Sapporo", "country": "Japan"},
    {"code": "OKA", "name": "Naha Airport", "city": "Okinawa", "country": "Japan"},
    {"code": "KOJ", "name": "Kagoshima Airport", "city": "Kagoshima", "country": "Japan"},
    {"code": "HIJ", "name": "Hiroshima Airport", "city": "Hiroshima", "country": "Japan"},
    {"code": "KMQ", "name": "Komatsu Airport", "city": "Kanazawa", "country": "Japan"},
    {"code": "SDJ", "name": "Sendai Airport", "city": "Sendai", "country": "Japan"},
    
    # Other Major Airports
    {"code": "DXB", "name": "Dubai International Airport", "city": "Dubai", "country": "United Arab Emirates"},
    {"code": "SYD", "name": "Sydney Kingsford Smith Airport", "city": "Sydney", "country": "Australia"},
    {"code": "MEL", "name": "Melbourne Airport", "city": "Melbourne", "country": "Australia"},
    {"code": "BNE", "name": "Brisbane Airport", "city": "Brisbane", "country": "Australia"},
    {"code": "PER", "name": "Perth Airport", "city": "Perth", "country": "Australia"},
    {"code": "SIN", "name": "Singapore Changi Airport", "city": "Singapore", "country": "Singapore"},
    {"code": "HKG", "name": "Hong Kong International Airport", "city": "Hong Kong", "country": "Hong Kong"},
    {"code": "BKK", "name": "Suvarnabhumi Airport", "city": "Bangkok", "country": "Thailand"},
    
    # Canadian Airports
    {"code": "YYZ", "name": "Toronto Pearson International Airport", "city": "Toronto", "country": "Canada"},
    {"code": "YVR", "name": "Vancouver International Airport", "city": "Vancouver", "country": "Canada"},
    {"code": "YUL", "name": "Montréal-Pierre Elliott Trudeau International Airport", "city": "Montreal", "country": "Canada"},
    {"code": "YYC", "name": "Calgary International Airport", "city": "Calgary", "country": "Canada"},
    {"code": "YEG", "name": "Edmonton International Airport", "city": "Edmonton", "country": "Canada"},
    {"code": "YOW", "name": "Ottawa Macdonald-Cartier International Airport", "city": "Ottawa", "country": "Canada"},
    {"code": "YHZ", "name": "Halifax Stanfield International Airport", "city": "Halifax", "country": "Canada"},
    
    # Mexican Airports
    {"code": "MEX", "name": "Mexico City International Airport", "city": "Mexico City", "country": "Mexico"},
    {"code": "CUN", "name": "Cancún International Airport", "city": "Cancun", "country": "Mexico"},
    {"code": "GDL", "name": "Guadalajara International Airport", "city": "Guadalajara", "country": "Mexico"},
    {"code": "MTY", "name": "Monterrey International Airport", "city": "Monterrey", "country": "Mexico"},
    {"code": "TIJ", "name": "Tijuana International Airport", "city": "Tijuana", "country": "Mexico"},
    
    # Brazilian Airports
    {"code": "GRU", "name": "São Paulo/Guarulhos International Airport", "city": "São Paulo", "country": "Brazil"},
    {"code": "GIG", "name": "Rio de Janeiro-Galeão International Airport", "city": "Rio de Janeiro", "country": "Brazil"},
    {"code": "BSB", "name": "Brasília International Airport", "city": "Brasília", "country": "Brazil"},
    {"code": "CNF", "name": "Belo Horizonte Airport", "city": "Belo Horizonte", "country": "Brazil"},
    {"code": "POA", "name": "Porto Alegre Airport", "city": "Porto Alegre", "country": "Brazil"},
    {"code": "FOR", "name": "Fortaleza Airport", "city": "Fortaleza", "country": "Brazil"},
    {"code": "REC", "name": "Recife Airport", "city": "Recife", "country": "Brazil"},
    
    # Chinese Airports
    {"code": "PEK", "name": "Beijing Capital International Airport", "city": "Beijing", "country": "China"},
    {"code": "PVG", "name": "Shanghai Pudong International Airport", "city": "Shanghai", "country": "China"},
    {"code": "CAN", "name": "Guangzhou Baiyun International Airport", "city": "Guangzhou", "country": "China"},
    {"code": "SZX", "name": "Shenzhen Bao'an International Airport", "city": "Shenzhen", "country": "China"},
    {"code": "CTU", "name": "Chengdu Shuangliu International Airport", "city": "Chengdu", "country": "China"},
    {"code": "XIY", "name": "Xi'an Xianyang International Airport", "city": "Xi'an", "country": "China"},
    {"code": "KMG", "name": "Kunming Changshui International Airport", "city": "Kunming", "country": "China"},
    {"code": "TAO", "name": "Qingdao Liuting International Airport", "city": "Qingdao", "country": "China"},
    
    # South Korean Airports
    {"code": "ICN", "name": "Incheon International Airport", "city": "Seoul", "country": "South Korea"},
    {"code": "GMP", "name": "Gimpo International Airport", "city": "Seoul", "country": "South Korea"},
    {"code": "PUS", "name": "Gimhae International Airport", "city": "Busan", "country": "South Korea"},
    {"code": "CJU", "name": "Jeju International Airport", "city": "Jeju", "country": "South Korea"},
    
    # Russian Airports
    {"code": "SVO", "name": "Sheremetyevo International Airport", "city": "Moscow", "country": "Russia"},
    {"code": "DME", "name": "Domodedovo International Airport", "city": "Moscow", "country": "Russia"},
    {"code": "LED", "name": "Pulkovo Airport", "city": "Saint Petersburg", "country": "Russia"},
    {"code": "KRR", "name": "Krasnodar International Airport", "city": "Krasnodar", "country": "Russia"},
    
    # South African Airports
    {"code": "JNB", "name": "O. R. Tambo International Airport", "city": "Johannesburg", "country": "South Africa"},
    {"code": "CPT", "name": "Cape Town International Airport", "city": "Cape Town", "country": "South Africa"},
    {"code": "DUR", "name": "King Shaka International Airport", "city": "Durban", "country": "South Africa"},
    
    # Egyptian Airports
    {"code": "CAI", "name": "Cairo International Airport", "city": "Cairo", "country": "Egypt"},
    {"code": "HRG", "name": "Hurghada International Airport", "city": "Hurghada", "country": "Egypt"},
    {"code": "LXR", "name": "Luxor International Airport", "city": "Luxor", "country": "Egypt"},
    
    # Malaysian Airports
    {"code": "KUL", "name": "Kuala Lumpur International Airport", "city": "Kuala Lumpur", "country": "Malaysia"},
    {"code": "PEN", "name": "Penang International Airport", "city": "Penang", "country": "Malaysia"},
    {"code": "BKI", "name": "Kota Kinabalu International Airport", "city": "Kota Kinabalu", "country": "Malaysia"},
    
    # Indonesian Airports
    {"code": "CGK", "name": "Soekarno-Hatta International Airport", "city": "Jakarta", "country": "Indonesia"},
    {"code": "DPS", "name": "Ngurah Rai International Airport", "city": "Denpasar", "country": "Indonesia"},
    {"code": "SUB", "name": "Juanda International Airport", "city": "Surabaya", "country": "Indonesia"},
    
    # Philippine Airports
    {"code": "MNL", "name": "Ninoy Aquino International Airport", "city": "Manila", "country": "Philippines"},
    {"code": "CEB", "name": "Mactan-Cebu International Airport", "city": "Cebu", "country": "Philippines"},
    
    # Vietnamese Airports
    {"code": "SGN", "name": "Tan Son Nhat International Airport", "city": "Ho Chi Minh City", "country": "Vietnam"},
    {"code": "HAN", "name": "Noi Bai International Airport", "city": "Hanoi", "country": "Vietnam"},
    
    # Argentine Airports
    {"code": "EZE", "name": "Ministro Pistarini International Airport", "city": "Buenos Aires", "country": "Argentina"},
    {"code": "AEP", "name": "Jorge Newbery Airfield", "city": "Buenos Aires", "country": "Argentina"},
    {"code": "COR", "name": "Ingeniero Ambrosio Taravella Airport", "city": "Córdoba", "country": "Argentina"},
]

# Common train stations data
TRAIN_STATIONS = [
    # USA Train Stations
    {"name": "New York Penn Station", "city": "New York", "code": "NYP", "country": "United States"},
    {"name": "Grand Central Terminal", "city": "New York", "code": "GCT", "country": "United States"},
    {"name": "Boston South Station", "city": "Boston", "code": "BOS", "country": "United States"},
    {"name": "Philadelphia 30th Street Station", "city": "Philadelphia", "code": "PHL", "country": "United States"},
    {"name": "Washington Union Station", "city": "Washington", "code": "WAS", "country": "United States"},
    {"name": "Chicago Union Station", "city": "Chicago", "code": "CHI", "country": "United States"},
    {"name": "Los Angeles Union Station", "city": "Los Angeles", "code": "LAX", "country": "United States"},
    {"name": "San Francisco Transbay Terminal", "city": "San Francisco", "code": "SFO", "country": "United States"},
    {"name": "Seattle King Street Station", "city": "Seattle", "code": "SEA", "country": "United States"},
    {"name": "Portland Union Station", "city": "Portland", "code": "PDX", "country": "United States"},
    {"name": "Denver Union Station", "city": "Denver", "code": "DEN", "country": "United States"},
    {"name": "Dallas Union Station", "city": "Dallas", "code": "DAL", "country": "United States"},
    {"name": "Houston Amtrak Station", "city": "Houston", "code": "HOU", "country": "United States"},
    {"name": "Atlanta Peachtree Station", "city": "Atlanta", "code": "ATL", "country": "United States"},
    {"name": "Miami Central Station", "city": "Miami", "code": "MIA", "country": "United States"},
    {"name": "Baltimore Penn Station", "city": "Baltimore", "code": "BAL", "country": "United States"},
    {"name": "Richmond Main Street Station", "city": "Richmond", "code": "RVM", "country": "United States"},
    {"name": "Charleston Amtrak Station", "city": "Charleston", "code": "CHS", "country": "United States"},
    {"name": "New Orleans Union Passenger Terminal", "city": "New Orleans", "code": "NOL", "country": "United States"},
    {"name": "Kansas City Union Station", "city": "Kansas City", "code": "KCY", "country": "United States"},
    
    # Indian Train Stations
    {"name": "New Delhi Railway Station", "city": "New Delhi", "code": "NDLS", "country": "India"},
    {"name": "Mumbai Central Station", "city": "Mumbai", "code": "BCT", "country": "India"},
    {"name": "Mumbai CST", "city": "Mumbai", "code": "CSTM", "country": "India"},
    {"name": "Bangalore City Junction", "city": "Bangalore", "code": "SBC", "country": "India"},
    {"name": "Howrah Junction", "city": "Kolkata", "code": "HWH", "country": "India"},
    {"name": "Sealdah Station", "city": "Kolkata", "code": "SDAH", "country": "India"},
    {"name": "Chennai Central", "city": "Chennai", "code": "MAS", "country": "India"},
    {"name": "Secunderabad Junction", "city": "Hyderabad", "code": "SC", "country": "India"},
    {"name": "Pune Junction", "city": "Pune", "code": "PUNE", "country": "India"},
    {"name": "Ahmedabad Junction", "city": "Ahmedabad", "code": "ADI", "country": "India"},
    {"name": "Jaipur Junction", "city": "Jaipur", "code": "JP", "country": "India"},
    {"name": "Lucknow Charbagh", "city": "Lucknow", "code": "LKO", "country": "India"},
    {"name": "Kanpur Central", "city": "Kanpur", "code": "CNB", "country": "India"},
    {"name": "Varanasi Junction", "city": "Varanasi", "code": "BSB", "country": "India"},
    {"name": "Patna Junction", "city": "Patna", "code": "PNBE", "country": "India"},
    {"name": "Chandigarh Railway Station", "city": "Chandigarh", "code": "CDG", "country": "India"},
    {"name": "Amritsar Junction", "city": "Amritsar", "code": "ASR", "country": "India"},
    {"name": "Jodhpur Junction", "city": "Jodhpur", "code": "JU", "country": "India"},
    {"name": "Udaipur City", "city": "Udaipur", "code": "UDZ", "country": "India"},
    {"name": "Kochi Junction", "city": "Kochi", "code": "ERS", "country": "India"},
    {"name": "Trivandrum Central", "city": "Thiruvananthapuram", "code": "TVC", "country": "India"},
    {"name": "Coimbatore Junction", "city": "Coimbatore", "code": "CBE", "country": "India"},
    {"name": "Madurai Junction", "city": "Madurai", "code": "MDU", "country": "India"},
    {"name": "Vijayawada Junction", "city": "Vijayawada", "code": "BZA", "country": "India"},
    {"name": "Visakhapatnam Junction", "city": "Visakhapatnam", "code": "VSKP", "country": "India"},
    {"name": "Krishnarajapuram Junction", "city": "Bangalore", "code": "KRJ", "country": "India"},
    
    # European Train Stations
    {"name": "London King's Cross", "city": "London", "code": "KGX", "country": "United Kingdom"},
    {"name": "London Paddington", "city": "London", "code": "PAD", "country": "United Kingdom"},
    {"name": "London St Pancras", "city": "London", "code": "STP", "country": "United Kingdom"},
    {"name": "Paris Gare du Nord", "city": "Paris", "code": "GND", "country": "France"},
    {"name": "Paris Gare de Lyon", "city": "Paris", "code": "GDL", "country": "France"},
    {"name": "Frankfurt Hauptbahnhof", "city": "Frankfurt", "code": "FHF", "country": "Germany"},
    {"name": "Munich Hauptbahnhof", "city": "Munich", "code": "MHF", "country": "Germany"},
    {"name": "Berlin Hauptbahnhof", "city": "Berlin", "code": "BHF", "country": "Germany"},
    {"name": "Amsterdam Centraal", "city": "Amsterdam", "code": "AMS", "country": "Netherlands"},
    {"name": "Rome Termini", "city": "Rome", "code": "RTE", "country": "Italy"},
    {"name": "Milan Centrale", "city": "Milan", "code": "MCE", "country": "Italy"},
    {"name": "Madrid Atocha", "city": "Madrid", "code": "MAD", "country": "Spain"},
    {"name": "Barcelona Sants", "city": "Barcelona", "code": "BCN", "country": "Spain"},
    {"name": "Zurich Hauptbahnhof", "city": "Zurich", "code": "ZHF", "country": "Switzerland"},
    {"name": "Vienna Hauptbahnhof", "city": "Vienna", "code": "VHF", "country": "Austria"},
    {"name": "Brussels Midi", "city": "Brussels", "code": "BRU", "country": "Belgium"},
    {"name": "Copenhagen Central", "city": "Copenhagen", "code": "CPH", "country": "Denmark"},
    {"name": "Stockholm Central", "city": "Stockholm", "code": "STO", "country": "Sweden"},
    {"name": "Oslo Central", "city": "Oslo", "code": "OSL", "country": "Norway"},
    {"name": "Helsinki Central", "city": "Helsinki", "code": "HEL", "country": "Finland"},
    {"name": "Dublin Heuston", "city": "Dublin", "code": "DUB", "country": "Ireland"},
    {"name": "Lisbon Oriente", "city": "Lisbon", "code": "LIS", "country": "Portugal"},
    {"name": "Athens Central", "city": "Athens", "code": "ATH", "country": "Greece"},
    {"name": "Prague hlavní nádraží", "city": "Prague", "code": "PRG", "country": "Czech Republic"},
    {"name": "Warsaw Centralna", "city": "Warsaw", "code": "WAW", "country": "Poland"},
    {"name": "Istanbul Sirkeci", "city": "Istanbul", "code": "IST", "country": "Turkey"},
    
    # Japanese Train Stations
    {"name": "Tokyo Station", "city": "Tokyo", "code": "TKY", "country": "Japan"},
    {"name": "Shinjuku Station", "city": "Tokyo", "code": "SJK", "country": "Japan"},
    {"name": "Shibuya Station", "city": "Tokyo", "code": "SBY", "country": "Japan"},
    {"name": "Ueno Station", "city": "Tokyo", "code": "UEN", "country": "Japan"},
    {"name": "Ikebukuro Station", "city": "Tokyo", "code": "IKB", "country": "Japan"},
    {"name": "Osaka Station", "city": "Osaka", "code": "OSA", "country": "Japan"},
    {"name": "Shin-Osaka Station", "city": "Osaka", "code": "SOS", "country": "Japan"},
    {"name": "Kyoto Station", "city": "Kyoto", "code": "KYO", "country": "Japan"},
    {"name": "Nagoya Station", "city": "Nagoya", "code": "NGO", "country": "Japan"},
    {"name": "Yokohama Station", "city": "Yokohama", "code": "YHM", "country": "Japan"},
    {"name": "Fukuoka Hakata Station", "city": "Fukuoka", "code": "FUK", "country": "Japan"},
    {"name": "Sapporo Station", "city": "Sapporo", "code": "SPO", "country": "Japan"},
    {"name": "Hiroshima Station", "city": "Hiroshima", "code": "HRS", "country": "Japan"},
    {"name": "Sendai Station", "city": "Sendai", "code": "SDJ", "country": "Japan"},
    {"name": "Kanazawa Station", "city": "Kanazawa", "code": "KMQ", "country": "Japan"},
    {"name": "Nara Station", "city": "Nara", "code": "NAR", "country": "Japan"},
    {"name": "Kobe Station", "city": "Kobe", "code": "KOB", "country": "Japan"},
    {"name": "Nagasaki Station", "city": "Nagasaki", "code": "NGS", "country": "Japan"},
    
    # Canadian Train Stations
    {"name": "Toronto Union Station", "city": "Toronto", "code": "TOR", "country": "Canada"},
    {"name": "Vancouver Pacific Central Station", "city": "Vancouver", "code": "VAN", "country": "Canada"},
    {"name": "Montreal Central Station", "city": "Montreal", "code": "MON", "country": "Canada"},
    {"name": "Ottawa Station", "city": "Ottawa", "code": "OTT", "country": "Canada"},
    {"name": "Calgary Station", "city": "Calgary", "code": "CAL", "country": "Canada"},
    {"name": "Edmonton Station", "city": "Edmonton", "code": "EDM", "country": "Canada"},
    {"name": "Winnipeg Union Station", "city": "Winnipeg", "code": "WIN", "country": "Canada"},
    {"name": "Halifax Station", "city": "Halifax", "code": "HAL", "country": "Canada"},
    
    # Mexican Train Stations
    {"name": "Mexico City Buenavista Station", "city": "Mexico City", "code": "MCB", "country": "Mexico"},
    {"name": "Guadalajara Station", "city": "Guadalajara", "code": "GDL", "country": "Mexico"},
    {"name": "Monterrey Station", "city": "Monterrey", "code": "MTY", "country": "Mexico"},
    {"name": "Puebla Station", "city": "Puebla", "code": "PUE", "country": "Mexico"},
    
    # Brazilian Train Stations
    {"name": "São Paulo Luz Station", "city": "São Paulo", "code": "SPL", "country": "Brazil"},
    {"name": "Rio de Janeiro Central Station", "city": "Rio de Janeiro", "code": "RJC", "country": "Brazil"},
    {"name": "Brasília Central Station", "city": "Brasília", "code": "BRC", "country": "Brazil"},
    {"name": "Belo Horizonte Central Station", "city": "Belo Horizonte", "code": "BHC", "country": "Brazil"},
    {"name": "Curitiba Station", "city": "Curitiba", "code": "CUR", "country": "Brazil"},
    {"name": "Porto Alegre Station", "city": "Porto Alegre", "code": "POA", "country": "Brazil"},
    
    # Chinese Train Stations
    {"name": "Beijing Railway Station", "city": "Beijing", "code": "BJS", "country": "China"},
    {"name": "Beijing South Railway Station", "city": "Beijing", "code": "BJS", "country": "China"},
    {"name": "Shanghai Railway Station", "city": "Shanghai", "code": "SHA", "country": "China"},
    {"name": "Shanghai Hongqiao Railway Station", "city": "Shanghai", "code": "SHQ", "country": "China"},
    {"name": "Guangzhou Railway Station", "city": "Guangzhou", "code": "GZR", "country": "China"},
    {"name": "Shenzhen North Railway Station", "city": "Shenzhen", "code": "SZN", "country": "China"},
    {"name": "Chengdu East Railway Station", "city": "Chengdu", "code": "CDE", "country": "China"},
    {"name": "Xi'an North Railway Station", "city": "Xi'an", "code": "XAN", "country": "China"},
    {"name": "Nanjing South Railway Station", "city": "Nanjing", "code": "NJS", "country": "China"},
    {"name": "Hangzhou East Railway Station", "city": "Hangzhou", "code": "HZE", "country": "China"},
    
    # South Korean Train Stations
    {"name": "Seoul Station", "city": "Seoul", "code": "SEL", "country": "South Korea"},
    {"name": "Yongsan Station", "city": "Seoul", "code": "YON", "country": "South Korea"},
    {"name": "Busan Station", "city": "Busan", "code": "BUS", "country": "South Korea"},
    {"name": "Incheon Station", "city": "Incheon", "code": "INC", "country": "South Korea"},
    {"name": "Daegu Station", "city": "Daegu", "code": "DAE", "country": "South Korea"},
    {"name": "Gwangju Station", "city": "Gwangju", "code": "GWJ", "country": "South Korea"},
    
    # Russian Train Stations
    {"name": "Moscow Leningradsky Station", "city": "Moscow", "code": "MLS", "country": "Russia"},
    {"name": "Moscow Kazansky Station", "city": "Moscow", "code": "MKS", "country": "Russia"},
    {"name": "Moscow Yaroslavsky Station", "city": "Moscow", "code": "MYS", "country": "Russia"},
    {"name": "Saint Petersburg Moskovsky Station", "city": "Saint Petersburg", "code": "SPM", "country": "Russia"},
    {"name": "Novosibirsk-Glavny Station", "city": "Novosibirsk", "code": "NVS", "country": "Russia"},
    {"name": "Yekaterinburg-Passazhirsky Station", "city": "Yekaterinburg", "code": "YEK", "country": "Russia"},
    
    # South African Train Stations
    {"name": "Johannesburg Park Station", "city": "Johannesburg", "code": "JHB", "country": "South Africa"},
    {"name": "Cape Town Station", "city": "Cape Town", "code": "CPT", "country": "South Africa"},
    {"name": "Pretoria Station", "city": "Pretoria", "code": "PRE", "country": "South Africa"},
    {"name": "Durban Station", "city": "Durban", "code": "DUR", "country": "South Africa"},
    
    # Egyptian Train Stations
    {"name": "Cairo Ramses Station", "city": "Cairo", "code": "CAI", "country": "Egypt"},
    {"name": "Alexandria Station", "city": "Alexandria", "code": "ALX", "country": "Egypt"},
    {"name": "Giza Station", "city": "Giza", "code": "GIZ", "country": "Egypt"},
    
    # Malaysian Train Stations
    {"name": "Kuala Lumpur Sentral", "city": "Kuala Lumpur", "code": "KLS", "country": "Malaysia"},
    {"name": "Butterworth Station", "city": "Butterworth", "code": "BTW", "country": "Malaysia"},
    {"name": "Johor Bahru Sentral", "city": "Johor Bahru", "code": "JBS", "country": "Malaysia"},
    
    # Indonesian Train Stations
    {"name": "Jakarta Gambir Station", "city": "Jakarta", "code": "JKG", "country": "Indonesia"},
    {"name": "Bandung Station", "city": "Bandung", "code": "BDG", "country": "Indonesia"},
    {"name": "Surabaya Gubeng Station", "city": "Surabaya", "code": "SBG", "country": "Indonesia"},
    {"name": "Yogyakarta Station", "city": "Yogyakarta", "code": "YGY", "country": "Indonesia"},
    
    # Philippine Train Stations
    {"name": "Manila Tutuban Station", "city": "Manila", "code": "MNT", "country": "Philippines"},
    {"name": "Cebu Station", "city": "Cebu", "code": "CEB", "country": "Philippines"},
    
    # Vietnamese Train Stations
    {"name": "Ho Chi Minh City Station", "city": "Ho Chi Minh City", "code": "HCM", "country": "Vietnam"},
    {"name": "Hanoi Station", "city": "Hanoi", "code": "HAN", "country": "Vietnam"},
    {"name": "Da Nang Station", "city": "Da Nang", "code": "DAN", "country": "Vietnam"},
    {"name": "Hue Station", "city": "Hue", "code": "HUE", "country": "Vietnam"},
    
    # Argentine Train Stations
    {"name": "Buenos Aires Retiro Station", "city": "Buenos Aires", "code": "BAR", "country": "Argentina"},
    {"name": "Buenos Aires Constitución Station", "city": "Buenos Aires", "code": "BAC", "country": "Argentina"},
    {"name": "Córdoba Station", "city": "Córdoba", "code": "COR", "country": "Argentina"},
    {"name": "Rosario Central Station", "city": "Rosario", "code": "ROS", "country": "Argentina"},
]

@app.get("/api/autocomplete/airports")
async def autocomplete_airports(query: str = Query(..., min_length=1), country: Optional[str] = Query(None)):
    """Autocomplete airports based on query and optional country filter"""
    query_lower = query.lower()
    results = []
    for airport in AIRPORTS:
        # Filter by country if provided
        if country:
            country_lower = country.lower()
            if "country" not in airport or country_lower not in airport.get("country", "").lower():
                continue
        
        if (query_lower in airport["code"].lower() or 
            query_lower in airport["name"].lower() or 
            query_lower in airport["city"].lower()):
            results.append({
                "code": airport["code"],
                "name": airport["name"],
                "city": airport["city"],
                "country": airport.get("country", ""),
                "display": f"{airport['name']} ({airport['code']}) - {airport['city']}"
            })
    return {"results": results[:10]}  # Limit to 10 results

@app.get("/api/autocomplete/train-stations")
async def autocomplete_train_stations(query: str = Query(..., min_length=1), country: Optional[str] = Query(None)):
    """Autocomplete train stations based on query and optional country filter"""
    query_lower = query.lower()
    results = []
    for station in TRAIN_STATIONS:
        # Filter by country if provided
        if country:
            country_lower = country.lower()
            if "country" not in station or country_lower not in station.get("country", "").lower():
                continue
        
        if (query_lower in station["name"].lower() or 
            query_lower in station["city"].lower() or
            query_lower in station["code"].lower()):
            results.append({
                "name": station["name"],
                "city": station["city"],
                "code": station["code"],
                "country": station.get("country", ""),
                "display": f"{station['name']} - {station['city']}"
            })
    return {"results": results[:10]}  # Limit to 10 results

@app.get("/api/countries")
async def get_countries():
    """Get list of all available countries from airports and train stations"""
    countries = set()
    
    # Get countries from airports
    for airport in AIRPORTS:
        if "country" in airport and airport["country"]:
            countries.add(airport["country"])
    
    # Get countries from train stations
    for station in TRAIN_STATIONS:
        if "country" in station and station["country"]:
            countries.add(station["country"])
    
    # Sort countries alphabetically
    sorted_countries = sorted(list(countries))
    return {"countries": sorted_countries}

@app.get("/api/images/{category}")
async def get_image(category: str):
    """Get a random image from Unsplash based on category"""
    try:
        # Using Unsplash Source API (no key required for basic usage)
        # Categories: movies, trains, flights
        search_terms = {
            "movies": "cinema movie theater",
            "trains": "train railway station",
            "flights": "airplane airport"
        }
        
        search_term = search_terms.get(category, "travel")
        # Using Unsplash Source API - random image by keyword
        image_url = f"https://source.unsplash.com/800x600/?{search_term}"
        
        return JSONResponse({
            "url": image_url,
            "category": category
        })
    except Exception as e:
        # Fallback images
        fallback_images = {
            "movies": "https://images.unsplash.com/photo-1489599849927-2ee91cede3ba?w=800&h=600&fit=crop",
            "trains": "https://images.unsplash.com/photo-1519904981063-b0cf448d479e?w=800&h=600&fit=crop",
            "flights": "https://images.unsplash.com/photo-1436491865332-7a61a109cc05?w=800&h=600&fit=crop"
        }
        return JSONResponse({
            "url": fallback_images.get(category, fallback_images["flights"]),
            "category": category
        })

if __name__ == "__main__":
    import uvicorn
    # Create necessary directories
    os.makedirs("static", exist_ok=True)
    os.makedirs("templates", exist_ok=True)
    uvicorn.run(app, host="0.0.0.0", port=8000)

